``mrs_tools``
=============
**The command-line tool for manipulation of NIfTI-MRS files.**


:code:`usage: mrs_tools [-h] [-v] {info,vis,merge,split,reorder,conjugate} ...`

NIfTI-MRS (Magnetic Resonance Spectroscopy) tools

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

subcommands:
  Available tools

  {info, vis, merge, split, reorder, conjugate}



info
----
Information about the NIfTI-MRS file.

:code:`usage: mrs_tools info [-h] FILE or list of FILEs [FILE or list of FILEs ...]``

positional arguments:
  FILE or list of FILEs
                        NIfTI MRS file(s)

optional arguments:
  -h, --help            show this help message and exit


vis
---
Quick visualisation of a NIfTI-MRS file or FSL-MRS basis set.

:code:`usage: mrs_tools vis [-h] [--ppmlim LOW HIGH] [--mask MASK] [--save SAVE] [--display_dim DISPLAY_DIM] [--no_mean] FILE or DIR`

positional arguments:
  FILE or DIR           
                        NIfTI file or directory of basis sets

optional arguments:
  -h, --help             show this help message and exit
  --ppmlim LOW-HIGH      limit the fit to a freq range (default=(.2,4.2))
  --mask MASK            Mask for MRSI
  --save SAVE            Save fig to path
  --display_dim          DISPLAY_DIM. A NIFTI-MRS tag. Do not average across this dimension.
  --no_mean              Do not plot the mean signal line in the case of multiple spectra.


merge
-----
Merge NIfTI-MRS along higher dimensions.

:code:`usage: mrs_tools merge [-h] --files FILES [FILES ...] --dim DIM [--output OUTPUT][--filename FILENAME]`

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       output folder (defaults to current directory)
  --filename FILENAME   Override output file name.

required arguments:
  --files FILES [FILES ...]
                        List of files to merge

  --dim DIM             NIFTI-MRS dimension tag to merge across.


split
-----
Split NIfTI-MRS along higher dimensions.

:code:`usage: mrs_tools split [-h] --file FILE --dim DIM (--indices INDICES [INDICES ...] | --index INDEX) [--output OUTPUT] [--filename FILENAME]`

optional arguments:
  -h, --help            show this help message and exit

  --indices INDICES [INDICES ...]
                        List of indices to extract into second file. All indices are zero-indexed.

  --index INDEX         Index to split at (split after index, zero-indexed).
  --output OUTPUT       output folder (defaults to current directory)
  --filename FILENAME   Override output file names.

required arguments:
  --file FILE           File to split
  --dim DIM             NIFTI-MRS dimension tag to split across.

reorder
-------
Reorder higher dimensions of NIfTI-MRS.

:code:`usage: mrs_tools reorder [-h] --file FILE --dim_order DIM_ORDER [DIM_ORDER ...] [--output OUTPUT] [--filename FILENAME]`

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       output folder (defaults to current directory)
  --filename FILENAME   Override output file names.

required arguments:
  --file FILE           File to reorder

  --dim_order DIM_ORDER [DIM_ORDER ...]
                        NIFTI-MRS dimension tags in desired order. Enter as strings (min:1, max:3). Can create singleton dimension at end.

conjugate
---------
Conjugate data to correct phase/frequency convention in a NIfTI-MRS file.

:code:`usage: mrs_tools conjugate [-h] --file FILE [--output OUTPUT] [--filename FILENAME]`

optional arguments:
  -h, --help           show this help message and exit
  --output OUTPUT      output folder (defaults to current directory)
  --filename FILENAME  Override output file names.

required arguments:
  --file FILE          File to conjugate