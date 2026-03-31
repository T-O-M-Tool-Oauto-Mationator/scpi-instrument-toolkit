"""Tests for ScriptEditor widget and dispatcher script methods."""

from __future__ import annotations

import asyncio

from lab_instruments.tui.app import SCPIApp
from lab_instruments.tui.widgets.script_editor import ScriptEditor

# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class _StubDispatcher:
    """Stub with script load/save/delete support."""

    def __init__(self, scripts=None):
        self._commands: list[str] = []
        self._scripts: dict[str, str] = scripts or {}
        self._deleted: list[str] = []

    def handle_command(self, cmd: str, line_callback=None) -> str:
        self._commands.append(cmd)
        return f"OK: {cmd}"

    def get_completions(self, text: str) -> list[str]:
        return []

    def get_device_snapshot(self) -> list[dict]:
        return []

    def get_measurement_snapshot(self) -> list[dict]:
        return []

    def get_script_names(self) -> list[str]:
        return sorted(self._scripts.keys())

    def get_vars_snapshot(self) -> dict[str, str]:
        return {}

    def get_safety_snapshot(self) -> dict:
        return {
            "limit_count": 0,
            "active_script": False,
            "exit_on_error": False,
            "limits": [],
            "measurement_count": 0,
            "data_dir": "",
        }

    def get_script_content(self, name: str) -> str:
        return self._scripts.get(name, "")

    def save_script_content(self, name: str, content: str) -> None:
        self._scripts[name] = content

    def delete_script(self, name: str) -> None:
        self._scripts.pop(name, None)
        self._deleted.append(name)


# ---------------------------------------------------------------------------
# ScriptEditor widget tests
# ---------------------------------------------------------------------------


class TestScriptEditorWidget:
    def test_editor_mounts_in_app(self):
        """ScriptEditor should exist in the widget tree."""

        async def inner():
            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(120, 40)):
                editor = app.query_one(ScriptEditor)
                assert editor is not None

        asyncio.run(inner())

    def test_load_content_sets_text(self):
        """load_content should populate the TextArea."""

        async def inner():
            from textual.widgets import TextArea

            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(120, 40)):
                editor = app.query_one(ScriptEditor)
                editor.load_content("test_script", "psu set 5.0\npsu chan on\n")
                ta = editor.query_one("#editor-textarea", TextArea)
                assert "psu set 5.0" in ta.text
                assert "psu chan on" in ta.text

        asyncio.run(inner())

    def test_save_dispatches_to_app(self):
        """Save button should post SaveRequested message."""

        async def inner():
            scripts = {"my_test": "psu set 3.0"}
            stub = _StubDispatcher(scripts=scripts)
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                editor.load_content("my_test", "psu set 5.0\npsu chan on")
                await pilot.pause(0.1)

                # Post save message directly
                editor.post_message(ScriptEditor.SaveRequested("my_test", "psu set 5.0\npsu chan on"))
                await pilot.pause(0.2)

                assert stub._scripts["my_test"] == "psu set 5.0\npsu chan on"

        asyncio.run(inner())

    def test_run_dispatches_command(self):
        """Run button should dispatch 'run <name>' command."""

        async def inner():
            stub = _StubDispatcher(scripts={"demo": "scan"})
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                editor.post_message(ScriptEditor.RunRequested("demo"))
                await pilot.pause(0.2)

                assert "run demo" in stub._commands

        asyncio.run(inner())

    def test_delete_removes_script(self):
        """Delete button should remove the script."""

        async def inner():
            stub = _StubDispatcher(scripts={"old_script": "help"})
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                editor.post_message(ScriptEditor.DeleteRequested("old_script"))
                await pilot.pause(0.2)

                assert "old_script" in stub._deleted
                assert "old_script" not in stub._scripts

        asyncio.run(inner())

    def test_alt_e_toggles_editor_view(self):
        """Alt+E should toggle the editor tab."""

        async def inner():
            from textual.widgets import TabbedContent

            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(120, 40)) as pilot:
                tabbed = app.query_one("#main-content", TabbedContent)

                await app.run_action("show_editor")
                await pilot.pause(0.05)
                assert tabbed.active == "editor-view"

                await app.run_action("show_editor")
                await pilot.pause(0.05)
                assert tabbed.active == "log-view"

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Dispatcher script method regression tests
# ---------------------------------------------------------------------------


class TestDispatcherScriptMethods:
    def test_get_script_content(self):
        """get_script_content should return script text."""
        import time

        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        time.sleep(0.5)
        # Create a script via the context
        disp.repl.ctx.scripts["regression_test"] = ["psu set 5.0", "psu chan on"]
        content = disp.get_script_content("regression_test")
        assert "psu set 5.0" in content
        assert "psu chan on" in content

    def test_save_script_content(self):
        """save_script_content should persist to ctx.scripts."""
        import time

        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        time.sleep(0.5)
        disp.save_script_content("new_script", "scan\nlist\nhelp")
        assert "new_script" in disp.repl.ctx.scripts
        assert disp.repl.ctx.scripts["new_script"] == ["scan", "list", "help"]

    def test_delete_script(self):
        """delete_script should remove from ctx.scripts."""
        import time

        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        time.sleep(0.5)
        disp.repl.ctx.scripts["to_delete"] = ["help"]
        disp.delete_script("to_delete")
        assert "to_delete" not in disp.repl.ctx.scripts

    def test_get_script_names_still_works(self):
        """Existing get_script_names should still return sorted list."""
        import time

        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        time.sleep(0.5)
        disp.repl.ctx.scripts["beta"] = ["help"]
        disp.repl.ctx.scripts["alpha"] = ["scan"]
        names = disp.get_script_names()
        assert names.index("alpha") < names.index("beta")


# ---------------------------------------------------------------------------
# Regression: existing ScriptBrowser still works
# ---------------------------------------------------------------------------


class TestScriptBrowserRegression:
    def test_script_browser_still_mounts(self):
        """ScriptBrowser should still exist in the widget tree alongside ScriptEditor."""

        async def inner():
            from lab_instruments.tui.widgets.script_browser import ScriptBrowser

            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(120, 40)):
                browser = app.query_one(ScriptBrowser)
                assert browser is not None

        asyncio.run(inner())

    def test_script_browser_still_fires_selected(self):
        """ScriptBrowser should still post ScriptSelected when a script is clicked."""

        async def inner():
            from lab_instruments.tui.widgets.script_browser import ScriptBrowser

            stub = _StubDispatcher(scripts={"test_run": "help"})
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                browser = app.query_one(ScriptBrowser)
                browser.scripts = ["test_run"]
                await pilot.pause(0.1)

                # Simulate script selection
                browser.post_message(ScriptBrowser.ScriptSelected("test_run"))
                await pilot.pause(0.2)

                assert "run_script test_run" in stub._commands

        asyncio.run(inner())
