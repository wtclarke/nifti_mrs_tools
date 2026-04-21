"""Axes helper class for NIfTI-MRS objects.

Author:  Vasilis Karlaftis      <vasilis.karlaftis@ndcn.ox.ac.uk>

Copyright (C) 2026 University of Oxford
"""

import numpy as np
from mrs_tools.constants import PPM_SHIFT
from nifti_mrs.nifti_mrs import NIFTI_MRS


class Axes():
    """Generate spectral axes from NIfTI-MRS acquisition metadata."""

    def __init__(
            self,
            npoints: int,
            ResonantNucleus: str,
            SpectrometerFrequency: float,
            dwelltime: float,
            SpecFreqChemShift: float = None,
            RxOffset: float = 0.0):
        """Create an axes helper object.

        :param npoints: Number of points along the spectral dimension.
        :type npoints: int
        :param ResonantNucleus: Resonant nucleus string (e.g. ``1H``).
        :type ResonantNucleus: str
        :param SpectrometerFrequency: Spectrometer frequency in MHz.
        :type SpectrometerFrequency: float
        :param dwelltime: Spectral dwell time in seconds.
        :type dwelltime: float
        :param SpecFreqChemShift: Nominal chemical shift in ppm.
            If not provided defaults are used. Current defaults follow the
            FSL-MRS convention.
        :type SpecFreqChemShift: float [optional]
        :param RxOffset: Receiver chemical shift in ppm, defaults to 0.0.
        :type RxOffset: float [optional]
        """
        self._npoints               = int(npoints)
        self._ResonantNucleus       = str(ResonantNucleus)
        self._SpectrometerFrequency = float(SpectrometerFrequency)
        self._dwelltime             = float(dwelltime)
        self._RxOffset              = float(RxOffset)

        if self._npoints <= 0:
            raise ValueError('npoints must be positive.')
        if self._dwelltime <= 0:
            raise ValueError('dwelltime must be positive.')
        if self._SpectrometerFrequency <= 0:
            raise ValueError('SpectrometerFrequency must be positive.')

        if SpecFreqChemShift is None:
            self._SpecFreqChemShift = self.default_shift(self._ResonantNucleus)
        else:
            self._SpecFreqChemShift = float(SpecFreqChemShift)

    @classmethod
    def from_nifti_mrs(cls,
                       nifti_mrs_obj: NIFTI_MRS,
                       SpecFreqChemShift: float = None,
                       RxOffset: float = 0.0):
        """Initialise from a :class:`nifti_mrs.nifti_mrs.NIFTI_MRS` object.

        :param nifti_mrs_obj: NIfTI-MRS object to initialise from.
        :type nifti_mrs_obj: NIFTI_MRS
        :param SpecFreqChemShift: Nominal chemical shift in ppm.
            If not provided defaults are used. Current defaults follow the
            FSL-MRS convention.
        :type SpecFreqChemShift: float [optional]
        :param RxOffset: Receiver chemical shift in ppm, defaults to 0.0.
        :type RxOffset: float [optional]
        :return: Axes object initialised from the NIfTI-MRS object.
        :rtype: Axes
        """
        return cls(
            ResonantNucleus=nifti_mrs_obj.nucleus[0],
            SpectrometerFrequency=nifti_mrs_obj.spectrometer_frequency[0],
            dwelltime=nifti_mrs_obj.dwelltime,
            SpecFreqChemShift=SpecFreqChemShift,
            RxOffset=RxOffset,
            npoints=nifti_mrs_obj.shape[3])

    @staticmethod
    def default_shift(ResonantNucleus: str):
        """Return the default chemical shift position for a nucleus."""
        return PPM_SHIFT.get(str(ResonantNucleus), 0.0)

    @property
    def npoints(self):
        """Number of points in the spectral dimension."""
        return self._npoints

    @property
    def ResonantNucleus(self):
        """Resonant nucleus string (e.g. ``1H``)."""
        return self._ResonantNucleus

    @property
    def SpectrometerFrequency(self):
        """Spectrometer frequency in MHz."""
        return self._SpectrometerFrequency

    @property
    def dwelltime(self):
        """Dwell time in seconds."""
        return self._dwelltime

    @property
    def SpecFreqChemShift(self):
        """Nominal chemical shift in ppm."""
        return self._SpecFreqChemShift

    @property
    def RxOffset(self):
        """Receiver chemical shift in ppm."""
        return self._RxOffset

    @property
    def SpectralWidth(self):
        """Spectral width in Hz."""
        return 1.0 / self.dwelltime

    @property
    def ppmshift(self):
        """Chemical shift offset from SpectrometerFrequency in ppm."""
        return self.SpecFreqChemShift + self.RxOffset

    @staticmethod
    def hz2ppm(cf: float, hz: float, shift: bool = True, shift_amount: float = PPM_SHIFT['1H']):
        """Convert frequency scale to frequency scale with optional shift.

        :param cf: Spectrometer frequency in MHz.
        :type cf: float
        :param hz: Frequency in Hz.
        :type hz: float
        :param shift: Whether to apply chemical shift.
        :type shift: bool
        :param shift_amount: Chemical shift amount in ppm.
        :type shift_amount: float
        """
        if shift:
            return hz / cf + shift_amount
        else:
            return hz / cf

    @property
    def timeAxis(self) -> np.ndarray:
        """Return the time axis in seconds."""
        return np.linspace(self.dwelltime, self.dwelltime * self.npoints, self.npoints)

    @property
    def frequencyAxis(self) -> np.ndarray:
        """Return the frequency axis in Hz."""
        bandwidth = 1 / self.dwelltime
        return np.linspace(-bandwidth / 2, bandwidth / 2, self.npoints)

    @property
    def ppmAxis(self) -> np.ndarray:
        """Return the ppm axis centred at zero ppm."""
        return self.hz2ppm(self.SpectrometerFrequency, self.frequencyAxis, shift=False)

    @property
    def ppmAxisShift(self) -> np.ndarray:
        """Return the ppm axis referenced to the chemical shift position."""
        return self.hz2ppm(self.SpectrometerFrequency, self.frequencyAxis, shift=True,
                           shift_amount=self.ppmshift)

    @staticmethod
    def axis_indices(axis: np.ndarray, limits: tuple = None) -> slice:
        """Return indices spanning an inclusive range on the supplied axis.

        :param axis: Axis values to find indices on.
        :type axis: np.ndarray
        :param limits: Tuple of (lower, upper) limits to find indices spanning, defaults
             to None (return all indices).
        :type limits: tuple, list, np.ndarray [optional]
        :return: Indices spanning the range.
        :rtype: slice
        """
        axis = np.asarray(axis)
        if limits is None:
            return np.arange(0, axis.size)
        if not isinstance(limits, (tuple, list, np.ndarray)) or len(limits) != 2:
            raise ValueError("'limits' must be a 2-tuple")
        lo, hi = sorted(limits)
        # find nearest indices that satisfy the input range
        first = np.argmin(np.abs(axis - lo))
        last  = np.argmin(np.abs(axis - hi))
        if first > last:
            first, last = last, first
        return slice(first, last + 1)

    def timeIndices(self, limits: tuple) -> slice:
        """Return indices spanning a time range in seconds.

        :param limits: Tuple of (lower, upper) limits to find indices spanning, defaults
             to None (return all indices).
        :type limits: tuple, list, np.ndarray [optional]
        :return: timeAxis indices spanning the range.
        :rtype: slice
        """
        return self.axis_indices(self.timeAxis, limits)

    def frequencyIndices(self, limits: tuple) -> slice:
        """Return indices spanning a frequency range in Hz.

        :param limits: Tuple of (lower, upper) limits to find indices spanning, defaults
             to None (return all indices).
        :type limits: tuple, list, np.ndarray [optional]
        :return: frequencyAxis indices spanning the range.
        :rtype: slice
        """
        return self.axis_indices(self.frequencyAxis, limits)

    def ppmIndices(self, limits: tuple) -> slice:
        """Return indices spanning a ppm range on the zero-centred ppm axis.

        :param limits: Tuple of (lower, upper) limits to find indices spanning, defaults
             to None (return all indices).
        :type limits: tuple, list, np.ndarray [optional]
        :return: ppmAxis indices spanning the range.
        :rtype: slice
        """
        return self.axis_indices(self.ppmAxis, limits)

    def ppmShiftIndices(self, limits: tuple) -> slice:
        """Return indices spanning a ppm range on the referenced ppm axis.

        :param limits: Tuple of (lower, upper) limits to find indices spanning, defaults
             to None (return all indices).
        :type limits: tuple, list, np.ndarray [optional]
        :return: ppmAxisShift indices spanning the range.
        :rtype: slice
        """
        return self.axis_indices(self.ppmAxisShift, limits)

    # TODO add a default plotting method with correct axis limits, FID list (or spectra).
    # Returns a matplolib axes or fig object.
