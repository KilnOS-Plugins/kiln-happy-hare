# PRINT_START loads the first tool through Happy Hare.
#
# Kiln OS's PRINT_START loads TOOL= through its own IFS driver, which this plugin turns off,
# so with Happy Hare that step never runs. This moves Kiln's PRINT_START to _KILN_PRINT_START
# and puts a PRINT_START in front of it that runs `macro` (default _MMU_PRINT_START) with the
# same parameters; that macro loads the tool and then runs _KILN_PRINT_START. Kiln's
# [gcode_macro PRINT_START] object and its variables stay where they are. (A second
# [gcode_macro PRINT_START] section with rename_existing can't do this: Klipper merges sections
# of the same name.)
#
#   [hh_print_start]
#   macro: _MMU_PRINT_START
#
# This file may be distributed under the terms of the GNU GPLv3 license.


class HhPrintStart:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.macro = config.get('macro', '_MMU_PRINT_START')
        self.printer.register_event_handler('klippy:connect', self._connect)

    def _connect(self):
        kiln = self.gcode.register_command('PRINT_START', None)
        if kiln is None:
            raise self.printer.config_error("[hh_print_start] there is no PRINT_START to wrap")
        self.gcode.register_command('_KILN_PRINT_START', kiln,
                                    desc="Kiln OS's print start (home, heat, purge, brush, mesh)")
        self.gcode.register_command('PRINT_START', self.cmd_PRINT_START,
                                    desc="Load TOOL= with Happy Hare, then Kiln OS's print start")

    def cmd_PRINT_START(self, gcmd):
        self.gcode.run_script_from_command(
            "%s %s" % (self.macro, gcmd.get_raw_command_parameters()))


def load_config(config):
    return HhPrintStart(config)
