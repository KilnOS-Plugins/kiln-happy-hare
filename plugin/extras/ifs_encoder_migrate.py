# One-time move of the IFS encoder calibration to the per-slot encoders.
#
# Up to v4.1.0.5 the four stall wheels were one encoder, ifs_encoder, and its calibration is
# saved under that name (mmu_ifs_encoder_encoder_resolution, and the clog detection length).
# From v4.2.0.1 each slot is its own encoder, ifs_encoder_0 ... _3, which reads its own name. At
# start-up this copies the old values to every new encoder that has none yet, before Happy Hare
# reads them, so an update doesn't ask for four calibrations of the same part. It never
# overwrites: an encoder calibrated since keeps its value. The old values stay where they are.
#
#   [ifs_encoder_migrate]
#   from: ifs_encoder
#   to: ifs_encoder_0, ifs_encoder_1, ifs_encoder_2, ifs_encoder_3
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

# Happy Hare's saved variables that belong to an encoder (namespaced by its name)
VARIABLES = ('mmu_encoder_resolution', 'mmu_encoder_clog_length')


class IfsEncoderMigrate:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.old = config.get('from', 'ifs_encoder')
        self.new = config.getlist('to', ['ifs_encoder_%d' % g for g in range(4)])
        self.copied = []
        # Connect comes before ready, when Happy Hare's encoders read their calibration
        self.printer.register_event_handler('klippy:connect', self._connect)

    def _connect(self):
        machine = self.printer.lookup_object('mmu_machine', None)
        variables = getattr(machine, 'var_manager', None)
        if variables is None:
            return
        for variable in VARIABLES:
            value = variables.get(variable, None, namespace=self.old)
            if value is None:
                continue
            for name in self.new:
                if variables.get(variable, None, namespace=name) is None:
                    # Staged now, written when Happy Hare flushes at ready
                    variables.set(variable, value, namespace=name, write=True)
                    self.copied.append((variables.namespace(variable, name), value))
        if self.copied:
            logging.info("ifs_encoder_migrate: copied the %s calibration: %s" % (
                self.old, ", ".join("%s = %s" % c for c in self.copied)))

    def get_status(self, eventtime):
        return {'copied': [k for k, _ in self.copied]}


def load_config(config):
    return IfsEncoderMigrate(config)
