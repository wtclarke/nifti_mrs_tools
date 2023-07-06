"""Test the reorder tool for NIFTI-MRS

Author: Will Clarke <william.clarke@ndcn.ox.ac.uk>
Copyright (C) 2023 University of Oxford
"""

from pathlib import Path
import pytest

import numpy as np

from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs import tools as nmrs_tools
from nifti_mrs.utils import NIfTI_MRSIncompatible
from nifti_mrs.create_nmrs import gen_nifti_mrs

testsPath = Path(__file__).parent
test_data = testsPath / 'test_data' / 'metab_raw.nii.gz'


@pytest.fixture
def complex_hdr_data():
    nmrs = gen_nifti_mrs(
        np.ones((1, 1, 1, 512, 2, 2), dtype=complex),
        1 / 1000,
        123.2,
        dim_tags=['DIM_COIL', 'DIM_USER_0', None]
    )
    nmrs.set_dim_tag(
        'DIM_USER_0',
        'DIM_USER_0',
        info="EchoTime",
        header={"EchoTime": [0.001, 0.003]})

    return nmrs


def test_complex(complex_hdr_data):
    out = nmrs_tools.reorder(complex_hdr_data, ['DIM_USER_0', 'DIM_COIL'])
    assert out.hdr_ext['dim_5'] == 'DIM_USER_0'
    assert out.hdr_ext['dim_5_info'] == 'EchoTime'
    assert out.hdr_ext['dim_5_header'] == {"EchoTime": [0.001, 0.003]}
    assert out.hdr_ext['dim_6'] == 'DIM_COIL'

    out = nmrs_tools.reorder(complex_hdr_data, ['DIM_USER_0', 'DIM_COIL', 'DIM_EDIT'])
    assert out.ndim == 7
    assert out.shape == (1, 1, 1, 512, 2, 2, 1)

    out = nmrs_tools.reorder(complex_hdr_data, ['DIM_COIL', 'DIM_EDIT', 'DIM_USER_0'])
    assert out.ndim == 7
    assert out.shape == (1, 1, 1, 512, 2, 1, 2)
    assert out.hdr_ext['dim_7'] == 'DIM_USER_0'
    assert out.hdr_ext['dim_7_info'] == 'EchoTime'
    assert out.hdr_ext['dim_7_header'] == {"EchoTime": [0.001, 0.003]}
    assert out.hdr_ext['dim_6'] == 'DIM_EDIT'


def test_reorder():
    """Test the reorder functionality
    """
    nmrs = NIFTI_MRS(test_data)
    # Error testing
    # Miss existing tag
    with pytest.raises(NIfTI_MRSIncompatible) as exc_info:
        nmrs_tools.reorder(nmrs, ['DIM_COIL', 'DIM_EDIT'])

    assert exc_info.type is NIfTI_MRSIncompatible
    assert exc_info.value.args[0] == "The existing tag (DIM_DYN) does not appear"\
                                     " in the requested tag order (['DIM_COIL', 'DIM_EDIT'])."

    # Functionality testing
    # Swap order of dimensions
    out = nmrs_tools.reorder(nmrs, ['DIM_DYN', 'DIM_COIL'])
    assert out[:].shape == (1, 1, 1, 4096, 16, 4)
    assert np.allclose(np.swapaxes(nmrs[:], 4, 5), out[:])
    assert out.hdr_ext['dim_5'] == 'DIM_DYN'
    assert out.hdr_ext['dim_6'] == 'DIM_COIL'

    # Add an additional singleton at end (not reported in shape)
    out = nmrs_tools.reorder(nmrs, ['DIM_COIL', 'DIM_DYN', 'DIM_EDIT'])
    assert out[:].shape == (1, 1, 1, 4096, 4, 16)
    assert out.shape == (1, 1, 1, 4096, 4, 16, 1)
    assert out.hdr_ext['dim_5'] == 'DIM_COIL'
    assert out.hdr_ext['dim_6'] == 'DIM_DYN'
    assert out.hdr_ext['dim_7'] == 'DIM_EDIT'

    # Add an additional singleton at 5
    out = nmrs_tools.reorder(nmrs, ['DIM_EDIT', 'DIM_COIL', 'DIM_DYN'])
    assert out[:].shape == (1, 1, 1, 4096, 1, 4, 16)
    assert out.shape == (1, 1, 1, 4096, 1, 4, 16)
    assert out.hdr_ext['dim_5'] == 'DIM_EDIT'
    assert out.hdr_ext['dim_6'] == 'DIM_COIL'
    assert out.hdr_ext['dim_7'] == 'DIM_DYN'
