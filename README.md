# nifti-snapshot
Tools used to summarize Nifti files into figures

## Contents

- TBSS figures


## TBSS figures

```py
# example
fw = 'tbss_FA_tfce_corrp_tstat1_filled.nii.gz'
fw_color = 'Blues_r'

# SLE FW only
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

