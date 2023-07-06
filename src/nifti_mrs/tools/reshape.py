"""Tools for reshaping the higher dimensions of NIfTI-MRS

    Author: Will Clarke <william.clarke@ndcn.ox.ac.uk>
    Copyright (C) 2021 University of Oxford
"""
from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs import utils

import numpy as np

# TO DO:
# def _reshape_hdr(dynamic_hdr, target):

#     return reshaped_hdr


def reshape(nmrs, reshape, d5=None, d6=None, d7=None):
    """Reshape the higher dimensions (5-7) of an nifti-mrs file.
    Uses numpy reshape syntax to reshape. Use -1 for automatic sizing.

    If the dimension exists after reshaping a tag is required. If None is passed
    but one already exists no change will be made. If no value exists then an
    exception will be raised.

    :param nmrs: Input NIfTI-MRS file
    :type nmrs: NIFTI_MRS
    :param reshape: Tuple of target sizes in style of numpy.reshape, higher dimensions only.
    :type reshape: tuple
    :param d5: Dimension tag to set dim_5, defaults to None
    :type d5: str, optional
    :param d6: Dimension tag to set dim_6, defaults to None
    :type d6: str, optional
    :param d7: Dimension tag to set dim_7, defaults to None
    :type d7: str, optional
    """

    shape = nmrs[:].shape[0:4]
    shape += reshape
    reshaped_data = np.reshape(nmrs[:], shape)
    new_hdr_ext = nmrs.hdr_ext.copy()

    # Note numerical index is N-1
    if d5:
        new_hdr_ext.set_dim_info('5th', d5)
    elif reshaped_data.ndim > 4\
            and nmrs.dim_tags[0] is None:
        raise TypeError(f'An appropriate d5 dim tag must be given as ndim = {reshaped_data.ndim}.')
    if d6:
        new_hdr_ext.set_dim_info('6th', d6)
    elif reshaped_data.ndim > 5\
            and nmrs.dim_tags[1] is None:
        raise TypeError(f'An appropriate d6 dim tag must be given as ndim = {reshaped_data.ndim}.')
    if d7:
        new_hdr_ext.set_dim_info('7th', d7)
    elif reshaped_data.ndim > 6\
            and nmrs.dim_tags[2] is None:
        raise TypeError(f'An appropriate d7 dim tag must be given as ndim = {reshaped_data.ndim}.')

    new_header = utils.modify_hdr_ext(new_hdr_ext, nmrs.header)

    nmrs_reshaped = NIFTI_MRS(reshaped_data, header=new_header)

    # reshpaed_hrd = _reshape_hdr(nmrs_reshaped.dynamic_hdr_vals[2],)

    return nmrs_reshaped
