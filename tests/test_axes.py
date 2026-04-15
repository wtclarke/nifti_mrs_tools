from pathlib import Path

import numpy as np
import pytest

from nifti_mrs.axes import Axes
from nifti_mrs.nifti_mrs import NIFTI_MRS


testsPath = Path(__file__).parent
data = {'unprocessed': testsPath / 'test_data' / 'metab_raw.nii.gz'}


def test_axes_from_init():
    axes = Axes(
        ResonantNucleus='1H',
        SpectrometerFrequency=123.4,
        dwelltime=1/2000.0,
        SpecFreqChemShift=10.0,
        npoints=8)

    assert np.allclose(axes.timeAxis, np.linspace(1/2000.0, 8/2000.0, 8))
    assert np.allclose(axes.frequencyAxis, np.linspace(-2000.0/2, 2000.0/2, 8))
    assert np.allclose(axes.ppmAxis, axes.hz2ppm(1E6 * 123.4, axes.frequencyAxis, shift=False))
    assert np.allclose(axes.ppmAxisShift, axes.hz2ppm(1E6 * 123.4, axes.frequencyAxis, shift=True, shift_amount=10.0))


def test_axes_with_rx_offset_and_indices():
    axes = Axes(
        ResonantNucleus='1H',
        SpectrometerFrequency=297.219948,
        dwelltime=1/2000.0,
        RxOffset=100.0,
        npoints=8)

    assert np.allclose(axes.frequencyAxis, np.linspace(-2000.0/2, 2000.0/2, 8))
    assert np.array_equal(axes.timeIndices(0.001, 0.0025), np.array([1, 2, 3, 4]))
    assert np.array_equal(axes.frequencyIndices(-200.0, 400.0), np.array([3, 4]))


def test_axes_from_nifti_mrs():
    nmrs = NIFTI_MRS(data['unprocessed'])
    axes = Axes.from_nifti_mrs(nmrs)

    assert axes.ResonantNucleus == '1H'
    assert axes.SpectrometerFrequency == pytest.approx(297.219948)
    assert axes.dwelltime == pytest.approx(nmrs.dwelltime)
    assert axes.npoints == nmrs.shape[3]
    assert axes.SpecFreqChemShift == pytest.approx(4.65)
    assert axes.timeAxis.shape == (nmrs.shape[3],)
    assert axes.frequencyAxis.shape == (nmrs.shape[3],)
    assert axes.ppmAxis.shape == (nmrs.shape[3],)
    assert axes.ppmAxisShift.shape == (nmrs.shape[3],)
