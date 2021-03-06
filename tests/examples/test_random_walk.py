"""
:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
:Date: 2018-02-17
:Copyright: 2018-2020, Karr Lab
:License: MIT
"""

import unittest
import warnings
from argparse import Namespace
from capturer import CaptureOutput

from de_sim.examples.config import core
from de_sim.examples.random_walk import RunRandomWalkSimulation


class TestRandomStateVariableSimulation(unittest.TestCase):

    def setUp(self):
        # turn off console logging
        self.config = core.get_debug_logs_config()
        self.console_level = self.config['debug_logs']['handlers']['debug.example.console']['level']
        self.config['debug_logs']['handlers']['debug.example.console']['level'] = 'error'
        warnings.simplefilter("ignore")

    def tearDown(self):
        # restore console logging
        self.config['debug_logs']['handlers']['debug.example.console']['level'] = self.console_level

    def test_random_walk_simulation(self):
        with CaptureOutput(relay=False):
            args = Namespace(initial_state=3, time_max=10, output=False)
            self.assertTrue(0 < RunRandomWalkSimulation.main(args).num_events)
            args = Namespace(initial_state=3, time_max=10, output=True)
            self.assertTrue(0 < RunRandomWalkSimulation.main(args).num_events)
