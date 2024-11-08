try:
    from fsl_mrs.utils.plotting import plot_spectrum, plot_spectra
    from fsl_mrs.core.mrs import MRS
    from fsl_mrs.core.mrsi import MRSI
    from fsl_mrs.utils.preproc import nifti_mrs_proc
    from fsl_mrs.utils import constants
except ImportError:
    raise ImportError(
        "NIfTI-MRS visualisation requires FSL-MRS tools to be installed. "
        "See fsl-mrs.com for installation instructions.")

import numpy as np
import nibabel as nib


def vis_nifti_mrs(data, display_dim=None, ppmlim=None, plot_avg=False, mask=None, legend=True):

    if ppmlim is None:
        nuc_info = constants.nucleus_constants(data.nucleus[0])
        if nuc_info.ppm_range:
            ppmlim = nuc_info.ppm_range
        else:
            ppmlim = (None, None)

    if data.ndim > 4 \
            and 'DIM_COIL' in data.dim_tags\
            and display_dim != 'DIM_COIL'\
            and data.shape[4+data.dim_tags.index('DIM_COIL')]>1:
        print('Performing coil combination')
        data = nifti_mrs_proc.coilcombine(data)

    def handle_dim_if_multiple(dd, dim):
        """Handles a dimension if non-singleton"""
        if dim is None:
            # Protect against loss of dimension during process.
            return dd
        if dd.shape[dd.dim_position(dim)] > 1\
                and dim in ('DIM_EDIT', 'DIM_METCYCLE', 'DIM_ISIS'):
            print(f'Subtracting {dim}')
            return nifti_mrs_proc.subtract(dd, dim=dim)
        elif dd.shape[dd.dim_position(dim)] > 1:
            print(f'Averaging {dim}')
            return nifti_mrs_proc.average(dd, dim)
        else:
            return dd

    if np.prod(data.shape[:3]) == 1:
        # SVS
        if display_dim:
            for dim in data.dim_tags:
                if dim is None:
                    continue
                if dim != display_dim:
                    data = handle_dim_if_multiple(data, dim)
            mrs = []
            for fid, _ in data.iterate_over_dims():
                mrs.append(
                    MRS(
                        fid.squeeze(),
                        bw=data.bandwidth,
                        cf=data.spectrometer_frequency[0],
                        nucleus=data.nucleus[0]))
            fig = plot_spectra(mrs, ppmlim=ppmlim, plot_avg=plot_avg, legend=legend)

        else:
            for dim in data.dim_tags:
                data = handle_dim_if_multiple(data, dim)
            mrs = MRS(
                data[:].squeeze(),
                bw=data.bandwidth,
                cf=data.spectrometer_frequency[0],
                nucleus=data.nucleus[0])
            fig = plot_spectrum(mrs, ppmlim=ppmlim)

        return fig

    else:
        for dim in data.dim_tags:
            data = handle_dim_if_multiple(data, dim)

        mrsi = MRSI(
            data[:],
            bw=data.bandwidth,
            cf=data.spectrometer_frequency[0],
            nucleus=data.nucleus[0])

        if mask is not None:
            mask_hdr = nib.load(mask)
            mask = np.asanyarray(mask_hdr.dataobj)
            if mask.ndim == 2:
                mask = np.expand_dims(mask, 2)
            mrsi.set_mask(mask)
        mrsi.plot(ppmlim=ppmlim)
