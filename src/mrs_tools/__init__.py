""" mrs_tools - top level script for calling NIfTI-MRS handling tools

Author: William Clarke <william.clarke@ndcn.ox.ac.uk>

Copyright (C) William Clarke, 2023, University of Oxford
"""

import argparse
from pathlib import Path

from nifti_mrs import __version__


def main(import_args=None):
    # Parse command-line arguments
    p = argparse.ArgumentParser(description="NIfTI-MRS (Magnetic Resonance Spectroscopy) tools")

    p.add_argument('-v', '--version', action='version', version=__version__)

    sp = p.add_subparsers(title='subcommands',
                          description='Available tools',
                          required=True,
                          dest='subcommand')

    # Info tool
    infoparser = sp.add_parser(
        'info',
        help='Information about the NIfTI-MRS file.')
    infoparser.add_argument(
        'file',
        type=Path,
        metavar='FILE or list of FILEs',
        help='NIfTI MRS file(s)', nargs='+')
    infoparser.set_defaults(func=info)

    # Vis tool
    visparser = sp.add_parser(
        'vis',
        help='Quick visualisation of a NIfTI-MRS file or FSL-MRS basis set.')
    visparser.add_argument('file', type=Path, metavar='FILE or DIR',
                           help='NIfTI file or directory of basis sets')
    visparser.add_argument('--ppmlim', default=(.2, 4.2), type=float,
                           nargs=2, metavar=('LOW', 'HIGH'),
                           help='limit the fit to a freq range (default=(.2,4.2))')
    visparser.add_argument('--mask', default=None, type=str, help='Mask for MRSI')
    visparser.add_argument('--save', default=None, type=str, help='Save fig to path')
    visparser.add_argument('--display_dim', default=None, type=str,
                           help='NIFTI-MRS tag. Do not average across this dimension.')
    visparser.add_argument('--no_mean', action="store_false",
                           help='Do not plot the mean signal line in the case of multiple spectra.')
    visparser.set_defaults(func=vis)

    # Merge tool - Merge NIfTI MRS along higher dimensions
    mergeparser = sp.add_parser(
        'merge',
        help='Merge NIfTI-MRS along higher dimensions.')
    merge_req = mergeparser.add_argument_group('required arguments')
    merge_req.add_argument('--files', type=Path, nargs='+', required=True,
                           help='List of files to merge')
    merge_req.add_argument('--dim', type=str, required=True,
                           help='NIFTI-MRS dimension tag to merge across.')
    mergeparser.add_argument('--newaxis', action="store_true",
                             help='Join files along a new axis (tag specified by --dim).')
    mergeparser.add_argument('--output', type=Path, default=Path('.'),
                             help='output folder (defaults to current directory)')
    mergeparser.add_argument('--filename', type=str,
                             help='Override output file name.')
    mergeparser.set_defaults(func=merge)

    # Split tool
    splitparser = sp.add_parser(
        'split',
        help='Split NIfTI-MRS along higher dimensions.')
    split_req = splitparser.add_argument_group('required arguments')
    split_req.add_argument('--file', type=Path, required=True,
                           help='File to split')
    split_req.add_argument('--dim', type=str, required=True,
                           help='NIFTI-MRS dimension tag to split across.')
    group = splitparser.add_mutually_exclusive_group(required=True)
    group.add_argument('--indices', type=int, nargs='+',
                       help='List of indices to extract into second file.'
                            ' All indices are zero-indexed.')
    group.add_argument('--index', type=int,
                       help='Index to split at (split after index, zero-indexed).')
    splitparser.add_argument('--output',
                             required=False, type=Path, default=Path('.'),
                             help='output folder (defaults to current directory)')
    splitparser.add_argument('--filename', type=str,
                             help='Override output file names.')
    splitparser.set_defaults(func=split)

    # Reorder tool
    reorderparser = sp.add_parser(
        'reorder',
        help='Reorder higher dimensions of NIfTI-MRS.')
    reord_req = reorderparser.add_argument_group('required arguments')
    reord_req.add_argument('--file', type=Path, required=True,
                           help='File to reorder')
    reord_req.add_argument('--dim_order', type=str, nargs='+', required=True,
                           help='NIFTI-MRS dimension tags in desired order. '
                                'Enter as strings (min:1, max:3). '
                                'Can create singleton dimension at end.')
    reorderparser.add_argument('--output',
                               required=False, type=Path, default=Path('.'),
                               help='output folder (defaults to current directory)')
    reorderparser.add_argument('--filename', type=str,
                               help='Override output file names.')
    reorderparser.set_defaults(func=reorder)

    # Reshape tool
    reshapeparser = sp.add_parser(
        'reshape',
        help='Reorder higher dimensions of NIfTI-MRS.')
    resh_req = reshapeparser.add_argument_group('required arguments')
    resh_req.add_argument('--file', type=Path, required=True,
                          help='File to reshape')
    resh_req.add_argument('--shape', type=int, nargs='+', required=True,
                          help='Numpy-like target shape.'
                               'Enter as integers, -1 is used for any. '
                               'Only enter shape for higher (5th-7th) dimensions.')
    reshapeparser.add_argument('--d5',
                               required=False, type=str,
                               help='5th dimension tag (e.g. DIM_DYN).')
    reshapeparser.add_argument('--d6',
                               required=False, type=str,
                               help='6th dimension tag (e.g. DIM_DYN).')
    reshapeparser.add_argument('--d7',
                               required=False, type=str,
                               help='7th dimension tag (e.g. DIM_DYN).')
    reshapeparser.add_argument('--output',
                               required=False, type=Path, default=Path('.'),
                               help='output folder (defaults to current directory)')
    reshapeparser.add_argument('--filename', type=str,
                               help='Override output file names.')
    reshapeparser.set_defaults(func=reshape)

    # conjugate tool
    conjparser = sp.add_parser(
        'conjugate',
        help='Conjugate data to correct phase/frequency convention in a NIfTI-MRS file.')
    conj_req = conjparser.add_argument_group('required arguments')
    conj_req.add_argument('--file', type=Path, required=True,
                          help='File to conjugate')
    conjparser.add_argument('--output',
                            required=False, type=Path, default=Path('.'),
                            help='output folder (defaults to current directory)')
    conjparser.add_argument('--filename', type=str,
                            help='Override output file names.')
    conjparser.set_defaults(func=conj)

    # Parse command-line arguments
    args = p.parse_args(import_args)

    # Call function
    args.func(args)


