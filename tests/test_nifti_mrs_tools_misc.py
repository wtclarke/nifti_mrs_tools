from pathlib import Path

import numpy as np

from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs import tools as nmrs_tools


testsPath = Path(__file__).parent
test_data = testsPath / 'test_data' / 'metab_raw.nii.gz'


def test_conjugate():
    # Data is (1, 1, 1, 4096, 32, 64) ['DIM_COIL', 'DIM_DYN', None]
    nmrs = NIFTI_MRS(test_data)

    conjugated = nmrs_tools.conjugate(nmrs)

    assert np.allclose(conjugated[:], np.conjugate(nmrs[:]))
