"""Variable inspector widget - shows current script variable bindings."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Label


class VarInspector(Widget):
    """Two-column DataTable showing {variable: value} script bindings.

    Updated reactively; polling is driven by the App.
    """

    DEFAULT_CSS = """
    VarInspector {
        height: 1fr;
        padding: 0 1;
    }
    VarInspector #var-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    VarInspector DataTable {
        height: 1fr;
    }
    """

    variables: reactive[dict[str, str]] = reactive(dict, layout=True)

    def compose(self) -> ComposeResult:
        yield Label("Variables", id="var-title")
        yield DataTable(id="var-table", zebra_stripes=True)

    def on_mount(self) -> None:
        table = self.query_one("#var-table", DataTable)
        table.add_columns("Variable", "Value")

    def watch_variables(self, variables: dict[str, str]) -> None:
        """Repopulate table rows whenever the snapshot changes."""
        table = self.query_one("#var-table", DataTable)
        table.clear()
        for var, val in sorted(variables.items()):
            table.add_row(var, str(val), key=var)
