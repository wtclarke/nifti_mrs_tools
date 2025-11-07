This document contains the nifti_mrs_tools release history in reverse chronological order.

1.3.4 (Friday 7th November 2025)
-----------------------------------
- Improved behaviour around removing dimensions when copying NIfTI-MRS objects. Thanks to @mbrammerloh.
- Dropped support for python 3.9, added support and testing for 3.14
- Handle files with integer spectrometer frequency.

1.3.3 (Friday 8th November 2024)
-----------------------------------
- Handle different time units in nifti header for dwelltime (with thanks to @Septem).
- Handle singleton coil dimensions with `mrs_tools vis`  (with thanks to @Septem).

1.3.2 (Wednesday 23rd October 2024)
-----------------------------------
- Better visualisation using `mrs_tools vis` for data containing ISIS, metabolite cycling or editing.
- Dimension tags can now be set to `None` to remove trailing singleton dimension.

1.3.1 (Monday 21st October 2024)
--------------------------------
- Drop support for python 3.8. Testing extended to python 3.12 and 3.13.
- Fix compatibility issue with nibabel > 5.3

1.3.0 (Wednesday 26th June 2024)
--------------------------------
- Added `--full-hdr` argumet to `mrs_tools info` which enables printing of the full header extension.
- Improved NIfTI-MRS object inspection in python interface.
- Added `.plot()` method to `NIFTI_MRS` objects. This matches the behaviour of `mrs_tools vis`.
- Update definitions to NIfTI-MRS V0.10

1.2.1 (Thursday 4th April 2024)
-------------------------------
- Removed unnecessary file accidentally included in distribution. PR#25. Thanks to Ben Beasley.
- Fixed encoding error bug on import when using FSL-MRS. PR#26. Thanks to Donnie Cameron.

1.2.0 (Monday 1st April 2024)
-----------------------------
- When reading files any user defined parameters without a description will print a warning to the user and generate an empty description key.
- The package now automatically includes the machine-readable JSON formatted definitions file from V0.9 of the [official standard](https://github.com/wtclarke/mrs_nifti_standard).
- Better handling of numbers as either `floats` or `ints` to allow for variable implementations of JSON libraries across packages.

1.1.1 (Wednesday 6th December 2023)
-----------------------------------
- Validator checks consistency of any `SpectraWidth` header extension value with the dwell time in `pixdim[4]`.

1.1.0 (Wednesday 6th December 2023)
-----------------------------------
- Update definitions to NIfTI-MRS V0.8
- Fixes issue with displaying spectra with a singleton dimension
- Code spelling changes.

1.0.2 (Friday 28th July 2023)
-----------------------------
- Bugfix release for NIfTI-MRS header extension validator.

1.0.1 (Friday 28th July 2023)
-----------------------------
- Ensure that the xyzt_units header is correctly set to (mm, s).
- Validation on creation of a NIfTI-MRS object can now be turned off.
- Python 3.7 now in [end of life](https://devguide.python.org/versions/) status and is no longer supported.

1.0.0 (Friday 7th July 2023)
----------------------------
- Major version increment due to breaking API changes.
- Under the hood rework of the validator and how the main classes handle dimensionality.
- Reordering should better handle dim_N_header fields.
- Validation is now much stricter.

0.1.7 (Friday 31st March 2023)
--------------------------------
- Added `--newaxis` option to `mrs_tools merge` allowing the user to merge files along a previously non-existent dimension (without using `reorder` first).

0.1.6 (Thursday 30th March 2023)
--------------------------------
- Fixed `mrs_tools reshape` option to allow Numpy-style reshaping of higher dimensions.

0.1.5 (Wednesday 22nd March 2023)
---------------------------------
- Fixed `mrs_tools vis` with `--display_dim` option as the last dimension
- Fixed `mrs_tools vis` ppm limit not being applied to MRSI code.

0.1.4 (Tuesday 17th January 2023)
---------------------------------
- Fixed a bug in NIFTI_MRS.copy() when reducing dimensionality
- Fixed type of ProcessingApplied key in definitions
- Fixed bug in hdr_ext dimensions when creating NIFTI_MRS from NIFTI_MRS
- Added utility members to NIFTI_MRS class

0.1.3 (Tuesday 17th January 2023)
---------------------------------
- Increment definitions to match standard V0.7
- Typos in definitions

0.1.2 (Thursday 12th January 2023)
----------------------------------
- Add option to prevent conjugation with numpy data. For spec2nii compatibility.

0.1.1 (Wednesday 11th January 2023)
-----------------------------------
- Make compliant with NIfTI-MRS V0.6

0.1.0 (Monday 9th January 2023)
-------------------------------
- First full release
- Update README
- Generate DOI

0.0.8 (Monday 9th January 2023)
-------------------------------
- Manual documentation build in CI. 

0.0.7 (Monday 9th January 2023)
-------------------------------
- Manual documentation build in CI. 

0.0.5 (Monday 9th January 2023)
-------------------------------
- Update CI for publication 

0.0.4 (Monday 9th January 2023)
-------------------------------
- Update CI publication CI

0.0.3 (Monday 9th January 2023)
-------------------------------
- Added API documentation
- Updated README

0.0.2 (Friday 6th January 2023)
-------------------------------
- Tweaked publishing metadata.

0.0.1 (Friday 6th January 2023)
-------------------------------
- Initial release