from pathlib import Path

import pytest

from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs import tools as nmrs_tools

testsPath = Path('/Users/wclarke/Documents/Python/fsl_mrs/fsl_mrs/tests')
# testsPath = Path(__file__).parent
test_data = testsPath / 'testdata' / 'fsl_mrs_preproc' / 'metab_raw.nii.gz'


def test_reshape():
    # Data is (1, 1, 1, 4096, 32, 64) ['DIM_COIL', 'DIM_DYN', None]
    nmrs = NIFTI_MRS(test_data)

    new_shape = (16, 2, 64)
    with pytest.raises(TypeError) as exc_info:
        reshaped = nmrs_tools.reshape(nmrs, new_shape, d6='DIM_USER_0')

    assert exc_info.type is TypeError
    assert exc_info.value.args[0] == 'An appropriate d7 dim tag must be given as ndim = 7.'

    reshaped = nmrs_tools.reshape(nmrs, new_shape, d6='DIM_USER_0', d7='DIM_DYN')

    assert reshaped.shape == (1, 1, 1, 4096, 16, 2, 64)
    assert reshaped.dim_tags == ['DIM_COIL', 'DIM_USER_0', 'DIM_DYN']

    new_shape = (16, -1, 64)
    reshaped = nmrs_tools.reshape(nmrs, new_shape, d7='DIM_USER_0')

    assert reshaped.shape == (1, 1, 1, 4096, 16, 2, 64)
    assert reshaped.dim_tags == ['DIM_COIL', 'DIM_DYN', 'DIM_USER_0']
