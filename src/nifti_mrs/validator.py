import json
from .definitions import dimension_tags, standard_defined
import numpy as np
import re


class Error(Exception):
    """Base class for other exceptions"""
    pass


class headerExtensionError(Error):
    """Raised if problems with header extension are found."""
    pass


class niftiHeaderError(Error):
    """Raised if problems with nifti header are found."""
    pass


class niftiDataError(Error):
    """Raised if problems with nifti data are found."""
    pass


def validate_nifti_mrs(nifti_mrs):
    """Validate a full NIfTI MRS image."""

    # Validate data
    validate_nifti_data(nifti_mrs[:])

    # Validate nifit header
    validate_nifti_header(nifti_mrs.header)

    # Validate header extension
    validate_hdr_ext(nifti_mrs.header.extensions[0].get_content(),
                     nifti_mrs.ndim)


def validate_nifti_data(nifti_img_data):
    """Validate the data inside a nibabel nifti image
    1. Check data is complex
    2. Check number of dimensions is at least 4 but less than 8.
    """

    # 1. Check for complexity
    if not np.iscomplexobj(nifti_img_data):
        raise niftiDataError('Data must be complex.')

    # 2. Check for between 4 and 7 dimensions
    if nifti_img_data.ndim < 4\
            or nifti_img_data.ndim > 7:
        raise niftiDataError('Data must have between 4 and 7 dimensions.'
                             f' It has {nifti_img_data.ndim}.')


def validate_nifti_header(nifti_header):
    """Validate the header of a nibabel nifti image
    Check data type is complex
    Check orientation data. - How? TO DO
    Check dwell time
    Check intent name
    """
    if nifti_header.get_data_dtype() not in (complex, np.complex64, np.complex128):
        raise niftiHeaderError('Data type is not complex.')

    if nifti_header['pixdim'][4] <= 0 or nifti_header['pixdim'][4] > 1.0:
        raise niftiHeaderError(f'Dwell time ({nifti_header["pixdim"][4]}) is unrealistic')

    intent_ptrn = re.compile(r'mrs_v\d+_\d+')
    intent_str = nifti_header.get_intent()[2]
    if intent_ptrn.match(intent_str) is None:
        raise niftiHeaderError(f'Intent string ({intent_str}) does not match "mrs_vMajor_minor".')


def validate_hdr_ext(header_ex, data_dimensions):
    """ Validate the header extension
    1. Check that it is json formatted string.
    2. Check that it contains the required meta-data
    3. Check that it contains any required dimension information.
    4. Check that standard-defined data is of correct type.
    Inputs:

    """
    # 1. Check that header_ext is json
    try:
        json_dict = json.loads(header_ex)
    except json.JSONDecodeError as exc:
        raise headerExtensionError("Header extension is not json deserialisable.") from exc

    # 2. Check the two required bits of meta-data
    if "SpectrometerFrequency" in json_dict:
        if not isinstance(json_dict["SpectrometerFrequency"], (list, tuple))\
                and not isinstance(json_dict["SpectrometerFrequency"][0], float):

            raise headerExtensionError("SpectrometerFrequency must be list of floats.")
    else:
        raise headerExtensionError("Header extension must contain SpectrometerFrequency.")

    if "ResonantNucleus" in json_dict:
        if not isinstance(json_dict["ResonantNucleus"], (list, tuple))\
                and not isinstance(json_dict["ResonantNucleus"][0], str):

            raise headerExtensionError("ResonantNucleus must be list of strings.")
    else:
        raise headerExtensionError("Header extension must contain ResonantNucleus.")

    # 3. Dimension information
    for ddx in range(5, 8):
        if data_dimensions > (ddx - 1):
            if f"dim_{ddx}" in json_dict:
                if json_dict[f"dim_{ddx}"] not in dimension_tags:
                    raise headerExtensionError(f"'dim_{ddx}' must be a defined tag.")

                if f"dim_{ddx}_info" in json_dict\
                        and not isinstance(json_dict[f"dim_{ddx}_info"], str):
                    raise headerExtensionError(f"'dim_{ddx}_info' must be a string.")

                if f"dim_{ddx}_header" in json_dict\
                        and not isinstance(json_dict[f"dim_{ddx}_header"], dict):
                    raise headerExtensionError(f"'dim_{ddx}_header' must be a dict.")
            else:
                raise headerExtensionError(f" With {data_dimensions} dimensions the header extension"
                                           f" must contain 'dim_{ddx}'.")

    # 4. Check standard-defined data types
    for key in json_dict:
        if key in standard_defined and not check_type(json_dict[key], standard_defined[key][0]):
            raise headerExtensionError(f'{key} must be a {standard_defined[key][0]}. '
                                       f'{key} is a {type(json_dict[key])}, with value {json_dict[key]}.')

    # print('Header extension validated!')


def check_type(value, json_type):
    '''Checks that values is of type json_type
       json_type may be a tuple to handle array types
       e.g. (list, float) indicates a list of floats.
    '''
    if isinstance(json_type, tuple):
        while len(json_type) > 1:
            if not check_type(value, json_type[0]):
                return False
            try:
                # TO DO: check more than the first element!
                value = value[0]
            except TypeError:
                return False
            json_type = json_type[1:]
        return check_type(value, json_type[0])
    else:
        if isinstance(value, json_type):
            return True
    return False
