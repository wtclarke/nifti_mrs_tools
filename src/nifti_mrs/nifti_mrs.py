"""Core NIfTI-MRS class.
For more information on NIfTI-MRS see https://github.com/wtclarke/mrs_nifti_standard

Copyright William Clarke, University of Oxford, 2023
"""
import json
from pathlib import Path
import re

import nibabel as nib
import numpy as np

from fsl.data.image import Image

from . import validator
from .hdr_ext import Hdr_Ext
from .definitions import dimension_tags, standard_defined
import nifti_mrs.utils as utils


class NIFTIMRS_DimDoesntExist(Exception):
    pass


class NotNIFTI_MRS(Exception):
    pass


class NIFTI_MRS():
    """A class to load and represent NIfTI-MRS formatted data.
    Utilises the fslpy Image class and nibabel nifti headers.

    Access the underlying fslpy Image object for useful attributes using obj.image.
    """

    def __init__(self, *args, validate_on_creation=True, **kwargs):
        """Create a NIFTI_MRS object with the given image data or file name.

        Arguments mirror those of the leveraged fsl.data.image.IMage class.

        :arg image:      A string containing the name of an image file to load,
                         or a Path object pointing to an image file, or a
                         :mod:`numpy` array, or a :mod:`nibabel` image object,
                         or an ``Image`` object.

        :arg name:       A name for the image.

        :arg header:     If not ``None``, assumed to be a
                         :class:`nibabel.nifti1.Nifti1Header` or
                         :class:`nibabel.nifti2.Nifti2Header` to be used as the
                         image header. Not applied to images loaded from file,
                         or existing :mod:`nibabel` images.

        :arg xform:      A :math:`4\\times 4` affine transformation matrix
                         which transforms voxel coordinates into real world
                         coordinates. If not provided, and a ``header`` is
                         provided, the transformation in the header is used.
                         If neither a ``xform`` nor a ``header`` are provided,
                         an identity matrix is used. If both a ``xform`` and a
                         ``header`` are provided, the ``xform`` is used in
                         preference to the header transformation.

        :arg dataSource: If ``image`` is not a file name, this argument may be
                         used to specify the file from which the image was
                         loaded.

        :arg loadMeta:   If ``True``, any metadata contained in JSON sidecar
                         files is loaded and attached to this ``Image`` via
                         the :class:`.Meta` interface. if ``False``, metadata
                         can be loaded at a later stage via the
                         :func:`loadMeta` function. Defaults to ``False``.

        :arg dataMgr:    Object implementing the :class:`DataManager`
                         interface, for managing access to the image data.

        All other arguments are passed through to the ``nibabel.load`` function
        (if it is called).

        :arg validate_on_creation:   If True (default) then the header extension will
                                     be validated on creation of the NIfTI-MRS object.
                                     Use False to just print warnings.
        """
        # Handle various options for the first (data source) argument
        input_hdr_ext = None
        if isinstance(args[0], np.ndarray):
            # If generated from np.array include conjugation
            # to make sure generation from data of existing NIfTI-MRS
            # object results in consistent phase/freq convention.
            args = list(args)
            args[0] = args[0].conj()
            filename = None
        elif isinstance(args[0], Path):
            args = list(args)
            filename = args[0].name
            args[0] = str(args[0])
        elif isinstance(args[0], str):
            args = list(args)
            filename = Path(args[0]).name
        elif isinstance(args[0], NIFTI_MRS):
            args = list(args)
            filename = args[0].filename
            input_hdr_ext = args[0].hdr_ext
            args[0] = args[0].image

        # Instantiate Image object
        self.image = Image(*args, **kwargs)

        # Store original filename for reports etc
        self._filename = filename

        # Check that file meets minimum requirements
        try:
            if float(self.nifti_mrs_version) < 0.2:
                raise NotNIFTI_MRS('NIFTI-MRS > V0.2 required.')
        except IndexError:
            raise NotNIFTI_MRS('NIFTI-MRS intent code not set.')

        if input_hdr_ext is not None:
            self._hdr_ext = input_hdr_ext
        else:
            hdr_ext_codes = self.header.extensions.get_codes()
            if 44 not in hdr_ext_codes:
                raise NotNIFTI_MRS('NIFTI-MRS must have a header extension.')

            self._hdr_ext = Hdr_Ext.from_header_ext(
                json.loads(
                    self.header.extensions[hdr_ext_codes.index(44)].get_content()))

        # Some validation upon creation
        if validate_on_creation:
            validator.validate_hdr_ext(
                self._hdr_ext.to_json(),
                self.image.shape,
                np.max((self._hdr_ext.ndim, self.image.ndim)))
        else:
            try:
                validator.validate_hdr_ext(
                    self._hdr_ext.to_json(),
                    self.image.shape,
                    np.max((self._hdr_ext.ndim, self.image.ndim)))
            except validator.headerExtensionError as exc:
                print(f"This file's header extension is currently invalid. Reason: {str(exc)}")

        try:
            self.nucleus
            self.spectrometer_frequency
        except KeyError:
            raise NotNIFTI_MRS('NIFTI-MRS header extension must have nucleus and spectrometerFrequency keys.')

    def __getitem__(self, sliceobj):
        '''Apply conjugation at use. This swaps from the
        NIFTI-MRS and Levvit inspired right-handed reference frame
        to a left-handed one, which FSL-MRS development started in.'''
        # print(f'getting {sliceobj} to conjugate {super().__getitem__(sliceobj)}')
        return self.image[sliceobj].conj()

    def __setitem__(self, sliceobj, values):
        '''Apply conjugation back at write. This swaps from the
        FSL-MRS left handed convention to the NIFTI-MRS and Levvit
        inspired right-handed reference frame.'''
        # print(f'setting {sliceobj} to conjugate of {values[0]}')
        # print(super().__getitem__(sliceobj)[0])
        self.image[sliceobj] = values.conj()
        # print(super().__getitem__(sliceobj)[0])

    # Implement useful calls to attributes of the image class object. Should I just be using inheretence here? Not sure.
    @property
    def header(self):
        """Returns NIfTI-MRS header object"""
        return self.image.header

    @property
    def ndim(self):
        """Returns number of dimensions in the NIfTI-MRS object"""
        return self.hdr_ext.ndim

    @property
    def shape(self):
        """Returns the data shape. Singleton dimensions implied by header extension keys are included.
        Use obj.image.shape to get the shape of the stored data"""
        base_shape = self.image.shape
        for _ in range(self.image.ndim, self.hdr_ext.ndim):
            base_shape += (1, )
        return base_shape

    @property
    def dtype(self):
        """Returns data type"""
        return self.image.dtype

    @property
    def nifti_mrs_version(self):
        """Get NIfTI-MRS version string."""
        tmp_vstr = self.image.header.get_intent()[2].split('_')
        return tmp_vstr[1].lstrip('v') + '.' + tmp_vstr[2]

    def set_version_info(self, major, minor):
        """Puts mrs_v{major}_{minor} into intent_name"""
        self.header['intent_name'] = f'mrs_v{major}_{minor}'.encode()

    @property
    def dwelltime(self):
        '''Return dwelltime in seconds'''
        return self.header['pixdim'][4]

    @dwelltime.setter
    def dwelltime(self, new_dt):
        """Sets new dwelltime (pixdim[4]). Units = seconds"""
        self.header['pixdim'][4] = new_dt

    @property
    def spectralwidth(self):
        '''Return spectral width in Hz'''
        return 1 / self.dwelltime

    @property
    def bandwidth(self):
        '''Alias for spectralwidth (Hz)'''
        return self.spectralwidth

    @property
    def nucleus(self):
        """Returns resonant nucleus string(s) - returns list"""
        return self.hdr_ext['ResonantNucleus']

    @property
    def spectrometer_frequency(self):
        '''Central or spectrometer frequency in MHz - returns list'''
        return self.hdr_ext['SpectrometerFrequency']

    def getAffine(self, *args):
        """Return an affine transformation which can be used to transform
        coordinates from ``from_`` to ``to``.

        Valid values for the ``from_`` and ``to`` arguments are:

         - ``'voxel'``: The voxel coordinate system
         - ``'world'``: The world coordinate system, as defined by the image
           sform/qform
         - ``'fsl'``: The FSL coordinate system (scaled voxels, with a
           left-right flip if the sform/qform has a positive determinant)

        :arg from_: Source coordinate system
        :arg to:    Destination coordinate system
        :returns:   A ``numpy`` array of shape ``(4, 4)``
        """
        return self.image.getAffine(*args)

    @property
    def worldToVoxMat(self):
        """Returns a ``numpy`` array of shape ``(4, 4)`` containing an
        affine transformation from world coordinates to voxel coordinates.
        """
        return self.getAffine('world', 'voxel')

    @property
    def voxToWorldMat(self):
        """Returns a ``numpy`` array of shape ``(4, 4)`` containing an
        affine transformation from voxel coordinates to world coordinates.
        """
        return self.getAffine('voxel', 'world')

    @property
    def hdr_ext(self):
        '''Return MRS JSON header extension object.'''
        return self._hdr_ext

    def _save_hdr_ext(self):
        """Method to place Hdr_ext object into underlying Image object"""
        extension = nib.nifti1.Nifti1Extension(
            44,
            self._hdr_ext.to_json().encode('UTF-8'))
        self.header.extensions.clear()
        self.header.extensions.append(extension)

    @hdr_ext.setter
    def hdr_ext(self, new_hdr):
        '''Update MRS JSON header extension from python dict or Hdr_Ext object'''
        if isinstance(new_hdr, dict):
            validator.validate_hdr_ext(json.dumps(new_hdr), self.shape)
            self._hdr_ext = Hdr_Ext.from_header_ext(new_hdr)
        elif isinstance(new_hdr, Hdr_Ext):
            validator.validate_hdr_ext(new_hdr.to_json(), self.shape)
            self._hdr_ext = new_hdr
        else:
            raise TypeError('Passed header extension must be a dict or Hdr_Ext object')

        # Update the underlying Image object headers with new hdr extension
        self._save_hdr_ext()

    # Utility / legacy functions for hdr extension manipulation
    def add_hdr_field(self, key, value, doc=None):
        """Add a field to the header extension

        :param key: Field key
        :type key: str
        :param value: Value of field to add
        :param doc: Use to convey meaning of user-defined header value.
        :type doc: optional, str
        """
        dim_n = re.compile(r'dim_[567].*')
        if dim_n.match(key):
            raise ValueError('Modify dimension headers through dedicated methods.')

        new_hdr = self.hdr_ext
        if key in standard_defined:
            new_hdr.set_standard_def(key, value)
        else:
            if doc is None:
                raise ValueError('Please provide info about user defined value.')
            new_hdr.set_user_def(key=key, value=value, doc=doc)

        self.hdr_ext = new_hdr

    def remove_hdr_field(self, key):
        """Remove a field from the header extension

        :param key: Key to remove
        :type key: str
        """
        if key == 'SpectrometerFrequency' or key == 'ResonantNucleus':
            raise ValueError('You cannot remove the required metadata.')

        dim_n = re.compile(r'dim_[567].*')
        if dim_n.match(key):
            raise ValueError('Modify dimension headers through dedicated methods.')

        curr_hdr_ext = self.hdr_ext
        if key in standard_defined:
            curr_hdr_ext.remove_standard_def(key)
        else:
            curr_hdr_ext.remove_user_def(key)
        self.hdr_ext = curr_hdr_ext

    @property
    def filename(self):
        '''Name of file object was generated from.
        Returns empty string if N/A.'''
        if self._filename:
            return self._filename
        else:
            return ''

    @property
    def dim_tags(self):
        """Return the three higher dimension tags"""
        return self._read_dim_tags()

    def _read_dim_tags(self):
        """Read dim tags from current header extension"""
        dim_tags = [None, None, None]
        std_tags = ['DIM_COIL', 'DIM_DYN', 'DIM_INDIRECT_0']
        for idx in range(3):
            curr_dim = idx + 5
            curr_tag = f'dim_{curr_dim}'
            if curr_tag in self.hdr_ext:
                dim_tags[idx] = self.hdr_ext[curr_tag]
            elif curr_dim < self.ndim:
                dim_tags[idx] = std_tags[idx]
        return dim_tags

    def dim_position(self, dim_tag):
        '''Return position of dim if it exists.'''
        if dim_tag in self.dim_tags:
            return self._dim_tag_to_index(dim_tag)
        else:
            raise NIFTIMRS_DimDoesntExist(f"{dim_tag} doesn't exist in list of tags: {self.dim_tags}")

    def _dim_tag_to_index(self, dim):
        '''Convert DIM tag str or index (4, 5, 6) to numpy dimension index'''
        if isinstance(dim, str):
            if dim in self.dim_tags:
                dim = self.dim_tags.index(dim)
                dim += 4
            else:
                raise NIFTIMRS_DimDoesntExist(f"{dim} doesn't exist in list of tags: {self.dim_tags}")
        return dim

    def set_dim_tag(self, dim, tag, info=None, header=None):
        """Set or update the dim_N, dim_N_info, and dim_N_header fields

        Tag must be one of the standard-defined tags (e.g. DIM_DYN)

        :param dim: The existing dim tag or python dimension index (i.e. N-1)
        :type dim: str or int
        :param tag: New tag
        :type tag: str
        :param info: New info string
        :type info: str
        :param header: dict containing the dimension headers
        :type header: dict
        """
        if tag not in dimension_tags.keys():
            raise ValueError(f'Tag must be one of: {", ".join(list(dimension_tags.keys()))}.')

        dim = self._dim_tag_to_index(dim)

        if header is not None:
            # Check size
            def size_chk(obj):
                # Allow for expansion along the next dimension
                if dim == self.ndim:
                    dim_len = 1
                else:
                    dim_len = self.shape[dim]
                if len(obj) != dim_len:
                    raise ValueError(f'New dim header length must be {self.shape[dim]}')

            for key in header:
                if isinstance(header[key], list):
                    size_chk(header[key])
                elif isinstance(header[key], dict)\
                        and 'Value' in header[key]:
                    size_chk(header[key]['Value'])

        current_hdr_ext = self.hdr_ext
        current_hdr_ext.set_dim_info(dim - 4, tag, info=info, hdr=header)
        self.hdr_ext = current_hdr_ext

    def copy(self, remove_dim=None):
        """Return a copy of this image, optionally with a dimension removed.

        :param remove_dim: dimension index (4, 5, 6) or tag to remove. Takes first index. Defaults to None/no removal
        :type remove_dim: str or int, optional
        :return: Copy of object
        :rtype: NIFTI_MRS
        """
        if remove_dim:
            dim = self._dim_tag_to_index(remove_dim)
            reduced_data = self[:].take(0, axis=dim)
            new_hdr_ext = self.hdr_ext.copy()
            new_hdr_ext.remove_dim_info(dim - 4)
            new_hd = utils.modify_hdr_ext(
                new_hdr_ext,
                self.header)

            new_obj = NIFTI_MRS(reduced_data, header=new_hd)
            new_obj._filename = self.filename

            return new_obj
        else:
            return NIFTI_MRS(self[:], header=self.header)

    def save(self, filepath):
        """Save NIfTI-MRS to file

        :param filepath: Name and path of save loaction
        :type filepath: str or pathlib.Path
        """
        # Ensure final copy of header extension is loaded into Image object
        self._save_hdr_ext()

        # Run validation
        validator.validate_nifti_mrs(self.image)

        # Save underlying image object to file
        self.image.save(filepath)

    # Methods for iteration over dimensions
    def iterate_over_dims(self, dim=None, iterate_over_space=False, reduce_dim_index=False, voxel_index=None):
        """Return generator to iterate over all indices or one dimension (and FID).

        :param dim: None, dimension index (4, 5, 6) or tag. None iterates over all indices. Defaults to None
        :type dim: str or int, optional
        :param iterate_over_space: If True also iterate over spatial dimension, defaults to False
        :type iterate_over_space: bool, optional
        :param reduce_dim_index: If True the returned slice index will have the selected dimension removed.
            Defaults to False.
        :type reduce_dim_index: bool, optional
        :param voxel_index: slice or tuple of first three spatial dimensions., defaults to None
        :type voxel_index: slice or tuple, optional
        :return: yeildsarray of sliced data
        :rtype: np.array
        :return: data location slice object.
        :rtype: slice
        """

        data = self[:]
        dim = self._dim_tag_to_index(dim)

        # Convert indicies to slices to preserve singleton dimensions
        if voxel_index is not None:
            tmp = []
            for vi in voxel_index:
                if isinstance(vi, slice):
                    tmp.append(vi)
                elif isinstance(vi, int):
                    tmp.append(slice(vi, vi + 1))
                else:
                    raise TypeError('voxel index elements must be slice or int type.')
            voxel_index = tuple(tmp)

        def calc_slice_idx(idx):
            if iterate_over_space:
                slice_obj = list(idx[:3]) + [slice(None), ] + list(idx[3:])
            else:
                slice_obj = [slice(None), slice(None), slice(None), slice(None)]\
                    + list(idx[0:])
            if dim is not None and not reduce_dim_index:
                slice_obj.insert(dim + 1, slice(None))
            return tuple(slice_obj)

        if isinstance(dim, (int, str)):
            # Move FID dim to last
            data = np.moveaxis(data, 3, -1)
            dim -= 1
            # Move identified dim to last
            data = np.moveaxis(data, dim, -1)

            if voxel_index is not None:
                voxel_index
                data = data[voxel_index]

            if iterate_over_space:
                iteration_skip = -2
            else:
                data = np.moveaxis(data, (0, 1, 2), (-5, -4, -3))
                iteration_skip = -5

            for idx in np.ndindex(data.shape[:iteration_skip]):
                yield data[idx], calc_slice_idx(idx)

        elif dim is None:
            # Move FID dim to last
            data = np.moveaxis(data, 3, -1)

            if voxel_index is not None:
                data = data[voxel_index]

            if iterate_over_space:
                iteration_skip = -1
            else:
                data = np.moveaxis(data, (0, 1, 2), (-4, -3, -2))
                iteration_skip = -4

            for idx in np.ndindex(data.shape[:iteration_skip]):
                yield data[idx], calc_slice_idx(idx)

        else:
            raise TypeError('dim should be int or a string matching one of the dim tags.')

    def iterate_over_spatial(self):
        """Iterate over spatial voxels yeilding a data array the shape of the FID and any higher dimensions + index.

        :yield: Complex FID data with any higher dimensions. Index to data.
        :rtype: tuple
        """
        data = self[:]

        def calc_slice_idx(idx):
            slice_obj = list(idx[:3]) + [slice(None), ] * (data.ndim - 3)
            return tuple(slice_obj)

        for idx in np.ndindex(data.shape[:3]):
            yield self[idx], calc_slice_idx(idx)

    def dynamic_hdr_vals(self):
        """Return representations of the dynamic header values

        :return: List of dicts containing labelled header parameters
        :return: List of tuples containing header values
        :return: Flattened numpy array for each generated spectrum containing header values
        """
        def list_of_dict_from_dim(dim_hdr, size):
            """Form a list of dicts where each index of the list corresponds to one element"""
            out = []
            for idx in range(size):
                tmp_dict = {}
                for key in dim_hdr:
                    # Handle the non-standard case with an extra level
                    if 'Value' in dim_hdr[key]:
                        curr_val = dim_hdr[key]['Value']
                    else:
                        curr_val = dim_hdr[key]
                    # Handle the short form!
                    if 'increment' in curr_val:
                        start = curr_val['start']
                        inc = curr_val['increment']
                        tmp_dict.update({key: start + inc * idx})
                    else:
                        tmp_dict.update({key: curr_val[idx]})
                out.append(tmp_dict)
            return out

        def sort_output(hdr_list):
            if len(hdr_list) == 1:
                X = np.meshgrid(hdr_list[0])
                tvar = [x for x in X[0]]
            elif len(hdr_list) == 2:
                X, Y = np.meshgrid(hdr_list[0], hdr_list[1], indexing='ij')
                tvar = [dict(x, **y) for x, y in zip(X.ravel(), Y.ravel())]
            elif len(hdr_list) == 3:
                X, Y, Z = np.meshgrid(hdr_list[0], hdr_list[1], hdr_list[2], indexing='ij')
                tvar = [dict(x, **y, **z) for x, y, z in zip(X.ravel(), Y.ravel(), Z.ravel())]
            return tvar

        def convert_to_tuples(dict_list):
            out_list = []
            for dl in dict_list:
                tl = []
                for key in dl:
                    tl.append(dl[key])
                out_list.append(tuple(tl))
            return out_list

        all_dim_hdrs_dict = []
        for dim in range(5, 8):
            if f'dim_{dim}_header' in self.hdr_ext:
                all_dim_hdrs_dict.append(
                    list_of_dict_from_dim(self.hdr_ext[f'dim_{dim}_header'], self.shape[dim - 1]))

        tvar_dict = sort_output(all_dim_hdrs_dict)
        tvar_tuple = convert_to_tuples(tvar_dict)

        tvar_dict2 = np.asarray(tvar_dict, dtype=object).reshape(self.shape[4:])
        tvar_tuple2 = np.empty_like(tvar_dict2).flatten()
        for idx, elm in enumerate(tvar_tuple):
            tvar_tuple2[idx] = elm
        tvar_array = np.asarray(tvar_tuple, dtype=object).reshape(np.prod(self.shape[4:]), len(tvar_tuple[0]))

        return tvar_dict2, tvar_tuple2.reshape(self.shape[4:]), tvar_array
