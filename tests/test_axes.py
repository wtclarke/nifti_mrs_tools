'''Tests for the Axes class.

Author:  Vasilis Karlaftis      <vasilis.karlaftis@ndcn.ox.ac.uk>

Copyright (C) 2026 University of Oxford
'''

from pathlib import Path
import numpy as np

from nifti_mrs.axes import Axes
from nifti_mrs.nifti_mrs import NIFTI_MRS


testsPath = Path(__file__).parent
metab = testsPath / 'test_data' / 'metab_raw.nii.gz'


def test_axes_init():
    axes = Axes(
        ResonantNucleus='1H',
        SpectrometerFrequency=123.4,
        dwelltime=1/2000.0,
        SpecFreqChemShift=5.0,
        RxOffset=1.0,
        npoints=8)
    
    assert axes.ResonantNucleus == '1H'
    assert axes.SpectrometerFrequency == 123.4
    assert axes.dwelltime == 1/2000.0
    assert axes.SpecFreqChemShift == 5.0
    assert axes.RxOffset == 1.0
    assert axes.npoints == 8
    assert axes.SpectralWidth == 2000.0
    assert axes.timeAxis.shape == (8,)
    assert axes.frequencyAxis.shape == (8,)
    assert axes.ppmAxis.shape == (8,)
    assert axes.ppmAxisShift.shape == (8,)

    assert np.allclose(axes.timeAxis, np.linspace(1/2000.0, 8/2000.0, 8))
    assert np.allclose(axes.frequencyAxis, np.linspace(-2000.0/2, 2000.0/2, 8))
    assert np.allclose(axes.ppmAxis, axes.hz2ppm(1E6 * 123.4, axes.frequencyAxis, shift=False))
    assert np.allclose(axes.ppmAxisShift, axes.hz2ppm(1E6 * 123.4, axes.frequencyAxis, shift=True, shift_amount=5.0))


def test_axes_from_nifti_mrs():
    nmrs = NIFTI_MRS(metab, validate_on_creation=False)
    axes = Axes.from_nifti_mrs(nmrs)

    assert axes.ResonantNucleus == '1H'
    assert axes.SpectrometerFrequency == 297.219948
    assert axes.dwelltime == nmrs.dwelltime
    assert axes.SpecFreqChemShift == 4.65
    assert axes.RxOffset == 0
    assert axes.npoints == nmrs.shape[3]
    assert axes.SpectralWidth == 1/nmrs.dwelltime
    assert axes.timeAxis.shape == (nmrs.shape[3],)
    assert axes.frequencyAxis.shape == (nmrs.shape[3],)
    assert axes.ppmAxis.shape == (nmrs.shape[3],)
    assert axes.ppmAxisShift.shape == (nmrs.shape[3],)

    assert np.allclose(axes.timeAxis, np.linspace(nmrs.dwelltime, nmrs.shape[3] * nmrs.dwelltime, nmrs.shape[3]))
    assert np.allclose(axes.frequencyAxis, np.linspace(-1/nmrs.dwelltime/2, 1/nmrs.dwelltime/2, nmrs.shape[3]))
    assert np.allclose(axes.ppmAxis, axes.hz2ppm(1E6 * 297.219948, axes.frequencyAxis, shift=False))
    assert np.allclose(axes.ppmAxisShift, axes.hz2ppm(1E6 * 297.219948, axes.frequencyAxis, shift=True, shift_amount=4.65))


def test_axes_indices():
    axes = Axes(
        ResonantNucleus='1H',
        SpectrometerFrequency=123.4,
        dwelltime=1/2000.0,
        SpecFreqChemShift=5.0,
        RxOffset=1.0,
        npoints=8)

    assert np.array_equal(axes.timeIndices((0.001, 0.0025)), np.array([1, 2, 3, 4]))
    assert np.array_equal(axes.frequencyIndices((-200.0, 400.0)), np.array([3, 4, 5]))
    assert np.array_equal(axes.ppmIndices((1, 4)), np.array([4, 5]))
    assert np.array_equal(axes.ppmShiftIndices((6, 9)), np.array([4, 5]))
    ppmlim = (2, 8)
    ppmlim_shifted = tuple([i + axes.SpecFreqChemShift for i in ppmlim])
    assert np.array_equal(axes.ppmShiftIndices(ppmlim_shifted), axes.ppmIndices(ppmlim))

