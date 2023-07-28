"""Generate new NIfTI-MRS objects and files from data blocks.

Copyright William Clarke, University of Oxford, 2023
"""
import nibabel as nib
import numpy as np

from nifti_mrs.definitions import nifti_mrs_version
from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs.hdr_ext import Hdr_Ext


def _checkCFUnits(cf, units='Hz'):
    """ Check the units of central frequency and adjust if required."""
    # Assume cf in Hz > 1E5, if it isn't assume that user has passed in MHz
    if cf < 1E5:
        if units.lower() == 'hz':
            cf *= 1E6
        elif units.lower() == 'mhz':
            pass
        else:
            raise ValueError('Only Hz or MHz defined')
    else:
        if units.lower() == 'hz':
            pass
        elif units.lower() == 'mhz':
            cf /= 1E6
        else:
            raise ValueError('Only Hz or MHz defined')
    return cf


def _default_affine():
    """Return NIfTI-MRS default affine matrix"""
    default = np.eye(4) * 10000.0
    default[3, 3] = 1.0
    return default


def gen_nifti_mrs(
        data,
        dwelltime,
        spec_freq,
        nucleus='1H',
        affine=None,
        dim_tags=[None, None, None],
        nifti_version=2,
        no_conj=False):
    """Generate NIfTI-MRS from data and required metadata

    :param data: Complex-typed numpy array of at least 4 dimensions (max 7)
    :type data: numpy.array
    :param dwelltime: Spectral (4th dimension) dwelltime in seconds
    :type dwelltime: float
    :param spec_freq: Spectrometer Frequency in MHz
    :type spec_freq: float
    :param nucleus: Resonant Nucleus string (e.g. 1H, 31P, 2H), defaults to '1H'
    :type nucleus: str, optional
    :param affine: 4x4 orientation/position affine, defaults to None which will use default (scaled identity).
    :type affine: numpy.array, optional
    :param dim_tags: List of dimension tags (e.g. DIM_DYN), defaults to [None, None, None]
    :type dim_tags: list, optional
    :param nifti_version: Version of NIfTI header format, defaults to 2
    :type nifti_version: int, optional
    :param no_conj: If true stops conjugation of data on creation, defaults to False
    :type no_conj: bool, optional
    :return: NIfTI-MRS object
    :rtype: nifti_mrs.nifti_mrs.NIFTI_MRS
    """
    # Create header_ext
    hdr_ext = Hdr_Ext(
        _checkCFUnits(spec_freq, units='MHz'),
        nucleus,
        dimensions=data.ndim)

    for idx, tag in enumerate(dim_tags):
        if tag is not None\
                and idx + 4 < data.ndim:
            hdr_ext.set_dim_info(idx, tag)

    # Pass data and hdr_ext to gen_nifti_mrs_hdr_ext
    return gen_nifti_mrs_hdr_ext(
        data,
        dwelltime,
        hdr_ext,
        affine=affine,
        nifti_version=nifti_version,
        no_conj=no_conj)


def gen_nifti_mrs_hdr_ext(data, dwelltime, hdr_ext, affine=None, nifti_version=2, no_conj=False):
    """Generate NIfTI-MRS from data and header extension object

    :param data: Complex-typed numpy array of at least 4 dimensions (max 7)
    :type data: numpy.array
    :param dwelltime: Spectral (4th dimension) dwelltime in seconds
    :type dwelltime: float
    :param hdr_ext: Populated NIfTI-MRS header extension
    :type hdr_ext: nifti_mrs.hdr_ext.Hdr_Ext
    :param affine: 4x4 orientation/position affine, defaults to None which will use default (scaled identity).
    :type affine: numpy.array, optional
    :param dim_tags: List of dimension tags (e.g. DIM_DYN), defaults to [None, None, None]
    :type dim_tags: list, optional
    :param nifti_version: Version of NIfTI header format, defaults to 2
    :type nifti_version: int, optional
    :param no_conj: If true stops conjugation of data on creation, defaults to False
    :type no_conj: bool, optional
    :return: NIfTI-MRS object
    :rtype: nifti_mrs.nifti_mrs.NIFTI_MRS
    """

    if not np.iscomplexobj(data):
        raise ValueError('data must be complex')
    if data.ndim < 4 or data.ndim > 7:
        raise ValueError(f'data must have between 4 and 7 dimensions, currently has {data.ndim}')

    if affine is None:
        affine = _default_affine()

    # Create a nifti image as a short cut to creating a header
    if nifti_version == 1:
        tmp_img = nib.nifti1.Nifti1Image(
            data,
            affine=affine)
        header = tmp_img.header
    elif nifti_version == 2:
        tmp_img = nib.nifti2.Nifti2Image(
            data,
            affine=affine)
        header = tmp_img.header
    else:
        raise ValueError('nifti_version must be 1 or 2')

    # Orientation/position info
    header.set_qform(affine)
    header.set_sform(affine)

    # Touch up header with required NIfTI-MRS metadata
    header['pixdim'][4] = dwelltime
    v_major = nifti_mrs_version[0]
    v_minor = nifti_mrs_version[1]
    header['intent_name'] = f'mrs_v{v_major}_{v_minor}'.encode()

    # Ensure that xyzt_units is set correctly
    # define NIFTI_UNITS_MM      2 /! NIFTI code for millimeters. /
    # define NIFTI_UNITS_SEC     8 /! NIFTI code for seconds. /
    header.set_xyzt_units(xyz=2, t=8)

    # Add header extension to header
    json_s = hdr_ext.to_json()
    extension = nib.nifti1.Nifti1Extension(44, json_s.encode('UTF-8'))
    header.extensions.append(extension)

    if no_conj:
        return NIFTI_MRS(data.conj(), header=header)
    else:
        return NIFTI_MRS(data, header=header)
