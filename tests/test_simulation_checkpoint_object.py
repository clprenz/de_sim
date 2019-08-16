""" Test the simulation checkpoint objects

:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
:Date: 2018-05-03
:Copyright: 2017-2018, Karr Lab
:License: MIT
"""

import unittest
import shutil
import tempfile
from math import ceil

from wc_utils.util.rand import RandomStateManager
from de_sim.simulation_engine import SimulationEngine
from de_sim.simulation_checkpoint_object import (AbstractCheckpointSimulationObject,
                                                  CheckpointSimulationObject,
                                                  AccessStateObjectInterface)
from de_sim.simulation_message import SimulationMessage
from de_sim.simulation_object import ApplicationSimulationObject
from de_sim.errors import SimulatorError
from de_sim.checkpoint import Checkpoint


class PeriodicCheckpointSimuObj(AbstractCheckpointSimulationObject):
    """ Test checkpointing by simplistically saving checkpoints to a list
    """

    def __init__(self, name, checkpoint_period, simulation_state, shared_checkpoints):
        self.simulation_state = simulation_state
        self.shared_checkpoints = shared_checkpoints
        super().__init__(name, checkpoint_period)

    def create_checkpoint(self):
        self.shared_checkpoints.append((self.time, self.simulation_state.get_checkpoint_state(self.time)))


class MessageSentToSelf(SimulationMessage):
    "A message that's sent to self"


class PeriodicLinearUpdatingSimuObj(ApplicationSimulationObject):
    """ Sets a shared value to a linear function of the simulation time
    """

    def __init__(self, name, delay, simulation_state, a, b):
        self.delay = delay
        self.simulation_state = simulation_state
        self.a = a
        self.b = b
        super().__init__(name)

    def send_initial_events(self):
        self.send_event(self.delay, self, MessageSentToSelf())

    def handle_simulation_event(self, event):
        self.simulation_state.set(self.a * self.time + self.b)
        self.send_event(self.delay, self, MessageSentToSelf())

    def get_state(self): return ''

    # register the event handler and message type sent
    event_handlers = [(MessageSentToSelf, handle_simulation_event)]
    messages_sent = [MessageSentToSelf]


class SharedValue(AccessStateObjectInterface):

    def __init__(self, init_val):
        self.value = init_val
        self.random_state = RandomStateManager.instance()

    def set(self, val):
        self.value = val

    def get_checkpoint_state(self, time):
        return self.value

    def get_random_state(self):
        return self.random_state.get_state()

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return False
        return other.value == self.value

    def __ne__(self, other):
        return not self.__eq__(other)


class TestCheckpointSimulationObjects(unittest.TestCase):

    def setUp(self):
        self.checkpoint_dir = tempfile.mkdtemp()

        self.simulator = SimulationEngine()
        self.a = 4
        self.b = 3
        self.state = SharedValue(self.b)
        self.update_period = 3
        self.updating_obj = PeriodicLinearUpdatingSimuObj('self.updating_obj', self.update_period,
                                                          self.state, self.a, self.b)
        self.checkpoint_period = 11

    def tearDown(self):
        shutil.rmtree(self.checkpoint_dir)

    def test_abstract_checkpoint_simulation_object(self):
        '''
        Run a simulation with a subclass of AbstractCheckpointSimulationObject and another object.
        Take checkpoints and test them.
        '''

        checkpoints = []
        checkpointing_obj = PeriodicCheckpointSimuObj('checkpointing_obj', self.checkpoint_period,
                                                      self.state, checkpoints)
        self.simulator.add_objects([self.updating_obj, checkpointing_obj])
        self.simulator.initialize()
        run_time = 100
        self.simulator.run(run_time)
        checkpointing_obj.create_checkpoint()
        for i in range(1 + int(run_time/self.checkpoint_period)):
            time, value = checkpoints[i]
            self.assertEqual(time, i * self.checkpoint_period)
            # updating_obj sets the shared value to a * time + b, at the instants 0, update_period, 2 * update_period, ...
            # checkpointing_obj samples the value at times unsynchronized with updating_obj
            # therefore, for 0<a, the sampled values are at most a * update_period less than the line a * time + b
            linear_prediction = self.a * self.checkpoint_period * i + self.b
            self.assertTrue(linear_prediction - self.a * self.update_period <= value <= linear_prediction)

    def test_checkpoint_simulation_object(self):
        '''
        Run a simulation with CheckpointSimulationObject and another object.
        Take checkpoints and test them.
        '''
        # prepare
        checkpointing_obj = CheckpointSimulationObject('checkpointing_obj', self.checkpoint_period,
                                                       self.checkpoint_dir, self.state)
        self.simulator.add_objects([self.updating_obj, checkpointing_obj])
        self.simulator.initialize()

        # run
        run_time = 241
        expected_num_events = int(run_time/self.update_period) + int(run_time/self.checkpoint_period)
        num_events = self.simulator.run(run_time)

        # check results
        self.assertEqual(expected_num_events, num_events)
        expected_checkpoint_times = [float(t) for t in
                                     range(0, self.checkpoint_period * int(run_time/self.checkpoint_period) + 1, self.checkpoint_period)]
        checkpoints = Checkpoint.list_checkpoints(self.checkpoint_dir)
        self.assertEqual(expected_checkpoint_times, checkpoints)
        checkpoint = Checkpoint.get_checkpoint(self.checkpoint_dir)
        self.assertEqual(checkpoint, Checkpoint.get_checkpoint(self.checkpoint_dir, time=run_time))

        for i in range(1 + int(run_time/self.checkpoint_period)):
            time = i * self.checkpoint_period
            state_value = Checkpoint.get_checkpoint(self.checkpoint_dir, time=time).state
            max_value = self.a * self.checkpoint_period * i + self.b
            self.assertTrue(max_value - self.a * self.update_period <= state_value <= max_value)

    def test_checkpoint_simulation_object_exception(self):
        with self.assertRaises(SimulatorError) as context:
            PeriodicCheckpointSimuObj('', 0, None, None)
