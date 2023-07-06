"""Test the split and merge tools for NIFTI-MRS

Author: Will Clarke <william.clarke@ndcn.ox.ac.uk>
Copyright (C) 2021 University of Oxford
"""

from pathlib import Path
import pytest

import numpy as np


from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs.hdr_ext import Hdr_Ext
from nifti_mrs import tools as nmrs_tools
from nifti_mrs.create_nmrs import gen_nifti_mrs
from nifti_mrs.utils import NIfTI_MRSIncompatible

testsPath = Path(__file__).parent
test_data_split = testsPath / 'test_data' / 'metab_raw.nii.gz'
test_data_merge_1 = testsPath / 'test_data' / 'wref_raw.nii.gz'
test_data_merge_2 = testsPath / 'test_data' / 'quant_raw.nii.gz'
test_data_other = testsPath / 'test_data' / 'ecc.nii.gz'


def test_split_dim_header():
    """Test the ability to split the dim_N_header fields"""
    hdr_in = Hdr_Ext.from_header_ext(
        {'SpectrometerFrequency': [100.0, ],
         'ResonantNucleus': ['1H', ],
         'dim_5': 'DIM_DYN',
         'dim_5_info': 'averages',
         'dim_5_header': {'p1': [1, 2, 3, 4],
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_6': 'DIM_EDIT',
         'dim_6_info': 'edit',
         'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_7': 'DIM_USER_0',
         'dim_7_info': 'other',
         'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                          'p2': [0.1, 0.2, 0.3, 0.4]}})

    # Headers occuring as a list.
    hdr1, hdr2 = nmrs_tools.split_merge._split_dim_header(hdr_in, 5, 4, 1)
    assert hdr1 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [1, 2],
                                     'p2': [0.1, 0.2]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2, 0.3, 0.4]}}
    assert hdr2 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [3, 4],
                                     'p2': [0.3, 0.4]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2, 0.3, 0.4]}}

    hdr1, hdr2 = nmrs_tools.split_merge._split_dim_header(hdr_in, 5, 4, [1, 3])
    assert hdr1 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [1, 3],
                                     'p2': [0.1, 0.3]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2, 0.3, 0.4]}}
    assert hdr2 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [2, 4],
                                     'p2': [0.2, 0.4]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2, 0.3, 0.4]}}

    # Headers as a dict
    hdr1, hdr2 = nmrs_tools.split_merge._split_dim_header(hdr_in, 6, 4, 1)
    assert hdr1 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [1, 2, 3, 4],
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                     'p2': [0.1, 0.2]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2, 0.3, 0.4]}}
    assert hdr2 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [1, 2, 3, 4],
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': {'start': 3, 'increment': 1},
                                     'p2': [0.3, 0.4]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2, 0.3, 0.4]}}

    hdr1, hdr2 = nmrs_tools.split_merge._split_dim_header(hdr_in, 6, 4, [1, ])
    assert hdr1 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [1, 2, 3, 4],
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': [1, 3, 4],
                                     'p2': [0.1, 0.3, 0.4]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2, 0.3, 0.4]}}
    assert hdr2 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [1, 2, 3, 4],
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': [2, ],
                                     'p2': [0.2, ]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2, 0.3, 0.4]}}

    # User defined structures
    hdr1, hdr2 = nmrs_tools.split_merge._split_dim_header(hdr_in, 7, 4, 1)
    assert hdr1 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [1, 2, 3, 4],
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.1, 0.2]}}
    assert hdr2 == {'SpectrometerFrequency': [100.0, ],
                    'ResonantNucleus': ['1H', ],
                    'dim_5': 'DIM_DYN',
                    'dim_5_info': 'averages',
                    'dim_5_header': {'p1': [1, 2, 3, 4],
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_6': 'DIM_EDIT',
                    'dim_6_info': 'edit',
                    'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                     'p2': [0.1, 0.2, 0.3, 0.4]},
                    'dim_7': 'DIM_USER_0',
                    'dim_7_info': 'other',
                    'dim_7_header': {'p1': {'Value': {'start': 3, 'increment': 1}, 'Description': 'user'},
                                     'p2': [0.3, 0.4]}}


def test_merge_dim_header():
    """Test the ability to merge the dim_N_header fields"""
    hdr_in_1 = Hdr_Ext.from_header_ext(
        {'SpectrometerFrequency': [100.0, ],
         'ResonantNucleus': ['1H', ],
         'dim_5': 'DIM_DYN',
         'dim_5_info': 'averages',
         'dim_5_header': {'p1': [1, 2, 3, 4],
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_6': 'DIM_EDIT',
         'dim_6_info': 'edit',
         'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_7': 'DIM_USER_0',
         'dim_7_info': 'other',
         'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                          'p2': [0.1, 0.2, 0.3, 0.4]}})
    hdr_in_2 = Hdr_Ext.from_header_ext(
        {'SpectrometerFrequency': [100.0, ],
         'ResonantNucleus': ['1H', ],
         'dim_5': 'DIM_DYN',
         'dim_5_info': 'averages',
         'dim_5_header': {'p1': [1, 2, 3],
                          'p2': [0.1, 0.2, 0.3]},
         'dim_6': 'DIM_EDIT',
         'dim_6_info': 'edit',
         'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_7': 'DIM_USER_0',
         'dim_7_info': 'other',
         'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                          'p2': [0.1, 0.2, 0.3, 0.4]}})

    hdr_out = nmrs_tools.split_merge._merge_dim_header(hdr_in_1, hdr_in_2, 5, 4, 3)
    assert hdr_out == {'SpectrometerFrequency': [100.0, ],
                       'ResonantNucleus': ['1H', ],
                       'dim_5': 'DIM_DYN',
                       'dim_5_info': 'averages',
                       'dim_5_header': {'p1': [1, 2, 3, 4, 1, 2, 3],
                                        'p2': [0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3]},
                       'dim_6': 'DIM_EDIT',
                       'dim_6_info': 'edit',
                       'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                        'p2': [0.1, 0.2, 0.3, 0.4]},
                       'dim_7': 'DIM_USER_0',
                       'dim_7_info': 'other',
                       'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                        'p2': [0.1, 0.2, 0.3, 0.4]}}

    hdr_in_2 = Hdr_Ext.from_header_ext(
        {'SpectrometerFrequency': [100.0, ],
         'ResonantNucleus': ['1H', ],
         'dim_5': 'DIM_DYN',
         'dim_5_info': 'averages',
         'dim_5_header': {'p1': [1, 2, 3, 4],
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_6': 'DIM_EDIT',
         'dim_6_info': 'edit',
         'dim_6_header': {'p1': {'start': 5, 'increment': 1},
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_7': 'DIM_USER_0',
         'dim_7_info': 'other',
         'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                          'p2': [0.1, 0.2, 0.3, 0.4]}})
    hdr_out = nmrs_tools.split_merge._merge_dim_header(hdr_in_1, hdr_in_2, 6, 4, 4)
    assert hdr_out == {'SpectrometerFrequency': [100.0, ],
                       'ResonantNucleus': ['1H', ],
                       'dim_5': 'DIM_DYN',
                       'dim_5_info': 'averages',
                       'dim_5_header': {'p1': [1, 2, 3, 4],
                                        'p2': [0.1, 0.2, 0.3, 0.4]},
                       'dim_6': 'DIM_EDIT',
                       'dim_6_info': 'edit',
                       'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                        'p2': [0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 0.4]},
                       'dim_7': 'DIM_USER_0',
                       'dim_7_info': 'other',
                       'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                        'p2': [0.1, 0.2, 0.3, 0.4]}}

    hdr_out = nmrs_tools.split_merge._merge_dim_header(hdr_in_2, hdr_in_1, 6, 4, 4)
    assert hdr_out == {'SpectrometerFrequency': [100.0, ],
                       'ResonantNucleus': ['1H', ],
                       'dim_5': 'DIM_DYN',
                       'dim_5_info': 'averages',
                       'dim_5_header': {'p1': [1, 2, 3, 4],
                                        'p2': [0.1, 0.2, 0.3, 0.4]},
                       'dim_6': 'DIM_EDIT',
                       'dim_6_info': 'edit',
                       'dim_6_header': {'p1': [5, 6, 7, 8, 1, 2, 3, 4],
                                        'p2': [0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 0.4]},
                       'dim_7': 'DIM_USER_0',
                       'dim_7_info': 'other',
                       'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                        'p2': [0.1, 0.2, 0.3, 0.4]}}

    hdr_in_2 = Hdr_Ext.from_header_ext(
        {'SpectrometerFrequency': [100.0, ],
         'ResonantNucleus': ['1H', ],
         'dim_5': 'DIM_DYN',
         'dim_5_info': 'averages',
         'dim_5_header': {'p1': [1, 2, 3, 4],
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_6': 'DIM_EDIT',
         'dim_6_info': 'edit',
         'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                          'p2': [0.1, 0.2, 0.3, 0.4]},
         'dim_7': 'DIM_USER_0',
         'dim_7_info': 'other',
         'dim_7_header': {'p1': {'Value': {'start': 5, 'increment': 1}, 'Description': 'user'},
                          'p2': [0.1, 0.2, 0.3, 0.4]}})
    hdr_out = nmrs_tools.split_merge._merge_dim_header(hdr_in_1, hdr_in_2, 7, 4, 4)
    assert hdr_out == {'SpectrometerFrequency': [100.0, ],
                       'ResonantNucleus': ['1H', ],
                       'dim_5': 'DIM_DYN',
                       'dim_5_info': 'averages',
                       'dim_5_header': {'p1': [1, 2, 3, 4],
                                        'p2': [0.1, 0.2, 0.3, 0.4]},
                       'dim_6': 'DIM_EDIT',
                       'dim_6_info': 'edit',
                       'dim_6_header': {'p1': {'start': 1, 'increment': 1},
                                        'p2': [0.1, 0.2, 0.3, 0.4]},
                       'dim_7': 'DIM_USER_0',
                       'dim_7_info': 'other',
                       'dim_7_header': {'p1': {'Value': {'start': 1, 'increment': 1}, 'Description': 'user'},
                                        'p2': [0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 0.4]}}

    with pytest.raises(NIfTI_MRSIncompatible) as exc_info:
        hdr_out = nmrs_tools.split_merge._merge_dim_header(hdr_in_1, hdr_in_2, 5, 4, 4)
    assert exc_info.type is NIfTI_MRSIncompatible
    assert exc_info.value.args[0] == "Both files must have matching dimension headers apart from the one being merged."\
                                     " dim_7_header does not match."


def test_split():
    """Test the split functionality
    """
    nmrs = NIFTI_MRS(test_data_split)

    # Error testing
    # Wrong dim tag
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.split(nmrs, 'DIM_EDIT', 1)

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "DIM_EDIT not found as dimension tag."\
                                     " This data contains ['DIM_COIL', 'DIM_DYN', None]."

    # Wrong dim index (no dim in this data)
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.split(nmrs, 6, 1)

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "Dimension must be one of 4, 5, or 6 (or DIM_TAG string)."\
                                     " This data has 6 dimensions,"\
                                     " i.e. a maximum dimension value of 5."

    # Wrong dim index (too low)
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.split(nmrs, 3, 1)

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "Dimension must be one of 4, 5, or 6 (or DIM_TAG string)."\
                                     " This data has 6 dimensions,"\
                                     " i.e. a maximum dimension value of 5."

    # Wrong dim index type
    with pytest.raises(TypeError) as exc_info:
        nmrs_tools.split(nmrs, [3, ], 1)

    assert exc_info.type is TypeError
    assert exc_info.value.args[0] == "Dimension must be an int (4, 5, or 6) or string (DIM_TAG string)."

    # Single index - out of range low
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.split(nmrs, 'DIM_DYN', -1)

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "index_or_indicies must be between 0 and N-1,"\
                                     " where N is the size of the specified dimension (16)."

    # Single index - out of range high
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.split(nmrs, 'DIM_DYN', 64)

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "index_or_indicies must be between 0 and N-1,"\
                                     " where N is the size of the specified dimension (16)."

    # List of indicies - out of range low
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.split(nmrs, 'DIM_DYN', [-1, 0, 1])

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "index_or_indicies must have elements between 0 and N,"\
                                     " where N is the size of the specified dimension (16)."

    # List of indicies - out of range high
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.split(nmrs, 'DIM_DYN', [0, 65])

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "index_or_indicies must have elements between 0 and N,"\
                                     " where N is the size of the specified dimension (16)."

    # List of indicies - wrong type
    with pytest.raises(TypeError) as exc_info:
        nmrs_tools.split(nmrs, 'DIM_DYN', '1')

    assert exc_info.type is TypeError
    assert exc_info.value.args[0] == "index_or_indicies must be single index or list of indicies"

    # Functionality testing

    out_1, out_2 = nmrs_tools.split(nmrs, 'DIM_DYN', 7)
    assert out_1[:].shape == (1, 1, 1, 4096, 4, 8)
    assert out_2[:].shape == (1, 1, 1, 4096, 4, 8)
    assert np.allclose(out_1[:], nmrs[:, :, :, :, :, 0:8])
    assert np.allclose(out_2[:], nmrs[:, :, :, :, :, 8:])
    assert out_1.hdr_ext == nmrs.hdr_ext
    assert out_1.hdr_ext == nmrs.hdr_ext
    assert np.allclose(out_1.getAffine('voxel', 'world'), nmrs.getAffine('voxel', 'world'))
    assert np.allclose(out_2.getAffine('voxel', 'world'), nmrs.getAffine('voxel', 'world'))

    out_1, out_2 = nmrs_tools.split(nmrs, 'DIM_DYN', [0, 4, 15])
    assert out_1[:].shape == (1, 1, 1, 4096, 4, 13)
    assert out_2[:].shape == (1, 1, 1, 4096, 4, 3)
    test_list = np.arange(0, 16)
    test_list = np.delete(test_list, [0, 4, 15])
    assert np.allclose(out_1[:], nmrs[:][:, :, :, :, :, test_list])
    assert np.allclose(out_2[:], nmrs[:][:, :, :, :, :, [0, 4, 15]])

    # Split some synthetic data with header information
    nhdr_1 = gen_nifti_mrs(
        np.ones((1, 1, 1, 10, 4), dtype=complex),
        1 / 1000,
        100.0,
        '1H',
        dim_tags=['DIM_DYN', None, None])

    nhdr_1.set_dim_tag(
        'DIM_DYN',
        'DIM_DYN',
        header={'RepetitionTime': [1, 2, 3, 4]})

    out_1, out_2 = nmrs_tools.split(nhdr_1, 'DIM_DYN', 1)
    assert out_1.shape == (1, 1, 1, 10, 2)
    assert out_1.hdr_ext['dim_5'] == 'DIM_DYN'
    assert out_1.hdr_ext['dim_5_header'] == {'RepetitionTime': [1, 2]}
    assert out_2.hdr_ext['dim_5_header'] == {'RepetitionTime': [3, 4]}


def test_merge():
    """Test the merge functionality
    """
    nmrs_1 = NIFTI_MRS(test_data_merge_1)
    nmrs_2 = NIFTI_MRS(test_data_merge_2)

    nmrs_bad_shape, _ = nmrs_tools.split(nmrs_2, 'DIM_COIL', 1)
    nmrs_no_tag = NIFTI_MRS(test_data_other)

    # Error testing
    # Wrong dim tag
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.merge((nmrs_1, nmrs_2), 'DIM_EDIT')

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "DIM_EDIT not found as dimension tag."\
                                     " This data contains ['DIM_COIL', 'DIM_DYN', None]."

    # Wrong dim index (no dim in this data)
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.merge((nmrs_1, nmrs_2), 6)

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "Dimension must be one of 4, 5, or 6 (or DIM_TAG string)."\
                                     " This data has 6 dimensions,"\
                                     " i.e. a maximum dimension value of 5."

    # Wrong dim index (too low)
    with pytest.raises(ValueError) as exc_info:
        nmrs_tools.merge((nmrs_1, nmrs_2), 3)

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "Dimension must be one of 4, 5, or 6 (or DIM_TAG string)."\
                                     " This data has 6 dimensions,"\
                                     " i.e. a maximum dimension value of 5."

    # Wrong dim index type
    with pytest.raises(TypeError) as exc_info:
        nmrs_tools.merge((nmrs_1, nmrs_2), [3, ])

    assert exc_info.type is TypeError
    assert exc_info.value.args[0] == "Dimension must be an int (4, 5, or 6) or string (DIM_TAG string)."

    # Incompatible shapes
    with pytest.raises(NIfTI_MRSIncompatible) as exc_info:
        nmrs_tools.merge((nmrs_1, nmrs_bad_shape), 'DIM_DYN')

    assert exc_info.type is NIfTI_MRSIncompatible
    assert exc_info.value.args[0] == "The shape of all concatenated objects must match. "\
                                     "The shape ((1, 1, 1, 4096, 2, 2)) of the 1 object does "\
                                     "not match that of the first ((1, 1, 1, 4096, 4, 2))."

    # Incompatible tags
    with pytest.raises(NIfTI_MRSIncompatible) as exc_info:
        nmrs_tools.merge((nmrs_1, nmrs_no_tag), 'DIM_DYN')

    assert exc_info.type is NIfTI_MRSIncompatible
    assert exc_info.value.args[0] == "The tags of all concatenated objects must match. "\
                                     "The tags (['DIM_COIL', None, None]) of the 1 object does "\
                                     "not match that of the first (['DIM_COIL', 'DIM_DYN', None])."

    # Functionality testing
    out = nmrs_tools.merge((nmrs_1, nmrs_2), 'DIM_DYN')
    assert out[:].shape == (1, 1, 1, 4096, 4, 4)
    assert np.allclose(out[:][:, :, :, :, :, 0:2], nmrs_1[:])
    assert np.allclose(out[:][:, :, :, :, :, 2:], nmrs_2[:])
    assert out.hdr_ext == nmrs_1.hdr_ext
    assert np.allclose(out.getAffine('voxel', 'world'), nmrs_1.getAffine('voxel', 'world'))

    # Merge along squeezed singleton
    nmrs_1_e = nmrs_tools.reorder(nmrs_1, ['DIM_COIL', 'DIM_DYN', 'DIM_EDIT'])
    nmrs_2_e = nmrs_tools.reorder(nmrs_2, ['DIM_COIL', 'DIM_DYN', 'DIM_EDIT'])
    out = nmrs_tools.merge((nmrs_1_e, nmrs_2_e), 'DIM_EDIT')
    assert out[:].shape == (1, 1, 1, 4096, 4, 2, 2)
    assert out.hdr_ext['dim_7'] == 'DIM_EDIT'

    # Merge some synthetic data with header information
    nhdr_1 = gen_nifti_mrs(
        np.ones((1, 1, 1, 10, 4), dtype=complex),
        1 / 1000,
        100.0,
        '1H',
        dim_tags=['DIM_DYN', None, None])
    nhdr_2 = nhdr_1.copy()

    nhdr_1.set_dim_tag('DIM_DYN', 'DIM_DYN', header={'RepetitionTime': [1, 2, 3, 4]})
    nhdr_2.set_dim_tag('DIM_DYN', 'DIM_DYN', header={'RepetitionTime': [1, 2, 3, 4]})

    out = nmrs_tools.merge((nhdr_1, nhdr_2, nhdr_2), 'DIM_DYN')
    assert out[:].shape == (1, 1, 1, 10, 12)
    assert out.hdr_ext['dim_5'] == 'DIM_DYN'
    assert out.hdr_ext['dim_5_header'] == {'RepetitionTime': [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4]}

    nhdr_1.set_dim_tag('DIM_DYN', 'DIM_DYN', header={'RepetitionTime': {'start': 1, 'increment': 1}})
    nhdr_2.set_dim_tag('DIM_DYN', 'DIM_DYN', header={'RepetitionTime': [5, 6, 7, 8]})

    out = nmrs_tools.merge((nhdr_1, nhdr_2), 'DIM_DYN')
    assert out[:].shape == (1, 1, 1, 10, 8)
    assert out.hdr_ext['dim_5'] == 'DIM_DYN'
    assert out.hdr_ext['dim_5_header'] == {'RepetitionTime': {'start': 1, 'increment': 1}}

    # Merge along squeezed singleton with header
    nhdr_1 = gen_nifti_mrs(
        np.ones((1, 1, 1, 10, 4), dtype=complex),
        1 / 1000,
        100.0,
        '1H',
        dim_tags=['DIM_DYN', None, None])
    nhdr_2 = nhdr_1.copy()
    nhdr_1_e = nmrs_tools.reorder(nhdr_1, ['DIM_DYN', 'DIM_EDIT', None])
    nhdr_2_e = nmrs_tools.reorder(nhdr_2, ['DIM_DYN', 'DIM_EDIT', None])

    nhdr_1_e.set_dim_tag('DIM_DYN', 'DIM_DYN', header={'RepetitionTime': {'start': 1, 'increment': 1}})
    nhdr_2_e.set_dim_tag('DIM_DYN', 'DIM_DYN', header={'RepetitionTime': {'start': 1, 'increment': 1}})
    nhdr_1_e.set_dim_tag('DIM_EDIT', 'DIM_EDIT', header={'OtherTime': {'Value': [0.1, ], 'Description': 'N/A'}})
    nhdr_2_e.set_dim_tag('DIM_EDIT', 'DIM_EDIT', header={'OtherTime': {'Value': [0.2, ], 'Description': 'N/A'}})

    out = nmrs_tools.merge((nhdr_1_e, nhdr_2_e), 'DIM_EDIT')
    assert out[:].shape == (1, 1, 1, 10, 4, 2)
    assert out.hdr_ext['dim_6'] == 'DIM_EDIT'
    assert out.hdr_ext['dim_6_header'] == {'OtherTime': {'Description': 'N/A', 'Value': [0.1, 0.2]}}