def info(args):
    """Prints basic information about NIfTI-MRS files
    :param args: Argparse interpreted arguments
    :type args: Namespace
    """
    from nifti_mrs.nifti_mrs import NIFTI_MRS
    from mrs_tools.constants import GYRO_MAG_RATIO

    for file in args.file:
        data = NIFTI_MRS(file)

        print(f'\nRead file {file.name} ({file.parent.resolve()}).')
        print(f'NIfTI-MRS version {data.nifti_mrs_version}')
        print(f'Data shape {data.shape}')
        print(f'Dimension tags: {data.dim_tags}')

        print(f'Spectrometer Frequency: {data.spectrometer_frequency[0]} MHz')
        print(f'Dwelltime (Bandwidth): {data.dwelltime:0.3E}s ({data.bandwidth:0.0f} Hz)')
        print(f'Nucleus: {data.nucleus[0]}')
        if data.nucleus[0] in GYRO_MAG_RATIO:
            field_strength = data.spectrometer_frequency[0] / GYRO_MAG_RATIO[data.nucleus[0]]
            print(f'Field Strength: {field_strength:0.2f} T')
        print()


def vis(args):
    """Visualiser for NIfTI-MRS files

    Visualisation requires FSL-MRS to be installed.

    TO DO: Make fall-back visualisation.

    :param args: Argparse interpreted arguments
    :type args: Namespace
    """
    try:
        from fsl_mrs.utils.plotting import plot_spectrum, plot_spectra
        from fsl_mrs.utils.mrs_io import read_FID, read_basis
        from fsl_mrs.utils.mrs_io.main import FileNotRecognisedError
        import matplotlib.pyplot as plt
        from fsl_mrs.utils.preproc import nifti_mrs_proc
    except ImportError:
        raise ImportError(
            "mrs_tools vis requires FSL-MRS tools to be installed. "
            "See fsl-mrs.com for installation instructions.")

    import numpy as np
    import nibabel as nib

    # Single nifti file
    def vis_nifti_mrs(file):
        data = read_FID(file)
        if data.ndim > 4 \
                and 'DIM_COIL' in data.dim_tags\
                and args.display_dim != 'DIM_COIL':
            print('Performing coil combination')
            data = nifti_mrs_proc.coilcombine(data)

        if np.prod(data.shape[:3]) == 1:
            # SVS
            if args.display_dim:
                for dim in data.dim_tags:
                    if dim is None:
                        continue
                    if dim != args.display_dim:
                        print(f'Averaging {dim}')
                        data = nifti_mrs_proc.average(data, dim)
                fig = plot_spectra(data.mrs(), ppmlim=args.ppmlim, plot_avg=args.no_mean)

            else:
                while data.ndim > 4:
                    print(f'Averaging {data.dim_tags[0]}')
                    data = nifti_mrs_proc.average(data, data.dim_tags[0])
                fig = plot_spectrum(data.mrs(), ppmlim=args.ppmlim)

            if args.save is not None:
                fig.savefig(args.save)
            else:
                plt.show()

        else:
            while data.ndim > 4:
                print(f'Averaging {data.dim_tags[0]}')
                data = nifti_mrs_proc.average(data, data.dim_tags[0])

            mrsi = data.mrs()
            if args.mask is not None:
                mask_hdr = nib.load(args.mask)
                mask = np.asanyarray(mask_hdr.dataobj)
                if mask.ndim == 2:
                    mask = np.expand_dims(mask, 2)
                mrsi.set_mask(mask)
            mrsi.plot(ppmlim=args.ppmlim)

    # Some logic to figure out what we are dealing with
    p = args.file
    nifti_files = list(p.glob('*.nii*'))

    # Identify BASIS
    if (p.is_dir() and len(nifti_files) == 0)\
            or p.suffix.upper() == '.BASIS':

        # Some heuristics
        if p.is_dir():
            conj = True
        else:
            conj = False

        basis = read_basis(args.file)
        _ = basis.plot(ppmlim=args.ppmlim, conjugate=conj)
        if args.save is not None:
            plt.savefig(args.save)
        else:
            plt.show()

    # Identify directory of nifti files
    elif p.is_dir() and len(nifti_files) > 0:
        raise ValueError('mrs_tools vis should be called on a single'
                         ' NIFTI-MRS file, not a directory (unless'
                         ' it contains basis files).')

    elif p.is_file():
        vis_nifti_mrs(p)

    else:
        try:
            vis_nifti_mrs(p)
        except FileNotRecognisedError as exc:
            raise FileNotFoundError(
                f"No file or directory '{p}' found."
                " Please specify correct file extension (e.g. nii.gz) if there is one.")\
                from exc


