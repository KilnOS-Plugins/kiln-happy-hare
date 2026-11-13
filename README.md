# happy-hare

[Happy Hare](https://github.com/moggieuk/Happy-Hare) v4 for the Flashforge
AD5X IFS on Kiln OS, in place of Kiln's own `[ifs]` driver.

- **Parking at the toolhead:** a tool change parks the strand just above the
  4-to-1 combiner instead of pulling back the whole bowden.
- **Synced feeding:** the IFS gear runs with the extruder while printing.
- **Clog detection:** the IFS's per-slot stall sensors (a magnet wheel the
  filament turns) are Happy Hare's encoder, so FlowGuard sees a strand that
  stops. The readings are graphed as `ifs_spool1_stall` ... `ifs_spool4_stall`.
- **AD5X purge box:** purge, cooling dwell, box-edge scrape and brush.
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

## Limits

- **The first tool of a print:** Kiln OS's `PRINT_START` doesn't load a tool
  through a plugin yet, so a print that starts with an empty toolhead needs
  a `T<n>` in the slicer's start G-code after `PRINT_START`.
- **The encoder is coarse:** one pulse per about 5.3 mm, read on the host.
  It is for FlowGuard only: `encoder_move_validation` is off, and gate
  homing uses the toolhead sensor, not the encoder.

`BUILD` says which Happy Hare this was built from.
