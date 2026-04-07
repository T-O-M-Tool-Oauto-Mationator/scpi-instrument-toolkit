"""Live-updating plot widgets backed by pyqtgraph.

Provides :class:`LivePlotWidget` — a self-contained, interactive chart that
polls the shared :class:`MeasurementStore` and redraws matched series on a
timer.  Users can rectangle-select a region and open it in a standalone
:class:`DetailPlotWindow` for editing, exporting, and CSV saving.
"""

from __future__ import annotations

import csv
import fnmatch
import math
import os
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPointF, QRectF, QTimer, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from lab_instruments.repl.measurement_store import MeasurementStore

try:
    import pyqtgraph as pg

    pg.setConfigOptions(antialias=True)
    _HAS_PG = True
except ImportError:
    pg = None  # type: ignore[assignment]
    _HAS_PG = False

# ---------------------------------------------------------------------------
# Styling constants
# ---------------------------------------------------------------------------

_BG = "#1e1e2e"
_SURFACE = "#181825"
_GRID_ALPHA = 0.15
_AXIS_PEN = "#6c7086"
_AXIS_TEXT = "#a6adc8"
_TITLE_COLOR = "#cdd6f4"
_LEGEND_TEXT = "#cdd6f4"
_CROSSHAIR_PEN = "#585b70"
_TOOLTIP_BG = "#313244"
_TOOLTIP_FG = "#cdd6f4"
_TOOLTIP_BORDER = "#45475a"
_SELECT_COLOR = QColor(255, 255, 255, 20)   # barely-visible white fill
_SELECT_BORDER = QColor(255, 255, 255, 180)  # crisp white border

_PALETTE = [
    "#2196F3",  # blue
    "#F44336",  # red
    "#4CAF50",  # green
    "#FF9800",  # orange
    "#9C27B0",  # purple
    "#00BCD4",  # cyan
    "#795548",  # brown
    "#607D8B",  # blue-grey
]

_DEFAULT_INTERVAL_MS = 250

_BTN_STYLE = """
    QPushButton {
        background: #313244; color: #cdd6f4; border: 1px solid #45475a;
        border-radius: 3px; padding: 3px 8px; font-size: 11px;
    }
    QPushButton:hover { background: #45475a; }
    QPushButton:pressed { background: #585b70; }
    QPushButton:checked { background: #585b70; border-color: #89b4fa; color: #89b4fa; }
"""
_BTN_ACCENT = """
    QPushButton {
        background: #89b4fa; color: #1e1e2e; border: 1px solid #89b4fa;
        border-radius: 3px; padding: 3px 8px; font-size: 11px; font-weight: bold;
    }
    QPushButton:hover { background: #b4d0fb; }
"""

_INFO_STYLE = "font-size: 10px; color: #6c7086;"
_COORD_STYLE = (
    "font-size: 11px; color: #a6adc8; font-family: 'JetBrains Mono', "
    "'Cascadia Code', 'Consolas', monospace;"
)
_TOOLTIP_STYLE = f"""
    background: {_TOOLTIP_BG}; color: {_TOOLTIP_FG};
    border: 1px solid {_TOOLTIP_BORDER}; border-radius: 4px;
    padding: 6px 10px; font-size: 11px;
    font-family: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
"""
_FIELD_STYLE = """
    QLineEdit {
        background: #313244; color: #cdd6f4; border: 1px solid #45475a;
        border-radius: 3px; padding: 4px 8px; font-size: 12px;
    }
    QLineEdit:focus { border-color: #89b4fa; }
"""
_DETAIL_BG = "background: #1e1e2e;"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _match_entries(
    entries: list[dict[str, Any]], patterns: list[str]
) -> dict[str, list[dict[str, Any]]]:
    """Return entries grouped by the pattern that matched them."""
    groups: dict[str, list[dict[str, Any]]] = {p: [] for p in patterns}
    for entry in entries:
        for pat in patterns:
            if fnmatch.fnmatch(entry["label"], pat):
                groups[pat].append(entry)
                break
    return groups


