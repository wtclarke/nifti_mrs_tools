"""Axis helper class for NIfTI-MRS objects.

Author:  Vasilis Karlaftis      <vasilis.karlaftis@ndcn.ox.ac.uk>

Copyright (C) 2026 University of Oxford
"""

import numpy as np


class Axes():
    """Generate spectral axes from NIfTI-MRS acquisition metadata."""

    def __init__(
            self,
            ResonantNucleus,
            SpectrometerFrequency,
            dwelltime,
            SpecFreqChemShift=None,
            RxOffset=0.0,
            npoints=None):
        """Create an axes helper object.

        :param ResonantNucleus: Resonant nucleus string (e.g. ``1H``).
        :type ResonantNucleus: str
        :param SpectrometerFrequency: Spectrometer frequency in MHz.
        :type SpectrometerFrequency: float
        :param dwelltime: Spectral dwell time in seconds.
        :type dwelltime: float
        :param SpecFreqChemShift: Chemical shift position in ppm.
            If not provided defaults are used. Current defaults follow the
            FSL-MRS convention of 4.65 ppm for proton/deuterium and 0.0 ppm
            otherwise.
        :type SpecFreqChemShift: float, optional
        :param RxOffset: Receiver offset in Hz, defaults to 0.0.
        :type RxOffset: float, optional
        :param npoints: Number of points along the spectral dimension.
        :type npoints: int, optional
        """
        self._ResonantNucleus = str(ResonantNucleus)
        self._SpectrometerFrequency = float(SpectrometerFrequency)
        self._dwelltime = float(dwelltime)
        self._RxOffset = float(RxOffset)
        self._npoints = None if npoints is None else int(npoints)

        if self._dwelltime <= 0:
            raise ValueError('dwelltime must be positive.')
        if self._SpectrometerFrequency <= 0:
            raise ValueError('SpectrometerFrequency must be positive.')
        if self._npoints is not None and self._npoints <= 0:
            raise ValueError('npoints must be positive.')

        if SpecFreqChemShift is None:
            self._SpecFreqChemShift = self.default_shift(self._ResonantNucleus)
        else:
            self._SpecFreqChemShift = float(SpecFreqChemShift)

    @classmethod
    def from_nifti_mrs(cls, nifti_mrs_obj, SpecFreqChemShift=None, RxOffset=0.0):
        """Initialise from a :class:`nifti_mrs.nifti_mrs.NIFTI_MRS` object."""
        return cls(
            ResonantNucleus=nifti_mrs_obj.nucleus[0],
            SpectrometerFrequency=nifti_mrs_obj.spectrometer_frequency[0],
            dwelltime=nifti_mrs_obj.dwelltime,
            SpecFreqChemShift=SpecFreqChemShift,
            RxOffset=RxOffset,
            npoints=nifti_mrs_obj.shape[3])

    @staticmethod
    def default_shift(ResonantNucleus):
        """Return the default chemical shift position for a nucleus."""
        from mrs_tools.constants import PPM_SHIFT
        return PPM_SHIFT.get(str(ResonantNucleus), 0.0)

    @property
    def ResonantNucleus(self):
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
        """Chemical shift position in ppm."""
        return self._SpecFreqChemShift

    @property
    def RxOffset(self):
        """Receiver offset in Hz."""
        return self._RxOffset

    @property
    def npoints(self):
        """Number of points in the spectral dimension."""
        return self._npoints

    @property
    def SpectralWidth(self):
        """Spectral width in Hz."""
        return 1.0 / self.dwelltime

    def _resolve_npoints(self, npoints=None):
        if npoints is None:
            npoints = self.npoints
        if npoints is None:
            raise ValueError('npoints must be provided or set on initialisation.')
        npoints = int(npoints)
        if npoints <= 0:
            raise ValueError('npoints must be positive.')
        return npoints

    def time_axis_array(self, npoints=None):
        """Return the time axis in seconds."""
        npts = self._resolve_npoints(npoints)
        return np.arange(npts) * self.dwelltime

    def frequency_axis_array(self, npoints=None):
        """Return the frequency axis in Hz including receiver offset."""
        npts = self._resolve_npoints(npoints)
        return np.fft.fftshift(np.fft.fftfreq(npts, d=self.dwelltime)) + self.RxOffset

    def ppm_axis_array(self, npoints=None):
        """Return the ppm axis referenced to the chemical shift position."""
        return self.SpecFreqChemShift - (self.frequency_axis_array(npoints) / self.SpectrometerFrequency)

    def ppm_axis_shiftless_array(self, npoints=None):
        """Return the ppm axis centred at zero ppm."""
        return -(self.frequency_axis_array(npoints) / self.SpectrometerFrequency)

    @property
    def time_axis(self):
        return self.time_axis_array()

    @property
    def frequency_axis(self):
        return self.frequency_axis_array()

    @property
    def ppm_axis(self):
        return self.ppm_axis_array()

    @property
    def ppm_axis_shiftless(self):
        return self.ppm_axis_shiftless_array()

    def axis_indices(self, axis, lower, upper):
        """Return indices spanning an inclusive range on the supplied axis."""
        axis = np.asarray(axis)
        lo, hi = sorted((lower, upper))
        return np.where((axis >= lo) & (axis <= hi))[0]

    def time_indices(self, lower, upper, npoints=None):
        """Return indices spanning a time range in seconds."""
        return self.axis_indices(self.time_axis_array(npoints), lower, upper)

    def frequency_indices(self, lower, upper, npoints=None):
        """Return indices spanning a frequency range in Hz."""
        return self.axis_indices(self.frequency_axis_array(npoints), lower, upper)

    def ppm_indices(self, lower, upper, npoints=None):
        """Return indices spanning a ppm range on the referenced ppm axis."""
        return self.axis_indices(self.ppm_axis_array(npoints), lower, upper)

    def ppm_shiftless_indices(self, lower, upper, npoints=None):
        """Return indices spanning a ppm range on the zero-centred ppm axis."""
        return self.axis_indices(self.ppm_axis_shiftless_array(npoints), lower, upper)
