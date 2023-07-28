'''Test the NIFTI-MRS object generation.

Copyright Will Clarke, University of Oxford, 2023'''

# Imports
from pathlib import Path

import numpy as np

from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs.hdr_ext import Hdr_Ext
from nifti_mrs.create_nmrs import gen_nifti_mrs, gen_nifti_mrs_hdr_ext


# Files
testsPath = Path(__file__).parent
data = {'metab': testsPath / 'test_data' / 'metab.nii.gz'}


def test_gen_new_nifti_mrs(tmp_path):
    data = np.zeros((1, 1, 1, 1024, 4), dtype=np.complex64)
    affine = np.eye(4)
    nmrs = gen_nifti_mrs(
        data,
        1 / 2000.0,
        128.0,
        nucleus='1H',
        affine=affine,
        dim_tags=['DIM_COIL', None, None])

    assert nmrs.shape == (1, 1, 1, 1024, 4)
    assert nmrs.dwelltime == 1 / 2000.0
    assert nmrs.nucleus == ['1H']
    assert nmrs.spectrometer_frequency == [128.0]
    assert nmrs.bandwidth == 2000.0
    assert nmrs.dim_tags == ['DIM_COIL', None, None]
    assert 'dim_5' in nmrs.hdr_ext

    assert nmrs.header.get_xyzt_units() == ('mm', 'sec')

    nmrs.save(tmp_path / 'out')
    assert (tmp_path / 'out.nii.gz').exists()


def test_gen_new_nifti_mrs_hdr_ext(tmp_path):
    data = np.zeros((1, 1, 1, 1024, 4), dtype=np.complex64)
    affine = np.eye(4)
    hdr_ext = Hdr_Ext(128.0, '1H', dimensions=5)
    hdr_ext.set_dim_info(0, 'DIM_COIL')
    nmrs = gen_nifti_mrs_hdr_ext(
        data,
        1 / 2000.0,
        hdr_ext,
        affine=affine)

    assert nmrs.shape == (1, 1, 1, 1024, 4)
    assert nmrs.dwelltime == 1 / 2000.0
    assert nmrs.nucleus == ['1H']
    assert nmrs.spectrometer_frequency == [128.0]
    assert nmrs.bandwidth == 2000.0
    assert nmrs.dim_tags == ['DIM_COIL', None, None]
    assert 'dim_5' in nmrs.hdr_ext

    nmrs.save(tmp_path / 'out')
    assert (tmp_path / 'out.nii.gz').exists()


def test_gen_new_nifti_mrs_conj(tmp_path):
    obj_in = NIFTI_MRS(data['metab'])

    nmrs = gen_nifti_mrs(obj_in[:],
                         obj_in.dwelltime,
                         obj_in.spectrometer_frequency[0],
                         nucleus='1H')

    assert np.allclose(nmrs[:], obj_in[:])

    nmrs = gen_nifti_mrs(obj_in[:],
                         obj_in.dwelltime,
                         obj_in.spectrometer_frequency[0],
                         nucleus='1H',
                         no_conj=True)

    assert np.allclose(nmrs[:], obj_in[:].conj())
