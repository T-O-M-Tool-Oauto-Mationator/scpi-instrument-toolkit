"""Generate concentric-circle architecture diagram (reference: AI/ML onion style)."""

import numpy as np
import matplotlib.pyplot as plt


def xy(r, deg):
    """Cartesian position at radius r, angle deg (CCW from +x axis)."""
    rad = np.radians(deg)
    return float(r * np.cos(rad)), float(r * np.sin(rad))


fig, ax = plt.subplots(figsize=(13, 13))
ax.set_xlim(-7, 7)
ax.set_ylim(-7.3, 7)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")

# ── layer definitions ──────────────────────────────────────────────────────
# (r_outer, fill, edge, title, title_fs, item_fs, [(label, x, y), ...])
#
# Radii:  5.5 | 4.4 | 3.3 | 2.1 | 1.0
# Mid-r:      4.95  3.85  2.70  1.55  0.55
#
# Angles are interleaved between rings so no two adjacent items share
# similar (angle, radius) coordinates — prevents cross-ring visual crowding.

m4, m3, m2, m1, m0 = 4.95, 3.85, 2.70, 1.55, 0.55

LAYERS = [
    # ── Layer 4 — Frontends ────────────────────────────────────────────────
    (
        5.5, "#F5F5F5", "#9E9E9E",
        "Layer 4 — Frontends", 14, 10,
        [
            ("REPL / CLI\nscpi-repl",    *xy(m4, 122)),   # upper-left
            ("GUI  (Tkinter)\nscpi-gui", *xy(m4,  58)),   # upper-right
            ("LabVIEW bridge",           *xy(m4, 165)),   # left
            ("Python scripts",           *xy(m4,  15)),   # right
            ("…",                        *xy(m4, 220)),   # lower-left
            ("…",                        *xy(m4, 320)),   # lower-right
        ],
    ),
    # ── Layer 3 — REPL Session Layer ───────────────────────────────────────
    (
        4.4, "#DCEEFB", "#1976D2",
        "Layer 3 — REPL Session Layer", 13, 9,
        [
            ("commands/",         *xy(m3, 143)),
            ("ReplContext",        *xy(m3,  37)),
            ("DeviceRegistry",    *xy(m3, 193)),
            ("ScriptEngine",      *xy(m3, 347)),
            ("MeasurementStore",  *xy(m3, 233)),
            ("SafetySystem",      *xy(m3, 307)),
        ],
    ),
    # ── Layer 2 — Instrument Drivers ───────────────────────────────────────
    (
        3.3, "#DCEDD9", "#388E3C",
        "Layer 2 — Instrument Drivers", 12, 8.5,
        [
            ("HP_E3631A",          *xy(m2, 132)),
            ("HP_34401A",          *xy(m2,  48)),
            ("Rigol_DHO804",       *xy(m2, 173)),
            ("TI_EV2300",          *xy(m2,   7)),
            ("NI_PXIe_4139",       *xy(m2, 213)),
            ("DeviceManager",      *xy(m2, 327)),
            ("discovery.py",       *xy(m2, 270)),
        ],
    ),
    # ── Layer 1 — Transport ────────────────────────────────────────────────
    (
        2.1, "#FFF9C4", "#F9A825",
        "Layer 1 — Transport", 11, 8.5,
        [
            ("pyvisa",             *xy(m1, 152)),
            ("ctypes / HID",       *xy(m1,  28)),
            ("nidcpower",          *xy(m1, 270)),
        ],
    ),
    # ── Layer 0 — Hardware ─────────────────────────────────────────────────
    (
        1.0, "#FFE0B2", "#E64A19",
        "Layer 0 — Hardware", 9, 7.5,
        [
            ("NI-VISA",            *xy(m0, 150)),
            ("USB HID",            *xy(m0,  30)),
            ("PXIe",               *xy(m0, 270)),
        ],
    ),
]

# ── draw (largest → smallest so inner circles paint on top) ────────────────
for i, (radius, fill, edge, title, tfs, ifs, items) in enumerate(LAYERS):
    ax.add_patch(plt.Circle(
        (0, 0), radius,
        facecolor=fill, edgecolor=edge,
        linewidth=2.2, zorder=i + 1,
    ))

    # Title: bold, near top of this circle (0.5 units below the apex)
    ax.text(
        0, radius - 0.5, title,
        ha="center", va="top",
        fontsize=tfs, fontweight="bold", color="#212121",
        zorder=i + 20,
    )

    for label, x, y in items:
        ax.text(
            x, y, label,
            ha="center", va="center",
            fontsize=ifs, color="#424242",
            zorder=i + 20,
        )

ax.set_title(
    "SCPI Instrument Toolkit — Architecture",
    fontsize=16, fontweight="bold", color="#004D40", pad=12,
)

plt.tight_layout()
out = "docs/img/architecture.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="white", edgecolor="none")
print(f"Saved → {out}")
