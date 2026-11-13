#!/usr/bin/env python3
"""Check a built plugin tree (tools/build.sh OUT) before it is released.

usage: tools/check.py OUT [KLIPPER_DIR]

- plugin.json: valid, the fields Kiln OS reads, a version filled in
- every .py compiles
- plugin.cfg's includes exist; the IFS config parses, has the Happy Hare
  sections, and an analog_pin_<n> for each of the unit's num_gates
- with KLIPPER_DIR: no module in extras/ that Klipper already has (Kiln OS
  refuses a plugin module whose name Klipper's extras already use)
"""
import configparser
import json
import os
import re
import sys

errors = []


def fail(msg):
    errors.append(msg)


def read_cfg(path):
    cp = configparser.RawConfigParser(strict=False, inline_comment_prefixes=('#', ';'))
    with open(path) as f:
        cp.read_string(f.read(), path)
    return cp


def main(out, klipper=None):
    meta = json.load(open(os.path.join(out, 'plugin.json')))
    for key in ('name', 'version', 'requires_os', 'owns_ifs'):
        if key not in meta:
            fail('plugin.json: no %s' % key)
    if '@' in str(meta.get('version', '@')):
        fail('plugin.json: version not filled in')
    if meta.get('name') != 'happy-hare':
        fail('plugin.json: name is %r' % meta.get('name'))

    for root, _, files in os.walk(out):
        for f in files:
            if f.endswith('.py'):
                p = os.path.join(root, f)
                try:
                    compile(open(p, encoding='utf-8').read(), p, 'exec')
                except SyntaxError as e:
                    fail('compile: %s: %s' % (p, e))

    plugin_cfg = os.path.join(out, 'plugin.cfg')
    for inc in re.findall(r'^\[include ([^\]]+)\]', open(plugin_cfg).read(), re.M):
        if not os.path.exists(os.path.join(out, inc)):
            fail('plugin.cfg includes %s, which is missing' % inc)

    cfg = read_cfg(os.path.join(out, 'mmu-flashforge-ifs.cfg'))
    for sect in ('mmu_machine', 'mmu_parameters', 'mmu_unit ifs', 'mmu_unit_parameters ifs',
                 'mmu_encoder ifs_encoder', 'mmu_toolhead default'):
        if not cfg.has_section(sect):
            fail('mmu-flashforge-ifs.cfg: no [%s]' % sect)
    if cfg.has_section('mmu_unit ifs') and cfg.has_section('mmu_encoder ifs_encoder'):
        gates = cfg.getint('mmu_unit ifs', 'num_gates')
        enc = dict(cfg.items('mmu_encoder ifs_encoder'))
        missing = [g for g in range(gates) if not enc.get('analog_pin_%d' % g)]
        if missing:
            fail('[mmu_encoder ifs_encoder]: no analog_pin_%s' % ', analog_pin_'.join(map(str, missing)))

    for need in ('extras/mmu/__init__.py', 'extras/mmu_machine.py',
                 'extras/mmu/unit/mmu_analog_counter.py', 'moonraker/components/mmu_server.py'):
        if not os.path.exists(os.path.join(out, need)):
            fail('missing %s' % need)

    if klipper:
        kextras = os.path.join(klipper, 'klippy', 'extras')
        have = {os.path.splitext(n)[0] for n in os.listdir(kextras)}
        for n in os.listdir(os.path.join(out, 'extras')):
            name = os.path.splitext(n)[0]
            if name in have and name != '__pycache__':
                fail('extras/%s: Klipper already has a module of that name' % n)

    for e in errors:
        print('check: ' + e)
    print('check: %s (%s)' % ('FAILED' if errors else 'ok', meta.get('version')))
    return 1 if errors else 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:3]))
