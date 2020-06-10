#!/usr/bin/env python

import nibabel as nb
from pathlib import Path

script_dir = Path(__file__).absolute()
lib_dir = script_dir.parent
root_dir = lib_dir.parent

def get_nifti_data(img_loc):
    """return matrix from nibabel loaded nifti
    Key arguments
        img_loc: Path or string of nifti image

    Returns:
        numpy array of the data
    """
    return nb.load(str(img_loc)).get_fdata()


def get_nifti_img_data(img_loc):
    """return nibabel img and matrix from nibabel loaded nifti
    Key arguments
        img_loc: Path or string of nifti image

    Returns:
        (nibabel img, numpy array of the data)
    """
    img = nb.load(str(img_loc))
    data = img.get_fdata()
    return img, data

