'''Test the NIFTI-MRS class implementation

Copyright Will Clarke, University of Oxford, 2023'''

# Imports
from pathlib import Path
from copy import deepcopy
import json

import pytest
import numpy as np
from nibabel.nifti1 import Nifti1Extension

from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs.validator import headerExtensionError
from nifti_mrs.create_nmrs import gen_nifti_mrs, gen_nifti_mrs_hdr_ext

# Files
testsPath = Path(__file__).parent
data = {'unprocessed': testsPath / 'test_data' / 'metab_raw.nii.gz'}


def test_nifti_mrs_class():
    obj = NIFTI_MRS(data['unprocessed'])

    assert obj.nifti_mrs_version == '0.2'
    assert obj.shape == (1, 1, 1, 4096, 4, 16)
    assert obj.ndim == 6
    assert obj.dwelltime == 8.33e-05
    assert obj.nucleus == ['1H']
    assert obj.spectrometer_frequency == [297.219948]
    assert obj.bandwidth == 1 / obj.dwelltime
    assert obj.dim_tags == ['DIM_COIL', 'DIM_DYN', None]
    assert obj.dim_position('DIM_DYN') == 5

    copy_obj = obj.copy(remove_dim='DIM_DYN')
    assert copy_obj.shape == (1, 1, 1, 4096, 4)
    assert copy_obj.dim_tags == ['DIM_COIL', None, None]
    assert copy_obj.hdr_ext.ndim == 5
    assert copy_obj.ndim == 5


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

    # Test dictionary like access of keys
    assert 'EchoTime' in obj.hdr_ext
    assert obj.hdr_ext['EchoTime'] == 0.011

    # Test direct manipulation of hdr_ext
    obj.hdr_ext.set_user_def('bogus', 'test', 'Description')
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
            match='New dim header length must be 16'):
        nmrs.set_dim_tag(
            'DIM_DYN',
            'DIM_DYN',
            header={'EchoTime': np.arange(10).tolist()})

    nmrs.set_dim_tag(
        'DIM_DYN',
        'DIM_DYN',
        header={'EchoTime': np.arange(16).tolist()})
    assert nmrs.hdr_ext['dim_6_header'] == {'EchoTime': np.arange(16).tolist()}


def test_nifti_mrs_filename():
    obj = NIFTI_MRS(data['unprocessed'])
    assert obj.filename == 'metab_raw.nii.gz'

    obj = gen_nifti_mrs(np.zeros((1, 1, 1, 2), dtype=complex), 0.0005, 120.0)
    assert obj.filename == ''


def test_nifti_mrs_save(tmp_path):
    obj = NIFTI_MRS(data['unprocessed'])
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
        assert gen_data.shape == (1, 1, 1, 4096, 4)
        assert slice_idx == (slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             0)
        break

    for gen_data, slice_idx in obj.iterate_over_dims(dim='DIM_DYN'):
        assert gen_data.shape == (1, 1, 1, 4096, 16)
        assert slice_idx == (slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             0, slice(None, None, None))
        break

    for gen_data, slice_idx in obj.iterate_over_dims(dim='DIM_DYN', iterate_over_space=True):
        assert gen_data.shape == (4096, 16)
        assert slice_idx == (0, 0, 0, slice(None, None, None), 0, slice(None, None, None))
        break

    for gen_data, slice_idx in obj.iterate_over_dims(dim='DIM_DYN', iterate_over_space=True,
                                                     reduce_dim_index=True):
        assert gen_data.shape == (4096, 16)
        assert slice_idx == (0, 0, 0, slice(None, None, None), 0)
        break

    obj2 = gen_nifti_mrs(
        np.zeros((1, 1, 1, 100, 2, 10), dtype=complex),
        0.0005,
        120.0,
        dim_tags=['DIM_EDIT', 'DIM_DYN', None])

    for gen_data, slice_idx in obj2.iterate_over_dims(dim='DIM_DYN'):
        assert gen_data.shape == (1, 1, 1, 100, 10)
        assert slice_idx == (slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             0,
                             slice(None, None, None))
        break

    for gen_data, slice_idx in obj2.iterate_over_dims(dim='DIM_EDIT'):
        assert gen_data.shape == (1, 1, 1, 100, 2)
        assert slice_idx == (slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None),
                             0)
        break


