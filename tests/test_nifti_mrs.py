'''Test the NIFTI-MRS class implementation

Copyright Will Clarke, University of Oxford, 2023'''

# Imports
from pathlib import Path
from copy import deepcopy

import pytest
import numpy as np

from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs.validator import headerExtensionError

# Files
testsPath = Path('/Users/wclarke/Documents/Python/fsl_mrs/fsl_mrs/tests')
# testsPath = Path(__file__).parent
data = {'metab': testsPath / 'testdata/fsl_mrs/metab.nii.gz',
        'unprocessed': testsPath / 'testdata/fsl_mrs_preproc/metab_raw.nii.gz',
        'water': testsPath / 'testdata/fsl_mrs/wref.nii.gz',
        'basis': testsPath / 'testdata/fsl_mrs/steam_basis'}


def test_nifti_mrs():
    obj = NIFTI_MRS(data['unprocessed'])

    assert obj.nifti_mrs_version == '0.2'
    assert obj.shape == (1, 1, 1, 4096, 32, 64)
    assert obj.ndim == 6
    assert obj.dwelltime == 8.33e-05
    assert obj.nucleus == ['1H']
    assert obj.spectrometer_frequency == [297.219948]
    assert obj.bandwidth == 1 / obj.dwelltime
    assert obj.dim_tags == ['DIM_COIL', 'DIM_DYN', None]
    assert obj.dim_position('DIM_DYN') == 5

    assert obj.copy(remove_dim='DIM_DYN').shape == (1, 1, 1, 4096, 32)


def test_copy():
    obj1 = NIFTI_MRS(data['unprocessed'])
    obj2 = obj1.copy()
    obj3 = NIFTI_MRS(obj1)

    assert np.allclose(obj2[:], obj1[:])
    assert np.allclose(obj3[:], obj1[:])


def test_modification_mrs_meta():
    obj = NIFTI_MRS(data['unprocessed'])

    obj.dwelltime = 1 / 5000
    assert obj.spectralwidth == 5000
    assert obj.bandwidth == 5000

    obj.set_version_info(1, 3)
    assert obj.nifti_mrs_version == '1.3'


def test_hdr_ext():
    obj = NIFTI_MRS(data['unprocessed'])

    # Test dictionay like access of keys
    assert 'EchoTime' in obj.hdr_ext
    assert obj.hdr_ext['EchoTime'] == 0.011

    # Test direct manipulation of hdr_ext
    obj.hdr_ext.set_user_def(
        key='bogus',
        value='test')
    assert 'bogus' in obj.hdr_ext

    # Test external manipulation
    newhdr = obj.hdr_ext
    newhdr.SpectrometerFrequency = [10.0, ]
    obj.hdr_ext = newhdr
    assert obj.spectrometer_frequency == [10.0]
    newhdr = obj.hdr_ext.to_dict()
    newhdr['SpectrometerFrequency'] = [20.0, ]
    obj.hdr_ext = newhdr
    assert obj.spectrometer_frequency == [20.0]
    # Break it
    newhdr.pop('ResonantNucleus')
    with pytest.raises(
            headerExtensionError,
            match='Header extension must contain ResonantNucleus.'):
        obj.hdr_ext = newhdr


def test_add_remove_field():

    nmrs = NIFTI_MRS(data['unprocessed'])

    with pytest.raises(
            ValueError,
            match='You cannot remove the required metadata.'):
        nmrs.remove_hdr_field('SpectrometerFrequency')

    with pytest.raises(
            ValueError,
            match='You cannot remove the required metadata.'):
        nmrs.remove_hdr_field('ResonantNucleus')

    with pytest.raises(
            ValueError,
            match='Modify dimension headers through dedicated methods.'):
        nmrs.remove_hdr_field('dim_5')

    with pytest.raises(
            KeyError,
            match='test_key is not defined in the header extension.'):
        nmrs.remove_hdr_field('test_key')

    with pytest.raises(
            ValueError,
            match='Modify dimension headers through dedicated methods.'):
        nmrs.add_hdr_field('dim_5_header', {'p1': [1, 2, 3]})

    nmrs.add_hdr_field('RepetitionTime', 5.0)
    assert 'RepetitionTime' in nmrs.hdr_ext
    assert nmrs.hdr_ext['RepetitionTime'] == 5.0

    nmrs.remove_hdr_field('RepetitionTime')
    assert 'RepetitionTime' not in nmrs.hdr_ext

    with pytest.raises(
            ValueError,
            match='Please provide info about user defined value.'):
        nmrs.add_hdr_field('my_hdr', 5.0)

    nmrs.add_hdr_field('my_hdr', 5.0, doc='doc_here')
    assert 'my_hdr' in nmrs.hdr_ext
    assert nmrs.hdr_ext['my_hdr'] == {'Value': 5.0, 'Description': 'doc_here'}

    nmrs.remove_hdr_field('my_hdr')
    assert 'my_hdr' not in nmrs.hdr_ext


