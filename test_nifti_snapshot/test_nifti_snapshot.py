from pathlib import Path
import sys
script_dir = Path(__file__).absolute().parent.parent / 'nifti_snapshot'
sys.path.append(str(script_dir))
from nifti_snapshot import Enigma, Fsl
from nifti_snapshot import TbssFigure, SimpleFigure
import nibabel as nb
import pytest


@pytest.fixture
def enigma():
    p = Enigma()
    return p

def test_enigma_path_fa_loc(enigma):
    assert enigma.template_fa_loc.is_file()

def test_enigma_path_fa_skel_loc(enigma):
    assert enigma.template_skeleton_loc.is_file()

@pytest.fixture
def fsl():
    p = Fsl()
    return p

def test_fsl_path_fa_loc(fsl):
    assert fsl.template_fa_loc.is_file()

def test_fsl_path_fa_skel_loc(fsl):
    assert fsl.template_skeleton_loc.is_file()


def test_tbss_figure():
    tbssFigure = TbssFigure(
        template='enigma',
        image_files=['data/tbss_FA_tfce_corrp_tstat1_filled.nii.gz'],
        output_file='tbss_figure.png',
        title='prac',
        dpi=50)
    tbssFigure.create_figure_one_map()

def test_tbss_figure_vmin():
    tbssFigure = TbssFigure(
        template='enigma',
        image_files=['data/tbss_FA_tfce_corrp_tstat1_filled.nii.gz'],
        output_file='tbss_figure_vmin.png',
        title='prac',
        dpi=50)
    tbssFigure.create_figure_one_map()

def test_tbss_figure_with_data():
    data = nb.load('data/tbss_FA_tfce_corrp_tstat1_filled.nii.gz').get_fdata()
    tbssFigure = TbssFigure(
        template='enigma',
        image_data_list=[data],
        output_file='tbss_figure_direct_data_input.png',
        title='prac',
        dpi=50)
    tbssFigure.create_figure_one_map()

def test_simple_figure():
    simpleFigure = SimpleFigure(
        image_files=['data/tbss_FA_tfce_corrp_tstat1_filled.nii.gz'],
        output_file='simple_figure.png',
        title='figure',
        dpi=50)

def test_simple_figure_with_data():
    data = nb.load('data/tbss_FA_tfce_corrp_tstat1_filled.nii.gz').get_fdata()
    simpleFigure = SimpleFigure(
        image_data_list=[data],
        output_file='simple_figure_direct_data_input.png',
        title='figure',
        dpi=50)
