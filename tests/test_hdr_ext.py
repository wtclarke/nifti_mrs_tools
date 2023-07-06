'''Tests for the header extension class Hdr_Ext

William Clarke, University of Oxford, 2023'''

from pytest import raises

from nifti_mrs.hdr_ext import Hdr_Ext


def test_init():
    '''Test basic initialisation'''

    # Test wrong spec frequency
    with raises(ValueError):
        Hdr_Ext('7T', '1H')

    # Test wrong nucleus
    with raises(ValueError):
        Hdr_Ext(100., 10)

    # Test wrong number of dimensions
    with raises(ValueError):
        Hdr_Ext(100., '1H', dimensions=10)

    hdr = Hdr_Ext(100., '1H')
    assert hdr.SpectrometerFrequency == [100.0, ]
    assert hdr.ResonantNucleus == ['1H', ]
    assert hdr._dim_info == [{"tag": None, "info": None, "hdr": None}, ] * 3

    hdr = Hdr_Ext(100., '1H', dimensions=6)
    assert hdr._dim_info == [
        {"tag": "DIM_COIL", "info": None, "hdr": None},
        {"tag": "DIM_DYN", "info": None, "hdr": None},
        {"tag": None, "info": None, "hdr": None}]


def test_ndim_and_set_remove():
    hdr = Hdr_Ext(100., '1H')
    assert hdr.ndim == 4

    for idx in range(5, 8):
        hdr = Hdr_Ext(100., '1H', dimensions=idx)
        assert hdr.ndim == idx

    # Basic setting
    hdr = Hdr_Ext(100., '1H')
    hdr.set_dim_info('5th', 'DIM_COIL')
    assert hdr.ndim == 5
    assert hdr._dim_info[0] == {"tag": "DIM_COIL", "info": None, "hdr": None}
    assert hdr._dim_info[1] == {"tag": None, "info": None, "hdr": None}

    # Change already set + meta
    hdr.set_dim_info('5th', 'DIM_EDIT', info='test', hdr={'EchoTime': [0.003]})
    assert hdr.ndim == 5
    assert hdr._dim_info[0] == {"tag": "DIM_EDIT", "info": 'test', "hdr": {'EchoTime': [0.003]}}
    assert hdr._dim_info[1] == {"tag": None, "info": None, "hdr": None}

    # add another dim
    hdr.set_dim_info(1, 'DIM_DYN')
    assert hdr.ndim == 6
    assert hdr._dim_info[0] == {"tag": "DIM_EDIT", "info": 'test', "hdr": {'EchoTime': [0.003]}}
    assert hdr._dim_info[1] == {"tag": "DIM_DYN", "info": None, "hdr": None}

    # Wrong format
    with raises(ValueError):
        hdr.set_dim_info(5, 'DIM_DYN')
    with raises(ValueError):
        hdr.set_dim_info('DIM_EDIT', 'DIM_DYN')

    # Remove a dimension
    hdr.remove_dim_info('5th')
    assert hdr.ndim == 5
    assert hdr._dim_info[0] == {"tag": "DIM_DYN", "info": None, "hdr": None}
    assert hdr._dim_info[1] == {"tag": None, "info": None, "hdr": None}

    # Wrong format
    with raises(ValueError):
        hdr.remove_dim_info(5)


def test_set_remove_standard():
    hdr = Hdr_Ext(100., '1H')

    hdr.set_standard_def('EchoTime', 0.3)
    assert 'EchoTime' in hdr._standard_data
    assert hdr._standard_data['EchoTime'] == 0.3

    with raises(ValueError):
        hdr.set_standard_def('non-standard', 0.3)

    hdr.remove_standard_def('EchoTime')
    assert 'EchoTime' not in hdr._standard_data

    with raises(KeyError):
        hdr.remove_standard_def('not-present')


def test_set_remove_user():
    hdr = Hdr_Ext(100., '1H')

    hdr.set_user_def('my_value', 123, 'test metadata')
    assert 'my_value' in hdr._user_data
    assert hdr._user_data['my_value'] == {'Value': 123, 'Description': 'test metadata'}

    hdr.set_user_def('my_value2', {'foo': 123, 'bar': 456, }, 'test metadata')
    assert 'my_value2' in hdr._user_data
    assert hdr._user_data['my_value2'] == {'foo': 123, 'bar': 456, 'Description': 'test metadata'}

    hdr.remove_user_def('my_value2')
    assert 'my_value2' not in hdr._user_data

    with raises(KeyError):
        hdr.remove_user_def('my_value2')


def test_to_from_dict():
    hdr = Hdr_Ext(100., '1H', dimensions=5)
    hdr.set_standard_def('EchoTime', 0.3)
    hdr.set_user_def('my_value', 123, 'test metadata')
    hdr.set_user_def('my_value2', {'foo': 123, 'bar': 456, }, 'test metadata')

    dict_rep = hdr.to_dict()
    assert isinstance(dict_rep, dict)
    for key in ['SpectrometerFrequency', 'ResonantNucleus', 'dim_5', 'EchoTime', 'my_value', 'my_value2']:
        assert key in dict_rep

    dict_rep.update({'dim_6': 'DIM_EDIT', 'RepetitionTime': 1.0})
    hdr2 = Hdr_Ext.from_header_ext(dict_rep)
    assert hdr2.ndim == 6
    assert hdr2._dim_info[1] == {"tag": "DIM_EDIT", "info": None, "hdr": None}
    assert 'RepetitionTime' in hdr2._standard_data


def test_to_json():
    hdr = Hdr_Ext(100., '1H', dimensions=5)
    hdr.set_standard_def('EchoTime', 0.3)
    hdr.set_user_def('my_value', 123, 'test metadata')
    hdr.set_user_def('my_value2', {'foo': 123, 'bar': 456, }, 'test metadata')

    assert isinstance(hdr.to_json(), str)

    assert str(hdr) == hdr.to_json()


def test_current_keys_and_iter():
    hdr = Hdr_Ext(100., '1H', dimensions=5)
    hdr.set_standard_def('EchoTime', 0.3)
    hdr.set_user_def('my_value', 123, 'test metadata')
    hdr.set_user_def('my_value2', {'foo': 123, 'bar': 456, }, 'test metadata')

    assert len(hdr.current_keys) == 6

    keys = [key for key in hdr]
    assert keys == list(hdr.current_keys)


def test_copy_and_eq():
    hdr = Hdr_Ext(100., '1H', dimensions=5)
    hdr.set_standard_def('EchoTime', 0.3)
    hdr.set_user_def('my_value', 123, 'test metadata')

    hdr2 = hdr.copy()

    assert hdr == hdr2

    hdr.remove_dim_info('5th')
    assert hdr != hdr2


def test_access():
    hdr = Hdr_Ext(100., '1H', dimensions=5)
    assert hdr['SpectrometerFrequency'] == [100.0, ]

    assert 'SpectrometerFrequency' in hdr
