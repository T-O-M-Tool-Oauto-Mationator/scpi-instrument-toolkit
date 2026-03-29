"""Plot command: visualise measurement log data with matplotlib."""

import fnmatch

from lab_instruments.src.terminal import ColorPrinter

from .base import BaseCommand


class PlotCommand(BaseCommand):
    """Handler for the ``plot`` REPL command."""

    def execute(self, arg: str) -> None:
        """Plot measurements from the log.

        Syntax
        ------
        plot [label_pattern ...] [--title "text"]
        """
        args = self.parse_args(arg)
        args, help_flag = self.strip_help(args)

        if help_flag:
            self._show_help()
            return

        # ---- parse --title ------------------------------------------------
        title = "Measurements"
        patterns: list[str] = []
        i = 0
        while i < len(args):
            if args[i] == "--title" and i + 1 < len(args):
                title = args[i + 1]
                i += 2
            else:
                patterns.append(args[i])
                i += 1

        # ---- gather matching entries --------------------------------------
        entries = self.measurements.entries
        if not entries:
            ColorPrinter.warning("No measurements recorded — nothing to plot.")
            return

        if patterns:
            matched = [e for e in entries if any(fnmatch.fnmatch(e["label"], pat) for pat in patterns)]
        else:
            matched = list(entries)

        if not matched:
            ColorPrinter.warning(f"No measurements match pattern(s): {', '.join(patterns)}")
            return

        # ---- group by unit ------------------------------------------------
        units: dict[str, list[dict]] = {}
        for entry in matched:
            unit = entry.get("unit", "") or ""
            units.setdefault(unit, []).append(entry)

        # ---- import matplotlib lazily -------------------------------------
        try:
            import matplotlib.pyplot as plt
        except ImportError:  # pragma: no cover
            ColorPrinter.error("matplotlib is not installed.  Run:  pip install matplotlib")
            return

        # ---- plot ---------------------------------------------------------
        unit_keys = list(units.keys())
        n_units = len(unit_keys)

        if n_units == 1:
            fig, ax = plt.subplots()
            self._plot_series(ax, matched, title, unit_keys[0])
        else:
            fig, axes = plt.subplots(n_units, 1, sharex=False)
            if n_units == 1:
                axes = [axes]
            for ax, unit_key in zip(axes, unit_keys, strict=False):
                subtitle = f"{title} ({unit_key})" if unit_key else title
                self._plot_series(ax, units[unit_key], subtitle, unit_key)

        plt.tight_layout()
        plt.show(block=False)
        ColorPrinter.success("Plot window opened.")

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _plot_series(ax, entries: list[dict], title: str, unit: str) -> None:
        labels = [e["label"] for e in entries]
        values = [e["value"] for e in entries]
        indices = list(range(len(values)))

        ax.plot(indices, values, marker="o", linestyle="-")
        ax.set_title(title)
        ax.set_ylabel(unit if unit else "value")
        ax.set_xlabel("measurement")
        ax.set_xticks(indices)
        ax.set_xticklabels(labels, rotation=45 if len(labels) > 5 else 0, ha="right")

    def _show_help(self) -> None:
        self.print_colored_usage(
            [
                "# PLOT",
                "",
                "plot",
                "  - plot ALL logged measurements",
                "plot <pattern> [<pattern> ...]",
                "  - plot measurements whose label matches the glob pattern(s)",
                'plot --title "My Title"',
                "  - set the plot window title",
                "",
                "  Examples:",
                "    plot",
                "    plot linereg_*",
                "    plot loadreg_* ilim_*",
                '    plot linereg_* --title "Line Regulation"',
            ]
        )
