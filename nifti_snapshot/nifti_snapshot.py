#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import nibabel as nb
from scipy import ndimage
import os
import functools

class Enigma:
    # @functools.cached_property
    def __init__(self):
        self.enigma_dir = Path(os.environ['ENIGMA_dir'])
        self.enigma_fa_loc = self.enigma_dir / 'ENIGMA_DTI_FA.nii.gz'
        self.enigma_fa_data = nb.load(str(self.enigma_fa_loc)).get_data()
        self.enigma_skeleton_mask_loc = self.enigma_dir / \
            'ENIGMA_DTI_FA_skeleton_mask.nii.gz'
        self.enigma_skeleton_data = nb.load(
            str(self.enigma_skeleton_mask_loc)).get_data()

class Fsl:
    def __init__(self):
        self.fsldir = os.environ['FSLDIR']
        self.fmrib_fa_loc = Path(self.fsldir) / \
            'data/standard/FMRIB58_FA_1mm.nii.gz'
        self.fmrib_fa_data = nb.load(str(self.fmrib_fa_loc)).get_data()

        self.fmrib_skeleton_loc = Path(self.fsldir) / \
            'data/standard/FMRIB58_FA-skeleton_1mm.nii.gz'
        self.fmrib_skeleton_data = nb.load(
            str(self.fmrib_skeleton_loc)).get_data()

class FigureSettings:
    def __init__(self):
        self.ncols = 5
        self.nrows = 4
        self.nslice = self.ncols * self.nrows
        self.size_w = 4
        self.size_h = 4
        self.slice_gap = 3
        self.dpi = 200

    def get_cbar_horizontal_info(self):
        self.cbar_x = 0.25
        self.cbar_y = 0.03
        self.cbar_height = 0.03
        self.cbar_width = 0.15

    def add_cbars_horizontal(self):
        self.cbar_x_steps = 0.2

        for num, image_data in enumerate(self.image_data_list):
            # x, y, width, height
            cbar_title = self.cbar_titles[num]
            axbar = self.fig.add_axes([
                self.cbar_x,
                self.cbar_y,
                self.cbar_width,
                self.cbar_height])

            if cbar_title.lower() != 'overlap':
                cb = self.fig.colorbar(
                        self.imshow_list[num],
                        axbar,
                        orientation='horizontal',
                        ticks=[0, 1])

                cb.ax.set_xticklabels(['P = 0.05', 'P < 0.01'], color='white')
            else:
                cb = self.fig.colorbar(
                        self.imshow_list[num],
                        axbar,
                        orientation='horizontal',
                        boundaries=[0.999, 1],
                        ticks=[])

            cb.outline.set_edgecolor('white')
            cb.ax.set_title(
                    cbar_title,
                    fontsize=15, fontweight='bold', color='white')
            cb.ax.yaxis.set_label_position('left')
            self.cbar_x += self.cbar_x_steps


class FigureNifti:
    def get_slice(self, data, z_num):
        return np.flipud(data[:, :, z_num].T)

    def transparent_mask(self, mask_data):
        mask_data = np.where(mask_data < 1, np.nan, mask_data)
        return mask_data

    def transparent_zero(self, data):
        data = np.where(data == 0, np.nan, data)
        return data

    def transparent_threshold(self, data, threshold):
        with np.errstate(invalid='ignore'):
            data = np.where(data < threshold, np.nan, data)
        return data

    def transparent_out_the_skeleton(self, data):
        data = np.where(self.enigma_skeleton_data == 1, data, np.nan)
        return data

    def get_center(self, data):
        # Get the center of data
        # slices below z=40 have been zeroed in order to move the
        # center_of_data upwards for better visualization
        data_zeroed_below = data.copy()
        data_zeroed_below[:, :, :40] = 0
        self.center_of_data = np.array(
            ndimage.measurements.center_of_mass(data_zeroed_below)).astype(int)

        # Get the center slice number
        self.z_slice_center = self.center_of_data[-1]
        self.get_slice_nums()

    def get_slice_nums(self):
        self.slice_nums = np.arange(
            self.z_slice_center - (self.nslice * self.slice_gap),
            self.z_slice_center + (self.nslice * self.slice_gap),
            self.slice_gap)[::2]

    def annotate_with_z(self):
        for num, ax in enumerate(np.ravel(self.axes)):
            ax.annotate(
                f'z = {self.slice_nums[num]}',
                (0.01, 0.1),
                xycoords='axes fraction',
                color='white')

    def get_overlap_between_maps(self):
        self.overlap_map = np.where(
                (self.image_data_list[0] > 0) * (self.image_data_list[1] > 0),
                1-self.image_data_list[0],
                np.nan)
        # self.overlap_map = np.where(
                # (self.image_data_list[0] > 0) * (self.image_data_list[1] > 0),
                # 1,
                # np.nan)

        self.image_data_list.append(self.overlap_map)


