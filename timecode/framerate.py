class Framerate(object):

    _NTSC_NDF_rates = ['30', '60']
    _NTSC_DF_rates = ['29.97', '59.94']
    _NTSC_P_rates = ['23.98', '24']  # Progressive rates. Is 24fps really NTSC?
    _NTSC_rates = _NTSC_DF_rates + _NTSC_NDF_rates + _NTSC_P_rates
    _PAL_rates = ['25', '50']
    # Special case framerates
    _misc_rates = {'ms': '1000', 'frames': '1'}
    _supported_framerates = _NTSC_NDF_rates + _NTSC_DF_rates + _NTSC_P_rates + _PAL_rates + list(_misc_rates.iterkeys())

    _DF_to_NDF = dict(zip(_NTSC_DF_rates, _NTSC_NDF_rates))
    _NDF_to_DF = dict(zip(_NTSC_NDF_rates, _NTSC_DF_rates))

    def __init__(self, frames_per_second):

        self._framerate = self._validate_framerate(frames_per_second)

        self._drop_frame = None
        self._int_framerate = None

    def __float__(self):
        if self.framerate in self._misc_rates:
            return float(self._misc_rates[self.framerate])
        else:
            return float(self._framerate)

    def __int__(self):
        if self._framerate in self._misc_rates:
            return int(self._misc_rates[self._framerate])
        elif self.isDropFrame:
            return int(round(float(self.nonDropFrameRate)))
        else:
            return int(round(float(self.framerate)))

    def __str__(self):
        return self.framerate

    def __eq__(self, other):
        if isinstance(other, int):
            return int(self) == other
        elif isinstance(other, float):
            return float(self) == other
        elif isinstance(other, basestring):
            # Try to convert str to float to eliminate false negatives due to
            # significant digits. If that fails, compare strings directly in
            # case it's a misc case.
            try:
                return float(self) == float(other)
            except ValueError:
                return self.framerate == other
        elif isinstance(other, self.__class__):
            return self.framerate == other.framerate
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def _validate_framerate(self, fps):
        if not isinstance(fps, (basestring, int, float)):
            raise TypeError("Type {} not supported for fps".format(fps.__class__.__name__))

        # Convert to float to make sure float strings will be accepted
        if isinstance(fps, basestring) and fps not in self._misc_rates:
            try:
                fps = float(fps)
            except ValueError:
                raise ValueError("{} is not a valid framerate".format(fps))

        # Convert number types to strings for comparison. Reduces accidentally
        # including invalid rates by floating-point rounding. Still some margin
        # of error, but so small it should be safely ignorable.
        if isinstance(fps, float):
            fps = str(int(fps)) if fps.is_integer() else str(fps)
        elif isinstance(fps, int):
            fps = str(fps)

        if fps not in self._supported_framerates:
            raise ValueError("Framerate {} is not supported.".format(fps))

        return fps

    @property
    def framerate(self):
        """Return current framerate value as string"""
        return self._framerate

    @framerate.setter
    def framerate(self, value):
        self._framerate = self._validate_framerate(value)

    @property
    def isDropFrame(self):
        """Return True if Framerate is drop-frame"""
        return self.framerate in self._NTSC_DF_rates

    @property
    def dropFrameRate(self):
        """Return drop-frame equivalent of current framerate.
        Returns None if framerate has no drop-frame equivalent
        """
        if self._framerate not in self._NTSC_rates or self._framerate in self._NTSC_P_rates:
            return None
        else:
            return self._framerate if self._framerate in self._NTSC_DF_rates else self._NDF_to_DF[self._framerate]

    @property
    def nonDropFrameRate(self):
        """Return non-drop-frame equivalent of current framerate.
        Returns current framerate if already non-drop-frame or if framerate is
        PAL.
        """
        if (self._framerate in self._PAL_rates) or (self._framerate in self._NTSC_P_rates):
            return self.framerate
        elif self._framerate not in self._misc_rates:
            return self._framerate if self._framerate in self._NTSC_NDF_rates else self._DF_to_NDF[self._framerate]

    @property
    def framesDroppedPerMinute(self):
        """Return rounded percent of frames to drop."""
        # From dropdrame rates, dropped frames is 6% of the rate rounded to nearest integer
        return int(round(float(self.framerate) * .066666)) if self.isDropFrame else 0

    @property
    def isPAL(self):
        """Return True if assigned framerate is PAL"""
        return self._framerate in self._PAL_rates

    @property
    def isNTSC(self):
        """Return True if assigned framerate is NTSC"""
        return any(self._framerate in f for f in (self._NTSC_DF_rates, self._NTSC_NDF_rates, self._NTSC_P_rates))
