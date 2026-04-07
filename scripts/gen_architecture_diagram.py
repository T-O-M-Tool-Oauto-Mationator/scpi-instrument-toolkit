"""Generate the architecture layer diagram as a PNG for docs."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── palette (teal family, dark→light bottom→top) ───────────────────────────
LAYERS = [
    # (layer_tag, title, items, bg, fg)
    (
        "Layer 0",
        "Hardware & OS Interfaces",
        ["Physical instruments (oscilloscopes, PSUs, DMMs, AWGs, SMUs)",
         "NI-VISA / USBTMC  ·  USB HID (/dev/hidrawN, hid.dll)  ·  NI PXIe chassis"],
        "#004D40", "#FFFFFF",
    ),
    (
        "Layer 1",
        "Transport Libraries",
        ["pyvisa  — VISA session management (USB, GPIB, Serial)",
         "ctypes + OS HID APIs  — byte-level I/O for TI EV2300 (no pip needed)",
         "nidcpower  — NI official Python SDK for PXIe-4139 SMU"],
        "#00695C", "#FFFFFF",
    ),
    (
        "Layer 2",
        "Instrument Drivers  (lab_instruments/src/)",
        ["SCPI drivers (inherit DeviceManager via pyvisa):",
         "  HP_E3631A · HP_34401A · Rigol_DHO804 · Keysight_EDU33212A",
         "  Keysight_DSOX1204G · Keysight_EDU36311A · Tektronix_MSO2024",
         "  MATRIX_MPS6010H · BK_4063 · Owon_XDM1041 · JDS6600_Generator",
         "Non-SCPI drivers (own transport):",
         "  TI_EV2300 (ctypes/HID)  ·  NI_PXIe_4139 (nidcpower)",
         "Shared:  DeviceManager (base)  ·  discovery.py  ·  mock_instruments.py"],
        "#00897B", "#FFFFFF",
    ),
    (
        "Layer 3",
        "REPL Session Layer  (lab_instruments/repl/)",
        ["commands/  — psu · awg · dmm · scope · smu · ev2300 · scripting · logging",
         "ReplContext / DeviceRegistry  — live instrument map + active selection",
         "ScriptEngine  — loops, variables, for/while/if/repeat directives",
         "MeasurementStore  — labelled log, CSV export, calc expressions",
         "SafetySystem  — voltage/current limits, interlock checks"],
        "#26A69A", "#FFFFFF",
    ),
    (
        "Layer 4",
        "Frontends",
        ["REPL / CLI  (scpi-repl)              → Layer 3 (commands)",
         "GUI  (scpi-gui, Tkinter)              → Layer 3 + direct Layer 2 for live polling",
         "LabVIEW bridge  (labview_bridge.py)   → Layer 3 (wraps REPL commands for Python Node)",
         "Python scripts  (import lab_instruments) → direct Layer 2 access"],
        "#4DB6AC", "#003330",
    ),
]

FIG_W, FIG_H = 15, 11
BAND_H = FIG_H / len(LAYERS)
LEFT_PAD = 1.2   # space for layer badge on left
RIGHT_PAD = 0.25
TITLE_X = LEFT_PAD + 0.15

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")
fig.patch.set_facecolor("#ECEFF1")

for i, (tag, title, items, bg, fg) in enumerate(LAYERS):
    y_bottom = i * BAND_H
    band_w = FIG_W - RIGHT_PAD

    # Main band
    rect = FancyBboxPatch(
        (0.1, y_bottom + 0.07), band_w - 0.1, BAND_H - 0.14,
        boxstyle="round,pad=0.06",
        linewidth=0,
        facecolor=bg,
        zorder=1,
    )
    ax.add_patch(rect)

    # Left badge
    badge = FancyBboxPatch(
        (0.18, y_bottom + 0.15), LEFT_PAD - 0.38, BAND_H - 0.30,
        boxstyle="round,pad=0.05",
        linewidth=0,
        facecolor="#FFFFFF",
        alpha=0.15,
        zorder=2,
    )
    ax.add_patch(badge)

    ax.text(
        0.18 + (LEFT_PAD - 0.38) / 2,
        y_bottom + BAND_H / 2,
        tag,
        ha="center", va="center",
        fontsize=9, fontweight="bold", color=fg,
        rotation=0, zorder=3,
        fontfamily="monospace",
    )

    # Title
    title_y = y_bottom + BAND_H - 0.28
    ax.text(
        TITLE_X, title_y, title,
        ha="left", va="top",
        fontsize=10, fontweight="bold", color=fg,
        zorder=3,
    )

    # Bullet items
    item_y = title_y - 0.30
    for item in items:
        ax.text(
            TITLE_X + 0.1, item_y, item,
            ha="left", va="top",
            fontsize=7.8, color=fg, alpha=0.93,
            zorder=3,
            fontfamily="monospace",
        )
        item_y -= 0.245

# ── thin white dividers between bands ──────────────────────────────────────
for i in range(1, len(LAYERS)):
    ax.axhline(i * BAND_H, color="#ECEFF1", linewidth=2, zorder=4)

# ── title ──────────────────────────────────────────────────────────────────
ax.text(
    FIG_W / 2, FIG_H - 0.12,
    "SCPI Instrument Toolkit  —  Architecture",
    ha="center", va="top",
    fontsize=14, fontweight="bold", color="#004D40",
    zorder=5,
)

# ── side arrow showing data flow ───────────────────────────────────────────
arrow_x = FIG_W - 0.55
ax.annotate(
    "", xy=(arrow_x, 0.3), xytext=(arrow_x, FIG_H - 0.5),
    arrowprops=dict(
        arrowstyle="<->",
        color="#78909C",
        lw=1.8,
    ),
    zorder=5,
)
ax.text(
    arrow_x + 0.12, FIG_H / 2,
    "abstraction",
    ha="left", va="center",
    fontsize=8, color="#78909C", rotation=270,
    zorder=5,
)

plt.tight_layout(pad=0)
out = "docs/img/architecture.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved → {out}")
