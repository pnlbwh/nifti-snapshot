from pathlib import Path
import sys
script_dir = Path(__file__).absolute().parent.parent / 'nifti_snapshot'
sys.path.append(str(script_dir))
from nifti_snapshot import Enigma, Fsl
from nifti_snapshot import TbssFigure
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
        output_file='prac.png',
        title='prac')
    tbssFigure.create_figure_one_map()