def _extract_series(
    entries: list[dict[str, Any]],
) -> tuple[list[float], list[float], list[str], str]:
    """Convert matched entries into (xs, ys, labels, unit)."""
    xs: list[float] = []
    ys: list[float] = []
    labels: list[str] = []
    unit = ""
    for entry in entries:
        try:
            y = float(entry["value"])
        except (ValueError, TypeError):
            continue
        x = entry.get("time")
        if x is None:
            x = float(len(xs))
        xs.append(x)
        ys.append(y)
        labels.append(entry.get("label", ""))
        if not unit:
            unit = entry.get("unit", "")
    return xs, ys, labels, unit


def _fmt(v: float) -> str:
    """Format a number compactly for display."""
    if abs(v) >= 1e6 or (0 < abs(v) < 1e-3):
        return f"{v:.4g}"
    if v == int(v):
        return f"{int(v)}"
    return f"{v:.4f}".rstrip("0").rstrip(".")


def _make_btn(text: str, width: int, slot=None, checkable: bool = False,
              style: str = _BTN_STYLE) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedWidth(width)
    btn.setStyleSheet(style)
    btn.setCheckable(checkable)
    if slot and not checkable:
        btn.clicked.connect(slot)
    return btn


def _vsep() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.VLine)
    sep.setStyleSheet("color: #45475a;")
    sep.setFixedWidth(1)
    return sep


# ---------------------------------------------------------------------------
# Floating tooltip label
# ---------------------------------------------------------------------------


