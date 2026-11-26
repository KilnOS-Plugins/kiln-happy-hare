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
branch `kiln-4.2.0`: v4.2.0 with the AD5X IFS changes (linked sensors, a
gate homing option for an MMU without gate sensors, cam selector homing,
parking at the toolhead with preload to the park point, an analog encoder
per gate with interpolation). The encoder changes are also offered upstream
(moggieuk/Happy-Hare#1606). `kiln` is the v4.1.0 branch.

## Building

```
tools/build.sh out [HAPPY_HARE_DIR]   # the release tree
tools/check.py out [KLIPPER_DIR]      # checks it
```

Without `HAPPY_HARE_DIR` it clones the pinned tag into `hh/`.

## Releasing

1. When Happy Hare changes: tag the fork's branch (`kiln-4.2.0`:
   `v4.2.0-kiln.N`) and set `HH_REF` in `happy-hare.version`.
2. Give the release its section in [CHANGELOG.md](CHANGELOG.md)
   (`## v4.2.0.1 (date)`): the GitHub release's notes come from it.
3. Tag `main` `v<Happy Hare version>.<revision>` (`v4.2.0.1`, `v4.2.0.2`, ...:
   a version Moonraker can read and order) and push the tag.

The release workflow runs Happy Hare's tests, builds and checks the tree,
commits it to `release`, moves the tag onto that commit (Fluidd shows the
version from it) and attaches a zip to the GitHub release. The CI
workflow does the same for every push and pull request, without publishing.

## License

GPLv3, as Happy Hare and Klipper.
