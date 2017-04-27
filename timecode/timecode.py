#!-*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2014 Joshua Banton and PyTimeCode developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from framerate import Framerate


class Timecode(object):

    # Common conversion multipliers
    _HOUR_PER_DAY = 24
    _MIN_PER_HOUR = 60
    _SEC_PER_MIN = 60
    _SEC_PER_HOUR = _SEC_PER_MIN * _MIN_PER_HOUR

    def __init__(self, framerate, start_timecode=None, start_seconds=None,
                 frames=None):
        """An SMPTE timecode object. Represents an absolute number of frames
        modulated by the assigned framerate.

        Can be initialized using a timecode string representation, a total
        number of seconds, or a total number of frames. If more than one of
        these values are provided, only one value will be used, selected in the
        following order of precedence: timecode > frames > . If no starting
        value is provided, it will be initialized at 00:00:00:00

        :param basestring, int, float, Framerate framerate: The frame rate of
          the Timecode instance. It will be converted to a Framerate object
          if it is not one already. Required. Raises FramerateError if value
          is invalid.
        :param str, None start_timecode: String timecode representation.
`       :param float, None, int start_seconds: Number of seconds to represent..
        :param int, None frames: Number of frames to represent
        :raises: FramerateError
        """

        if isinstance(framerate, Framerate):
            self._framerate = framerate
        else:
            # NOTE: This will raise a FramerateError if framerate is invalid
            self._framerate = Framerate(framerate)

        self.frames = None

        # attribute override order
        # start_timecode > frames > start_seconds
        if start_timecode:
            self.frames = self.time_to_frames(*self.split_timecode(start_timecode))
        else:
            if frames is not None:  # because 0==False, and frames can be 0
                self.frames = frames
            elif start_seconds is not None:
                self.frames = self.time_to_frames(seconds=start_seconds)
            else:
                # use default value of 00:00:00:00
                self.frames = self.time_to_frames()

    def set_timecode(self, timecode):
        """
        Set current value to new timecode.
        :param str timecode: Timecode string representation
        """

        self.frames = self.time_to_frames(*self.split_timecode(timecode))

    def time_to_frames(self, hours=0, minutes=0, seconds=0, frames=0):
        """
        Convert real times to frames modulated by assigned framerate.
        Values that should wrap into the next highest unit will be handled
        automatically (eg. 60 seconds will become 1 minute).
        :param int, float hours: Number of hours
        :param int, float minutes: Number of minutes
        :param int, float seconds: Number of seconds
        :param int frames: Number of frames
        """

        # Drop drop_frame number of frames every minute except when minute
        # is divisible by 10.
        total_minutes = (hours * self._MIN_PER_HOUR) + minutes
        frs_to_drop = self._framerate.framesDroppedPerMinute * (total_minutes - (total_minutes // 10))

        # Finish converting time to frames, then remove and dropped frames.
        frame_number = (((total_minutes * self._SEC_PER_MIN) + seconds) * int(self._framerate)) + frames - frs_to_drop

        # Calculated frame number is an offset from starting frame, so
        # increment by 1 to include the starting frame.
        frame_count = frame_number + 1

        return frame_count

    def frames_to_time(self, frames):
        """
        Convert frames to time values.
        :returns (int, int, int, int): Tuple of time values (hours, minutes,
        seconds, frames)
        """
        ffps = float(self._framerate)

        # From dropdrame rates, dropped frames is 6% of the rate rounded to nearest integer
        frdrop_per_min = self._framerate.framesDroppedPerMinute

        # Number of frames in an hour
        frames_per_hour = int(round(ffps * self._SEC_PER_HOUR))
        # Number of frames in a day - timecode rolls over after 24 hours
        frames_per_24_hours = frames_per_hour * self._HOUR_PER_DAY
        # Number of frames per ten minutes
        frames_per_10_minutes = int(round(ffps * self._SEC_PER_MIN * 10))
        # Number of frames per minute is the round of the framerate * 60 minus
        # the number of dropped frames
        frames_per_minute = int(round(ffps) * self._SEC_PER_MIN) - frdrop_per_min

        # Remove base frame from count to generate offset
        frame_number = frames - 1

        if frame_number < 0:
            # Negative time. Add 24 hours.
            frame_number += frames_per_24_hours

        # If frame_number is greater than 24 hrs, next operation will rollover
        # clock
        frame_number %= frames_per_24_hours

        if self._framerate.isDropFrame:
            d = frame_number // frames_per_10_minutes
            m = frame_number % frames_per_10_minutes
            if m > frdrop_per_min:
                frame_number += ((frdrop_per_min * 9 * d) +
                                 (frdrop_per_min * ((m - frdrop_per_min) // frames_per_minute)))
            else:
                frame_number += frdrop_per_min * 9 * d

        # Convert final frame number to time
        ifps = int(self._framerate)
        total_seconds = (frame_number // ifps)
        total_minutes = (total_seconds // 60)

        frs = frame_number % ifps
        secs = total_seconds % 60
        mins = total_minutes % 60
        hrs = total_minutes // 60

        return hrs, mins, secs, frs

    @staticmethod
    def split_timecode(timecode):
        """
        Convert timecode string into time unit numbers.
        Accepts both frame-relative ('00:00:00:00' or '00:00:00;00') and
        millisecond-relative '00:00:00:000' forms
        """
        return map(int, timecode.replace(';', ':').replace('.', ':').split(':'))

    def add_frames(self, frames):
        """
        Add frames to current value
        :param int frames: Number of frames to add
        """

        # ToDo: Safeguard add_frames against non-int values
        self.frames += frames

    def sub_frames(self, frames):
        # ToDo: Safeguard sub_frames against non-int values
        """
        Subtract frames from current value
        :param int frames: Number of frames to substract
        """

        self.add_frames(-frames)

    def mult_frames(self, frames):
        """
        Multiply current number of frames
        :param int, float frames: Value to multiply by
        """

        self.frames *= frames

    def div_frames(self, frames):
        """
        Divide current number of frames
        :param int, float frames: Value to divide by
        """

        # ToDo: Safeguard div_frames against non-number values and div-by-zero
        self.frames = self.frames / frames

    def __eq__(self, other):

        if isinstance(other, Timecode):
            return (self.framerate == other.framerate and
                    self.frames == other.frames)
        elif isinstance(other, str):
            new_tc = Timecode(self.framerate, other)
            return self.__eq__(new_tc)
        elif isinstance(other, int):
            return self.frames == other

    def __add__(self, other):
        """
        Create new Timecode object whose total frame count is the sum of this
        timecode and the second value.
        :param Timecode, int other: Value to add
        """
        # ToDo: rewrite to be consistent with other math overrides
        # duplicate current timecode
        tc = Timecode(self.framerate, frames=self.frames)

        if isinstance(other, Timecode):
            tc.add_frames(other.frames)
        elif isinstance(other, int):
            tc.add_frames(other)
        else:
            raise TimecodeError(
                'Type %s not supported for arithmetic.' %
                other.__class__.__name__
            )

        return tc

    def __sub__(self, other):
        """
        Create new Timecode object whose total frame count is the difference
        of this timecode and the second value.
        :param Timecode, int other: Value to subtract
        """

        if isinstance(other, Timecode):
            subtracted_frames = self.frames - other.frames
        elif isinstance(other, int):
            subtracted_frames = self.frames - other
        else:
            raise TimecodeError(
                'Type %s not supported for arithmetic.' %
                other.__class__.__name__
            )
        return Timecode(self.framerate, start_timecode=None,
                        frames=subtracted_frames)

    def __mul__(self, other):
        """
        Create new Timecode object whose total frame count is the product of
        this timecode and the second value.
        :param Timecode, int, float other: Value to multiply by
        """

        if isinstance(other, Timecode):
            multiplied_frames = self.frames * other.frames
        elif isinstance(other, int):
            multiplied_frames = self.frames * other
        else:
            raise TimecodeError(
                'Type %s not supported for arithmetic.' %
                other.__class__.__name__
            )
        return Timecode(self.framerate, start_timecode=None,
                        frames=multiplied_frames)

    def __div__(self, other):
        """
        Create new Timecode object whose total frame count is the quotient of
        this timecode and the second value.
        :param Timecode, int, float other: Value to divide by
        """

        if isinstance(other, Timecode):
            div_frames = self.frames / other.frames
        elif isinstance(other, int):
            div_frames = self.frames / other
        else:
            raise TimecodeError(
                'Type %s not supported for arithmetic.' %
                other.__class__.__name__
            )
        return Timecode(self.framerate, start_timecode=None,
                        frames=div_frames)

    def __repr__(self):
        # ToDo: Restricting frames value to 2 digits is not always correct
        return "%02d:%02d:%02d:%02d" % self.frames_to_time(self.frames)

    @property
    def hrs(self):
        """
        Number of whole hours in Timecode.
        :rtype int
        """

        hrs, mins, secs, frs = self.frames_to_time(self.frames)
        return hrs

    @property
    def mins(self):
        """
        Number of whole minutes in Timecode. Does not include minutes from
        hours unit.
        :rtype int
        """

        hrs, mins, secs, frs = self.frames_to_time(self.frames)
        return mins

    @property
    def secs(self):
        """
        Number of whole seconds in Timecode. Does not include seconds from
        minutes or hours units.
        :rtype int
        """

        hrs, mins, secs, frs = self.frames_to_time(self.frames)
        return secs

    @property
    def frs(self):
        """
        Number of whole frames in Timecode. Does not include frames from
        minutes, hours, or seconds units.
        :rtype int
        """

        hrs, mins, secs, frs = self.frames_to_time(self.frames)
        return frs

    @property
    def frame_number(self):
        """
        The 0-based frame number of the timecode
        :rtype int
        """
        return self.frames - 1

    @property
    def framerate(self):
        """
        String representation of the timecode framerate
        :rtype str
        """
        # Don't expose the Framerate object directly to minimize risk from
        # accidentally changing it. If adjusting framerates is desired, that
        # should be added to the API.
        return str(self._framerate)


class TimecodeError(Exception):
    """Raised when an error occurred in timecode calculation
    """
    pass
