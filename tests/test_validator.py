'''Test the NIFTI-MRS class validator

Copyright Will Clarke, University of Oxford, 2023'''

from pytest import raises
import json

from nifti_mrs import validator
from nifti_mrs import hdr_ext


def test_required_hdr_ext():
    # No frequency
    test_dict = dict(
        ResonantNucleus=["1H", ]
    )
    with raises(
            validator.headerExtensionError,
            match='Header extension must contain SpectrometerFrequency.'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)

    # No nucleus
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
    )
    with raises(
            validator.headerExtensionError,
            match='Header extension must contain ResonantNucleus.'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)

    # Wrong formats
    test_dict = dict(
        SpectrometerFrequency=['7T', ],
        ResonantNucleus=["1H", ]
    )
    with raises(
            validator.headerExtensionError,
            match='SpectrometerFrequency must be list of floats.'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)
    test_dict = dict(
        SpectrometerFrequency=100.0,
        ResonantNucleus=["1H", ]
    )
    with raises(
            validator.headerExtensionError,
            match='SpectrometerFrequency must be list of floats.'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)

    test_dict = dict(
        SpectrometerFrequency=[123.0, ],
        ResonantNucleus=[1, ]
    )
    with raises(
            validator.headerExtensionError,
            match='ResonantNucleus must be list of strings.'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)
    test_dict = dict(
        SpectrometerFrequency=[100.0, ],
        ResonantNucleus="1H"
    )
    with raises(
            validator.headerExtensionError,
            match='ResonantNucleus must be list of strings.'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)


def test_dim_dim_tag_correspondence():
    '''Test whether the validator correctly deals with the number of dimensions and the tags'''
    hext = hdr_ext.Hdr_Ext(
        123.2,
        '1H',
        dimensions=5
    )

    with raises(
            validator.headerExtensionError,
            match='tag exceeds specified dimensions'):
        validator.validate_hdr_ext(hext.to_json(), (1,) * 4, data_dimensions=4)

    # Manual
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_5_header={'test': [0, 1]}
    )
    with raises(
            validator.headerExtensionError,
            match='tag exceeds specified dimensions'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)

    # Manual - more complex
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_5='DIM_DYN',
        dim_6_info='test'
    )
    with raises(
            validator.headerExtensionError,
            match='tag exceeds specified dimensions'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 5, data_dimensions=5)

    # Manual - Illegal dim tags
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_4='DIM_DYN'
    )
    with raises(
            validator.headerExtensionError,
            match='dim_4 tag is forbidden `dim_N...` can only take the values 5-7.'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)


def test_standard_meta():
    test_dict = dict(
        SpectrometerFrequency=[100.0, ],
        ResonantNucleus=["1H", ],
        EchoTime='test'
    )
    with raises(
            validator.headerExtensionError,
            match='EchoTime must be a'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)


def test_user_def_meta():
    test_dict = dict(
        SpectrometerFrequency=[100.0, ],
        ResonantNucleus=["1H", ],
        nonstandard='test'
    )
    with raises(
            validator.headerExtensionError,
            match='User-defined must be a JSON object and include a "Description"'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)

    test_dict = dict(
        SpectrometerFrequency=[100.0, ],
        ResonantNucleus=["1H", ],
        nonstandard={'Value': 'test'}
    )
    with raises(
            validator.headerExtensionError,
            match='User-defined must be a JSON object and include a "Description"'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1,) * 4, data_dimensions=4)


def test_dynamic_header_size():
    '''Test that dynamic headers have the format and size'''

    # Wrong type
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_5='DIM_DYN',
        dim_5_header={'EchoTime': 0.1}
    )
    with raises(
            validator.headerExtensionError,
            match='dim_5_header not an array or dict/object'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1, 1, 1, 512, 4), data_dimensions=5)

    # Array, standard but wrong size
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_5='DIM_DYN',
        dim_5_header={'EchoTime': [0, 1, 3]}
    )
    with raises(
            validator.headerExtensionError,
            match='does not match the dimension size '):
        validator.validate_hdr_ext(json.dumps(test_dict), (1, 1, 1, 512, 4), data_dimensions=5)

    # dict, standard but no increment
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_5='DIM_DYN',
        dim_5_header={'EchoTime': {'start': 0, 'step': 1}}
    )
    with raises(
            validator.headerExtensionError,
            match=' but does not contain'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1, 1, 1, 512, 4), data_dimensions=5)

    # Non standard but no description
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_5='DIM_DYN',
        dim_5_header={'test': {'Value': [0, 1, 3]}}
    )
    with raises(
            validator.headerExtensionError,
            match='with non-standard tag must contain a'):
        validator.validate_hdr_ext(json.dumps(test_dict), (1, 1, 1, 512, 4), data_dimensions=5)

    # Standard
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_5='DIM_DYN',
        dim_5_header={'EchoTime': [0, 1, 3, 4]}
    )
    validator.validate_hdr_ext(json.dumps(test_dict), (1, 1, 1, 512, 4), data_dimensions=5)

    # Non standard but no description
    test_dict = dict(
        SpectrometerFrequency=[123.2, ],
        ResonantNucleus=["1H", ],
        dim_5='DIM_DYN',
        dim_5_header={'test': {'Value': [0, 1, 3, 4], 'Description': 'test'}}
    )
    validator.validate_hdr_ext(json.dumps(test_dict), (1, 1, 1, 512, 4), data_dimensions=5)
