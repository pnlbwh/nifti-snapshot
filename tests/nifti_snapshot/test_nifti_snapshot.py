import os
import sys
from pathlib import Path

nifti_snapshot_paths = [x for x in sys.path if 'snapshot' in x]
for nifti_snapshot_path in nifti_snapshot_paths:
    sys.path.remove(nifti_snapshot_path)

SCRITS_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(SCRITS_ROOT))

import nifti_snapshot
print(nifti_snapshot.__file__)


from nifti_snapshot.nifti_snapshot import Figure, SimpleFigure, SimpleFigureGif
import nibabel as nb
import numpy as np
import imageio
import matplotlib.pyplot as plt



def test_basic():
    nifti_path = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ME97666/ses-202302011/dwi/sub-ME97666_ses-202302011_acq-176_dir-PA_run-1_dwi.nii.gz')
    img = nb.load(nifti_path)
    data = img.get_fdata()

        # image_files=[nifti_path],
    file_name_prefix = Path('test')
    n = 0

    filename_list = []
    for vol in range(data.shape[-1]):
        output_file = f'{file_name_prefix}_{vol:03d}.jpg'
        fig = SimpleFigure(
            image_data_list=[data],
            title=f'{nifti_path.name}: vol ({vol})',
            make_transparent_zero=True,
            cbar_width=0.5,
            cbar_title='Intensity',
            output_file=output_file,
            volumes=[vol],
        )
        filename_list.append(output_file)
        plt.close()
        n += 1
        if n == 5:
            break

    with imageio.get_writer('test.gif', mode='I', duration=0.1) as writer:
        for filename in filename_list:
            print(filename)
            image = imageio.imread(filename)
            writer.append_data(image)


def test_SimpleFigureGif():
    class SimpleFigureGif(Figure):
        def __init__(self, **kwargs):
            super(SimpleFigureGif, self).__init__()

            image_files = [Path(x) for x in kwargs.get('image_files', [])]
            image_data_list = [x for x in image_files]
            data_list = [nb.load(x).get_fdata() for x in image_data_list]
            file_name_prefix = kwargs.get('file_name_prefix',
                                          'test_fig_for_gif')

            filename_list = []
            for vol in range(0, data_list[0].shape[-1], 2):
                output_file = f'{file_name_prefix}_{vol:03d}.jpg'
                if Path(output_file).is_file():
                    continue

                _ = SimpleFigure(
                    image_data_list=data_list,
                    title=f'{file_name_prefix}: vol ({vol})',
                    make_transparent_zero=True,
                    cbar_width=0.5,
                    cbar_title='Intensity',
                    output_file=output_file,
                    volumes=[vol],
                    dpi=100
                )
                filename_list.append(output_file)
                plt.close()

            with imageio.get_writer(f'{file_name_prefix}.gif', mode='I', duration=0.1) as writer:
                for filename in filename_list:
                    image = imageio.imread(filename)
                    writer.append_data(image)

            # Clean-up frames
            for filename in filename_list:
                os.remove(filename)



    nifti_path = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ME97666/ses-202302011/dwi/sub-ME97666_ses-202302011_acq-176_dir-PA_run-1_dwi.nii.gz')
    _ = SimpleFigureGif(
        image_files=[nifti_path],
        file_name_prefix='hoho'
    )


def test_import():
    nifti_path = Path('/data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ME97666/ses-202302011/dwi/sub-ME97666_ses-202302011_acq-176_dir-PA_run-1_dwi.nii.gz')
    _ = SimpleFigureGif(
        image_files=[nifti_path],
        file_name_prefix='hoho'
    )
    



def hahah():
    dwi_dir = subject_dir / 'dwi'
    for nifti_path in dwi_dir.glob('*.nii.gz'):
        outname = nifti_path.name.split('.nii.gz')[0] + '.png'
        if not (outdir / outname).is_file():
            fig = nifti_snapshot.SimpleFigure(
                image_files = [nifti_path],
                title = nifti_path.name,
                make_transparent_zero = True,
                volumes=[0],
                cbar_width = 0.5,
                cbar_title = 'Intensity',
                output_file = outdir / outname,
            )

