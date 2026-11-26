# happy-hare

[Happy Hare](https://github.com/moggieuk/Happy-Hare) v4 for the Flashforge
AD5X IFS on Kiln OS, in place of Kiln's own `[ifs]` driver.

- **Parking at the toolhead:** a tool change parks the strand just above the
  4-to-1 combiner instead of pulling back the whole bowden.
- **Synced feeding:** the IFS gear runs with the extruder while printing.
- **Clog detection:** each slot's stall sensor (a magnet wheel the filament
  turns) is its own Happy Hare encoder, read to about 0.3 mm, so FlowGuard
  sees a strand that stops. The readings are graphed as `ifs_spool1_stall` ...
  `ifs_spool4_stall`.
- **Insert and go:** a spool pushed into a free slot is fed up to the toolhead
  and parked above the combiner. It stops at the toolhead's filament sensor,
  or, with another slot loaded, where its wheel shows it has met that strand.
- **First tool before levelling:** `PRINT_START ... TOOL=<n>` loads that slot
  first, so Kiln OS's purge, brush and mesh use the right filament.
- **AD5X purge box:** every tool change, also in a print: purge, cooling
  dwell, box-edge scrape and brush.
- **Kiln names:** `T0`-`T3`, `IFS_LOAD`, `IFS_UNLOAD`, `IFS_SWAP` and
  `IFS_SELECT` run the Happy Hare commands.

## Needs

- Kiln OS with plugin API 1.5 (`owns_ifs`, packages in `extras/`).
- The IFS on Klipper firmware (Settings > Devices > IFS firmware, or
  `ad5x-mcu flash-ifs`). `ENABLE_PLUGIN` refuses the plugin unless the IFS
  answered as Klipper at this boot.

## Install

```
cd /data/ad5x/plugins
su klipper -s /bin/sh -c 'git clone -b release https://github.com/KilnOS-Plugins/kiln-happy-hare.git happy-hare'
```

then `ENABLE_PLUGIN NAME=happy-hare` (or the switch under Settings > Plugins).
Fluidd lists it under updates afterwards; after an update, `RESTART` Klipper
(Kiln OS's Moonraker can't restart it for you).
`DISABLE_PLUGIN NAME=happy-hare` goes back to Kiln's IFS driver.

## Slicer

Start G-code (OrcaSlicer):

```
PRINT_START BED=[bed_temperature_initial_layer_single] EXTRUDER=[nozzle_temperature_initial_layer] TOOL=[initial_tool]
```

Filament change G-code: `T[next_extruder]`. End G-code: `PRINT_END`.

## Limits

- **The encoders are read on the host:** their counts arrive up to about
  0.2 s after the movement. They are for FlowGuard and for seeing a strand
  stop: `encoder_move_validation` is off, and homing uses the toolhead
  sensor, not the encoders.

What changed in each release: [CHANGELOG.md](../CHANGELOG.md).

`BUILD` says which Happy Hare this was built from.