def test_set_dim_tag():
    nmrs = NIFTI_MRS(data['unprocessed'])

    err_str = 'Tag must be one of: DIM_COIL, DIM_DYN, DIM_INDIRECT_0, DIM_INDIRECT_1, DIM_INDIRECT_2,'\
        ' DIM_PHASE_CYCLE, DIM_EDIT, DIM_MEAS, DIM_USER_0, DIM_USER_1, DIM_USER_2.'
    with pytest.raises(
            ValueError,
            match=err_str):
        nmrs.set_dim_tag('DIM_DYN', 'DIM_FOO')

    nmrs.set_dim_tag('DIM_DYN', 'DIM_USER_0')
    assert nmrs.hdr_ext['dim_6'] == 'DIM_USER_0'
    assert nmrs.dim_tags == ['DIM_COIL', 'DIM_USER_0', None]

    nmrs.set_dim_tag(4, 'DIM_USER_1')
    assert nmrs.hdr_ext['dim_5'] == 'DIM_USER_1'
    assert nmrs.dim_tags == ['DIM_USER_1', 'DIM_USER_0', None]

    nmrs.set_dim_tag('DIM_USER_0', 'DIM_DYN', info='my info')
    assert nmrs.hdr_ext['dim_6_info'] == 'my info'

    with pytest.raises(
            ValueError,
            match='New dim header length must be 64'):
        nmrs.set_dim_tag(
            'DIM_DYN',
            'DIM_DYN',
            header={'my_hdr': np.arange(10).tolist()})

    nmrs.set_dim_tag(
        'DIM_DYN',
        'DIM_DYN',
        header={'my_hdr': np.arange(64).tolist()})
    assert nmrs.hdr_ext['dim_6_header'] == {'my_hdr': np.arange(64).tolist()}


def test_nifti_mrs_filename():
    obj = NIFTI_MRS(data['unprocessed'])
    assert obj.filename == 'metab_raw.nii.gz'

#     obj = gen_new_nifti_mrs(np.zeros((1, 1, 1, 2), dtype=complex), 0.0005, 120.0)
#     assert obj.filename == ''


def test_nifti_mrs_save(tmp_path):
    obj = NIFTI_MRS(data['metab'])
    original = deepcopy(obj[:])

    obj.save(tmp_path / 'out')
    assert (tmp_path / 'out.nii.gz').exists()

    obj_reloaded = NIFTI_MRS(tmp_path / 'out.nii.gz')

    assert np.allclose(obj_reloaded[:], obj[:])
    assert np.allclose(obj_reloaded[:], original)


def test_nifti_mrs_generator():
    obj = NIFTI_MRS(data['unprocessed'])

    for gen_data, slice_idx in obj.iterate_over_dims():
        assert gen_data.shape == (1, 1, 1, 4096)
        assert slice_idx == (slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             0, 0)
        break

    for gen_data, slice_idx in obj.iterate_over_dims(dim='DIM_COIL'):
        assert gen_data.shape == (1, 1, 1, 4096, 32)
        assert slice_idx == (slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             0)
        break

    for gen_data, slice_idx in obj.iterate_over_dims(dim='DIM_DYN'):
        assert gen_data.shape == (1, 1, 1, 4096, 64)
        assert slice_idx == (slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             0, slice(None, None, None))
        break

    for gen_data, slice_idx in obj.iterate_over_dims(dim='DIM_DYN', iterate_over_space=True):
        assert gen_data.shape == (4096, 64)
        assert slice_idx == (0, 0, 0, slice(None, None, None), 0, slice(None, None, None))
        break

    for gen_data, slice_idx in obj.iterate_over_dims(dim='DIM_DYN', iterate_over_space=True,
                                                     reduce_dim_index=True):
        assert gen_data.shape == (4096, 64)
        assert slice_idx == (0, 0, 0, slice(None, None, None), 0)
        break

    # obj2 = gen_new_nifti_mrs(
    #     np.zeros((1, 1, 1, 100, 2, 10), dtype=complex),
    #     0.0005,
    #     120.0,
    #     dim_tags=['DIM_EDIT', 'DIM_DYN', None])

    # for gen_data, slice_idx in obj2.iterate_over_dims(dim='DIM_DYN'):
    #     assert gen_data.shape == (1, 1, 1, 100, 10)
    #     assert slice_idx == (slice(None, None, None),
    #                          slice(None, None, None),
    #                          slice(None, None, None),
    #                          slice(None, None, None),
    #                          0,
    #                          slice(None, None, None))
    #     break

    # for gen_data, slice_idx in obj2.iterate_over_dims(dim='DIM_EDIT'):
    #     assert gen_data.shape == (1, 1, 1, 100, 2)
    #     assert slice_idx == (slice(None, None, None),
    #                          slice(None, None, None),
    #                          slice(None, None, None),
    #                          slice(None, None, None),
    #                          slice(None, None, None),
    #                          0)
    #     break


def test_nifti_mrs_spatial_generator():
    obj = NIFTI_MRS(data['unprocessed'])

    for gen_data, slice_idx in obj.iterate_over_spatial():
        assert gen_data.shape == (4096, 32, 64)
        assert slice_idx == (0, 0, 0,
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None))
        break

# Test the dynamic header method
