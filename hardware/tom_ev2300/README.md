# tom_ev2300

3D-printable mount/enclosure for the TI EV2300 evaluation board, used with the
TOM (Tool-Oauto-Mationator) battery-test rig.

## Files

| File                                       | Purpose                                |
|--------------------------------------------|----------------------------------------|
| `tom_ev2300.stl`                           | source mesh                            |
| `tom_ev2300.3mf`                           | OrcaSlicer project (editable)          |
| `tom_ev2300_h2d_petg_0.20mm.gcode.3mf`     | sliced, ready to print on Bambu H2D    |

## Mesh verification

Verified with `trimesh` on 2026-05-05:

- Watertight: yes
- Winding consistent: yes
- Volume: 12.0 cm^3
- Bounding box: 57.40 x 66.12 x 19.47 mm
- Vertices / faces: 11,092 / 22,184
- Genus: 1 (one through-hole, expected for a mount)

## Print recipe (Bambu Lab H2D, 0.4 mm nozzle)

| Setting        | Value                                 |
|----------------|---------------------------------------|
| Filament       | Generic PETG (Bambu PETG Basic also OK)|
| Process        | 0.20mm Standard @BBL H2D              |
| Layer height   | 0.20 mm                               |
| Walls          | 3                                     |
| Top / bottom   | 4 / 3 layers                          |
| Infill         | 15 percent gyroid                     |
| Supports       | None                                  |
| Build plate    | Smooth PEI / Textured PEI at 70 C     |
| Brim           | Optional, 5 mm if adhesion is iffy    |

Auto-orient picks the +X face down (cost score 439.7 of 26 candidates) --
zero overhang, prints flat.

Slice stats from `tom_ev2300_h2d_petg_0.20mm.gcode.3mf`:

- Print time: 45 min 55 sec
- Filament: 4.33 m / 13.23 g PETG
- 96 layers

### Known warning

The slicer flags `bed_temperature_too_high_than_filament` (level 3) on the
H2D process profile. The PETG filament profile recommends 70 C bed; the H2D
process default sits higher. Open the project in OrcaSlicer and drop the bed
temp to 70 C if you see first-layer sag, otherwise the print is fine to send
as-is.

## Reslicing from CLI

The project `.3mf` already has all settings baked in. To re-export the
sliced file from the command line:

```sh
/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer \
  --slice 0 \
  --export-3mf "tom_ev2300_h2d_petg_0.20mm.gcode.3mf" \
  --outputdir "$(pwd)" \
  tom_ev2300.3mf
```

Passing the project `.3mf` (not the raw STL) avoids the `--load-settings`
inheritance segfault that OrcaSlicer 2.3.2 has on macOS when vendor profiles
are referenced by absolute path.

## Reslicing from GUI

```sh
open -a OrcaSlicer hardware/tom_ev2300/tom_ev2300.3mf
```

In OrcaSlicer: tweak settings -> **Slice plate** -> **Export plate sliced file**.
