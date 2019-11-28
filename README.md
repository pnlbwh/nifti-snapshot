# nifti-snapshot
Tools used to summarize Nifti files into figures

```py
git clone https://github.com/pnlbwh/nifti-snapshot
```


## Contents

- Dependencies
- TBSS figures


## Dependencies

```py
python 3.7
scipy==1.3.3
nibabel==2.4.0
numpy==1.16.2
pathlib2==2.3.3
matplotlib==3.0.3
```


## TBSS figures

```py
from nifti_snapshot import nifti_snapshot
```


### Snapshot of an `tbss_fill`ed image

```py
fw = 'tbss_FA_tfce_corrp_tstat1_filled.nii.gz'
fw_color = 'Blues_r'

tbssFigure = nifti_snapshot.TbssFigure(
        image_files=[fw],
        output_file='docs/fw_example.png',
        cmap_list=[fw_color],
        cbar_titles=['Increased FW'],
        alpha_list=[0.8],
        title='Increased Freewater in group A',
        cbar_x=0.35, cbar_width=0.3)
tbssFigure.create_figure_one_map()
```


![output](docs/fw_example.png)


### Snapshot of two `tbss_fill`ed images with overlap highlight


```py
fa = 'tbss_FA_tfce_corrp_tstat1_filled.nii.gz'
fat = 'tbss_FAt_tfce_corrp_tstat1_filled.nii.gz'

fa_color_1 = 'Blues_r'
fa_color_2 = 'autumn'
fa_color_overlap = 'summer'

tbssFigure = nifti_snapshot.TbssFigure(
    image_files=[fa, fat],
    output_file='docs/fa_fat_example.png',
    cmap_list=[fa_color_1, fa_color_2],
    overlap_cmap=fa_color_overlap,
    cbar_titles=[
        'Reduced FA',
        'Reduced FAt',
        'Overlap'],
    alpha_list=[1, 1, 0.8],
    title='Significant changes in FA and FAt in group A')
tbssFigure.create_figure_two_maps_and_overlap()
```

![output](docs/fa_fat_example.png)
