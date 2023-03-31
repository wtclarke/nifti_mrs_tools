# Python Tools for NIfTI-MRS

![PyPI](https://img.shields.io/pypi/v/nifti-mrs)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nifti-mrs)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7517423.svg)](https://doi.org/10.5281/zenodo.7517423)
![PyPI - License](https://img.shields.io/pypi/l/nifti-mrs)

This package contains python-based tools for representing, validating, and manipulating the [NIfTI-MRS format](https://github.com/wtclarke/mrs_nifti_standard/blob/master/specification.MD). [NIfTI-MRS](https://github.com/wtclarke/mrs_nifti_standard) is a standardised format for storing Magnetic Resonance Spectroscopy data. 

These tools are used extensively in the [spec2nii](https://github.com/wtclarke/spec2nii) format conversion program and the [FSL-MRS](fsl-mrs.com) analysis software. However, this library can also be used as a stand-alone set of tools.

If you use these tools please cite:
_Clarke, WT, Bell, TK, Emir, UE, et al. NIfTI-MRS: A standard data format for magnetic resonance spectroscopy. Magn Reson Med. 2022; 88: 2358- 2370. doi:[10.1002/mrm.29418](https://doi.org/10.1002/mrm.29418)_

## Installation
Installation is via [conda(-forge)]() or [Pypi](https://pypi.org/project/nifti-mrs/).

```conda install -c conda-forge nifti-mrs```

or

```pip install nifti-mrs```

Note this package is a requirement of _spec2nii_ (>v0.4.9) and _FSL-MRS_ (>v2.0.9) and will automatically be installed with them.

## Using the package
### Command-line tool - _mrs_tools_

MRS data stored in NIfTI-MRS format can contain multiple higher dimensions. For example it might contain dimensions encoding multiple receive coils, multiple temporal averages, or even a spectral editing dimension.

Data might need to be manipulated within the NIfTI-MRS storage framework before, after, or during preprocessing. For this, FLS-MRS provides the `mrs_tools` command line script. `mrs_tools` has the ability to merge and split NIfTI-MRS files along the higher encoding dimensions. It can also reorder the higher dimensions, or create a new singleton dimension for further manipulation.

`mrs_tools split` takes a single file and splits it along a specified dimension e.g. `--dim DIM_DYN`, at a single point (`--index 8`) or extracting multiple elements into a second file (`--indices 8 9 10`).

`mrs_tools merge` takes two or more files and merges them along a specified dimension e.g. `--dim DIM_EDIT`. Use `--newaxis` if that dimension doesn't exist in the files already.

`mrs_tools reorder` permutes the dimensions of an existing NIfTI-MRS file. For example, the 5th through 7th dimensions can be changed from `DIM_COIL, DIM_DYN, DIM_EDIT` to `DIM_DYN, DIM_EDIT, DIM_COIL` using `--dim_order DIM_DYN DIM_EDIT DIM_COIL`. Reorder can be used to add a tag to a singleton dimension.

`mrs_tools reshape` allows Numpy-style reshaping of the higher dimensions. For example if two editing conditions are interleaved you can reshape a file from (32, 128) to (32, 64, 2), and by specifying `-d6 DIM_DYN -d7 DIM_EDIT` you can tag the new dimensions appropriately.

`mrs_tools` also contains the `mrs_tools vis` and `mrs_tools info` options to provide quick visualisation and information on the command line. See the [FSL-MRS Visualisation documentation](https://open.win.ox.ac.uk/pages/fsl/fsl_mrs/visualisation.html#quick-glance) for more information on `mrs_tools vis/info`.

__Note: visualisation of NIfTI-MRS data using `mrs_tools` requires the installation of the [FSL-MRS package](fsl-mrs.com)__

### As a code library
The command-line tools presents an interface to the underlying code library. The library can be used directly in interactive or scripted python. For example:

```
from nifti_mrs.nifti_mrs import NIFTI_MRS
from nifti_mrs import tools

obj = NIFTI_MRS('path/to/data.nii.gz')

# Split the object at index 16 (1-16, 17-N) along the dynamics dimension
part_1, part_2 = tools.split(obj, 'DIM_DYN', 15)

# Save the first part
part_1.save('output/location/part_1.nii.gz')

```

See the [API documentation](https://wtclarke.github.io/nifti_mrs_tools/index.html) for details.

## Contributing and tests
Contributions to improve or extend these tools via pull requests are extremely welcome. Contributors, please take time to develop tests to continually validate new features or changes.

## Acknowledgements
### Contributors
William Clarke, University of Oxford  

### Funding acknowledgments
This work was funded by the Wellcome Trust [225924/Z/22/Z, 203139/Z/16/Z and 203139/A/16/Z].