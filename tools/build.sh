#!/bin/sh
# Build the installable plugin tree (the release branch) into OUT.
#
# usage: tools/build.sh OUT [HH_DIR]
#   OUT     output directory, emptied first
#   HH_DIR  a Happy Hare checkout to take the code from; without it the
#           HH_REF of happy-hare.version is cloned into ./hh
#
# OUT gets plugin/ (plugin.json, plugin.cfg, the IFS config, extras/) plus
# Happy Hare's Klipper modules in extras/ (mmu_*.py and the mmu package)
# and its Moonraker component in moonraker/components/. Kiln OS loads both
# from the plugin (plugin API 1.5: packages in extras/, 1.3: components).
set -eu
cd "$(dirname "$0")/.."
OUT=${1:?usage: tools/build.sh OUT [HH_DIR]}
HH=${2:-}
. ./happy-hare.version

if [ -z "$HH" ]; then
	HH=hh
	rm -rf "$HH"
	git clone -q --depth 1 --branch "$HH_REF" "$HH_REPO" "$HH"
fi
[ -d "$HH/extras/mmu" ] || { echo "build: $HH has no extras/mmu" >&2; exit 1; }

HH_COMMIT=$(git -C "$HH" rev-parse --short HEAD)
VERSION=${VERSION:-$(git describe --tags --always 2>/dev/null || echo dev)}

rm -rf "$OUT"
mkdir -p "$OUT/extras" "$OUT/moonraker/components"
cp -a plugin/. "$OUT/"
cp -a "$HH"/extras/mmu "$HH"/extras/mmu_*.py "$OUT/extras/"
cp -a "$HH/components/mmu_server.py" "$OUT/moonraker/components/"
cp LICENSE "$OUT/"
find "$OUT" -name __pycache__ -prune -exec rm -rf {} +
sed -i "s/@VERSION@/$VERSION/" "$OUT/plugin.json"
cat > "$OUT/BUILD" <<EOT
plugin $VERSION ($(git rev-parse --short HEAD 2>/dev/null || echo none))
happy-hare $HH_REF ($HH_COMMIT) from $HH_REPO
EOT
echo "build: $OUT: plugin $VERSION, Happy Hare $HH_REF ($HH_COMMIT)"
