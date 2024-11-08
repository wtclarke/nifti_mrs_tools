from pathlib import Path

import pytest

testsPath = Path(__file__).parent
test_data_raw = testsPath / 'test_data' / 'metab_raw.nii.gz'
test_data_proc = testsPath / 'test_data' / 'metab.nii.gz'


def test_vis_error(tmp_path):
    try:
        import fsl_mrs  # noqa: F401
    except ImportError:
        with pytest.raises(
                ImportError,
                match="mrs_tools vis requires FSL-MRS tools to be installed. "
                      "See fsl-mrs.com for installation instructions."):
            import nifti_mrs.vis   # noqa: F401
    else:
        pytest.skip("fsl-mrs present, skipping test")


@pytest.mark.with_fsl_mrs
def test_vis_svs(tmp_path):
    import nifti_mrs.vis as vis
    from nifti_mrs.nifti_mrs import NIFTI_MRS
    import matplotlib

    nmrs = NIFTI_MRS(test_data_raw)
    fig = vis.vis_nifti_mrs(nmrs)
    assert isinstance(fig, matplotlib.figure.Figure)

    nmrs = NIFTI_MRS(test_data_proc)
    fig = vis.vis_nifti_mrs(nmrs)
    assert isinstance(fig, matplotlib.figure.Figure)


@pytest.mark.with_fsl_mrs
def test_vis_svs_singleton_channels(tmp_path):
    import nifti_mrs.vis as vis
    from nifti_mrs.nifti_mrs import NIFTI_MRS
    import matplotlib

    nmrs = NIFTI_MRS(test_data_proc)
    nmrs.set_dim_tag(4, 'DIM_COIL')
    assert nmrs.shape[-1] == 1
    fig = vis.vis_nifti_mrs(nmrs)
    assert isinstance(fig, matplotlib.figure.Figure)
