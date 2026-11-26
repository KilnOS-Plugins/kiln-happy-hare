# extras/ifs_encoder_migrate.py: the single-encoder calibration copied to the per-slot encoders.
#
#   python3 -m unittest discover -s tests
#
# Happy Hare's SaveVariableManager is faked with the same get/set/namespace behaviour
# (variables named "mmu_<name>_..." for an encoder <name>).
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    'ifs_encoder_migrate', os.path.join(HERE, '..', 'plugin', 'extras', 'ifs_encoder_migrate.py'))
migrate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migrate)


class FakeVariables:
    def __init__(self, values):
        self.values = dict(values)
        self.writes = 0

    def namespace(self, variable, namespace):
        return variable.replace('mmu_', 'mmu_%s_' % namespace) if namespace else variable

    def get(self, variable, default, namespace=None):
        return self.values.get(self.namespace(variable, namespace), default)

    def set(self, variable, value, namespace=None, write=False):
        self.values[self.namespace(variable, namespace)] = value
        self.writes += bool(write)


class FakeMachine:
    def __init__(self, variables):
        self.var_manager = variables


class FakePrinter:
    def __init__(self, machine):
        self.machine = machine
        self.handlers = {}

    def lookup_object(self, name, default=None):
        return self.machine if name == 'mmu_machine' else default

    def register_event_handler(self, event, cb):
        self.handlers[event] = cb


class FakeConfig:
    def __init__(self, printer, options=None):
        self.printer = printer
        self.options = options or {}

    def get_printer(self):
        return self.printer

    def get(self, name, default=None):
        return self.options.get(name, default)

    def getlist(self, name, default=None):
        v = self.options.get(name)
        return default if v is None else [x.strip() for x in v.split(',')]


NEW = ['mmu_ifs_encoder_%d_encoder_resolution' % g for g in range(4)]


def run(values, machine=True):
    variables = FakeVariables(values)
    printer = FakePrinter(FakeMachine(variables) if machine else None)
    m = migrate.load_config(FakeConfig(printer))
    printer.handlers['klippy:connect']()
    return variables, m


class TestMigrate(unittest.TestCase):

    def test_the_old_calibration_goes_to_every_slot(self):
        v, m = run({'mmu_ifs_encoder_encoder_resolution': 5.2632})
        self.assertEqual([v.values[k] for k in NEW], [5.2632] * 4)
        self.assertGreater(v.writes, 0)
        self.assertEqual(len(m.get_status(0)['copied']), 4)

    def test_a_slot_calibrated_since_keeps_its_value(self):
        v, _ = run({'mmu_ifs_encoder_encoder_resolution': 5.2632,
                    'mmu_ifs_encoder_2_encoder_resolution': 5.31})
        self.assertEqual([v.values[k] for k in NEW], [5.2632, 5.2632, 5.31, 5.2632])

    def test_the_clog_length_is_copied_too(self):
        v, _ = run({'mmu_ifs_encoder_encoder_resolution': 5.2632,
                    'mmu_ifs_encoder_encoder_clog_length': 14.5})
        self.assertEqual(v.values['mmu_ifs_encoder_3_encoder_clog_length'], 14.5)

    def test_nothing_to_copy_writes_nothing(self):
        v, m = run({'mmu_ifs_encoder_0_encoder_resolution': 5.3})
        self.assertEqual(v.writes, 0)
        self.assertEqual(m.get_status(0)['copied'], [])
        self.assertNotIn('mmu_ifs_encoder_1_encoder_resolution', v.values)

    def test_the_old_values_stay(self):
        v, _ = run({'mmu_ifs_encoder_encoder_resolution': 5.2632})
        self.assertEqual(v.values['mmu_ifs_encoder_encoder_resolution'], 5.2632)

    def test_a_second_start_copies_nothing_more(self):
        v, _ = run({'mmu_ifs_encoder_encoder_resolution': 5.2632})
        v2, m2 = run(v.values)
        self.assertEqual(v2.writes, 0)
        self.assertEqual(m2.get_status(0)['copied'], [])

    def test_without_happy_hare_it_does_nothing(self):
        _, m = run({'mmu_ifs_encoder_encoder_resolution': 5.2632}, machine=False)
        self.assertEqual(m.get_status(0)['copied'], [])


if __name__ == '__main__':
    unittest.main()
