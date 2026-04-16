"""Logging commands: log, calc, check, report, data."""

import contextlib
import os
import re

from lab_instruments.src.terminal import ColorPrinter

from ..syntax import safe_eval, substitute_vars
from .base import BaseCommand


class LoggingCommands(BaseCommand):
    """Handles log, calc, check, report, data commands."""

    def do_data(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        has_dir_prefix = bool(args and args[0].lower() == "dir")
        if has_dir_prefix:
            args = args[1:]
        if help_flag or not args:
            ColorPrinter.cyan(f"Current data dir: {os.path.abspath(self.ctx.get_data_dir())}")
            self.print_colored_usage(
                [
                    "# DATA DIR",
                    "",
                    "data dir",
                    "  - show the current output directory",
                    "data dir <path>",
                    "  - set the output directory",
                    "data dir reset",
                    "  - restore the default output directory",
                    "",
                    "  Affects: scope screenshot, scope save, log save",
                ]
            )
            return
        path = self.raw_path_arg(arg, strip_word="dir" if has_dir_prefix else None)
        if not path:
            ColorPrinter.error("No path provided.")
            return
        if path.lower() == "reset":
            self.ctx._data_dir_override = None
            ColorPrinter.success(f"Data dir reset to default: {self.ctx.get_data_dir()}")
        else:
            resolved = os.path.abspath(path)
            try:
                os.makedirs(resolved, exist_ok=True)
                self.ctx._data_dir_override = resolved
                ColorPrinter.success(f"Data dir set to: {resolved}")
            except Exception as exc:
                ColorPrinter.error(f"Cannot use '{resolved}': {exc}")

    def do_log(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if help_flag or not args:
            self.print_colored_usage(
                [
                    "# LOG",
                    "",
                    "log print",
                    "  - display all stored measurements in a formatted table",
                    "log save <path> [csv|txt]",
                    "  - export measurements to a file",
                    "log clear",
                    "  - erase all stored measurements from this session",
                ]
            )
            return
        cmd_name = args[0].lower()
        if cmd_name == "clear":
            self.measurements.clear()
            ColorPrinter.success("Cleared measurements.")
            return
        if cmd_name == "print":
            if not self.measurements:
                ColorPrinter.warning("No measurements recorded.")
                return
            C, G, Y, R = ColorPrinter.CYAN, ColorPrinter.GREEN, ColorPrinter.YELLOW, ColorPrinter.RESET
            header = f"{'Label':<24} {'Value':>14} {'Unit':<8} {'Source':<12}"
            print(f"{Y}{header}{R}")
            print(f"{Y}{'-' * len(header)}{R}")
            for entry in self.measurements.entries:
                label = entry.get("label", "")
                value = entry.get("value", "")
                unit = entry.get("unit", "")
                source = entry.get("source", "")
                print(f"{C}{label:<24}{R} {G}{value:>14}{R} {Y}{unit:<8}{R} {source:<12}")
            return
        if cmd_name == "save" and len(args) >= 2:
            path = args[1]
            fmt = args[2].lower() if len(args) >= 3 else ""
            if not fmt:
                _, ext = os.path.splitext(path)
                fmt = ext.lstrip(".").lower()
            if fmt not in ("csv", "txt"):
                ColorPrinter.warning("log save expects format csv or txt.")
                return
            if not self.measurements:
                ColorPrinter.warning("No measurements recorded.")
                return
            if not os.path.isabs(path):
                # Resolve relative to script dir when running a script, else data dir
                base = self.ctx.get_scripts_dir() if self.ctx.in_script else self.ctx.get_data_dir()
                path = os.path.join(base, path)
            try:
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    if fmt == "csv":
                        handle.write("label,value,unit,source\n")
                        for entry in self.measurements.entries:
                            handle.write(
                                f"{entry.get('label', '')},{entry.get('value', '')},{entry.get('unit', '')},{entry.get('source', '')}\n"
                            )
                    else:
                        header = f"{'Label':<24} {'Value':>14} {'Unit':<8} {'Source':<12}"
                        handle.write(header + "\n")
                        handle.write("-" * len(header) + "\n")
                        for entry in self.measurements.entries:
                            handle.write(
                                f"{entry.get('label', ''):<24} {entry.get('value', ''):>14} {entry.get('unit', ''):<8} {entry.get('source', ''):<12}\n"
                            )
                ColorPrinter.success(f"Saved measurements to {os.path.abspath(path)}.")
            except Exception as exc:
                ColorPrinter.error(f"Failed to save measurements: {exc}")
            return
        ColorPrinter.warning(f"Unknown log command: log {arg}. Use: log print|save|clear")

    def do_calc(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if help_flag or len(args) < 2:
            self.print_colored_usage(
                [
                    "# CALC — compute a derived value and log it",
                    "",
                    "calc <label> = <expression> [unit=<str>]",
                    "  - label   : name for the result (stored in log + variables)",
                    "  - expression : any math expression using variable/label names",
                    "  - unit=   : optional unit string shown in log print",
                    "",
                    "  Tip: you can also write this as a plain assignment:",
                    "    power = psu_v * psu_i unit=W",
                    "  Both forms are equivalent; the plain assignment is preferred.",
                    "",
                    "  Examples:",
                    "    calc power = psu_v * psu_i unit=W",
                    "    calc error = (dmm_v - psu_v) / psu_v * 100 unit=%",
                    "    calc gain_db = 20 * log10(v_out / v_in) unit=dB",
                    "    calc rms = sqrt((v1**2 + v2**2) / 2) unit=V",
                ]
            )
            return
        label = args[0]
        # Handle optional = sign
        expr_args = args[1:]
        if expr_args and expr_args[0] == "=":
            expr_args = expr_args[1:]
        unit = ""
        for token in expr_args:
            if token.lower().startswith("unit="):
                unit = token.split("=", 1)[1]
        # Build expression from raw arg, stripping label and unit=
        raw = arg.strip()
        raw_after_label = re.sub(r"^\S+\s*", "", raw, count=1)
        # Strip optional = sign
        if raw_after_label.startswith("= ") or raw_after_label == "=" or raw_after_label.startswith("="):
            raw_after_label = raw_after_label[1:].lstrip()
        expr = re.sub(r"(?<!\S)unit=\S+", "", raw_after_label).strip()
        if not expr:
            ColorPrinter.warning("calc expects an expression.")
            return
        # Substitute {name} variables in expr
        expr = substitute_vars(expr, self.ctx.script_vars, self.ctx.measurements)
        last_entry = self.measurements.get_last()
        last = last_entry["value"] if last_entry else 0
        # Build names: last + script_vars (numeric) + measurement labels
        names: dict = {"last": last}
        for k, v in self.ctx.script_vars.items():
            with contextlib.suppress(TypeError, ValueError):
                names[k] = float(v)
        for entry in self.ctx.measurements.entries:
            with contextlib.suppress(TypeError, ValueError):
                names[entry["label"]] = float(entry["value"])
        try:
            value = safe_eval(expr, names)
            self.measurements.record(label, value, unit, "calc")
            self.ctx.script_vars[label] = str(value)
            suffix = f" {unit}" if unit else ""
            C, G, Y, R = ColorPrinter.CYAN, ColorPrinter.GREEN, ColorPrinter.YELLOW, ColorPrinter.RESET
            print(f"{C}{label}{R} = {G}{value}{R}{Y}{suffix}{R}")
        except Exception as exc:
            ColorPrinter.error(f"calc failed: {exc}")

    def do_check(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if help_flag or len(args) < 3:
            self.print_colored_usage(
                [
                    "# CHECK — pass/fail assertion on a stored measurement",
                    "",
                    "check <label> <min> <max>          # pass if min ≤ value ≤ max",
                    "check <label> <expected> tol=<N>   # pass if |value - expected| ≤ N",
                    "check <label> <expected> tol=<N>%  # pass if |value - expected| ≤ N/100 * expected",
                ]
            )
            return
        label = args[0]
        entry = self.measurements.get_by_label(label)
        if entry is None:
            ColorPrinter.error(f"check: no measurement found with label '{label}'")
            self.ctx.command_had_error = True
            return
        value = float(entry["value"])
        unit = entry.get("unit", "")
        tol_arg = None
        for a in args[2:]:
            if a.lower().startswith("tol="):
                tol_arg = a.split("=", 1)[1]
                break
        if tol_arg is not None:
            try:
                expected = float(args[1])
            except ValueError:
                ColorPrinter.error(f"check: invalid expected value '{args[1]}'")
                self.ctx.command_had_error = True
                return
            if tol_arg.endswith("%"):
                pct = float(tol_arg[:-1])
                tol = abs(pct / 100.0 * expected)
                limits_str = f"{expected} ±{pct}%"
            else:
                tol = float(tol_arg)
                limits_str = f"{expected} ±{tol}"
            min_val = expected - tol
            max_val = expected + tol
        else:
            if len(args) < 3:
                ColorPrinter.error("check: expected <label> <min> <max>")
                self.ctx.command_had_error = True
                return
            try:
                min_val = float(args[1])
                max_val = float(args[2])
            except ValueError:
                ColorPrinter.error(f"check: invalid range values '{args[1]}' '{args[2]}'")
                self.ctx.command_had_error = True
                return
            limits_str = f"[{min_val}, {max_val}]"
        passed = min_val <= value <= max_val
        G, R_COL, RST = ColorPrinter.GREEN, ColorPrinter.RED, ColorPrinter.RESET
        C, Y = ColorPrinter.CYAN, ColorPrinter.YELLOW
        unit_str = f" {unit}" if unit else ""
        status_str = f"{G}[PASS]{RST}" if passed else f"{R_COL}[FAIL]{RST}"
        print(f"{status_str} {C}{label}{RST} = {value}{unit_str}  limits: {Y}{limits_str}{RST}")
        self.ctx.test_results.append(
            {
                "label": label,
                "value": value,
                "unit": unit,
                "min": min_val,
                "max": max_val,
                "passed": passed,
                "limits_str": limits_str,
            }
        )
        if not passed:
            self.ctx.command_had_error = True

    def do_report(self, arg: str) -> None:
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)
        if help_flag or not args:
            self.print_colored_usage(
                [
                    "# REPORT — view or export a lab test report",
                    "",
                    "report print                  # print check results table to terminal",
                    "report save <path>            # generate PDF report",
                    "report clear                  # clear test results and screenshot list",
                    "report title <text>           # set report title",
                    "report operator <name>        # set operator name shown in report header",
                ]
            )
            return
        sub = args[0].lower()
        if sub == "print":
            self._report_print()
        elif sub == "save":
            if len(args) < 2:
                ColorPrinter.error("report save requires a path argument.")
                return
            path = args[1]
            if not os.path.isabs(path):
                path = os.path.join(self.ctx.get_data_dir(), path)
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            try:
                self._generate_pdf_report(path)
                ColorPrinter.success(f"Report saved to {path}")
            except ImportError:
                ColorPrinter.error("fpdf2 is required for PDF reports. Install: pip install fpdf2")
            except Exception as exc:
                ColorPrinter.error(f"Failed to generate report: {exc}")
        elif sub == "clear":
            self.ctx.test_results = []
            self.ctx.report_screenshots = []
            ColorPrinter.success("Cleared test results and screenshots.")
        elif sub == "title":
            if len(args) < 2:
                ColorPrinter.error("report title requires text.")
                return
            self.ctx.report_title = " ".join(args[1:])
            ColorPrinter.success(f"Report title set to: {self.ctx.report_title}")
        elif sub == "operator":
            if len(args) < 2:
                ColorPrinter.error("report operator requires a name.")
                return
            self.ctx.report_operator = " ".join(args[1:])
            ColorPrinter.success(f"Report operator set to: {self.ctx.report_operator}")
        else:
            ColorPrinter.warning(f"Unknown report sub-command: {sub}")

    def _report_print(self) -> None:
        if not self.ctx.test_results:
            ColorPrinter.warning("No check results recorded.")
            return
        C, G, R, Y, RST = (
            ColorPrinter.CYAN,
            ColorPrinter.GREEN,
            ColorPrinter.RED,
            ColorPrinter.YELLOW,
            ColorPrinter.RESET,
        )
        header = f"{'Label':<20} {'Value':>14} {'Unit':<8} {'Limits':<22} {'Status'}"
        print(f"{Y}{header}{RST}")
        print("-" * len(header))
        for tr in self.ctx.test_results:
            status = f"{G}PASS{RST}" if tr["passed"] else f"{R}FAIL{RST}"
            unit_s = tr["unit"] or ""
            print(f"{C}{tr['label']:<20}{RST} {tr['value']:>14g} {unit_s:<8} {tr['limits_str']:<22} {status}")
        total = len(self.ctx.test_results)
        n_pass = sum(1 for t in self.ctx.test_results if t["passed"])
        n_fail = total - n_pass
        verdict = f"{G}PASS{RST}" if n_fail == 0 else f"{R}FAIL{RST}"
        print(f"\nOverall: {verdict}  ({n_pass}/{total} passed)")

    def _generate_pdf_report(self, path: str) -> None:
        import datetime

        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 12, self.ctx.report_title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 11)
        if self.ctx.report_operator:
            pdf.cell(0, 7, f"Operator: {self.ctx.report_operator}", new_x="LMARGIN", new_y="NEXT", align="C")
        ts = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        pdf.cell(0, 7, f"Generated: {ts}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(4)

        total = len(self.ctx.test_results)
        n_pass = sum(1 for t in self.ctx.test_results if t["passed"])
        n_fail = total - n_pass
        verdict = "PASS" if (total > 0 and n_fail == 0) else ("FAIL" if total > 0 else "N/A")
        if verdict == "PASS":
            pdf.set_fill_color(34, 139, 34)
            pdf.set_text_color(255, 255, 255)
        elif verdict == "FAIL":
            pdf.set_fill_color(180, 30, 30)
            pdf.set_text_color(255, 255, 255)
        else:
            pdf.set_fill_color(180, 180, 180)
            pdf.set_text_color(50, 50, 50)
        pdf.set_font("Helvetica", "B", 28)
        pdf.cell(0, 18, verdict, new_x="LMARGIN", new_y="NEXT", align="C", fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(
            0, 7, f"{n_pass} passed  /  {n_fail} failed  /  {total} total", new_x="LMARGIN", new_y="NEXT", align="C"
        )
        pdf.ln(6)

        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Check Results", new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(180, 180, 180)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(2)
        if not self.ctx.test_results:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 7, "No checks recorded.", new_x="LMARGIN", new_y="NEXT")
        else:
            col_w = [60, 28, 18, 52, 22]
            headers = ["Label", "Value", "Unit", "Limits", "Status"]
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(220, 220, 220)
            for w, h in zip(col_w, headers, strict=True):
                pdf.cell(w, 7, h, border=1, fill=True)
            pdf.ln()
            pdf.set_font("Helvetica", "", 10)
            for tr in self.ctx.test_results:
                passed_flag = tr["passed"]
                pdf.cell(col_w[0], 7, str(tr["label"]), border=1)
                pdf.cell(col_w[1], 7, f"{tr['value']:.6g}", border=1, align="R")
                pdf.cell(col_w[2], 7, str(tr["unit"]), border=1)
                pdf.cell(col_w[3], 7, str(tr["limits_str"]), border=1)
                if passed_flag:
                    pdf.set_fill_color(200, 240, 200)
                    pdf.set_text_color(0, 120, 0)
                else:
                    pdf.set_fill_color(255, 200, 200)
                    pdf.set_text_color(160, 0, 0)
                pdf.cell(col_w[4], 7, "PASS" if passed_flag else "FAIL", border=1, fill=True, align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.ln()
        pdf.ln(6)

        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "All Measurements", new_x="LMARGIN", new_y="NEXT")
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(2)
        if not self.measurements:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 7, "No measurements recorded.", new_x="LMARGIN", new_y="NEXT")
        else:
            col_w2 = [65, 55, 30, 40]
            headers2 = ["Label", "Value", "Unit", "Source"]
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(220, 220, 220)
            for w, h in zip(col_w2, headers2, strict=True):
                pdf.cell(w, 7, h, border=1, fill=True)
            pdf.ln()
            pdf.set_font("Helvetica", "", 10)
            for m in self.measurements.entries:
                pdf.cell(col_w2[0], 7, str(m["label"]), border=1)
                pdf.cell(col_w2[1], 7, f"{m['value']:.6g}", border=1, align="R")
                pdf.cell(col_w2[2], 7, str(m.get("unit", "")), border=1)
                pdf.cell(col_w2[3], 7, str(m.get("source", "")), border=1)
                pdf.ln()
        pdf.ln(6)

        valid_shots = [p for p in self.ctx.report_screenshots if os.path.isfile(p)]
        if valid_shots:
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, "Scope Screenshots", new_x="LMARGIN", new_y="NEXT")
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(2)
            page_w = pdf.w - pdf.l_margin - pdf.r_margin
            for shot_path in valid_shots:
                caption = os.path.basename(shot_path)
                pdf.add_page()
                pdf.set_font("Helvetica", "I", 9)
                pdf.cell(0, 6, caption, new_x="LMARGIN", new_y="NEXT", align="C")
                try:
                    pdf.image(shot_path, x=pdf.l_margin, w=page_w)
                except Exception:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.cell(0, 7, f"[Could not embed image: {caption}]", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)

        pdf.output(path)
