#!/usr/bin/env python

import logging
import subprocess
import numpy as np
import pandas as pd
import nibabel as nb
from pathlib import Path
import matplotlib.colors as mcolors

logger = logging.getLogger(__name__)
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


def get_freesurfer_color_df(FREESURFER_HOME):
    """
    Retrieves the FreeSurfer color lookup table (LUT) as a DataFrame.

    Args:
        FREESURFER_HOME (str): The path to the FreeSurfer installation directory.

    Returns:
        pandas.DataFrame: The color lookup table as a DataFrame, with columns 'roi_num', 'label_name', 'R', 'G', 'B', 'A'.
    """

    with open(f'{FREESURFER_HOME}/FreeSurferColorLUT.txt', 'r') as fp:
        lines_list = [x.strip().split() for x in fp.readlines()]
        lines_list = [x for x in lines_list if len(x) == 6]

    df = pd.DataFrame(lines_list, columns=['roi_num', 'label_name', 'R', 'G', 'B', 'A'])
    df = df[~df.roi_num.str.contains('#')]
    df['roi_num'] = df['roi_num'].astype(int) 
    df['R'] = df['R'].astype(int) 
    df['G'] = df['G'].astype(int) 
    df['B'] = df['B'].astype(int) 
    # 75/76 removed. duplicates of 4/43
    df_tmp = df[df.roi_num == 4]
    df_tmp['roi_num'] = 75
    df = pd.concat([df, df_tmp], ignore_index=True)

    df_tmp = df[df.roi_num == 43]
    df_tmp['roi_num'] = 76
    df = pd.concat([df, df_tmp], ignore_index=True)

    return df


def get_cmap_wmparc(FREESURFER_HOME):
    df = get_freesurfer_color_df(FREESURFER_HOME)
    digit_colors = dict(zip(df['roi_num'].astype(int),
                         zip(df['R'].astype(int)/255, df['G'].astype(int)/255, df['B'].astype(int)/255)))

    # Initialize an empty list to store colors
    roi_colors = []

    # Loop through each row in digits array
    for roi_num in df.roi_num.unique():
        roi_colors.append(digit_colors[int(roi_num)])
    cmap = mcolors.ListedColormap(roi_colors)

    return cmap


def rotate_fs_created_nii(data: nb.Nifti1Image):
    return np.rot90(data, 1, (2,1))


def convert_mgz_to_nii(input, output, FREESURFER_HOME):
    fs_activate = f'{FREESURFER_HOME}/activate.sh'
    mri_convert_loc = f'{FREESURFER_HOME}/bin/mri_convert'
    command = f'source {fs_activate} && {mri_convert_loc} {input} {output}'
    subprocess.run(command, shell=True, executable='/bin/bash')


def get_filename_path_dict_from_fs_outdir(fs_outdir) -> dict:
    fs_outdir = Path(fs_outdir)
    if not fs_outdir.is_dir():
        logger.warning(f'No {fs_outdir}')
        return {}
    mri_dir = fs_outdir / 'mri'
    files_under_mri_dir = mri_dir.glob('*')

    filename_path_dict = {}
    for file_path in files_under_mri_dir:
        filename_path_dict[file_path.name.split('.')[0]] = file_path

    return filename_path_dict