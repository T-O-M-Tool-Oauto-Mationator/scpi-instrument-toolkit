"""Generate concentric-circle architecture diagram (reference: AI/ML onion style)."""

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 12))
ax.set_xlim(-6.5, 6.5)
ax.set_ylim(-6.8, 6.5)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")

# Each layer: (radius, fill, edge, title, title_fs, item_fs, [(label, x, y), ...])
# Items verified to be inside their ring (r_inner < sqrt(x²+y²) < r_outer)
LAYERS = [
    (
        5.2, "#F5F5F5", "#9E9E9E",
        "Layer 4 — Frontends", 14, 10,
        [
            ("REPL / CLI",        -2.5,  4.55),
            ("scpi-repl",         -2.5,  4.15),
            ("GUI  (Tkinter)",     2.5,  4.55),
            ("scpi-gui",           2.5,  4.15),
            ("LabVIEW bridge",    -4.75,  0.9),
            ("Python scripts",     4.4,   0.9),
            ("…",                 -4.0,  -3.2),
            ("…",                  4.0,  -3.2),
        ],
    ),
    (
        4.1, "#DCEEFB", "#1976D2",
        "Layer 3 — REPL Session Layer", 13, 9,
        [
            ("commands/",         -1.8,   3.65),
            ("ReplContext",         1.9,   3.25),
            ("DeviceRegistry",     -3.6,   0.75),
            ("ScriptEngine",        3.5,  -0.65),
            ("MeasurementStore",   -2.6,  -2.4),
            ("SafetySystem",        2.2,  -2.9),
        ],
    ),
    (
        3.0, "#DCEDD9", "#388E3C",
        "Layer 2 — Instrument Drivers", 12, 8.5,
        [
            ("HP_E3631A",    -1.35,  2.45),
            ("HP_34401A",     1.25,  2.65),
            ("Rigol_DHO804", -2.5,  -1.0),
            ("TI_EV2300",    2.25,   1.3),
            ("NI_PXIe_4139", -1.65, -2.1),
            ("DeviceManager", 2.2,  -1.75),
            ("discovery.py",  0.0,  -2.85),
        ],
    ),
    (
        1.9, "#FFF9C4", "#F9A825",
        "Layer 1 — Transport", 11, 8,
        [
            ("pyvisa",       -1.1,  0.85),
            ("ctypes / HID",  0.95, 0.85),
            ("nidcpower",    -0.1, -1.5),
        ],
    ),
    (
        0.9, "#FFE0B2", "#E64A19",
        "Layer 0 — Hardware", 9, 7.5,
        [
            ("NI-VISA",  -0.48,  0.2),
            ("USB HID",   0.42,  0.2),
            ("PXIe",      0.0,  -0.38),
        ],
    ),
]

# Draw largest → smallest so inner circles paint on top
for i, (radius, fill, edge, title, tfs, ifs, items) in enumerate(LAYERS):
    circle = plt.Circle(
        (0, 0), radius,
        facecolor=fill, edgecolor=edge,
        linewidth=2.2, zorder=i + 1,
    )
    ax.add_patch(circle)

    # Bold title just inside the top of each circle
    ax.text(
        0, radius - 0.33, title,
        ha="center", va="top",
        fontsize=tfs, fontweight="bold", color="#212121",
        zorder=i + 20,
    )

    # Scattered items
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
