
import sys

import pytest

from timecode.framerate import Framerate, FramerateError


def flatten(in_list):
    return [i for sub in in_list for i in sub]


# Timecodes
NTSC_NDF_rates = ['30', '60']
NTSC_DF_rates = ['29.97', '59.94']
NTSC_P_rates = ['24', '23.98']
NTSC_rates = flatten([NTSC_NDF_rates, NTSC_DF_rates, NTSC_P_rates])
PAL_rates = ['25', '50']
misc_rates = {"ms": 1000, "frames": 1}
all_rates = NTSC_rates + PAL_rates + list(misc_rates.iterkeys())

DF_to_NDF = dict(zip(NTSC_DF_rates, NTSC_NDF_rates))
NDF_to_DF = dict(zip(NTSC_NDF_rates, NTSC_DF_rates))

# Valid framerate input values
valid_int_values = [24, 25, 30, 50, 60]
valid_float_values = [23.98, 24.0, 25.00, 29.97, 30.000, 50.0, 59.94, 60.00000000]
valid_str_values = ['23.98', '23.980', '24', '24.0', '25', '25.00', '29.97', '30', '30.0', '50',
                    '50.00', '59.94', '59.94000', '60', '60.000000']
valid_unicode_values = [u'23.98', u'23.980', u'24', u'24.0', u'25', u'25.00', u'29.97', u'30', u'30.0', u'50',
                        u'50.00', u'59.94', u'59.94000', u'60', u'60.000000']

valid_values = flatten([valid_int_values, valid_float_values, valid_str_values, valid_unicode_values])

# Invalid framerate input values
invalid_int_values = [-sys.maxint - 1, 100, -1, 0, 1, 23, 26, 29, 31, 49, 51, 59, 61, sys.maxint]
invalid_float_values = [-100000000.00, -123463.34532, -.0000001, .00004, 23.979999999, 23.99999999, 59.9399999999,
                        1000.2341234, 12349082341234]
invalid_str_values = ['not_a_number', '-205.0', '24.0.1', '23.9800000001', '239485029345680']
invalid_unicode_values = [u'not_a_number', u'-205.0', u'24.0.1', u'23.9800000001', u'239485029345680']
invalid_type_values = [None, ['24'], (29.97, 30), {'fps': 30}]

invalid_values = flatten([invalid_int_values, invalid_float_values, invalid_str_values, invalid_unicode_values,
                          invalid_type_values])


@pytest.mark.parametrize('fps', valid_values + list(misc_rates.iterkeys()))
def testNewValidFramerate(fps):
    """Test that a Framerate can be created from a valid base framerate"""
    fr = Framerate(fps)
    # Check that Framerate value matches parameter
    if isinstance(fps, basestring) and fps not in misc_rates:
        # No try/except here; we expect this value to be valid.
        fps = float(fps)
    if isinstance(fps, float):
        assert fr.framerate == str(int(fps)) if fps.is_integer() else str(fr)
    else:
        assert fr.framerate == str(fps)


@pytest.mark.parametrize('fps', invalid_values)
def testNewInvalidFramerate(fps):
    with pytest.raises(FramerateError):
        fr = Framerate(fps)


@pytest.mark.parametrize('fps', all_rates)
def testFloatConversion(fps):
    fr = Framerate(fps)

    # If a misc rate, need to map to numeric value before testing
    fps_value = misc_rates.get(fps, fps)

    assert float(fr) == float(fps_value)


@pytest.mark.parametrize('fps', all_rates)
def testFloatConversion(fps):
    fr = Framerate(fps)

    # If a misc rate, need to map to numeric value before testing
    fps_value = misc_rates.get(fps, fps)

    assert int(fr) == int(round(float(fps_value)))


@pytest.mark.parametrize('fps', invalid_values)
def testSetInvalidFramerateValue(fps):
    fr = Framerate(24)
    with pytest.raises(FramerateError):
        fr.framerate = fps


@pytest.mark.parametrize('fps', all_rates)
def testIsEqual(fps):
    fr = Framerate(fps)

    # If a misc rate, need to map to numeric value before testing
    fps_value = misc_rates.get(fps, fps)

    assert fr == fps_value

@pytest.mark.parametrize('fps', [v for v in (valid_values + invalid_values) if v not in (24, '24', '24.0')])
def testIsNotEqual(fps):
    fr = Framerate(24)
    assert fr != fps


@pytest.mark.parametrize('fps', all_rates)
def testDropFrameIdentification(fps):
    fr = Framerate(fps)
    assert fr.isDropFrame == (fps in NTSC_DF_rates)


@pytest.mark.parametrize('fps', NTSC_DF_rates + NTSC_NDF_rates)
def testNTSCNonProgressiveDropFrameRates(fps):
    fr = Framerate(fps)
    assert fr.dropFrameRate == (fps if fps in NTSC_DF_rates else NDF_to_DF[fps])


@pytest.mark.parametrize('fps', NTSC_P_rates + PAL_rates + list(misc_rates.iterkeys()))
def testOtherDropFrameRates(fps):
    fr = Framerate(fps)
    assert fr.dropFrameRate is None


@pytest.mark.parametrize(('rate', 'expected_frames_dropped'),
                         [(29.97, 2), (59.94, 4)] + [(r, 0) for r in NTSC_NDF_rates + NTSC_P_rates + PAL_rates +
                                                     list(misc_rates.iterkeys())])
def testFramesDroppedPerMinute(rate, expected_frames_dropped):
    fr = Framerate(rate)
    assert fr.framesDroppedPerMinute == expected_frames_dropped


@pytest.mark.parametrize('rate', all_rates)
def testStandardsIdentification(rate):
    fr = Framerate(rate)
    assert fr.isNTSC == (rate in NTSC_rates)
    assert fr.isPAL == (rate in PAL_rates)


@pytest.mark.parametrize('rate', all_rates)
def testCopy(rate):
    fr_base = Framerate(rate)
    fr_copy = fr_base.copy()
    assert fr_copy == fr_base
    assert fr_copy is not fr_base