def merge(args):
    """Merges one or more NIfTI-MRS files along a specified dimension
    :param args: Argparse interpreted arguments
    :type args: Namespace
    """
    import nifti_mrs.tools as nmrs_tools
    from nifti_mrs.nifti_mrs import NIFTI_MRS
    # 1. Load the files
    if len(args.files) < 2:
        raise ValueError('Files argument must provide two or more files to merge.')

    to_concat = []
    concat_names = []
    for fp in args.files:
        concat_names.append(fp.with_suffix('').with_suffix('').name)
        curr_file = NIFTI_MRS(fp)

        # Merging along a new axis
        if args.newaxis:
            if args.dim in curr_file.dim_tags:
                raise ValueError(f'--dim ({args.dim}) must be different from existing tags: {curr_file.dim_tags}.')
            if curr_file.ndim == 7:
                raise ValueError('Inputs use all three higher dimension already, cannot add new axis.')
            new_order = curr_file.dim_tags
            new_order[curr_file.ndim - 4] = args.dim
            curr_file = nmrs_tools.reorder(curr_file, new_order)
        to_concat.append(curr_file)

    # 2. Merge the files
    merged = nmrs_tools.merge(to_concat, args.dim)

    # 3. Save the output file
    if args.filename:
        file_out = args.output / args.filename
    else:
        file_out = args.output / ('_'.join(concat_names) + '_merged')
    merged.save(file_out)


