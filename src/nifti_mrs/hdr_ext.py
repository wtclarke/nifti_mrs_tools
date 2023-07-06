from .definitions import dimension_tags, standard_defined
import json


class Hdr_Ext:
    """Class to hold meta data stored in a NIfTI MRS header extension.
    Required fields must be passed to initialise,
    Default dimension information automatically generated, but may be modified by set_dim_info method.
    Standard defined meta-data and user-defined data can be added using set_standard_def and
    set_user_def respectively.
    """
    def __init__(self, spec_frequency, resonant_nucleus, dimensions=None):
        """Initialise NIfTI-MRS header extension object with the two mandatory bits of meta-data.

        Use the dimensions kwarg to initialise with the default dimension tags (DIM_COIL, DIM_DYN,
        DIM_INDIRECT_0) for values for 5, 6, and 7 respectively.

        :param spec_frequency: Spectrometer frequency in MHz
        :type spec_frequency: float
        :param resonant_nucleus: Resonant nucleus e.g. '1H'
        :type resonant_nucleus: str
        :param dimensions: Number of dimensions in image. Defaults to None
        :type dimensions: int, optional
        """
        if isinstance(spec_frequency, float):
            self.SpectrometerFrequency = [spec_frequency, ]
        elif isinstance(spec_frequency, (list, tuple))\
                and isinstance(spec_frequency[0], float):
            self.SpectrometerFrequency = spec_frequency
        else:
            raise ValueError('spec_frequency must be a float or array of floats.')

        if isinstance(resonant_nucleus, str):
            self.ResonantNucleus = [resonant_nucleus, ]
        elif isinstance(resonant_nucleus, (list, tuple))\
                and isinstance(resonant_nucleus[0], str):
            self.ResonantNucleus = resonant_nucleus
        else:
            raise ValueError('resonant_nucleus must be a string or array of strings.')

        # Standard tags definition
        standard_tags = [{"tag": "DIM_COIL", "info": None, "hdr": None},
                         {"tag": "DIM_DYN", "info": None, "hdr": None},
                         {"tag": "DIM_INDIRECT_0", "info": None, "hdr": None}]
        if dimensions is None or dimensions <= 4:
            self._dim_info = [{"tag": None, "info": None, "hdr": None}, ] * 3
        elif dimensions > 4 and dimensions <= 7:
            self._dim_info = [{"tag": None, "info": None, "hdr": None}, ] * 3
            dim_higher = dimensions - 4
            self._dim_info[:dim_higher] = standard_tags[:dim_higher]
        else:
            raise ValueError('dimensions kwarg must be None or an int from 4 to 7.')

        self._standard_data = {}
        self._user_data = {}

    @classmethod
    def from_header_ext(cls, hdr_ext_dict):
        """Create a Hdr_Ext object from a json string deserialised into a python dict

        :param hdr_ext_dict: header extension as a dict.
        :type hdr_ext_dict: dict
        :return: Class object
        :rtype: Hdr_Ext
        """
        optional_dict = dict(hdr_ext_dict)
        obj = cls(
            hdr_ext_dict['SpectrometerFrequency'],
            hdr_ext_dict['ResonantNucleus'])
        optional_dict.pop('SpectrometerFrequency')
        optional_dict.pop('ResonantNucleus')

        for idx in range(5, 8):
            if f'dim_{idx}' in hdr_ext_dict:
                tag = hdr_ext_dict[f'dim_{idx}']
                optional_dict.pop(f'dim_{idx}')
                if f'dim_{idx}_info' in hdr_ext_dict:
                    info = hdr_ext_dict[f'dim_{idx}_info']
                    optional_dict.pop(f'dim_{idx}_info')
                else:
                    info = None
                if f'dim_{idx}_header' in hdr_ext_dict:
                    hdr = hdr_ext_dict[f'dim_{idx}_header']
                    optional_dict.pop(f'dim_{idx}_header')
                else:
                    hdr = None
                obj.set_dim_info(idx - 5, tag, info=info, hdr=hdr)

        for key in optional_dict:
            if key in standard_defined:
                obj.set_standard_def(key, hdr_ext_dict[key])
            else:
                if 'Value' in hdr_ext_dict[key]\
                        and 'Description' in hdr_ext_dict[key]:
                    obj.set_user_def(
                        key,
                        hdr_ext_dict[key]['Value'],
                        hdr_ext_dict[key]['Description'])
                elif isinstance(hdr_ext_dict[key], dict)\
                        and 'Description' in hdr_ext_dict[key]:
                    obj.set_user_def(
                        key,
                        hdr_ext_dict[key],
                        hdr_ext_dict[key]['Description'])
                else:
                    raise ValueError(f'User-defined key {key} must contain a "Description" field"')

        return obj

    @property
    def ndim(self):
        """Returns the number of dimensions implied by the 'dim_{5,6,7}' tags"""
        ndim = 4
        for ddx in range(5, 8):
            if f'dim_{ddx}' in self.current_keys:
                ndim += 1
        return ndim

    def set_dim_info(self, dim, tag, info=None, hdr=None):
        """Set information associated with the optional, higher data dimensions.

        :param dim:  May be (0,1,2) or ("5th","6th","7th")
        :type dim: str or int
        :param tag: Must be one of the defined dimension tag strings. E.g. DIM_DYN
        :type tag: str
        :param info: Optional, free-form for documentation, defaults to None
        :type info: str, optional
        :param hdr: Dict containing relevant header value names and values. Defaults to None
        :type hdr: dict, optional
        """
        if tag not in dimension_tags:
            raise ValueError("tag must be one of the defined dimension tag.")

        new_info = {"tag": tag,
                    "info": info,
                    "hdr": hdr}

        if dim in (0, 1, 2):
            self._dim_info[dim] = new_info
        elif dim in ("5th", "6th", "7th"):
            if dim == "5th":
                self._dim_info[0] = new_info
            elif dim == "6th":
                self._dim_info[1] = new_info
            elif dim == "7th":
                self._dim_info[2] = new_info
        else:
            raise ValueError('dim must be 0,1,2 or "5th","6th","7th".')

    def remove_dim_info(self, dim):
        """Set a dimension's information to None

        :param dim: 0,1,2 or "5th","6th","7th"
        :type dim: str or int
        """
        if dim in (0, 1, 2):
            pass
        elif dim in ("5th", "6th", "7th"):
            if dim == "5th":
                dim = 0
            elif dim == "6th":
                dim = 1
            elif dim == "7th":
                dim = 2
        else:
            raise ValueError('dim must be 0,1,2 or "5th","6th","7th".')

        self._dim_info.pop(dim)
        self._dim_info.append({"tag": None, "info": None, "hdr": None})

    def set_standard_def(self, key, value):
        """Add a single standard-defined bit of meta-data to the object."""
        if key not in standard_defined:
            raise ValueError("key must be one of the standard-defined keys.")

        self._standard_data[key] = value

    def set_user_def(self, key, value, doc):
        """Add user-defined metadata keys to the header extension.
        add keys and values one at a time using key, value and doc.
        """

        if key in standard_defined:
            raise ValueError("key must not be one of the standard-defined keys.")

        if isinstance(value, dict):
            self._user_data[key] = value
            self._user_data[key].update({'Description': doc})
        else:
            self._user_data[key] = {
                'Value': value,
                'Description': doc}

    def remove_standard_def(self, key):
        """Remove key from list of standard defined key-value pairs

        :param key: Key name
        :type key: str
        """
        if key not in self.current_keys:
            raise KeyError(f'{key} is not defined in the header extension.')
        self._standard_data.pop(key)

    def remove_user_def(self, key):
        """Remove key from list of user defined key-value pairs

        :param key: Key name
        :type key: str
        """
        if key not in self.current_keys:
            raise KeyError(f'{key} is not defined in the header extension.')
        self._user_data.pop(key)

    def to_dict(self):
        """Generate dictionary representation from properties."""

        # Required meta-data
        out_dict = {'SpectrometerFrequency': self.SpectrometerFrequency,
                    'ResonantNucleus': self.ResonantNucleus}

        # Dimension information
        update_dict = {}
        for idx in range(5, 8):
            if self._dim_info[idx - 5]['tag'] is not None:
                update_dict[f'dim_{idx}'] = self._dim_info[idx - 5]['tag']
            if self._dim_info[idx - 5]['info'] is not None:
                update_dict[f'dim_{idx}_info'] = self._dim_info[idx - 5]['info']
            if self._dim_info[idx - 5]['hdr'] is not None:
                update_dict[f'dim_{idx}_header'] = self._dim_info[idx - 5]['hdr']
        out_dict.update(update_dict)

        # Add standard defined
        out_dict.update(self._standard_data)

        # Add user defined
        out_dict.update(self._user_data)

        return out_dict

    @property
    def current_keys(self):
        return self.to_dict().keys()

    def to_json(self):
        return json.dumps(self.to_dict())

    # For dict-like behaviour
    def __getitem__(self, key):
        return self.to_dict()[key]

    def __contains__(self, key):
        return key in self.to_dict()

    def __str__(self) -> str:
        return self.to_json()

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        yield from self.current_keys

    def copy(self):
        from copy import deepcopy
        return deepcopy(self)

    def __eq__(self, other):
        if isinstance(other, Hdr_Ext):
            return self.to_dict() == other.to_dict()
        elif isinstance(other, dict):
            return self.to_dict() == other
        else:
            raise NotImplementedError('Equality can only be tested with dict or Hdr_Ext object.')
