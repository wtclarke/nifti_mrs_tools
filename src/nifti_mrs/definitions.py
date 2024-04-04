'''Translate the JSON definitions of NIfTI-MRS standard meta data and dimension tags
to python usable formats.

Type fields should either be generic python types: float, int, str
or a tuple indicating an array type and element type : (list, float) or (list, str)

Copyright Will Clarke, University of Oxford, 2021
'''

import sys
import json
from typing import NamedTuple

version_info = sys.version_info
if sys.version_info.minor >= 10:
    from importlib.resources import files
else:
    # See https://setuptools.pypa.io/en/latest/userguide/datafiles.html#accessing-data-files-at-runtime
    from importlib_resources import files

data_text = files('nifti_mrs.standard').joinpath('definitions.json').read_text(encoding='utf-8')
json_def = json.loads(data_text)

# Carry out translation
nifti_mrs_version = [
    json_def['nifti_mrs_version']['major'],
    json_def['nifti_mrs_version']['minor']]

# Possible dimension tags and descriptions
dimension_tags = json_def['dimension_tags']

field_def = NamedTuple(
    "HeaderExtensionField",
    [('type', list), ('units', str), ('doc', str), ('anon', bool)])


def translate_definitions(obj):
    """Translate the JSON defined object to python dicts with python types
    """
    python_typed_dict = {}

    def translate_types(x, jkey):
        ptype = []
        for jtype in x:
            if jtype == 'array':
                ptype.append(list)
            elif jtype == 'number':
                ptype.append((float, int))
            elif jtype == 'bool':
                ptype.append(bool)
            elif jtype == 'string':
                ptype.append(str)
            elif jtype == 'object':
                ptype.append(dict)
            else:
                raise ValueError(f"Unknown type value {jtype} in JSON definition of {jkey}.")
        return tuple(ptype)

    for key in obj:
        python_typed_dict[key] = field_def(
            translate_types(obj[key]['type'], key),
            obj[key]['units'],
            obj[key]['doc'],
            obj[key]['anon']
        )
    return python_typed_dict


# Required metadata fields
required = translate_definitions(json_def['required'])

standard_defined = translate_definitions(json_def['standard_defined'])
