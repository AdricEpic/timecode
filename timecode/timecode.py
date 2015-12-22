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
        """The main timecode class.

        Does all the calculation over frames, so the main data it holds is
        frames, then when required it converts the frames to a timecode by
        using the frame rate setting.

        :param basestring, int, float, Framerate framerate: The frame rate of
          the Timecode instance. It will be converted to a Framerate object
          if it is not one already. Required. Raises FramerateError if value
          is invalid.
        :param start_timecode: The start timecode. Use this to be able to
          set the timecode of this Timecode instance. It can be skipped and
          then the frames attribute will define the timecode, and if it is also
          skipped then the start_second attribute will define the start
          timecode, and if start_seconds is also skipped then the default value
          of '00:00:00:00' will be used.
        :type start_timecode: str or None
        :param start_seconds: A float or integer value showing the seconds.
        :param int frames: Timecode objects can be initialized with an
          integer number showing the total frames.
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
        """Sets the frames by using the given timecode
        """
        self.frames = self.time_to_frames(*self.split_timecode(timecode))

    def time_to_frames(self, hours=0, minutes=0, seconds=0, frames=0):
        """Converts the given timecode to frames
        """

        # Drop drop_frame number of frames every minute except when minute
        # is divisible by 10.
        total_minutes = (hours * self._MIN_PER_HOUR) + minutes
        frames_to_drop = self.framerate.framesDroppedPerMinute * (total_minutes - (total_minutes // 10))

        # Finish converting time to frames, then remove and dropped frames.
        frame_number = (((total_minutes * self._SEC_PER_MIN) + seconds) * int(self.framerate)) + frames - frames_to_drop

        # Calculated frame number is an offset from starting frame, so
        # increment by 1 to include the starting frame.
        frame_count = frame_number + 1

        return frame_count

    def frames_to_tc(self, frames):
        """Converts frames back to timecode

        :returns str: the string representation of the current time code
        """
        ffps = float(self._framerate)

        # From dropdrame rates, dropped frames is 6% of the rate rounded to nearest integer
        frames_dropped_per_min = self.framerate.framesDroppedPerMinute

        # Number of frames in an hour
        frames_per_hour = int(round(ffps * self._SEC_PER_HOUR))
        # Number of frames in a day - timecode rolls over after 24 hours
        frames_per_24_hours = frames_per_hour * self._HOUR_PER_DAY
        # Number of frames per ten minutes
        frames_per_10_minutes = int(round(ffps * self._SEC_PER_MIN * 10))
        # Number of frames per minute is the round of the framerate * 60 minus
        # the number of dropped frames
        frames_per_minute = int(round(ffps) * self._SEC_PER_MIN) - frames_dropped_per_min

        # Remove base frame from count to generate offset
        frame_number = frames - 1

        if frame_number < 0:
            # Negative time. Add 24 hours.
            frame_number += frames_per_24_hours

        # If frame_number is greater than 24 hrs, next operation will rollover
        # clock
        frame_number %= frames_per_24_hours

        if self.framerate.isDropFrame:
            d = frame_number // frames_per_10_minutes
            m = frame_number % frames_per_10_minutes
            if m > frames_dropped_per_min:
                frame_number += (frames_dropped_per_min * 9 * d) + \
                    frames_dropped_per_min * ((m - frames_dropped_per_min) // frames_per_minute)
            else:
                frame_number += frames_dropped_per_min * 9 * d

        # Convert final frame number to time
        ifps = int(self.framerate)
        total_seconds = (frame_number // ifps)
        total_minutes = (total_seconds // 60)

        frs = frame_number % ifps
        secs = total_seconds % 60
        mins = total_minutes % 60
        hrs = total_minutes // 60

        return hrs, mins, secs, frs

    @staticmethod
    def split_timecode(timecode):
        """parses timecode string frames '00:00:00:00' or '00:00:00;00' or
        milliseconds '00:00:00:000'
        """
        return map(int, timecode.replace(';', ':').replace('.', ':').split(':'))

    def __iter__(self):
        return self

    def next(self):
        self.add_frames(1)
        return self

    def back(self):
        self.sub_frames(1)
        return self

    def add_frames(self, frames):
        """adds or subtracts frames number of frames
        """
        self.frames += frames

    def sub_frames(self, frames):
        """adds or subtracts frames number of frames
        """
        self.add_frames(-frames)

    def mult_frames(self, frames):
        """multiply frames
        """
        self.frames *= frames

    def div_frames(self, frames):
        """adds or subtracts frames number of frames"""
        self.frames = self.frames / frames

    def __eq__(self, other):
        """the overridden equality operator
        """
        if isinstance(other, Timecode):
            return self._framerate == other.framerate and \
                self.frames == other.frames
        elif isinstance(other, str):
            new_tc = Timecode(self.framerate, other)
            return self.__eq__(new_tc)
        elif isinstance(other, int):
            return self.frames == other

    def __add__(self, other):
        """returns new Timecode instance with the given timecode or frames
        added to this one
        """
        # duplicate current one
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
        """returns new Timecode object with added timecodes"""
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
        """returns new Timecode object with added timecodes"""
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
        """returns new Timecode object with added timecodes"""
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
        return "%02d:%02d:%02d:%02d" % \
            self.frames_to_tc(self.frames)

    @property
    def hrs(self):
        hrs, mins, secs, frs = self.frames_to_tc(self.frames)
        return hrs

    @property
    def mins(self):
        hrs, mins, secs, frs = self.frames_to_tc(self.frames)
        return mins

    @property
    def secs(self):
        hrs, mins, secs, frs = self.frames_to_tc(self.frames)
        return secs

    @property
    def frs(self):
        hrs, mins, secs, frs = self.frames_to_tc(self.frames)
        return frs

    @property
    def frame_number(self):
        """returns the 0 based frame number of the current timecode instance
        """
        return self.frames - 1

    @property
    def framerate(self):
        return self._framerate


class TimecodeError(Exception):
    """Raised when an error occurred in timecode calculation
    """
    pass
