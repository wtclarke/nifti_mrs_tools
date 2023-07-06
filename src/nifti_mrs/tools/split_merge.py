"""Tools for merging and splitting the dimensions of NIfTI-MRS

    Author: Will Clarke <william.clarke@ndcn.ox.ac.uk>
    Copyright (C) 2021 University of Oxford
"""
import re

import numpy as np

from nifti_mrs.nifti_mrs import NIFTI_MRS, NIFTIMRS_DimDoesntExist
from nifti_mrs import utils


def split(nmrs, dimension, index_or_indicies):
    """Splits, or extracts indices from, a specified dimension of a
    NIFTI_MRS object. Output is two NIFTI_MRS objects. Header information preserved.

    :param nmrs: Input nifti_mrs object to split
    :type nmrs: fsl_mrs.core.nifti_mrs.NIFTI_MRS
    :param dimension: Dimension along which to split.
        Dimension tag or one of 4, 5, 6 (for 0-indexed 5th, 6th, and 7th)
    :type dimension: str or int
    :param index_or_indicies: Single integer index to split after,
        or list of interger indices to insert into second array.
        E.g. '0' will place the first index into the first output
        and 1 -> N in the second.
        '[1, 5, 10]' will place 1, 5 and 10 into the second output
        and all other will remain in the first.
    :type index_or_indicies: int or [int]
    :return: Two NIFTI_MRS object containing the split files
    :rtype: fsl_mrs.core.nifti_mrs.NIFTI_MRS
    """

    if isinstance(dimension, str):
        try:
            dim_index = nmrs.dim_position(dimension)
        except NIFTIMRS_DimDoesntExist:
            raise ValueError(f'{dimension} not found as dimension tag. This data contains {nmrs.dim_tags}.')
    elif isinstance(dimension, int):
        if dimension > (nmrs.ndim - 1) or dimension < 4:
            raise ValueError('Dimension must be one of 4, 5, or 6 (or DIM_TAG string).'
                             f' This data has {nmrs.ndim} dimensions,'
                             f' i.e. a maximum dimension value of {nmrs.ndim-1}.')
        dim_index = dimension
    else:
        raise TypeError('Dimension must be an int (4, 5, or 6) or string (DIM_TAG string).')

    # Construct indexing
    if isinstance(index_or_indicies, int):
        if index_or_indicies < 0\
                or (index_or_indicies + 1) >= nmrs.shape[dim_index]:
            raise ValueError('index_or_indicies must be between 0 and N-1,'
                             f' where N is the size of the specified dimension ({nmrs.shape[dim_index]}).')
        index = np.arange(index_or_indicies + 1, nmrs.shape[dim_index])

    elif isinstance(index_or_indicies, list):
        if not np.logical_and(np.asarray(index_or_indicies) >= 0,
                              np.asarray(index_or_indicies) <= nmrs.shape[dim_index]).all():
            raise ValueError('index_or_indicies must have elements between 0 and N,'
                             f' where N is the size of the specified dimension ({nmrs.shape[dim_index]}).')
        index = index_or_indicies

    else:
        raise TypeError('index_or_indicies must be single index or list of indicies')

    # Split header down
    split_hdr_ext_1, split_hdr_ext_2 = _split_dim_header(nmrs.hdr_ext,
                                                         dim_index + 1,
                                                         nmrs.shape[dim_index],
                                                         index_or_indicies)
    out_hdr_1 = utils.modify_hdr_ext(split_hdr_ext_1, nmrs.header)
    out_hdr_2 = utils.modify_hdr_ext(split_hdr_ext_2, nmrs.header)

    nmrs_1 = NIFTI_MRS(np.delete(nmrs[:], index, axis=dim_index), header=out_hdr_1)
    nmrs_2 = NIFTI_MRS(np.take(nmrs[:], index, axis=dim_index), header=out_hdr_2)

    return nmrs_1, nmrs_2


