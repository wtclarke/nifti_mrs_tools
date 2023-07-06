"""Tools for reordering the dimensions of NIfTI-MRS

    Author: Will Clarke <william.clarke@ndcn.ox.ac.uk>
    Copyright (C) 2021 University of Oxford
"""
import re

import numpy as np

from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs import utils


def reorder(nmrs, dim_tag_list):
    """Reorder the higher dimensions of a NIfTI-MRS object.
    Can force a singleton dimension with new tag.

    :param nmrs: NIFTI-MRS object to reorder.
    :type nmrs: fsl_mrs.core.nifti_mrs.NIFTI_MRS
    :param dim_tag_list: List of dimension tags in desired order
    :type dim_tag_list: List of str
    :return: Reordered NIfTI-MRS object.
    :rtype: fsl_mrs.core.nifti_mrs.NIFTI_MRS
    """

    # Check existing tags are in the list of desired tags
    for idx, tag in enumerate(nmrs.dim_tags):
        if tag not in dim_tag_list\
                and tag is not None:
            raise utils.NIfTI_MRSIncompatible(
                f'The existing tag ({tag}) does not appear '
                f'in the requested tag order ({dim_tag_list}).')

    # Create singleton dimensions if required
    original_dims = nmrs.ndim
    new_dim = sum(x is not None for x in nmrs.dim_tags) + 4
    dims_to_add = tuple(range(original_dims, new_dim + 1))
    data_with_singleton = np.expand_dims(nmrs[:], dims_to_add)

    # Create list of source indicies
    # Create list of destination indicies
    # Keep track of singleton tags
    source_indicies = []
    dest_indicies = []
    singleton_tags = {}
    counter = 0
    for idx, tag in enumerate(dim_tag_list):
        if tag is not None:
            if tag in nmrs.dim_tags:
                source_indicies.append(nmrs.dim_tags.index(tag) + 4)
            else:
                source_indicies.append(nmrs.ndim + counter)
                counter += 1
                singleton_tags.update({(idx + 5): tag})

            dest_indicies.append(idx + 4)

    # Sort header extension dim_tags
    dim_n = re.compile(r'^dim_[567]$')
    new_hdr_ext = nmrs.hdr_ext.copy()
    for key in nmrs.hdr_ext:
        if dim_n.match(key):
            # Look for matching _info/_header tags
            if (key + '_info') in nmrs.hdr_ext:
                tmp_info = nmrs.hdr_ext[key + '_info']
            else:
                tmp_info = None
            if (key + '_header') in nmrs.hdr_ext:
                tmp_header = nmrs.hdr_ext[key + '_header']
            else:
                tmp_header = None

            new_index = dest_indicies[source_indicies.index(int(key[4]) - 1)] + 1
            new_ind_str = f'{new_index}th'
            new_hdr_ext.set_dim_info(
                new_ind_str,
                nmrs.hdr_ext[key],
                info=tmp_info,
                hdr=tmp_header)

    # For any singleton dimensions we've added
    for dim in singleton_tags:
        new_hdr_ext.set_dim_info(f'{dim}th', singleton_tags[dim])

    new_header = utils.modify_hdr_ext(
        new_hdr_ext,
        nmrs.header)

    new_nmrs = NIFTI_MRS(
        np.moveaxis(data_with_singleton, source_indicies, dest_indicies),
        header=new_header)

    return new_nmrs
