"""
:Author: Arthur Goldberg <Arthur.Goldberg@mssm.edu>
:Date: 2018-01-22
:Copyright: 2018-2020, Karr Lab
:License: MIT
"""

import unittest

from de_sim.event import Event, iterable_not_str, nested_elements_to_str
from de_sim.simulation_message import SimulationMessage
from de_sim.simulation_object import (ApplicationSimulationObjMeta, ApplicationSimulationObject,
                                      SimObjClassPriority)
from de_sim.testing.example_simulation_objects import ExampleSimulationObject
from de_sim.testing.some_message_types import InitMsg, Eg1, MsgWithAttrs
from wc_utils.util.list import elements_to_str
from wc_utils.util.misc import round_direct


class TestEvent(unittest.TestCase):

    def setUp(self):
        self.sim_obj_a = ExampleSimulationObject('a')
        self.sim_obj_b = ExampleSimulationObject('b')

    def comparison(self, lesser, greater):
        self.assertTrue(lesser < greater)
        self.assertFalse(lesser > greater)
        self.assertTrue(lesser <= lesser)
        self.assertTrue(lesser <= greater)
        self.assertTrue(greater > lesser)
        self.assertFalse(greater < lesser)
        self.assertTrue(lesser >= lesser)
        self.assertTrue(greater >= lesser)

    def test_get_order_time(self):
        event_time = 1
        e = Event(0, event_time, self.sim_obj_a, self.sim_obj_a, InitMsg())
        class_priority_attr = ApplicationSimulationObjMeta.CLASS_PRIORITY
        self.assertEqual(e._get_order_time(),
                         (event_time, getattr(ExampleSimulationObject, class_priority_attr),
                          self.sim_obj_a.event_time_tiebreaker))

    def test_event_inequalities(self):

        # test Events with different event times
        e1 = Event(0, 1, self.sim_obj_a, self.sim_obj_a, InitMsg())
        e2 = Event(0, 2, self.sim_obj_a, self.sim_obj_b, InitMsg())
        self.comparison(e1, e2)

        # test Events with equal event times and recipients in the same class with different names
        e3 = Event(0, 1, self.sim_obj_a, self.sim_obj_b, InitMsg())
        self.comparison(e1, e3)

        # Events with equal event times and recipients in different classes
        class ASOwithLowPriority(ApplicationSimulationObject):
            def handler(self, event):
                pass
            event_handlers = [(InitMsg, 'handler')]
            # low priority
            class_priority = SimObjClassPriority.LOW

        # give lower priority sim object a name that sorts before 'a'
        new_sim_obj_a = ASOwithLowPriority('Z')
        e4 = Event(0, 1, self.sim_obj_a, new_sim_obj_a, InitMsg())
        self.comparison(e1, e4)

        # Events with equal event times and recipients in different classes
        class ASOwithDefaultLowPriority(ApplicationSimulationObject):
            def handler(self, event):
                pass
            event_handlers = [(InitMsg, 'handler')]

        # give lower priority sim object a name that sorts before 'a'
        new_sim_obj_a = ASOwithDefaultLowPriority('Z')
        e4 = Event(0, 1, self.sim_obj_a, new_sim_obj_a, InitMsg())
        self.comparison(e1, e4)

        # test Events with equal event times and recipients, and different messages
        times_n_objs = (0, 1, self.sim_obj_a, self.sim_obj_b)
        e4 = Event(*times_n_objs, Eg1())
        e5 = Event(*times_n_objs, Eg1())
        self.assertTrue(e4 <= e5)
        self.assertTrue(e4 >= e5)
        attrs1 = (1, 'bye')
        e6 = Event(*times_n_objs, MsgWithAttrs(*attrs1))
        e7 = Event(*times_n_objs, MsgWithAttrs(*attrs1))
        self.assertTrue(e6 <= e7)
        self.assertTrue(e7 >= e6)

    def test_event_w_message(self):
        attrs = ['attr1', 'attr2']

        class TestMsg(SimulationMessage):
            'docstring'
            attributes = ['attr1', 'attr2']
        vals = ['att1_val', 'att2_val']
        test_msg = TestMsg(*vals)
        times = (0, 1)
        SENDER = 'sender'
        RECEIVER = 'receiver'
        ev = Event(*(times + (ExampleSimulationObject(SENDER), ExampleSimulationObject(RECEIVER),
                              test_msg)))

        # test headers
        self.assertEqual(Event.BASE_HEADERS, Event.header(as_list=True)[:-1])
        self.assertIn('\t'.join(Event.BASE_HEADERS), Event.header())
        self.assertEqual(Event.BASE_HEADERS, ev.custom_header(as_list=True)[:-len(attrs)])
        self.assertIn('\t'.join(Event.BASE_HEADERS), ev.custom_header())
        self.assertIn('\t'.join(attrs), ev.custom_header())
        # data = list(times) + [SENDER, RECEIVER, TestMsg.__name__]

        # test data
        # todo: fix these tests
        # self.assertIn('\t'.join(elements_to_str(data)), ev.render())
        self.assertIn('\t'.join(elements_to_str(vals)), ev.render())
        # self.assertEqual(data+vals, ev.render(as_list=True))
        # self.assertIn('\t'.join(elements_to_str(data)), ev.render(annotated=True))
        # self.assertEqual(data, ev.render(annotated=True, as_list=True)[:len(data)])
        self.assertIn('\t'.join(elements_to_str(vals)), str(ev))
        self.assertIn('TestMsg', str(ev))
        offset_times = (0.000001, 0.999999)
        ev_offset = Event(*(offset_times + (ExampleSimulationObject(SENDER), ExampleSimulationObject(RECEIVER),
                                            test_msg)))
        for t in offset_times:
            self.assertIn(round_direct(t), str(ev_offset.render(round_w_direction=True, as_list=True)))
            self.assertIn(str(round_direct(t)), ev_offset.render(round_w_direction=True))
        # self.assertEqual(data+vals, ev.render(as_list=True))

        class NoBodyMessage(SimulationMessage):
            """A message with no attributes"""
        ev2 = Event(0, 1, ExampleSimulationObject('sender'), ExampleSimulationObject('receiver'),
                    NoBodyMessage())
        self.assertIn('\t'.join(Event.BASE_HEADERS), ev2.custom_header())
        # self.assertIn('\t'.join([str(t) for t in times]), str(ev2))


class TestStrMapFunctions(unittest.TestCase):

    def test_iterable_not_str(self):
        # some non-string iterables
        self.assertTrue(iterable_not_str(("f", "f")))   # tuple
        self.assertTrue(iterable_not_str(["f", "f"]))   # list
        self.assertTrue(iterable_not_str(iter("ff")))   # iterator
        self.assertTrue(iterable_not_str(range(4)))     # generator
        self.assertTrue(iterable_not_str(b"ff"))        # bytes (Python 2 calls this a string)

        # strings or non-iterables
        self.assertFalse(iterable_not_str(u"ff"))    # string
        self.assertFalse(iterable_not_str(44))       # integer
        self.assertFalse(iterable_not_str(iterable_not_str))  # function

    def test_nested_elements_to_str(self):
        arg_and_expected = (([1, 'x'], ['1', 'x']),
                            ((1, 'x'), ['1', 'x']),
                            ((1, [2, 'y']), ['1', ['2', 'y']]),
                            )
        for arg, expected in arg_and_expected:
            self.assertEqual(nested_elements_to_str(arg), expected)
