import unittest
import sys

from timecode.framerate import Framerate


class FramerateTests(unittest.TestCase):
    # Timecodes
    NTSC_NDF_rates = ['30', '60']
    NTSC_DF_rates = ['29.97', '59.94']
    NTSC_P_rates = ['24', '23.98']
    PAL_rates = ['25', '50']
    misc_rates = {"ms": 1000, "frames": 1}

    DF_to_NDF = dict(zip(NTSC_DF_rates, NTSC_NDF_rates))
    NDF_to_DF = dict(zip(NTSC_NDF_rates, NTSC_DF_rates))

    # Valid framerate input values
    valid_int_values = [24, 25, 30, 50, 60]
    valid_float_values = [23.98, 24.0, 25.00, 29.97, 30.000, 50.0, 59.94, 60.00000000]
    valid_str_values = ['23.98', '23.980', '24', '24.0', '25', '25.00', '29.97', '30', '30.0', '50',
                        '50.00', '59.94', '59.94000', '60', '60.000000']
    valid_unicode_values = [u'23.98', u'23.980', u'24', u'24.0', u'25', u'25.00', u'29.97', u'30', u'30.0', u'50',
                            u'50.00', u'59.94', u'59.94000', u'60', u'60.000000']

    valid_value_lists = [valid_int_values, valid_float_values, valid_str_values, valid_unicode_values]

    # Invalid framerate input values
    invalid_int_values = [-sys.maxint - 1, 100, -1, 0, 1, 23, 26, 29, 31, 49, 51, 59, 61, sys.maxint]
    invalid_float_values = [-100000000.00, -123463.34532, -.0000001, .00004, 23.979999999, 23.99999999, 59.9399999999,
                            1000.2341234, 12349082341234]
    invalid_str_values = ['not_a_number', '-205.0', '24.0.1', '23.9800000001', '239485029345680']
    invalid_unicode_values = [u'not_a_number', u'-205.0', u'24.0.1', u'23.9800000001', u'239485029345680']
    invalid_type_values = [None, ['24'], (29.97, 30), {'fps': 30}]

    invalid_value_lists = [invalid_int_values, invalid_float_values, invalid_str_values, invalid_unicode_values,
                           invalid_type_values]

    def shortDescription(self):
        description = super(FramerateTests, self).shortDescription()
        if description:
            description = "  " + description
        return description

    def test_init_valid_framerates(self):
        """Initializing with valid framerates"""

        def verify_valid_framerate(fps):
            fr = Framerate(fps)

            # Check that Framerate value matches parameter
            if isinstance(fps, basestring) and fps not in self.misc_rates:
                # No try/except here; we expect this value to be valid.
                fps = float(fps)
            if isinstance(fps, float):
                self.assertEqual(fr.framerate, str(int(fps)) if fps.is_integer() else str(fr))
            else:
                self.assertEqual(fr.framerate, str(fps))

        for valid_value_list in self.valid_value_lists:
            for valid_value in valid_value_list:
                verify_valid_framerate(valid_value)

        for valid_misc in self.misc_rates:
            verify_valid_framerate(valid_misc)

    def test_init_invalid_framerates(self):
        """Initializing with invalid framerates"""

        def verify_invalid_framerate(fps_):
            if isinstance(fps_, (basestring, int, float)):
                expected_exc = ValueError
            else:
                expected_exc = TypeError
            self.assertRaises(expected_exc, Framerate, fps_)

        for invalid_value_list in self.invalid_value_lists:
            for invalid_value in invalid_value_list:
                verify_invalid_framerate(invalid_value)

    def test_float_conversion(self):
        """__float__ functionality"""

        for number_rate in self.NTSC_NDF_rates + self.NTSC_DF_rates + self.NTSC_P_rates + self.PAL_rates:
            fr = Framerate(number_rate)
            self.assertEqual(float(fr), float(number_rate))

        for misc_rate in self.misc_rates:
            fr = Framerate(misc_rate)
            self.assertEqual(float(fr), float(self.misc_rates[misc_rate]))

    def test_int_conversion(self):
        """__int__ functionality"""

        for number_rate in self.NTSC_NDF_rates + self.NTSC_DF_rates + self.NTSC_P_rates + self.PAL_rates:
            fr = Framerate(number_rate)
            if number_rate in self.NTSC_DF_rates:
                self.assertEqual(int(fr), int(round(float(fr))))
            else:
                self.assertEqual(int(fr), int(round(float(number_rate))))

        for misc_rate in self.misc_rates:
            fr = Framerate(misc_rate)
            self.assertEqual(int(fr), int(self.misc_rates[misc_rate]))

    def test_set_valid_framerate_value(self):
        """Set framerate property to valid value"""

        for rate in self.NTSC_NDF_rates + self.NTSC_DF_rates + self.NTSC_P_rates + self.PAL_rates + list(self.misc_rates.iterkeys()):
            fr = Framerate(24)
            fr.framerate = rate
            self.assertEqual(rate, fr.framerate)

    def test_set_invalid_framerate_value(self):
        """Set framerate property to invalid value"""

        def set_value(obj, value):
            assert(isinstance(obj, Framerate))
            obj.framerate = value

        def verify_invalid_framerate(rate):
            if isinstance(rate, (basestring, int, float)):
                expected_exc = ValueError
            else:
                expected_exc = TypeError
            fr = Framerate(24)
            self.assertRaises(expected_exc, set_value, fr, rate)

        for invalid_value_list in self.invalid_value_lists:
            for invalid_value in invalid_value_list:
                verify_invalid_framerate(invalid_value)

    def test_equality_against_equivalent(self):
        """Compare Framerate against equivalent values"""

        for valid_value_list in self.valid_value_lists:
            for valid_value in valid_value_list:
                fr = Framerate(valid_value)
                self.assertEqual(fr, valid_value)

        for valid_value in self.misc_rates.iterkeys():
            fr = Framerate(valid_value)
            fr2 = Framerate(valid_value)

            self.assertEqual(fr, valid_value)
            self.assertEqual(fr, fr2)

    def test_equality_against_inqeual(self):
        """Compare Framerate against inequal values"""

        fr = Framerate(24)

        # Compare against other valid Framerates
        for value in self.valid_float_values:
            if value != 24:
                fr2 = Framerate(value)
                self.assertNotEqual(fr, fr2)

        # Compare against other non-Framerate values, both valid and invalid
        other_values = [25, 30, 50, 60, 23.98, 25.00, 29.97, 30.000, 50.0, 59.94, 60.00000000, '23.98', '23.980', '25',
                        '25.00', '29.97', '30', '30.0', '50', '50.00', '59.94', '59.94000', '60', '60.000000',
                        -sys.maxint - 1, 100, -1, 0, 1, 23, 26, 29, 31, 49, 51, 59, 61, sys.maxint, 'not_a_number',
                        '-205.0', '24.0.1', '23.9800000001', '239485029345680', None, ['24'], (29.97, 30), {'fps': 30}]

        for value in other_values:
            self.assertNotEqual(fr, value)

    def test_dropframe_identification(self):
        """Identification of dropframe rates"""

        for rate in self.NTSC_DF_rates:
            fr = Framerate(rate)
            self.assertTrue(fr.isDropFrame)

        for rate in self.NTSC_NDF_rates + self.PAL_rates + list(self.misc_rates.iterkeys()):
            fr = Framerate(rate)
            self.assertFalse(fr.isDropFrame)

    def test_dropframe_rate_NTSC_nonP(self):
        """NTSC non-progressive rates have dropframe-equivalent rates"""

        for rate in self.NTSC_DF_rates + self.NTSC_NDF_rates:
            fr = Framerate(rate)
            if rate in self.NTSC_DF_rates:
                self.assertEqual(fr.dropFrameRate, rate)
            else:
                self.assertEqual(fr.dropFrameRate, self.NDF_to_DF[rate])

    def test_dropframe_rate_others(self):
        """NTSC progressive and non-NTSC rates have no dropframe rate"""

        for rate in self.NTSC_P_rates + self.PAL_rates + list(self.misc_rates.iterkeys()):
            fr = Framerate(rate)
            self.assertIsNone(fr.dropFrameRate)

    def test_frames_dropped_per_min(self):
        """Dropframe rates drop the correct number of frames"""

        fr_DF_30 = Framerate(29.97)
        self.assertEqual(2, fr_DF_30.framesDroppedPerMinute)

        fr_DF_60 = Framerate(59.94)
        self.assertEqual(4, fr_DF_60.framesDroppedPerMinute)

        for rate in self.NTSC_NDF_rates + self.NTSC_P_rates + self.PAL_rates + list(self.misc_rates.iterkeys()):
            fr = Framerate(rate)
            self.assertEqual(0, fr.framesDroppedPerMinute)

    def test_standards_identification(self):
        """Identification of framerate standards"""
        for rate in self.NTSC_DF_rates + self.NTSC_NDF_rates + self.NTSC_P_rates:
            fr = Framerate(rate)
            self.assertTrue(fr.isNTSC)
            self.assertFalse(fr.isPAL)

        for rate in self.PAL_rates:
            fr = Framerate(rate)
            self.assertTrue(fr.isPAL)
            self.assertFalse(fr.isNTSC)

        for rate in self.misc_rates:
            fr = Framerate(rate)
            self.assertFalse(fr.isNTSC)
            self.assertFalse(fr.isPAL)

    def test_copy(self):
        """Copying functionality"""
        for value_list in self.valid_value_lists:
            for rate in value_list:
                fr_1 = Framerate(rate)
                fr_2 = fr_1.copy()
                self.assertEqual(fr_1, fr_2)
                self.assertIsNot(fr_1, fr_2)