def _split_dim_header(hdr, dimension, dim_length, index):
    """Split dim_N_header keys in header extensions.

    :param hdr: Header extension to split
    :type hdr: dict
    :param dimension: Dimension (5, 6, or 7) to split along
    :type dimension: int
    :param dim_length: Length of dimension
    :type index: int
    :param index: Index to split after or indicies to extract
    :type index: int or list of ints
    :return: Split header eextension dicts
    :rtype: dict
    """
    hdr1 = hdr.copy()
    hdr2 = hdr.copy()

    def split_list(in_list):
        if isinstance(index, int):
            out_1 = in_list[:(index + 1)]
            out_2 = in_list[(index + 1):]
        elif isinstance(index, list):
            out_1 = np.delete(np.asarray(in_list), index).tolist()
            out_2 = np.take(np.asarray(in_list), index).tolist()
        return out_1, out_2

    def split_user_or_std(hdr_val):
        if isinstance(hdr_val, dict)\
                and 'Value' in hdr_val:
            tmp_1, tmp_2 = split_list(hdr_val['Value'])
            out_1 = hdr_val.copy()
            out_2 = hdr_val.copy()
            out_1.update({'Value': tmp_1})
            out_2.update({'Value': tmp_2})
            return out_1, out_2
        else:
            return split_list(hdr_val)

    def split_single(hdr_val):
        hdr_type = utils.check_type(hdr_val)
        long_fmt = utils.dim_n_header_short_to_long(hdr_val, dim_length)
        long_fmt_1, long_fmt_2 = split_user_or_std(long_fmt)
        if hdr_type == 'long':
            return long_fmt_1, long_fmt_2
        else:
            return utils.dim_n_header_long_to_short(long_fmt_1), utils.dim_n_header_long_to_short(long_fmt_2)

    key_str = f'dim_{dimension}_header'
    key_str_tag = f'dim_{dimension}'
    key_str_info = f'dim_{dimension}_info'
    if key_str in hdr:
        new_h1 = {}
        new_h2 = {}
        for sub_key in hdr[key_str]:
            new_h1[sub_key], new_h2[sub_key] = split_single(hdr[key_str][sub_key])

        curr_tag = hdr[key_str_tag]
        if key_str_info in hdr:
            curr_info = hdr[key_str_info]
        else:
            curr_info = None
        hdr1.set_dim_info(dimension - 5, curr_tag, info=curr_info, hdr=new_h1)
        hdr2.set_dim_info(dimension - 5, curr_tag, info=curr_info, hdr=new_h2)

    return hdr1, hdr2


def merge(array_of_nmrs, dimension):
    """Concatenate NIfTI-MRS objects along specified higher dimension

    :param array_of_nmrs: Array of NIFTI-MRS objects to concatenate
    :type array_of_nmrs: tuple or list of fsl_mrs.core.nifti_mrs.NIFTI_MRS
    :param dimension: Dimension along which to concatenate.
        Dimension tag or one of 4, 5, 6 (for 0-indexed 5th, 6th, and 7th).
    :type dimension: int or str
    :return: Concatenated NIFTI-MRS object
    :rtype: fsl_mrs.core.nifti_mrs.NIFTI_MRS
    """
    if isinstance(dimension, str):
        try:
            dim_index = array_of_nmrs[0].dim_position(dimension)
        except NIFTIMRS_DimDoesntExist:
            raise ValueError(f'{dimension} not found as dimension tag. This data contains {array_of_nmrs[0].dim_tags}.')
    elif isinstance(dimension, int):
        if dimension > (array_of_nmrs[0].ndim - 1) or dimension < 4:
            raise ValueError('Dimension must be one of 4, 5, or 6 (or DIM_TAG string).'
                             f' This data has {array_of_nmrs[0].ndim} dimensions,'
                             f' i.e. a maximum dimension value of {array_of_nmrs[0].ndim-1}.')
        dim_index = dimension
    else:
        raise TypeError('Dimension must be an int (4, 5, or 6) or string (DIM_TAG string).')

    # Check shapes and tags are compatible.
    # If they are and enter the data into a tuple for concatenation
    def check_shape(to_compare):
        for dim in range(to_compare.ndim):
            # Do not compare on selected dimension
            if dim == dim_index:
                continue
            if to_compare.shape[dim] != array_of_nmrs[0].shape[dim]:
                return False
        return True

    def check_tag(to_compare):
        for tdx in range(3):
            if array_of_nmrs[0].dim_tags[tdx] != to_compare.dim_tags[tdx]:
                return False
        return True

    to_concat = []
    for idx, nmrs in enumerate(array_of_nmrs):
        # Check shape
        if not check_shape(nmrs):
            raise utils.NIfTI_MRSIncompatible(
                'The shape of all concatenated objects must match.'
                f' The shape ({nmrs.shape}) of the {idx} object does'
                f' not match that of the first ({array_of_nmrs[0].shape}).')
        # Check dim tags for compatibility
        if not check_tag(nmrs):
            raise utils.NIfTI_MRSIncompatible(
                'The tags of all concatenated objects must match.'
                f' The tags ({nmrs.dim_tags}) of the {idx} object does'
                f' not match that of the first ({array_of_nmrs[0].dim_tags}).')

        if nmrs.shape[-1] == 1:
            # If a squeezed singleton on the end.
            to_concat.append(np.expand_dims(nmrs[:], -1))
        else:
            to_concat.append(nmrs[:])

        # Merge header extension
        if idx == 0:
            merged_hdr_ext = nmrs.hdr_ext
            merged_length = to_concat[-1].shape[dim_index]
        else:
            merged_hdr_ext = _merge_dim_header(merged_hdr_ext,
                                               nmrs.hdr_ext,
                                               dim_index + 1,
                                               merged_length,
                                               to_concat[-1].shape[dim_index])
            merged_length += to_concat[-1].shape[dim_index]

    out_hdr = utils.modify_hdr_ext(merged_hdr_ext, array_of_nmrs[0].header)

    return NIFTI_MRS(np.concatenate(to_concat, axis=dim_index), header=out_hdr)


