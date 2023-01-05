from .definitions import dimension_tags, standard_defined
import json


class Hdr_Ext:
    """Class to hold meta data stored in a NIfTI MRS header extension.
    Required fields must be passed to initialise,
    Default dimension information automatically generated, but may be modified by set_dim_info method.
    Standard defined meta-data and user-defined data can be added using set_standard_def and
    set_user_def respectively.
    """
    def __init__(self, spec_frequency, resonant_nucleus, dimensions=7):
        """Initialise class object with the two required bits of meta-data
        Set default dimension information.
        Inputs:
            spec_frequency: Spectrometer frequency in MHz,
            resonant_nucleus: Resonant nucleus string e.g. '1H'
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

        self._dim_info = [{"tag": "DIM_COIL", "info": None, "hdr": None},
                          {"tag": "DIM_DYN", "info": None, "hdr": None},
                          {"tag": "DIM_INDIRECT_0", "info": None, "hdr": None}]

        self._standard_data = {}
        self._user_data = {}
        self.dimensions = dimensions

    @classmethod
    def from_header_ext(cls, hdr_ext_dict, dimensions=7):

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
                obj.set_user_def(key=key, value=hdr_ext_dict[key])

        obj.dimensions = dimensions

        return obj

    def set_dim_info(self, dim, tag, info=None, hdr=None):
        """Set information associated with the optional data dimensions.
        Inputs:
            dim: May be (0,1,2) or ("5th","6th","7th")
            tag: Must be one of the defined dimension tag strings.
            info: Optional, free-form use string.
            hdr: Dict containing relevant header value names and values.
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

    def set_user_def(self, all_keys=None, key=None, value=None, doc=None):
        """Add user defined meta data keys to the header extension.
        Pass dict as kwarg all_keys to set all key/value pairs, or
        add keys and values one at a time using key, value and doc.
        """

        if all_keys is not None:
            self._user_data = all_keys
        else:
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
        """Generate dictionay representation from properties."""

        # Required meta-data
        out_dict = {'SpectrometerFrequency': self.SpectrometerFrequency,
                    'ResonantNucleus': self.ResonantNucleus}

        # Dimension information
        if self.dimensions < 4:
            raise ValueError('dimensions must be 4 or greater')
        elif self.dimensions == 4:
            pass
        else:
            update_dict = {}
            for idx in range(5, self.dimensions + 1):
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
