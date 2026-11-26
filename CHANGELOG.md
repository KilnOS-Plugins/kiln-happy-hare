# Changelog

What changed for people using the plugin. A release's notes on GitHub come from its section here:
`## vX.Y.Z.N (date)`.

## v4.2.0.1 (unreleased)

**Happy Hare 4.2.0.** The plugin moves from Happy Hare v4.1.0 to v4.2.0 (upstream's release notes:
[moggieuk/Happy-Hare](https://github.com/moggieuk/Happy-Hare/releases)), with the AD5X IFS changes carried over.

- **Each IFS slot has its own encoder.** The four stall wheels (a Hall sensor on a magnet wheel the
  filament turns) used to be one encoder that switched wheels with the selected slot. Each is now its
  own encoder, `ifs_encoder_0` … `ifs_encoder_3`, with its own count and calibration. A slot change
  can no longer lose a pulse, and FlowGuard moves to the new slot's wheel with the tool change.
- **Finer encoder readings.** Between pulses, each wheel now reports where in its turn the filament is
  (`analog_interpolate`). It reads about 0.3 mm instead of 5.3 mm, the same in both directions and at
  any speed. Standing still adds nothing.
- **A spool you insert is fed in by itself, stopping at the toolhead.** Push filament into a free slot
  and the IFS feeds it up to the toolhead and parks it just above the 4-to-1 combiner, ready for its
  first tool change:
  - With nothing loaded, it stops when the toolhead's filament sensor sees it.
  - With another slot loaded, it stops when the slot's wheel shows the strand has met the occupied
    combiner.
  - It never stops at a fixed feed length.
  - A strand that is already at the stop isn't fed on. Pulling a strand out clears its "parked" state.
- **The first tool loads before the bed is levelled.** `PRINT_START ... TOOL=<n>` now loads that slot
  with Happy Hare first, then runs Kiln OS's print start, so the purge, brush and mesh use the right
  filament. Before, the print start purged whatever was loaded and the first tool only loaded at the
  file's first `T<n>`. Slicer start G-code (OrcaSlicer):

  ```
  PRINT_START BED=[bed_temperature_initial_layer_single] EXTRUDER=[nozzle_temperature_initial_layer] TOOL=[initial_tool]
  ```

  `START_PRINT` (zMod style) goes through it too.
- **Every tool change purges, wipes and brushes at the purge box, also in a print.** Before, a tool
  change in a print left purging to the slicer and went from the load straight back to the part.
  The slicer's own purge (prime tower) still runs as well; you can make it smaller.
- Fixes:
  - **Taking a spool out of a slot that isn't printing no longer pauses the print.** The slots'
    sensors are Klipper filament sensors too, and Klipper paused on any of them going empty. Happy
    Hare handles them: a runout of the slot in use still pauses (or swaps to the next spool),
    any other slot is only marked empty.
  - **The IFS gear no longer runs at full current while printing.** Synced to the extruder it now
    runs at half its run current (`sync_gear_current: 50`, Happy Hare's default), not 100%.
  - A slot parked above the toolhead stays parked after a recovery, instead of being pulled back the
    whole bowden.
  - mmu.log no longer writes every line twice after a Klipper restart.

**After updating:** the four new encoders start with the old shared calibration: the plugin copies it
(`mmu_ifs_encoder_encoder_resolution`, and the clog detection length) to each slot's encoder at the
first start, once, and never over a slot's own value. The wheels are the same part, but for each
wheel's own value run `MMU_CALIBRATE_ENCODER` with that slot selected.

Tested on Kiln OS v1.0.0.

## v4.1.0.5

Happy Hare v4.1.0 for the AD5X IFS (`v4.1.0-kiln.3`).