class Figure(FigureSettings, FigureNifti):
    def __init__(self, **kwargs):
        Enigma.__init__(self)
        # Fsl.__init__(self)
        FigureSettings.__init__(self)

        self.get_cbar_horizontal_info()
        print('Given parameters')
        for key, value in kwargs.items():
            print(f"\t{key} : {value}")
            setattr(self, key, value)

        # create fig and axes
        self.fig, self.axes = plt.subplots(
            ncols=self.ncols,
            nrows=self.nrows,
            figsize=(self.size_w * self.ncols,
                     self.size_h * self.nrows),
            dpi=self.dpi)

        # figure settings
        self.fig.subplots_adjust(hspace=0, wspace=0)
        plt.style.use('dark_background')

    def read_data(self):
        # load background data
        if hasattr(self, 'background_files'):
            self.background_data_list = [nb.load(x).get_data() for x
                                         in self.background_files]

        # load foreground ata
        self.image_data_list = [nb.load(x).get_data() for x
                                in self.image_files]

    def images_mask_out_the_skeleton(self):
        new_images = []
        for image in self.image_data_list:
            new_image = self.transparent_out_the_skeleton(image)
            new_images.append(new_image)
        self.image_data_list = new_images

    def images_mask_out_the_zero(self):
        new_images = []
        for image in self.image_data_list:
            new_image = self.transparent_zero(image)
            new_images.append(new_image)
        self.image_data_list = new_images

    def images_mask_by_threshold(self, threshold):
        new_images = []
        for image in self.image_data_list:
            new_image = self.transparent_threshold(image, threshold)
            new_images.append(new_image)
        self.image_data_list = new_images

    def image_mask_out_the_skeleton(self):
        self.image_data = self.transparent_out_the_skeleton(self.image_data)

    def loop_through_axes_draw_bg(self):
        for num, ax in enumerate(np.ravel(self.axes)):
            z_num = self.slice_nums[num]
            enigma_fa_d = self.get_slice(self.enigma_fa_data, z_num)
            enigma_skeleton_d = self.get_slice(
                    self.enigma_skeleton_data,
                    z_num)

            # background FA map
            img = ax.imshow(
                    enigma_fa_d,
                    cmap='gray')

            # background skeleton
            img = ax.imshow(
                    enigma_skeleton_d,
                    interpolation=None, cmap='ocean')
            ax.axis('off')

    def loop_through_axes_draw_images_corrp_map(self, threshold):
        for num, ax in enumerate(np.ravel(self.axes)):
            z_num = self.slice_nums[num]

            # background FA map
            self.imshow_list = []
            for img_num, image in enumerate(self.image_data_list):
                alpha = self.alpha_list[img_num]
                image_d = self.get_slice(image, z_num)
                img = ax.imshow(
                        image_d,
                        cmap=self.cmap_list[img_num],
                        vmin=threshold,
                        vmax=1, alpha=alpha)
                self.imshow_list.append(img)

    def loop_through_axes_draw_images(self):
        for num, ax in enumerate(np.ravel(self.axes)):
            z_num = self.slice_nums[num]

            # background FA map
            self.imshow_list = []
            for img_num, image in enumerate(self.image_data_list):
                alpha = self.alpha_list[img_num]
                image_d = self.get_slice(image, z_num)
                img = ax.imshow(
                        image_d,
                        cmap=self.cmap_list[img_num],
                        vmin=0,
                        vmax=1, alpha=alpha)
                self.imshow_list.append(img)

    def loop_through_axes_draw_overlap(self):
        image = self.image_data_list[-1]
        alpha = self.alpha_list[-1]
        for num, ax in enumerate(np.ravel(self.axes)):
            z_num = self.slice_nums[num]

            # background FA map
            image_d = self.get_slice(image, z_num)
            img = ax.imshow(
                    image_d,
                    cmap=self.overlap_cmap,
                    vmin=0,
                    vmax=1, alpha=alpha)
            self.imshow_list.append(img)
    # def create_figure_

class TbssFigure(Enigma, Figure, FigureNifti):
    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.get_center(self.enigma_fa_data)
        self.enigma_skeleton_data = self.transparent_mask(
            self.enigma_skeleton_data)
        self.read_data()

    def create_figure_one_map(self):
        self.images_mask_out_the_zero()
        self.loop_through_axes_draw_bg()
        self.annotate_with_z()

        self.loop_through_axes_draw_images()
        self.add_cbars_horizontal()

        self.fig.suptitle(self.title, y=0.9, fontsize=25)
        self.fig.savefig(self.output_file, dpi=200)#, bbox_inches='tight')

    def create_figure_two_maps_and_overlap(self):
        self.images_mask_out_the_zero()
        self.loop_through_axes_draw_bg()
        self.annotate_with_z()

        self.loop_through_axes_draw_images()
        # estimate overlap
        self.get_overlap_between_maps()
        self.loop_through_axes_draw_overlap()

        self.get_cbar_horizontal_info()
        self.add_cbars_horizontal()

        self.fig.suptitle(self.title, y=0.9, fontsize=25)
        self.fig.savefig(self.output_file, dpi=200)#, bbox_inches='tight')


