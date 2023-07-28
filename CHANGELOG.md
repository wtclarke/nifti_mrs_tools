This document contains the nifti_mrs_tools release history in reverse chronological order.

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
- Added `--newaxis` option to `mrs_tools merge` allowing the user to merge files along a previously non-existant dimension (without using `reorder` first).

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