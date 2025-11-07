from pathlib import Path

import numpy as np
import pytest

from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs import tools as nmrs_tools
from nifti_mrs.create_nmrs import gen_nifti_mrs

testsPath = Path(__file__).parent
test_data = testsPath / 'test_data' / 'metab_raw.nii.gz'


def test_reshape():
    # Data is (1, 1, 1, 4096, 5, 16) ['DIM_COIL', 'DIM_DYN', None]
    nmrs = NIFTI_MRS(test_data)

    new_shape = (2, 2, 16)
    with pytest.raises(TypeError) as exc_info:
        reshaped = nmrs_tools.reshape(nmrs, new_shape, d6='DIM_USER_0')

    assert exc_info.type is TypeError
    assert exc_info.value.args[0] == 'An appropriate d7 dim tag must be given as ndim = 7.'

    reshaped = nmrs_tools.reshape(nmrs, new_shape, d6='DIM_USER_0', d7='DIM_DYN')

    assert reshaped.shape == (1, 1, 1, 4096, 2, 2, 16)
    assert reshaped.dim_tags == ['DIM_COIL', 'DIM_USER_0', 'DIM_DYN']

    new_shape = (2, -1, 16)
    reshaped = nmrs_tools.reshape(nmrs, new_shape, d7='DIM_USER_0')

    assert reshaped.shape == (1, 1, 1, 4096, 2, 2, 16)
    assert reshaped.dim_tags == ['DIM_COIL', 'DIM_DYN', 'DIM_USER_0']


def test_remove_dim():
    """Test the wrapper for copy(remove_dim)"""
    example_singleton = gen_nifti_mrs(
        np.zeros((1, 1, 1, 256, 4, 1), complex),
        1 / 1000,
        123.0,
        dim_tags=['DIM_COIL', 'DIM_DYN']
    )
    assert example_singleton.shape == (1, 1, 1, 256, 4, 1)

    rm_dim_dyn = nmrs_tools.remove_dim(example_singleton, 'DIM_DYN')
    assert rm_dim_dyn.shape == (1, 1, 1, 256, 4)
    assert rm_dim_dyn.dim_tags == ['DIM_COIL', None, None]

    rm_dim_coil = nmrs_tools.remove_dim(example_singleton, 'DIM_COIL')
    assert rm_dim_coil.shape == (1, 1, 1, 256, 1)
    assert rm_dim_coil.dim_tags == ['DIM_DYN', None, None]
