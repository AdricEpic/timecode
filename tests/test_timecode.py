#!-*- coding: utf-8 -*-

import unittest

from timecode import Timecode


class TimecodeTests(unittest.TestCase):
    """Timecode class tests"""

    def shortDescription(self):
        description = super(TimecodeTests, self).shortDescription()
        if description:
            description = "  " + description
        return description

    def test_instance_creation(self):
        """Creating new instances; none of these should raise errors."""

        Timecode('23.98', '00:00:00:00')
        Timecode('24', '00:00:00:00')
        Timecode('25', '00:00:00:00')
        Timecode('29.97', '00:00:00:00')
        Timecode('30', '00:00:00:00')
        Timecode('50', '00:00:00:00')
        Timecode('59.94', '00:00:00:00')
        Timecode('60', '00:00:00:00')
        Timecode('ms', '03:36:09:230')

        Timecode('23.98')
        Timecode('24')
        Timecode('25')
        Timecode('29.97')
        Timecode('30')
        Timecode('50')
        Timecode('59.94')
        Timecode('60')
        Timecode('ms')

        Timecode('24', frames=12000)
        Timecode('24', start_seconds=10)

    def test_repr_overload(self):
        """__repr__ returns expected string"""

        timeobj = Timecode('24', '01:00:00:00')
        self.assertEqual('01:00:00:00', timeobj.__repr__())

        timeobj = Timecode('23.98', '20:00:00:00')
        self.assertEqual('20:00:00:00', timeobj.__repr__())

        timeobj = Timecode('29.97', '00:09:00:00')
        self.assertEqual('00:08:59:28', timeobj.__repr__())

        timeobj = Timecode('30', '00:10:00:00')
        self.assertEqual('00:10:00:00', timeobj.__repr__())

        timeobj = Timecode('60', '00:00:09:00')
        self.assertEqual('00:00:09:00', timeobj.__repr__())

        timeobj = Timecode('59.94', '00:00:20:00')
        self.assertEqual('00:00:20:00', timeobj.__repr__())

        timeobj = Timecode('ms', '00:00:00:900')
        self.assertEqual('00:00:00:900', timeobj.__repr__())

        timeobj = Timecode('24', frames=49)
        self.assertEqual('00:00:02:00', timeobj.__repr__())

    def test_timecode_init(self):
        """Initializing of several timecode variations"""
        # ToDo: This should be merged with instance creation tests

        tc = Timecode('29.97')
        self.assertEqual('00:00:00:00', tc.__str__())
        self.assertEqual(1, tc.frames)

        tc = Timecode('29.97', '00:00:00:01')
        self.assertEqual(2, tc.frames)

        tc = Timecode('29.97', '03:36:09:23')
        self.assertEqual(388704, tc.frames)

        tc = Timecode('29.97', '03:36:09:23')
        self.assertEqual(388704, tc.frames)

        tc = Timecode('30', '03:36:09:23')
        self.assertEqual(389094, tc.frames)

        tc = Timecode('25', '03:36:09:23')
        self.assertEqual(324249, tc.frames)

        tc = Timecode('59.94', '03:36:09:23')
        self.assertEqual(777384, tc.frames)

        tc = Timecode('60', '03:36:09:23')
        self.assertEqual(778164, tc.frames)

        tc = Timecode('59.94', '03:36:09:23')
        self.assertEqual(777384, tc.frames)

        tc = Timecode('23.98', '03:36:09:23')
        self.assertEqual(311280, tc.frames)

        tc = Timecode('24', '03:36:09:23')
        self.assertEqual(311280, tc.frames)

        tc = Timecode('ms', '03:36:09:230')
        self.assertEqual(3, tc.hrs)
        self.assertEqual(36, tc.mins)
        self.assertEqual(9, tc.secs)
        self.assertEqual(230, tc.frs)

        tc = Timecode('24', frames=12000)
        self.assertEqual('00:08:19:23', tc.__str__())

        tc = Timecode('29.97', frames=2589408)
        self.assertEqual('23:59:59:29', tc.__str__())

        tc = Timecode('29.97', frames=2589409)
        self.assertEqual('00:00:00:00', tc.__str__())

        tc = Timecode('59.94', frames=5178816)
        self.assertEqual('23:59:59:59', tc.__str__())

        tc = Timecode('59.94', frames=5178817)
        self.assertEqual('00:00:00:00', tc.__str__())

    def test_frame_to_tc(self):
        """Converting from frames to timecode"""

        def assertFrameToTC(tc_, hrs, mins, secs, frs):
            self.assertEqual(hrs, tc_.hrs)
            self.assertEqual(mins, tc_.mins)
            self.assertEqual(secs, tc_.secs)
            self.assertEqual(frs, tc_.frs)

        tc = Timecode('29.97', '00:00:00:01')
        assertFrameToTC(tc, 0, 0, 0, 1)
        self.assertEqual('00:00:00:01', tc.__str__())

        test_code = '03:36:09:23'
        framerates = ['23.98', '24', '25', '29.97', '30', '59.94', '60']

        for fr in framerates:
            tc = Timecode(fr, test_code)
            assertFrameToTC(tc, 3, 36, 9, 23)

        tc = Timecode('ms', '03:36:09:230')
        assertFrameToTC(tc, 3, 36, 9, 230)

        tc = Timecode('24', frames=12000)
        assertFrameToTC(tc, 0, 8, 19, 23)
        self.assertEqual('00:08:19:23', tc.__str__())

    def test_tc_to_frame_test_in_2997(self):
        """Converting to frames from 29.97"""

        tc = Timecode('29.97', '00:00:00:00')
        self.assertEqual(tc.frames, 1)

        tc = Timecode('29.97', '00:00:00:21')
        self.assertEqual(tc.frames, 22)

        tc = Timecode('29.97', '00:00:00:29')
        self.assertEqual(tc.frames, 30)

        tc = Timecode('29.97', '00:00:00:60')
        self.assertEqual(tc.frames, 61)

        tc = Timecode('29.97', '00:00:01:00')
        self.assertEqual(tc.frames, 31)

        tc = Timecode('29.97', '00:00:10:00')
        self.assertEqual(tc.frames, 301)

        # test with non existing timecodes
        tc = Timecode('29.97', '00:01:00:00')
        self.assertEqual(1799, tc.frames)
        self.assertEqual('00:00:59:28', tc.__str__())

        # test the limit
        tc = Timecode('29.97', '23:59:59:29')
        self.assertEqual(2589408, tc.frames)

    def test_drop_frame(self):
        """Miscellaneous drop-frame tests"""
        # ToDo: Split these into more explicit cases

        tc = Timecode('29.97', '13:36:59:29')
        tc.add_frames(1)
        self.assertEqual("13:37:00:02", str(tc))

        tc = Timecode('59.94', '13:36:59:59')
        self.assertEqual("13:36:59:59", str(tc))

        tc.add_frames(1)
        self.assertEqual("13:37:00:04", str(tc))

        tc = Timecode('59.94', '13:39:59:59')
        tc.add_frames(1)
        self.assertEqual("13:40:00:00", str(tc))

        tc = Timecode('29.97', '13:39:59:29')
        tc.add_frames(1)
        self.assertEqual("13:40:00:00", str(tc))

    def test_op_overloads_add(self):
        """__add__ functionality"""

        def assertTcAdded(base_tc, add_tc, expected_str, expected_frs):
            from_tc = base_tc + add_tc
            from_frames = base_tc + add_tc.frames

            self.assertIsNot(base_tc._framerate, from_tc._framerate,
                             "New timecode from addition has its own "
                             "framerate object")
            self.assertEqual(from_tc, from_frames,
                             "Adding a timecode results in the same offset "
                             "as adding the equivalent number of frames")

            for _tc in (from_tc, from_frames):
                self.assertIsInstance(_tc, Timecode)
                self.assertEqual(expected_str, _tc.__str__())
                self.assertEqual(expected_frs, _tc.frames)

        tc = Timecode('23.98', '03:36:09:23')
        tc2 = Timecode('23.98', '00:00:29:23')
        assertTcAdded(tc, tc2, "03:36:39:23", 312000)

        tc = Timecode('25', '03:36:09:23')
        tc2 = Timecode('25', '00:00:29:23')
        assertTcAdded(tc, tc2, "03:36:39:22", 324998)

        tc = Timecode('29.97', '03:36:09:23')
        tc2 = Timecode('29.97', '00:00:29:23')
        assertTcAdded(tc, tc2, "03:36:39:17", 389598)

        tc = Timecode('30', '03:36:09:23')
        tc2 = Timecode('30', '00:00:29:23')
        assertTcAdded(tc, tc2, "03:36:39:17", 389988)

        tc = Timecode('59.94', '03:36:09:23')
        tc2 = Timecode('59.94', '00:00:29:23')
        assertTcAdded(tc, tc2, "03:36:38:47", 779148)

        tc = Timecode('60', '03:36:09:23')
        tc2 = Timecode('60', '00:00:29:23')
        assertTcAdded(tc, tc2, "03:36:38:47", 779928)

        tc = Timecode('ms', '03:36:09:230')
        tc2 = Timecode('ms', '01:06:09:230')
        assertTcAdded(tc, tc2, "04:42:18:461", 16938462)

        tc = Timecode('24', frames=12000)
        tc2 = Timecode('24', frames=485)
        assertTcAdded(tc, tc2, "00:08:40:04", 12485)

    def test_add_with_two_different_frame_rates(self):
        """
        Adding two timecodes with different framerates creates a
        timecode whose framerate matches the left-hand timecode's framerate
        """

        tc1 = Timecode('29.97', '00:00:00:00')
        tc2 = Timecode('24', '00:00:00:10')
        tc3 = tc1 + tc2
        self.assertEqual('29.97', tc3.framerate)
        self.assertEqual(12, tc3.frames)
        self.assertEqual('00:00:00:11', tc3)

    def test_frame_number_attribute_value_is_correctly_calculated(self):
        """Timecode.frame_number calculations"""

        tc1 = Timecode('24', '00:00:00:00')
        self.assertEqual(1, tc1.frames)
        self.assertEqual(0, tc1.frame_number)

        tc2 = Timecode('24', '00:00:01:00')
        self.assertEqual(25, tc2.frames)
        self.assertEqual(24, tc2.frame_number)

        tc3 = Timecode('29.97', '00:01:00:00')
        self.assertEqual(1799, tc3.frames)
        self.assertEqual(1798, tc3.frame_number)

        tc4 = Timecode('30', '00:01:00:00')
        self.assertEqual(1801, tc4.frames)
        self.assertEqual(1800, tc4.frame_number)

        tc5 = Timecode('50', '00:01:00:00')
        self.assertEqual(3001, tc5.frames)
        self.assertEqual(3000, tc5.frame_number)

        tc6 = Timecode('59.94', '00:01:00:00')
        self.assertEqual(3597, tc6.frames)
        self.assertEqual(3596, tc6.frame_number)

        tc7 = Timecode('60', '00:01:00:00')
        self.assertEqual(3601, tc7.frames)
        self.assertEqual(3600, tc7.frame_number)

    def test_op_overloads_subtract(self):
        """__sub__ functionality"""

        def assertTcSubtracted(base_tc, sub_tc, expected_str, expected_frs):
            from_tc = base_tc - sub_tc
            from_frames = base_tc - sub_tc.frames

            self.assertIsNot(base_tc._framerate, from_tc._framerate,
                             "New timecode from subtraction has its own "
                             "framerate object")
            self.assertEqual(from_tc, from_frames,
                             "Subtracting a timecode results in the same offset"
                             " as subtracting the equivalent number of frames")

            for _tc in (from_tc, from_frames):
                self.assertIsInstance(_tc, Timecode)
                self.assertEqual(expected_str, _tc.__str__())
                self.assertEqual(expected_frs, _tc.frames)

        tc = Timecode('23.98', '03:36:09:23')
        tc2 = Timecode('23.98', '00:00:29:23')
        assertTcSubtracted(tc, tc2, "03:35:39:23", 310560)

        tc = Timecode('25', '03:36:09:23')
        tc2 = Timecode('25', '00:00:29:23')
        assertTcSubtracted(tc, tc2, "03:35:39:24", 323500)

        tc = Timecode('29.97', '03:36:09:23')
        tc2 = Timecode('29.97', '00:00:29:23')
        assertTcSubtracted(tc, tc2, "03:35:39:27", 387810)

        tc = Timecode('30', '03:36:09:23')
        tc2 = Timecode('30', '00:00:29:23')
        assertTcSubtracted(tc, tc2, "03:35:39:29", 388200)

        tc = Timecode('59.94', '03:36:09:23')
        tc2 = Timecode('59.94', '00:00:29:23')
        assertTcSubtracted(tc, tc2, "03:35:39:55", 775620)

        tc = Timecode('60', '03:36:09:23')
        tc2 = Timecode('60', '00:00:29:23')
        assertTcSubtracted(tc, tc2, "03:35:39:59", 776400)

        tc = Timecode('ms', '03:36:09:230')
        tc2 = Timecode('ms', '01:06:09:230')
        assertTcSubtracted(tc, tc2, "02:29:59:999", 9000000)

        tc = Timecode('24', frames=12000)
        tc2 = Timecode('24', frames=485)
        assertTcSubtracted(tc, tc2, "00:07:59:18", 11515)

    def test_op_overloads_mult(self):
        """__mult__ functionality"""

        def assertTcMultiplied(base_tc, add_tc, expected_str, expected_frs):
            from_tc = base_tc * add_tc
            from_frames = base_tc * add_tc.frames

            self.assertIsNot(base_tc._framerate, from_tc._framerate,
                             "New timecode from multiplication has its own "
                             "framerate object")
            self.assertEqual(from_tc, from_frames,
                             "Multiplying a timecode results in the same "
                             "offset as multiplying by the equivalent number "
                             "of frames")

            for _tc in (from_tc, from_frames):
                self.assertIsInstance(_tc, Timecode)
                self.assertEqual(expected_str, _tc.__str__())
                self.assertEqual(expected_frs, _tc.frames)

        tc = Timecode('23.98', '03:36:09:23')
        tc2 = Timecode('23.98', '00:00:29:23')
        assertTcMultiplied(tc, tc2, "04:09:35:23", 224121600)

        tc = Timecode('25', '03:36:09:23')
        tc2 = Timecode('25', '00:00:29:23')
        assertTcMultiplied(tc, tc2, "10:28:20:00", 242862501)

        tc = Timecode('29.97', '00:00:09:23')
        tc2 = Timecode('29.97', '00:00:29:23')
        assertTcMultiplied(tc, tc2, "02:26:09:29", 262836)

        tc = Timecode('30', '03:36:09:23')
        tc2 = Timecode('30', '00:00:29:23')
        assertTcMultiplied(tc, tc2, "04:50:01:05", 347850036)

        tc = Timecode('59.94', '03:36:09:23')
        tc2 = Timecode('59.94', '00:00:29:23')
        assertTcMultiplied(tc, tc2, "18:59:27:35", 1371305376)

        tc = Timecode('60', '03:36:09:23')
        tc2 = Timecode('60', '00:00:29:23')
        assertTcMultiplied(tc, tc2, "19:00:21:35", 1372681296)

        tc = Timecode('ms', '03:36:09:230')
        tc2 = Timecode('ms', '01:06:09:230')
        assertTcMultiplied(tc, tc2, "17:22:11:360", 51477873731361)

        tc = Timecode('24', frames=12000)
        tc2 = Timecode('24', frames=485)
        assertTcMultiplied(tc, tc2, "19:21:39:23", 5820000)

    # ToDo: Add tests for __div__. Alternatively, remove div functionality?

    def test_24_hour_limit_in_24fps(self):
        """24fps timecode loops back after 24 hours"""

        tc = Timecode('24', '00:00:00:21')
        tc2 = Timecode('24', '23:59:59:23')
        self.assertEqual(
            '00:00:00:21',
            (tc + tc2).__str__()
        )
        self.assertEqual(
            '02:00:00:00',
            (tc2 + 159840001).__str__()
        )

    def test_24_hour_limit_in_2997fps(self):
        """29.97fps timecode loops back after 24 hours"""

        tc = Timecode('29.97', '00:00:00:21')
        self.assertTrue(tc._framerate.isDropFrame)
        self.assertEqual(22, tc.frames)

        tc2 = Timecode('29.97', '23:59:59:29')
        self.assertTrue(tc2._framerate.isDropFrame)
        self.assertEqual(2589408, tc2.frames)

        self.assertEqual(
            '00:00:00:21',
            tc.__repr__()
        )
        self.assertEqual(
            '23:59:59:29',
            tc2.__repr__()
        )

        self.assertEqual(
            '00:00:00:21',
            (tc + tc2).__str__()
        )

        self.assertEqual(
            '02:00:00:00',
            (tc2 + 215785).__str__()
        )

        self.assertEqual(
            '02:00:00:00',
            (tc2 + 215785 + 2589408).__str__()
        )

        self.assertEqual(
            '02:00:00:00',
            (tc2 + 215785 + 2589408 + 2589408).__str__()
        )

    def test_24_hour_limit(self):
        """Timecode addition and conversion"""
        # ToDo: Split this into multiple, more explicit tests

        tc0 = Timecode('59.94', '23:59:59:29')
        self.assertEqual(5178786, tc0.frames)
        tc0 = Timecode('29.97', '23:59:59:29')
        self.assertEqual(2589408, tc0.frames)

        tc1 = Timecode('29.97', frames=2589408)
        self.assertEqual('23:59:59:29', tc1.__str__())

        tc2 = Timecode('29.97', '23:59:59:29')
        tc3 = tc2 + 1
        self.assertEqual('00:00:00:00', tc3.__str__())

        tc2 = Timecode('29.97', '23:59:59:29')
        tc3 = tc2 + 21
        self.assertEqual('00:00:00:20', tc3.__str__())

        tc = Timecode('29.97', '00:00:00:21')
        tc2 = Timecode('29.97', '23:59:59:29')
        tc3 = (tc + tc2)
        self.assertEqual('00:00:00:21', tc3.__str__())

        tc = Timecode('29.97', '04:20:13:21')
        tca = Timecode('29.97', frames=467944)
        self.assertEqual(467944, tca.frames)
        self.assertEqual(467944, tc.frames)
        self.assertEqual('04:20:13:21', tca.__str__())
        self.assertEqual('04:20:13:21', tc.__str__())

        tc2 = Timecode('29.97', '23:59:59:29')
        self.assertEqual(2589408, tc2.frames)
        self.assertEqual('23:59:59:29', tc2.__str__())
        tc2a = Timecode('29.97', frames=2589408)
        self.assertEqual(2589408, tc2a.frames)
        self.assertEqual('23:59:59:29', tc2a.__str__())

        tc3 = (tc + tc2)
        self.assertEqual('04:20:13:21', tc3.__str__())

        tc = Timecode('59.94', '04:20:13:21')
        self.assertEqual('04:20:13:21', tc.__str__())

        tc = Timecode('59.94', frames=935866)
        self.assertEqual('04:20:13:21', tc.__str__())

        tc2 = Timecode('59.94', '23:59:59:59')
        tc3 = (tc + tc2)
        self.assertEqual('04:20:13:21', tc3.__str__())

    # def test_exceptions(self):
    #     """test exceptions
    #     """
    #     with self.assertRaises(TimecodeError) as cm:
    #         Timecode('23.98', '01:20:30:303')
    # 
    #     self.assertEqual(
    #         'Timecode string parsing error. 01:20:30:303',
    #         cm.exception.__str__()
    #     )
    # 
    #     with self.assertRaises(TimecodeError) as cm:
    #         Timecode('24', '01:20:30:303')
    #     
    #     self.assertEqual(
    #         'Timecode string parsing error. 01:20:30:303',
    #         cm.exception.__str__()
    #     )
    #     
    #     with self.assertRaises(TimecodeError) as cm:
    #         Timecode('29.97', '01:20:30:303')
    #     
    #     self.assertEqual(
    #         'Timecode string parsing error. 01:20:30:303',
    #         cm.exception.__str__()
    #     )
    # 
    #     with self.assertRaises(TimecodeError) as cm:
    #         Timecode('30', '01:20:30:303')
    #     
    #     self.assertEqual(
    #         'Timecode string parsing error. 01:20:30:303',
    #         cm.exception.__str__()
    #     )
    # 
    #     with self.assertRaises(TimecodeError) as cm:
    #         Timecode('59.94', '01:20:30:303')
    #     
    #     self.assertEqual(
    #         'Timecode string parsing error. 01:20:30:303',
    #         cm.exception.__str__()
    #     )
    #     
    #     with self.assertRaises(TimecodeError) as cm:
    #         Timecode('60', '01:20:30:303')
    #     
    #     self.assertEqual(
    #         'Timecode string parsing error. 01:20:30:303',
    #         cm.exception.__str__()
    #     )
    #     
    #     with self.assertRaises(TimecodeError) as cm:
    #         Timecode('ms', '01:20:30:3039')
    #     
    #     self.assertEqual(
    #         'Timecode string parsing error. 01:20:30:3039',
    #         cm.exception.__str__()
    #     )
    #     
    #     with self.assertRaises(TimecodeError) as cm:
    #         Timecode('60', '01:20:30:30')
    #     
    #     self.assertEqual(
    #         'Drop frame with 60fps not supported, only 29.97 & 59.94.',
    #         cm.exception.__str__(),
    #     )
    #     
    #     tc = Timecode('29.97', '00:00:09:23')
    #     tc2 = 'bum'
    #     with self.assertRaises(TimecodeError) as cm:
    #         d = tc * tc2
    #     self.assertEqual(
    #         "Type str not supported for arithmetic.",
    #         cm.exception.__str__()
    #     )
    #     
    #     tc = Timecode('30', '00:00:09:23')
    #     tc2 = 'bum'
    #     with self.assertRaises(TimecodeError) as cm:
    #         d = tc + tc2
    #     
    #     self.assertEqual(
    #         "Type str not supported for arithmetic.",
    #         cm.exception.__str__()
    #     )
    #     
    #     tc = Timecode('24', '00:00:09:23')
    #     tc2 = 'bum'
    #     with self.assertRaises(TimecodeError) as cm:
    #         d = tc - tc2
    #     
    #     self.assertEqual(
    #         "Type str not supported for arithmetic.",
    #         cm.exception.__str__()
    #     )
    #     
    #     tc = Timecode('ms', '00:00:09:237')
    #     tc2 = 'bum'
    #     with self.assertRaises(TimecodeError) as cm:
    #         d = tc / tc2
    #     
    #     self.assertEqual(
    #         "Type str not supported for arithmetic.",
    #         cm.exception.__str__()
    #     )