def _merge_dim_header(hdr1, hdr2, dimension, dim_length1, dim_length2):
    """Merge dim_N_header keys in header extensions.
    Output header copies all other fields from hdr1

    :param hdr1: header extension from 1st file
    :type hdr1: dict
    :param hdr2: header extension from 2nd file
    :type hdr2: dict
    :param dimension: Dimension (5,6, or 7) to merge along
    :type dimension: int
    :param dim_length1: Dimension length of first file
    :type dimension: int
    :param dim_length2: Dimension length of second file
    :type dimension: int
    :return: Merged header extension dict
    :rtype: dict
    """
    out_hdr = hdr1.copy()

    def merge_list(list_1, list_2):
        return list_1 + list_2

    def merge_user_or_std(hdr_val1, hdr_val2):
        if isinstance(hdr_val1, dict)\
                and 'Value' in hdr_val1:
            tmp = merge_list(hdr_val1['Value'], hdr_val2['Value'])
            out = hdr_val1.copy()
            out.update({'Value': tmp})
            return out
        else:
            return merge_list(hdr_val1, hdr_val2)

    def merge_single(hdr_val1, hdr_val2):
        hdr_type = utils.check_type(hdr_val1)
        long_fmt_1 = utils.dim_n_header_short_to_long(hdr_val1, dim_length1)
        long_fmt_2 = utils.dim_n_header_short_to_long(hdr_val2, dim_length2)
        long_fmt = merge_user_or_std(long_fmt_1, long_fmt_2)
        if hdr_type == 'long':
            return long_fmt
        else:
            return utils.dim_n_header_long_to_short(long_fmt)

    key_str = f'dim_{dimension}_header'
    key_str_tag = f'dim_{dimension}'
    key_str_info = f'dim_{dimension}_info'

    def run_check():
        # Check all other dimension fields are consistent
        dim_n = re.compile(r'dim_[567].*')
        for key in hdr1:
            if dim_n.match(key) and key != key_str:
                if hdr1[key] != hdr2[key]:
                    raise utils.NIfTI_MRSIncompatible(
                        f'Both files must have matching dimension headers apart from the '
                        f'one being merged. {key} does not match.')

    if key_str in hdr1 and key_str in hdr2:
        run_check()
        # Check the subfields of the header to merge are consistent
        if not hdr1[key_str].keys() == hdr2[key_str].keys():
            raise utils.NIfTI_MRSIncompatible(
                f'Both NIfTI-MRS files must have matching dim {dimension} header fields.'
                f'The first header contains {hdr1[key_str].keys()}. '
                f'The second header contains {hdr2[key_str].keys()}.')
        new_h = {}
        for sub_key in hdr1[key_str]:
            new_h[sub_key] = merge_single(hdr1[key_str][sub_key], hdr2[key_str][sub_key])

        curr_tag = hdr1[key_str_tag]
        if key_str_info in hdr1:
            curr_info = hdr1[key_str_info]
        else:
            curr_info = None
        out_hdr.set_dim_info(dimension - 5, curr_tag, info=curr_info, hdr=new_h)
    elif key_str in hdr1 and key_str not in hdr2\
            or key_str not in hdr1 and key_str in hdr2:
        # Incompatible headers
        raise utils.NIfTI_MRSIncompatible(f'Both NIfTI-MRS files must have matching dim {dimension} header fields')
    elif key_str not in hdr1 and key_str not in hdr2:
        # Nothing to merge - still run check
        run_check()
    return out_hdr