def test_nifti_mrs_spatial_generator():
    obj = NIFTI_MRS(data['unprocessed'])

    for gen_data, slice_idx in obj.iterate_over_spatial():
        assert gen_data.shape == (4096, 4, 16)
        assert slice_idx == (0, 0, 0,
                             slice(None, None, None),
                             slice(None, None, None),
                             slice(None, None, None))
        break


# Test the dynamic header method
def test_dynamic_headers():
    data = np.zeros((1, 1, 1, 512, 10), dtype=np.complex64)
    affine = np.eye(4)

    from nifti_mrs.hdr_ext import Hdr_Ext
    hdr_ext = Hdr_Ext(128.0, '1H', dimensions=5)
    hdr_ext.set_dim_info(
        0,
        'DIM_INDIRECT_0',
        info="Incremented echo time for j-evolution",
        hdr={
            "EchoTime": np.linspace(0.03, 0.12, 10).tolist(),
            "EchoTime2": {
                'Value': {"start": 0.03, "increment": 0.01},
                'Description': "second echo time"},
            "RepetitionTime": np.linspace(1.0, 1.9, 10).tolist()})

    nmrs = gen_nifti_mrs_hdr_ext(
        data,
        1 / 2000.0,
        hdr_ext,
        affine=affine)

    dictrep, tuplerep, arrayrep = nmrs.dynamic_hdr_vals()
    assert len(dictrep) == 10
    assert len(tuplerep) == 10
    for d, t, a in zip(dictrep, tuplerep, arrayrep):
        assert 'EchoTime' in d.keys()\
            and 'EchoTime2' in d.keys()\
            and 'RepetitionTime' in d.keys()
        assert len(t) == 3
        assert a.shape[0] == 3
        assert d['EchoTime'] == t[0] == t[1] == a[0] == a[1]

    # 2D
    data = np.zeros((1, 1, 1, 512, 2, 3), dtype=np.complex64)
    affine = np.eye(4)
    hdr_ext = Hdr_Ext(128.0, '1H', dimensions=6)
    hdr_ext.set_dim_info(
        0,
        'DIM_EDIT',
        info="Editing condition",
        hdr={
            "EditCondition": ['ON', 'OFF']})
    hdr_ext.set_dim_info(
        1,
        'DIM_INDIRECT_0',
        info="Incremented echo time for j-evolution",
        hdr={
            "EchoTime": np.linspace(0.03, 0.09, 3).tolist()})

    nmrs = gen_nifti_mrs_hdr_ext(
        data,
        1 / 2000.0,
        hdr_ext,
        affine=affine)

    dictrep, tuplerep, arrayrep = nmrs.dynamic_hdr_vals()
    assert dictrep.shape == tuplerep.shape == (2, 3)
    assert arrayrep.shape == (6, 2)
    for d, t, a in zip(dictrep.ravel(), tuplerep.ravel(), arrayrep):
        assert 'EditCondition' in d.keys()\
            and 'EchoTime' in d.keys()
        assert len(t) == 2
        assert a.shape[0] == 2
        assert d['EditCondition'] == t[0] == a[0]


def test_getaffine():
    obj = NIFTI_MRS(data['unprocessed'])
    assert np.allclose(
        obj.getAffine('voxel', 'world'),
        obj.image.getAffine('voxel', 'world'))


def test_on_load_validator(capsys):
    obj = NIFTI_MRS(data['unprocessed'])
    hdr_ext = obj.hdr_ext.to_dict()
    hdr_ext.pop('dim_5')
    header = obj.header

    bad_extension = Nifti1Extension(
        44,
        json.dumps(hdr_ext).encode('UTF-8'))
    header.extensions.clear()
    header.extensions.append(bad_extension)

    with pytest.raises(
            headerExtensionError,
            match="With 6 dimensions the header extension must contain 'dim_5'."):
        NIFTI_MRS(obj[:], header=header)

    NIFTI_MRS(obj[:], header=header, validate_on_creation=False)
    captured = capsys.readouterr()
    assert captured.out == \
        "This file's header extension is currently invalid. "\
        "Reason:  With 6 dimensions the header extension must contain 'dim_5'.\n"
