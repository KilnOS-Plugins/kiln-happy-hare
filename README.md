# kiln-happy-hare

A [Kiln OS](https://github.com/djvalic/kiln-os) plugin that runs
[Happy Hare](https://github.com/moggieuk/Happy-Hare) on the Flashforge AD5X
IFS. What it does and how to install it: [plugin/README.md](plugin/README.md).

## Branches

- `main`: the source. `plugin/` is the Kiln side (plugin.json, plugin.cfg,
  the IFS configuration, `extras/ifs_stall.py`); `happy-hare.version` pins the
  Happy Hare it is built with.
- `release`: the installable plugin, built by the release workflow. Kiln OS
  clones this branch into `/data/ad5x/plugins/happy-hare`, and Moonraker's
  update manager pulls it. Don't commit to it by hand.

Happy Hare comes from [KilnOS-Plugins/Happy-Hare](https://github.com/KilnOS-Plugins/Happy-Hare),
branch `kiln`: v4.1.0 with the AD5X IFS changes (linked sensors, a gate
homing option for an MMU without gate sensors, cam selector homing, parking
at the toolhead, and an encoder read from one analog sensor per gate).

## Building

```
tools/build.sh out [HAPPY_HARE_DIR]   # the release tree
tools/check.py out [KLIPPER_DIR]      # checks it
```

Without `HAPPY_HARE_DIR` it clones the pinned tag into `hh/`.

## Releasing

1. When Happy Hare changes: tag the fork's `kiln` branch (`v4.1.0-kiln.N`)
   and set `HH_REF` in `happy-hare.version`.
2. Tag `main` `v<Happy Hare version>.<revision>` (`v4.1.0.4`, `v4.1.0.5`, ...:
   a version Moonraker can read and order) and push the tag.

The release workflow runs Happy Hare's tests, builds and checks the tree,
commits it to `release`, moves the tag onto that commit (Fluidd shows the
version from it) and attaches a zip to the GitHub release. The CI
workflow does the same for every push and pull request, without publishing.

## License

GPLv3, as Happy Hare and Klipper.
