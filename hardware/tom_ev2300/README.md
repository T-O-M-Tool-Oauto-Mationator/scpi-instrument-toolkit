# tom_ev2300

3D-printable mount/enclosure for the TI EV2300 evaluation board, used with the
TOM (Tool-Oauto-Mationator) battery-test rig.

## Files

| File                                       | Purpose                                          |
|--------------------------------------------|--------------------------------------------------|
| `tom_ev2300.stl`                           | source mesh                                      |
| `tom_ev2300.3mf`                           | OrcaSlicer project (editable, targets X1 Carbon) |
| `tom_ev2300_x1c_pla_0.20mm.gcode.3mf`      | sliced, ready to print on Bambu X1 Carbon        |

## Mesh verification

Verified with `trimesh` on 2026-05-05:

- Watertight: yes
- Winding consistent: yes
- Volume: 12.0 cm^3
- Bounding box: 57.40 x 66.12 x 19.47 mm
- Vertices / faces: 11,092 / 22,184
- Genus: 1 (one through-hole, expected for a mount)

## Print recipe (Bambu Lab X1 Carbon, 0.4 mm hardened nozzle)

| Setting        | Value                                 |
|----------------|---------------------------------------|
| Filament       | Bambu PLA Basic                       |
| Process        | 0.20mm Standard @BBL X1C              |
| Layer height   | 0.20 mm                               |
| Walls          | 2                                     |
| Top / bottom   | 5 / 3 layers                          |
| Infill         | 15 percent crosshatch                 |
| Supports       | None                                  |
| Build plate    | Cool Plate at 55 C                    |
| Nozzle temp    | 220 C                                 |
| Brim           | Auto                                  |

Slice stats from `tom_ev2300_x1c_pla_0.20mm.gcode.3mf`:

- Print time: 36 min 8 sec
- Filament: 4.48 m / 13.57 g PLA
- 97 layers

## Reslicing from CLI

The project `.3mf` already has all settings baked in. To re-export the
sliced file from the command line:

```sh
/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer \
  --slice 0 \
  --export-3mf "tom_ev2300_x1c_pla_0.20mm.gcode.3mf" \
  --outputdir "$(pwd)" \
  tom_ev2300.3mf
```

Passing the project `.3mf` (not the raw STL) avoids the `--load-settings`
inheritance segfault that OrcaSlicer 2.3.2 has on macOS when vendor profiles
are referenced by absolute path. Cross-machine swaps (e.g. retargeting the
project from H2D to X1C) still segfault in CLI even with flattened profiles;
do those in the GUI.

## Reslicing from GUI

```sh
open -a OrcaSlicer hardware/tom_ev2300/tom_ev2300.3mf
```

In OrcaSlicer: tweak settings -> **Slice plate** -> **Export plate sliced file**.