def split(args):
    """Splits a NIfTI-MRS file into two along a specified dimension
    :param args: Argparse interpreted arguments
    :type args: Namespace
    """
    import nifti_mrs.tools as nmrs_tools
    from nifti_mrs.nifti_mrs import NIFTI_MRS
    # 1. Load the file
    to_split = NIFTI_MRS(args.file)
    split_name = args.file.with_suffix('').with_suffix('').name

    # 2. Merge the files
    if args.index is not None:
        split_1, split_2 = nmrs_tools.split(to_split, args.dim, args.index)
    elif args.indices:
        split_1, split_2 = nmrs_tools.split(to_split, args.dim, args.indices)

    # 3. Save the output file
    if args.index is not None:
        first_name = '_low'
        second_name = '_high'
    elif args.indices:
        first_name = '_others'
        second_name = '_selected'

    if args.filename:
        file_out_1 = args.output / (args.filename + first_name)
        file_out_2 = args.output / (args.filename + second_name)
    else:
        file_out_1 = args.output / (split_name + first_name)
        file_out_2 = args.output / (split_name + second_name)
    split_1.save(file_out_1)
    split_2.save(file_out_2)


def reorder(args):
    """Reorders the higher dimensions of a NIfTI-MRS file
    :param args: Argparse interpreted arguments
    :type args: Namespace
    """
    import nifti_mrs.tools as nmrs_tools
    from nifti_mrs.nifti_mrs import NIFTI_MRS
    # 1. Load the file
    to_reorder = NIFTI_MRS(args.file)
    reorder_name = args.file.with_suffix('').with_suffix('').name

    # 2. Reorder the files
    dim_order = args.dim_order
    while len(dim_order) < 3:
        dim_order.append(None)
    reordered = nmrs_tools.reorder(to_reorder, args.dim_order)

    # 3. Save the output file
    if args.filename:
        file_out = args.output / args.filename
    else:
        file_out = args.output / (reorder_name + '_reordered')
    reordered.save(file_out)


def reshape(args):
    """Reshapes the higher dimensions of a NIfTI-MRS file
    :param args: Argparse interpreted arguments
    :type args: Namespace
    """
    import nifti_mrs.tools as nmrs_tools
    from nifti_mrs.nifti_mrs import NIFTI_MRS
    # 1. Load the file
    to_reshape = NIFTI_MRS(args.file)
    reshape_name = args.file.with_suffix('').with_suffix('').name

    # 2. Reshape
    reshaped = nmrs_tools.reshape(
        to_reshape,
        tuple(args.shape),
        d5=args.d5,
        d6=args.d6,
        d7=args.d7)

    # 3. Save the output file
    if args.filename:
        file_out = args.output / args.filename
    else:
        file_out = args.output / (reshape_name + '_reshaped')
    reshaped.save(file_out)


def conj(args):
    """Conjugate the data in a nifti-mrs file

    :param args: Argparse interpreted arguments
    :type args: Namespace
    """
    import nifti_mrs.tools as nmrs_tools
    from nifti_mrs.nifti_mrs import NIFTI_MRS
    # 1. Load the file
    infile = NIFTI_MRS(args.file)
    name = args.file.with_suffix('').with_suffix('').name

    # 2. conjugate the file
    outfile = nmrs_tools.conjugate(infile)

    # 3. Save the output file
    if args.filename:
        file_out = args.output / args.filename
    else:
        file_out = args.output / name
    outfile.save(file_out)