class _Tooltip(QLabel):
    """Floating label that appears near a data point on click."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setStyleSheet(_TOOLTIP_STYLE)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hide()

    def show_at(self, pos, text: str) -> None:
        self.setText(text)
        self.adjustSize()
        x = int(pos.x()) + 12
        y = int(pos.y()) - self.height() - 8
        parent = self.parent()
        if parent:
            if x + self.width() > parent.width():
                x = int(pos.x()) - self.width() - 12
            if y < 0:
                y = int(pos.y()) + 16
        self.move(x, y)
        self.show()
        self.raise_()


# ---------------------------------------------------------------------------
# Detail Plot Window — standalone window for examining selected data
# ---------------------------------------------------------------------------


class DetailPlotWindow(QMainWindow):
    """Standalone plot window for examining a data segment.

    Features: editable title/axis labels, grid toggle, crosshair,
    export to PNG, save to CSV.
    """

    _open_windows: list[DetailPlotWindow] = []  # prevent GC

    def __init__(
        self,
        series: dict[str, tuple[list[float], list[float], list[str]]],
        title: str = "Detail View",
        xlabel: str = "Time (s)",
        ylabel: str = "",
    ) -> None:
        super().__init__()
        DetailPlotWindow._open_windows.append(self)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle(title)
        self.resize(900, 600)
        self.setStyleSheet(_DETAIL_BG)

        self._series = series

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(4)

        # -- Editable fields ------------------------------------------------
        fields = QHBoxLayout()
        fields.setSpacing(6)

        fields.addWidget(self._flabel("Title:"))
        self._title_edit = QLineEdit(title)
        self._title_edit.setStyleSheet(_FIELD_STYLE)
        self._title_edit.textChanged.connect(self._apply_labels)
        fields.addWidget(self._title_edit, 2)

        fields.addWidget(self._flabel("X:"))
        self._xlabel_edit = QLineEdit(xlabel)
        self._xlabel_edit.setStyleSheet(_FIELD_STYLE)
        self._xlabel_edit.textChanged.connect(self._apply_labels)
        fields.addWidget(self._xlabel_edit, 1)

        fields.addWidget(self._flabel("Y:"))
        self._ylabel_edit = QLineEdit(ylabel)
        self._ylabel_edit.setStyleSheet(_FIELD_STYLE)
        self._ylabel_edit.textChanged.connect(self._apply_labels)
        fields.addWidget(self._ylabel_edit, 1)

        root.addLayout(fields)

        # -- Plot -----------------------------------------------------------
        self._pw = pg.PlotWidget()
        self._pw.setBackground(_BG)
        self._pw.showGrid(x=True, y=True, alpha=_GRID_ALPHA)
        self._pw.setTitle(title, color=_TITLE_COLOR, size="12pt")
        self._pw.setMouseEnabled(x=True, y=True)
        for axis_name in ("bottom", "left"):
            ax = self._pw.getAxis(axis_name)
            ax.setPen(pg.mkPen(_AXIS_PEN))
            ax.setTextPen(pg.mkPen(_AXIS_TEXT))
        self._pw.setLabel("bottom", xlabel, color=_AXIS_TEXT)
        if ylabel:
            self._pw.setLabel("left", ylabel, color=_AXIS_TEXT)

        legend = self._pw.addLegend(offset=(10, 10))
        legend.setLabelTextColor(_LEGEND_TEXT)

        # Crosshair
        self._vline = pg.InfiniteLine(
            angle=90, movable=False,
            pen=pg.mkPen(_CROSSHAIR_PEN, width=1, style=Qt.PenStyle.DashLine),
        )
        self._hline = pg.InfiniteLine(
            angle=0, movable=False,
            pen=pg.mkPen(_CROSSHAIR_PEN, width=1, style=Qt.PenStyle.DashLine),
        )
        self._pw.addItem(self._vline, ignoreBounds=True)
        self._pw.addItem(self._hline, ignoreBounds=True)

        self._proxy = pg.SignalProxy(
            self._pw.scene().sigMouseMoved, rateLimit=60, slot=self._on_mouse_moved,
        )
        self._tooltip = _Tooltip(self._pw)
        self._pw.scene().sigMouseClicked.connect(self._on_click)

        # Plot the data
        total = 0
        for i, (pat, (xs, ys, labels)) in enumerate(series.items()):
            color = _PALETTE[i % len(_PALETTE)]
            self._pw.plot(
                xs, ys, pen=pg.mkPen(color=color, width=2),
                symbol="o", symbolSize=5, symbolBrush=color, name=pat,
            )
            total += len(xs)

        root.addWidget(self._pw, 1)

        # -- Coordinate readout ---------------------------------------------
        self._coord_label = QLabel("")
        self._coord_label.setStyleSheet(_COORD_STYLE)
        self._coord_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # -- Toolbar --------------------------------------------------------
        tb = QHBoxLayout()
        tb.setSpacing(4)

        self._grid_btn = _make_btn("Grid", 42, checkable=True)
        self._grid_btn.setChecked(True)
        self._grid_btn.clicked.connect(self._toggle_grid)
        tb.addWidget(self._grid_btn)

        self._cross_btn = _make_btn("Cross", 50, checkable=True)
        self._cross_btn.setChecked(True)
        self._cross_btn.clicked.connect(self._toggle_crosshair)
        tb.addWidget(self._cross_btn)

        tb.addWidget(_make_btn("Fit", 40, self._auto_fit))

        tb.addWidget(_vsep())

        tb.addWidget(_make_btn("Export PNG", 80, self._export_png))
        tb.addWidget(_make_btn("Save CSV", 72, self._save_csv))

        tb.addStretch()

        pts_label = QLabel(f"{total} points")
        pts_label.setStyleSheet(_INFO_STYLE)
        tb.addWidget(pts_label)

        tb.addWidget(_vsep())
        self._coord_label.setMinimumWidth(200)
        tb.addWidget(self._coord_label)

        root.addLayout(tb)

    @staticmethod
    def _flabel(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #a6adc8; font-size: 11px;")
        return lbl

    def _apply_labels(self) -> None:
        t = self._title_edit.text()
        self._pw.setTitle(t, color=_TITLE_COLOR, size="12pt")
        self.setWindowTitle(t or "Detail View")
        self._pw.setLabel("bottom", self._xlabel_edit.text(), color=_AXIS_TEXT)
        self._pw.setLabel("left", self._ylabel_edit.text(), color=_AXIS_TEXT)

    def _toggle_grid(self) -> None:
        on = self._grid_btn.isChecked()
        self._pw.showGrid(x=on, y=on, alpha=_GRID_ALPHA if on else 0)

    def _toggle_crosshair(self) -> None:
        on = self._cross_btn.isChecked()
        self._vline.setVisible(on)
        self._hline.setVisible(on)
        if not on:
            self._coord_label.setText("")

    def _auto_fit(self) -> None:
        self._pw.enableAutoRange(axis="xy", enable=True)

    def _on_mouse_moved(self, evt) -> None:
        pos = evt[0]
        if not self._pw.sceneBoundingRect().contains(pos):
            return
        pt = self._pw.plotItem.vb.mapSceneToView(pos)
        if self._cross_btn.isChecked():
            self._vline.setPos(pt.x())
            self._hline.setPos(pt.y())
            self._coord_label.setText(f"x={_fmt(pt.x())}  y={_fmt(pt.y())}")

    def _on_click(self, evt) -> None:
        if evt.double():
            self._auto_fit()
            self._tooltip.hide()
            return
        pos = evt.scenePos()
        if not self._pw.sceneBoundingRect().contains(pos):
            self._tooltip.hide()
            return
        pt = self._pw.plotItem.vb.mapSceneToView(pos)
        mx, my = pt.x(), pt.y()
        vr = self._pw.plotItem.vb.viewRange()
        xr = vr[0][1] - vr[0][0]
        yr = vr[1][1] - vr[1][0]
        if xr == 0 or yr == 0:
            return
        best_d, best_info, best_spos = float("inf"), None, None
        for pat, (xs, ys, labels) in self._series.items():
            for x, y, lbl in zip(xs, ys, labels):
                d = math.hypot((x - mx) / xr, (y - my) / yr)
                if d < best_d:
                    best_d = d
                    best_info = f"{lbl}\nvalue: {_fmt(y)}\ntime:  {_fmt(x)}s\nseries: {pat}"
                    best_spos = self._pw.plotItem.vb.mapViewToScene(pg.Point(x, y))
        if best_d < 0.05 and best_info and best_spos:
            self._tooltip.show_at(self._pw.mapFromScene(best_spos), best_info)
        else:
            self._tooltip.hide()

    def _export_png(self) -> None:
        import pyqtgraph.exporters as exporters
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Plot",
            f"{self._title_edit.text() or 'detail'}.png",
            "PNG Image (*.png);;All Files (*)",
        )
        if not path:
            return
        exporter = exporters.ImageExporter(self._pw.plotItem)
        exporter.parameters()["width"] = 1920
        exporter.export(path)

    def _save_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV",
            f"{self._title_edit.text() or 'detail'}.csv",
            "CSV Files (*.csv);;All Files (*)",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["series", "label", "time", "value"])
            for pat, (xs, ys, labels) in self._series.items():
                for x, y, lbl in zip(xs, ys, labels):
                    w.writerow([pat, lbl, x, y])

    def closeEvent(self, event) -> None:  # noqa: N802
        if self in DetailPlotWindow._open_windows:
            DetailPlotWindow._open_windows.remove(self)
        super().closeEvent(event)


# ---------------------------------------------------------------------------
# Main live-plot widget
# ---------------------------------------------------------------------------


class LivePlotWidget(QWidget):
    """Interactive pyqtgraph chart that auto-refreshes from the measurement store.

    Interactions
    ------------
    * **Scroll** to zoom, **drag** to pan.
    * **Hover** to see crosshair + coordinate readout.
    * **Click** a data point to inspect its label, value, and time.
    * **Double-click** to auto-fit the view to all data.
    * **Select** mode: click two corners to draw a rectangle, then open the
      selected data in a :class:`DetailPlotWindow` for editing and export.
    """

    def __init__(
        self,
        measurements: MeasurementStore,
        patterns: list[str],
        title: str = "Live Plot",
        xlabel: str = "",
        ylabel: str = "",
        interval_ms: int = _DEFAULT_INTERVAL_MS,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._measurements = measurements
        self._patterns = patterns
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._paused = False
        # Start from current store size — only show data recorded after this widget opens
        self._clear_offset: int = len(measurements) if measurements else 0
        self._seen: int = self._clear_offset
        self._series_data: dict[str, tuple[list[float], list[float], list[str]]] = {}
        self._series_visible: dict[str, bool] = {p: True for p in patterns}

        # Selection state
        self._select_mode = False
        self._sel_corner1: QPointF | None = None
        self._sel_bounds: tuple[float, float, float, float] | None = None  # x1,y1,x2,y2
        self._sel_outline: pg.PlotDataItem | None = None
        self._sel_fill: pg.FillBetweenItem | None = None
        self._sel_preview_outline: pg.PlotDataItem | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        if not _HAS_PG:
            layout.addWidget(
                QLabel("pyqtgraph is required.  pip install pyqtgraph")
            )
            return

        # -- Plot area ------------------------------------------------------
        self._pw: pg.PlotWidget = pg.PlotWidget()
        self._pw.setBackground(_BG)
        self._pw.showGrid(x=True, y=True, alpha=_GRID_ALPHA)
        self._pw.setTitle(title, color=_TITLE_COLOR, size="12pt")
        self._pw.setMouseEnabled(x=True, y=True)
        self._pw.enableAutoRange(axis="xy", enable=True)

        for axis_name in ("bottom", "left"):
            ax = self._pw.getAxis(axis_name)
            ax.setPen(pg.mkPen(_AXIS_PEN))
            ax.setTextPen(pg.mkPen(_AXIS_TEXT))

        if xlabel:
            self._pw.setLabel("bottom", xlabel, color=_AXIS_TEXT)
        else:
            self._pw.setLabel("bottom", "Time (s)", color=_AXIS_TEXT)
        if ylabel:
            self._pw.setLabel("left", ylabel, color=_AXIS_TEXT)

        self._legend = self._pw.addLegend(offset=(10, 10))
        self._legend.setLabelTextColor(_LEGEND_TEXT)

        layout.addWidget(self._pw, 1)

        # -- Crosshair ------------------------------------------------------
        self._crosshair_on = True
        self._vline = pg.InfiniteLine(
            angle=90, movable=False,
            pen=pg.mkPen(_CROSSHAIR_PEN, width=1, style=Qt.PenStyle.DashLine),
        )
        self._hline = pg.InfiniteLine(
            angle=0, movable=False,
            pen=pg.mkPen(_CROSSHAIR_PEN, width=1, style=Qt.PenStyle.DashLine),
        )
        self._pw.addItem(self._vline, ignoreBounds=True)
        self._pw.addItem(self._hline, ignoreBounds=True)

        # -- Coordinate readout + tooltip -----------------------------------
        self._coord_label = QLabel("")
        self._coord_label.setStyleSheet(_COORD_STYLE)
        self._coord_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._tooltip = _Tooltip(self._pw)

        # -- Mouse tracking -------------------------------------------------
        self._proxy = pg.SignalProxy(
            self._pw.scene().sigMouseMoved, rateLimit=60, slot=self._on_mouse_moved,
        )
        self._pw.scene().sigMouseClicked.connect(self._on_mouse_clicked)
        self._pw.plotItem.vb.sigRangeChanged.connect(self._on_range_changed)

        # -- Curves ---------------------------------------------------------
        self._curves: dict[str, pg.PlotDataItem] = {}
        for i, pat in enumerate(patterns):
            color = _PALETTE[i % len(_PALETTE)]
            pen = pg.mkPen(color=color, width=2)
            curve = self._pw.plot(
                [], [], pen=pen, symbol="o", symbolSize=5,
                symbolBrush=color, name=pat,
            )
            self._curves[pat] = curve

        # -- Toolbar --------------------------------------------------------
        tb = QHBoxLayout()
        tb.setContentsMargins(0, 2, 0, 0)
        tb.setSpacing(4)

        self._pause_btn = _make_btn("Pause", 64, checkable=True)
        self._pause_btn.clicked.connect(self._toggle_pause)
        tb.addWidget(self._pause_btn)

        tb.addWidget(_make_btn("Clear", 50, self._clear))
        tb.addWidget(_make_btn("Fit", 40, self._auto_fit))
        tb.addWidget(_make_btn("Export", 56, self._export_png))

        tb.addWidget(_vsep())

        self._select_btn = _make_btn("Select", 56, checkable=True)
        self._select_btn.setToolTip("Click two corners to select a region, then open it in a detail window")
        self._select_btn.clicked.connect(self._toggle_select)
        tb.addWidget(self._select_btn)

        self._open_sel_btn = _make_btn("Open Selection", 100, self._open_selection, style=_BTN_ACCENT)
        self._open_sel_btn.setVisible(False)
        self._open_sel_btn.setToolTip("Open selected data in a new detail window")
        tb.addWidget(self._open_sel_btn)

        tb.addWidget(_vsep())

        self._cross_btn = _make_btn("Cross", 50, checkable=True)
        self._cross_btn.setChecked(True)
        self._cross_btn.clicked.connect(self._toggle_crosshair)
        tb.addWidget(self._cross_btn)

        self._grid_btn = _make_btn("Grid", 42, checkable=True)
        self._grid_btn.setChecked(True)
        self._grid_btn.clicked.connect(self._toggle_grid)
        tb.addWidget(self._grid_btn)

        tb.addWidget(_vsep())

        # Series toggle buttons
        if len(patterns) > 1:
            for i, pat in enumerate(patterns):
                color = _PALETTE[i % len(_PALETTE)]
                btn = QPushButton(pat)
                btn.setStyleSheet(
                    _BTN_STYLE + f"QPushButton {{ border-left: 3px solid {color}; }}"
                    f"QPushButton:checked {{ border-left: 3px solid {color}; }}"
                )
                btn.setCheckable(True)
                btn.setChecked(True)
                btn.clicked.connect(lambda checked, p=pat: self._toggle_series(p, checked))
                btn.setToolTip(f"Show/hide {pat}")
                tb.addWidget(btn)
            tb.addWidget(_vsep())

        rl = QLabel("Refresh:")
        rl.setStyleSheet(_INFO_STYLE)
        tb.addWidget(rl)
        self._rate_spin = QSpinBox()
        self._rate_spin.setRange(1, 30)
        self._rate_spin.setSingleStep(1)
        self._rate_spin.setValue(max(1, 1000 // interval_ms))
        self._rate_spin.setMinimumWidth(52)
        self._rate_spin.valueChanged.connect(self._on_rate_changed)
        self._rate_spin.setToolTip("Refreshes per second")
        tb.addWidget(self._rate_spin)

        tb.addStretch()

        self._coord_label.setMinimumWidth(200)
        tb.addWidget(self._coord_label)

        tb.addWidget(_vsep())

        self._info = QLabel("")
        self._info.setStyleSheet(_INFO_STYLE)
        tb.addWidget(self._info)

        layout.addLayout(tb)

        # -- Poll timer -----------------------------------------------------
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(interval_ms)
        self._update()

    # -----------------------------------------------------------------
    # Toolbar actions
    # -----------------------------------------------------------------

    def _toggle_pause(self) -> None:
        self._paused = self._pause_btn.isChecked()
        self._pause_btn.setText("Resume" if self._paused else "Pause")

    def _clear(self) -> None:
        for curve in self._curves.values():
            curve.setData([], [])
        self._series_data.clear()
        self._clear_offset = len(self._measurements.entries)
        self._seen = self._clear_offset
        self._tooltip.hide()
        self._clear_selection()
        self._info.setText("Cleared")

    def _auto_fit(self) -> None:
        self._pw.enableAutoRange(axis="xy", enable=True)

    def _toggle_crosshair(self) -> None:
        self._crosshair_on = self._cross_btn.isChecked()
        self._vline.setVisible(self._crosshair_on)
        self._hline.setVisible(self._crosshair_on)
        if not self._crosshair_on:
            self._coord_label.setText("")

    def _toggle_grid(self) -> None:
        on = self._grid_btn.isChecked()
        self._pw.showGrid(x=on, y=on, alpha=_GRID_ALPHA if on else 0)

    def _toggle_series(self, pattern: str, visible: bool) -> None:
        self._series_visible[pattern] = visible
        curve = self._curves.get(pattern)
        if curve:
            curve.setVisible(visible)

    def _export_png(self) -> None:
        import pyqtgraph.exporters as exporters

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Plot", f"{self._title}.png",
            "PNG Image (*.png);;All Files (*)",
        )
        if not path:
            return
        exporter = exporters.ImageExporter(self._pw.plotItem)
        exporter.parameters()["width"] = 1920
        exporter.export(path)
        self._info.setText(f"Saved: {os.path.basename(path)}")

    def _on_rate_changed(self, hz: int) -> None:
        ms = max(33, 1000 // max(1, hz))
        self._timer.setInterval(ms)

    # -----------------------------------------------------------------
    # Selection mode
    # -----------------------------------------------------------------

    def _toggle_select(self) -> None:
        self._select_mode = self._select_btn.isChecked()
        if self._select_mode:
            self._sel_corner1 = None
            self._clear_selection_rect()
            self._open_sel_btn.setVisible(False)
            # Disable pan/zoom while selecting
            self._pw.setMouseEnabled(x=False, y=False)
            self._info.setText("Click first corner...")
        else:
            self._pw.setMouseEnabled(x=True, y=True)
            self._clear_selection_rect()
            self._clear_preview()
            self._open_sel_btn.setVisible(False)

    def _clear_selection(self) -> None:
        self._select_mode = False
        self._select_btn.setChecked(False)
        self._sel_corner1 = None
        self._sel_bounds = None
        self._remove_sel_items()
        self._remove_preview()
        self._open_sel_btn.setVisible(False)
        self._pw.setMouseEnabled(x=True, y=True)

    def _remove_sel_items(self) -> None:
        if self._sel_outline is not None:
            self._pw.removeItem(self._sel_outline)
            self._sel_outline = None
        if self._sel_fill is not None:
            self._pw.removeItem(self._sel_fill)
            self._sel_fill = None

    def _remove_preview(self) -> None:
        if self._sel_preview_outline is not None:
            self._pw.removeItem(self._sel_preview_outline)
            self._sel_preview_outline = None

    def _draw_rect(self, p1: QPointF, p2: QPointF, preview: bool = False) -> None:
        x1, x2 = min(p1.x(), p2.x()), max(p1.x(), p2.x())
        y1, y2 = min(p1.y(), p2.y()), max(p1.y(), p2.y())

        # Rectangle as a closed polygon in data coordinates
        rect_xs = [x1, x2, x2, x1, x1]
        rect_ys = [y1, y1, y2, y2, y1]

        if preview:
            self._remove_preview()
            self._sel_preview_outline = self._pw.plot(
                rect_xs, rect_ys,
                pen=pg.mkPen(color="#ffffff", width=1, style=Qt.PenStyle.DashLine),
            )
        else:
            self._remove_sel_items()
            self._remove_preview()
            self._sel_bounds = (x1, y1, x2, y2)
            self._sel_outline = self._pw.plot(
                rect_xs, rect_ys,
                pen=pg.mkPen(color="#ffffff", width=1.5),
            )
            # Fill between top and bottom edges
            top = pg.PlotCurveItem([x1, x2], [y2, y2])
            bot = pg.PlotCurveItem([x1, x2], [y1, y1])
            self._sel_fill = pg.FillBetweenItem(
                top, bot, brush=QBrush(_SELECT_COLOR),
            )
            self._pw.addItem(self._sel_fill)

    def _extract_selection(self) -> dict[str, tuple[list[float], list[float], list[str]]]:
        """Return series data clipped to the selection rectangle."""
        if self._sel_bounds is None:
            return {}
        x1, y1, x2, y2 = self._sel_bounds

        result: dict[str, tuple[list[float], list[float], list[str]]] = {}
        for pat, (xs, ys, labels) in self._series_data.items():
            if not self._series_visible.get(pat, True):
                continue
            sel_x, sel_y, sel_l = [], [], []
            for x, y, lbl in zip(xs, ys, labels):
                if x1 <= x <= x2 and y1 <= y <= y2:
                    sel_x.append(x)
                    sel_y.append(y)
                    sel_l.append(lbl)
            if sel_x:
                result[pat] = (sel_x, sel_y, sel_l)
        return result

    def _open_selection(self) -> None:
        """Open selected data in a standalone detail window."""
        selected = self._extract_selection()
        if not selected:
            self._info.setText("No data in selection")
            return

        total = sum(len(xs) for xs, _, _ in selected.values())
        win = DetailPlotWindow(
            selected,
            title=f"{self._title} — Selection ({total} pts)",
            xlabel=self._xlabel or "Time (s)",
            ylabel=self._ylabel,
        )
        win.show()
        self._clear_selection()
        self._info.setText(f"Opened detail view ({total} pts)")

    # -----------------------------------------------------------------
    # Mouse interaction
    # -----------------------------------------------------------------

    def _on_mouse_moved(self, evt) -> None:
        pos = evt[0]
        if not self._pw.sceneBoundingRect().contains(pos):
            return
        mouse_point = self._pw.plotItem.vb.mapSceneToView(pos)
        mx, my = mouse_point.x(), mouse_point.y()

        if self._crosshair_on:
            self._vline.setPos(mx)
            self._hline.setPos(my)
            self._coord_label.setText(f"x={_fmt(mx)}  y={_fmt(my)}")

        # Draw preview rectangle while selecting
        if self._select_mode and self._sel_corner1 is not None:
            self._draw_rect(self._sel_corner1, QPointF(mx, my), preview=True)

    def _on_mouse_clicked(self, evt) -> None:
        pos = evt.scenePos()
        if not self._pw.sceneBoundingRect().contains(pos):
            self._tooltip.hide()
            return

        mouse_point = self._pw.plotItem.vb.mapSceneToView(pos)

        # --- Selection mode ---
        if self._select_mode:
            if self._sel_corner1 is None:
                # First click — set corner 1
                self._sel_corner1 = QPointF(mouse_point.x(), mouse_point.y())
                self._info.setText("Click second corner...")
            else:
                # Second click — finalize rectangle
                corner2 = QPointF(mouse_point.x(), mouse_point.y())
                self._draw_rect(self._sel_corner1, corner2, preview=False)
                self._sel_corner1 = None
                self._select_mode = False
                self._select_btn.setChecked(False)
                self._pw.setMouseEnabled(x=True, y=True)

                selected = self._extract_selection()
                total = sum(len(xs) for xs, _, _ in selected.values())
                if total > 0:
                    self._open_sel_btn.setVisible(True)
                    self._info.setText(f"Selected {total} pts — click Open Selection")
                else:
                    self._info.setText("No data in selection — try again")
                    self._clear_selection_rect()
            return

        # --- Normal mode ---
        if evt.double():
            self._auto_fit()
            self._tooltip.hide()
            return

        mx, my = mouse_point.x(), mouse_point.y()

        # Find nearest point
        best_dist = float("inf")
        best_info: str | None = None
        best_screen_pos = None

        vb = self._pw.plotItem.vb
        view_range = vb.viewRange()
        x_range = view_range[0][1] - view_range[0][0]
        y_range = view_range[1][1] - view_range[1][0]
        if x_range == 0 or y_range == 0:
            return

        for pat, data in self._series_data.items():
            if not self._series_visible.get(pat, True):
                continue
            xs, ys, labels = data
            for x, y, lbl in zip(xs, ys, labels):
                dx = (x - mx) / x_range
                dy = (y - my) / y_range
                d = math.hypot(dx, dy)
                if d < best_dist:
                    best_dist = d
                    unit_str = self._ylabel or ""
                    best_info = (
                        f"{lbl}\n"
                        f"value: {_fmt(y)}{(' ' + unit_str) if unit_str else ''}\n"
                        f"time:  {_fmt(x)}s\n"
                        f"series: {pat}"
                    )
                    best_screen_pos = vb.mapViewToScene(pg.Point(x, y))

        if best_dist < 0.05 and best_info and best_screen_pos:
            widget_pos = self._pw.mapFromScene(best_screen_pos)
            self._tooltip.show_at(widget_pos, best_info)
        else:
            self._tooltip.hide()

    def _on_range_changed(self) -> None:
        self._tooltip.hide()

    # -----------------------------------------------------------------
    # Data refresh
    # -----------------------------------------------------------------

    def _update(self) -> None:
        if self._paused:
            return

        entries = self._measurements.entries
        if len(entries) == self._seen:
            return
        self._seen = len(entries)

        # Only show entries recorded after the last clear
        visible_entries = entries[self._clear_offset:]
        groups = _match_entries(visible_entries, self._patterns)
        total_points = 0
        detected_unit = ""

        for pat, curve in self._curves.items():
            matched = groups.get(pat, [])
            if not matched:
                continue

            xs, ys, labels, unit = _extract_series(matched)
            if xs:
                self._series_data[pat] = (xs, ys, labels)
                curve.setData(xs, ys)
                total_points += len(xs)
            if unit and not detected_unit:
                detected_unit = unit

        if detected_unit and not self._ylabel:
            self._pw.setLabel("left", detected_unit, color=_AXIS_TEXT)

        self._info.setText(
            f"{total_points} pts | {', '.join(self._patterns)}"
        )

    # -----------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------

    def stop(self) -> None:
        """Stop the refresh timer and release resources."""
        self._timer.stop()
