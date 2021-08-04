#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import ndimage
import os
import seaborn as sns

from nifti_snapshot.nifti_snapshot_utils import get_nifti_data, get_nifti_img_data
from nifti_snapshot.nifti_snapshot_utils import script_dir, lib_dir, root_dir

import matplotlib.ticker as ticker
from typing import List


class Enigma:
    def __init__(self):
        """ENIGMA template"""
        self.enigma_dir = root_dir / 'data' / 'enigmaDTI'
        self.template_fa_loc = self.enigma_dir / 'ENIGMA_DTI_FA.nii.gz'
        self.template_skeleton_loc = self.enigma_dir / \
            'ENIGMA_DTI_FA_skeleton_mask.nii.gz'

class Fsl:
    def __init__(self):
        """FSL template"""
        self.fsldir = os.environ['FSLDIR']
        self.template_fa_loc = Path(self.fsldir) / \
            'data/standard/FMRIB58_FA_1mm.nii.gz'
        self.template_skeleton_loc = Path(self.fsldir) / \
            'data/standard/FMRIB58_FA-skeleton_1mm.nii.gz'

class FigureSettings:
    def __init__(self):
        """Figure default settings"""
        self.ncols = 5
        self.nrows = 4
        self.size_w = 4
        self.size_h = 4
        self.slice_gap = 3
        self.dpi = 200
        self.hspace = 0
        self.top = 0.9
        self.bottom = 0.1
        self.wspace = 0
        self.title_font_size = 25

    def get_cbar_horizontal_info(self):
        """Default horizontal cbar settings"""
        self.cbar_x = 0.25
        self.cbar_y = 0.03
        self.cbar_height = 0.03
        self.cbar_width = 0.15
        self.cbar_ticks = [0, 1]

    def add_intensity_cbars_horizontal(self):
        self.cbar_x_steps = 0.2

        if len(self.image_data_list) == 1:
            self.cbar_width = 0.5

        for num, image_data in enumerate(self.image_data_list):
            # x, y, width, height
            if hasattr(self, 'cbar_titles'):
                cbar_title = self.cbar_titles[num]
            else:
                cbar_title = f'Image {num+1}'

            axbar = self.fig.add_axes([
                self.cbar_x,
                self.cbar_y,
                self.cbar_width,
                self.cbar_height])

            cb = self.fig.colorbar(
                    self.imshow_list[num],
                    axbar,
                    orientation='horizontal',)

            # cb.ax.set_xticklabels(['P = 0.05', 'P < 0.01'], color='white')

            cb.outline.set_edgecolor('white')
            cb.ax.set_title(
                    cbar_title,
                    fontsize=15, fontweight='bold', color='white')
            cb.ax.yaxis.set_label_position('left')

    def add_cbars_horizontal(self):
        """Add horizontal cbars for tbss stat maps"""
        self.cbar_x_steps = 0.2

        if len(self.image_data_list) == 1:
            self.cbar_width = 0.5

        for num, image_data in enumerate(self.image_data_list):
            # x, y, width, height
            if hasattr(self, 'cbar_titles'):
                cbar_title = self.cbar_titles[num]
            else:
                cbar_title = f'Image {num+1}'

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
                        ticks=[0.95,1])
                cb.ax.set_xticklabels(
                        ['P = 0.05', 'P < 0.01'],
                        color='white',
                        fontsize=15)
            else:
                cb = self.fig.colorbar(
                        self.imshow_list[num],
                        axbar,
                        orientation='horizontal',
                        boundaries=[0.999, 1],
                        ticks=[])
                # cb.ax.set_major_locator(ticker.LinearLocator(2))
                # cb.ax.set_xticklabels(['P = 0.05', 'P < 0.01'], color='white')

            cb.outline.set_edgecolor('white')
            cb.ax.set_title(
                    cbar_title,
                    fontsize=15, fontweight='bold', color='white')
            cb.ax.yaxis.set_label_position('left')
            self.cbar_x += self.cbar_x_steps

    def add_cbars_horizontal_tbss_filled(self):
        """Add horizontal cbars for tbss stat maps"""
        self.cbar_x_steps = 0.2

        if len(self.image_data_list) == 1:
            self.cbar_width = 0.5

        for num, image_data in enumerate(self.image_data_list):
            # x, y, width, height
            if hasattr(self, 'cbar_titles'):
                cbar_title = self.cbar_titles[num]
            else:
                cbar_title = f'Image {num+1}'

            axbar = self.fig.add_axes([
                self.cbar_x,
                self.cbar_y,
                self.cbar_width,
                self.cbar_height])

            cb = self.fig.colorbar(
                    self.imshow_list[num],
                    axbar,
                    orientation='horizontal',
                    ticks=[0, 1])
            cb.ax.set_xticklabels(
                    ['P = 0.05', 'P < 0.01'],
                    color='white',
                    fontsize=15)

            cb.outline.set_edgecolor('white')
            cb.ax.set_title(
                    cbar_title,
                    fontsize=15, fontweight='bold', color='white')
            cb.ax.yaxis.set_label_position('left')
            self.cbar_x += self.cbar_x_steps

class FigureNifti:
    def get_slice(self, data, z_num):
        return np.flipud(data[:, :, z_num].T)

    def make_lt_one_transparent(self, data):
        data = np.where(data < 1, np.nan, data)
        return data

    def transparent_zero(self, data):
        data = np.where(data == 0, np.nan, data)
        return data

    def transparent_threshold(self, data, threshold):
        with np.errstate(invalid='ignore'):
            data = np.where(data < threshold, np.nan, data)
        return data

    def transparent_out_the_skeleton(self, data):
        data = np.where(self.template_skeleton_data == 1, data, np.nan)
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

    def get_slice_nums_non_zero_linspace(self):
        """Get slice_nums based on the zmin and zmax"""
        # get nonzero z coordinates
        nonzero_coord_z = np.nonzero(self.image_data_list[0])[-1]
        zmin = nonzero_coord_z.min()
        zmax = nonzero_coord_z.max()

        # if there is enough nonzero slices to show
        # z_slices = zmax - zmin
        # if (zmax - zmin) > self.slice_num:
        self.slice_nums = np.linspace(zmin, zmax, self.slice_num).astype(int)
        # else:
            # zmin_new = zmin - (self.slice_num - z_slices)
            # self.slice_nums = np.linspace(zmin_new, zmax, self.slice_num)

        # make integer array
        # self.slice_nums = self.slice_nums.astype(int)

    def get_slice_nums_focused(self, data, padding=2):
        # Get the center of data
        # slices below z=40 have been zeroed in order to move the
        # center_of_data upwards for better visualization
        self.roi_bbox = {}
        for axis, axis_num in zip(['x','y','z'],
                                  [0,1,2]):
            self.roi_bbox[axis+'_min'] = np.where(data!=0)[axis_num].min() - \
                                         padding
            self.roi_bbox[axis+'_max'] = np.where(data!=0)[axis_num].max() + \
                                         padding

        self.slice_nums = np.linspace(self.roi_bbox['z_min'],
                                      self.roi_bbox['z_max'],
                                      self.nrows * self.ncols).astype(int)

    def get_slice_nums(self):
        """Get a list of slice numbers automatically"""

        # TODO : this does not work with non-enigma template TBSS currently
        # self.slice_nums = np.arange(
            # self.z_slice_center - (self.slice_num * self.slice_gap),
            # self.z_slice_center + (self.slice_num * self.slice_gap),
            # self.slice_gap)[::2]
        self.slice_nums = np.arange(
            self.z_slice_center - (self.slice_num * self.slice_gap),
            self.z_slice_center + (self.slice_num * self.slice_gap),
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
        FigureSettings.__init__(self)

        for key, value in kwargs.items():
            print(f"\t{key} : {value}")
            setattr(self, key, value)

        # The number of slices to be shown in the output figures depend on the
        # number of rows and columns
        self.slice_num = self.nrows * self.ncols

        # create fig and axes
        self.fig, self.axes = plt.subplots(
            ncols=self.ncols,
            nrows=self.nrows,
            figsize=(self.size_w * self.ncols,
                     self.size_h * self.nrows),
            dpi=self.dpi)

        self.get_cbar_horizontal_info()

        # figure settings
        self.fig.subplots_adjust(
                hspace=self.hspace,
                wspace=self.wspace,
                top=self.top,
                bottom=self.bottom)

        # dark background
        plt.style.use('dark_background')


    def read_data(self, volumes: List[int] = None):
        # load background data
        if hasattr(self, 'background_files') and \
                not hasattr(self, 'background_data_list'):
            self.background_data_list = [get_nifti_data(x) for x
                                         in self.background_files]

        # load foreground data
        if hasattr(self, 'image_files') and \
                not hasattr(self, 'image_data_list'):
            self.image_data_list = [get_nifti_data(x) for x
                                    in self.image_files]

        # if 4d, force to visualize the first volume
        if volumes is not None or \
                any([len(x.shape) == 4 for x in self.image_data_list]):
            volumes = [0 for x in self.image_data_list] if volumes is None \
                    else volumes
            new_image_data_list = []
            for image_data, vol in zip(self.image_data_list, volumes):
                image_data = image_data[:, :, :, vol] \
                        if len(image_data.shape) == 4 else image_data
                new_image_data_list.append(image_data)
            self.image_data_list = new_image_data_list

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

    def draw_image(self, array, cmap, vmin, vmax):
        for num, ax in enumerate(np.ravel(self.axes)):
            z_num = self.slice_nums[num]
            array_slice = self.get_slice(array, z_num)

            # background FA map
            ax.imshow(array_slice,cmap=cmap, vmin=vmin, vmax=vmax)
            ax.axis('off')

    def loop_through_axes_draw_bg_tbss(self):
        for num, ax in enumerate(np.ravel(self.axes)):
            z_num = self.slice_nums[num]
            # here bg is automatically set as the enigma files
            fa_d = self.get_slice(self.template_fa_data, z_num)
            skeleton_d = self.get_slice(self.template_skeleton_data, 
                                        z_num)

            # background FA map
            img = ax.imshow(fa_d, cmap='gray')

            # background skeleton
            # TODO: interpolation?
            img = ax.imshow(skeleton_d,
                    interpolation=None,
                    cmap='Greens_r')
            # img = ax.imshow(skeleton_d, cmap='Greens')
            ax.axis('off')

    def loop_through_axes_draw_images_corrp_map(self, vmin):
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
                        vmin=vmin,
                        vmax=1, alpha=alpha)
                self.imshow_list.append(img)

    def loop_through_axes_draw_hist(self):
        """Loop thorugh each axis drawing figures"""

        # bbox
        if hasattr(self, 'box_x'):
            self.image_data_list = [
                x[self.box_x[0]:self.box_x[1], :, :] \
                    for x in self.image_data_list]

        if hasattr(self, 'box_y'):
            self.image_data_list = [
                x[:, self.box_y[0]:self.box_y[1], :] \
                    for x in self.image_data_list]

        if hasattr(self, 'box_z'):
            self.image_data_list = [
                x[:, :, self.box_z[0]:self.box_z[1]] \
                    for x in self.image_data_list]

        for num, ax in enumerate(np.ravel(self.axes)):
            z_num = self.slice_nums[num]

            # background FA map
            self.imshow_list = []

            for img_num, image in enumerate(self.image_data_list):
                # vmin and vmax, which must be consistent across the figures
                if hasattr(self, 'vmin_list'):
                    vmin = self.vmin_list[img_num]
                    has_vmin = True
                else:
                    has_vmin = False

                if hasattr(self, 'vmax_list'):
                    vmax = self.vmax_list[img_num]
                    has_vmax = True
                else:
                    has_vmax = False

                image_d = self.get_slice(image, z_num)
                img = sns.distplot(np.ravel(image_d), ax=ax)

                if has_vmin:
                    ax.set_xlim(vmin, vmax)
                    ax.set_ylim(0, 0.0001)
                self.imshow_list.append(img)

    def loop_through_axes_draw_images(self):
        """TODO: make this clean Loop thorugh each axis drawing figures"""

        # make zero transparent
        if hasattr(self, 'make_transparent_zero'):
            if self.make_transparent_zero == True:
                self.image_data_list = [
                    np.where(x == 0, np.nan, x) for x in self.image_data_list]

        # bbox
        if hasattr(self, 'box_x'):
            self.image_data_list = [
                x[self.box_x[0]:self.box_x[1], :, :] \
                    for x in self.image_data_list]

        if hasattr(self, 'box_y'):
            self.image_data_list = [
                x[:, self.box_y[0]:self.box_y[1], :] \
                    for x in self.image_data_list]

        if hasattr(self, 'box_z'):
            self.image_data_list = [
                x[:, :, self.box_z[0]:self.box_z[1]] \
                    for x in self.image_data_list]

        # loop through slices
        for num, ax in enumerate(np.ravel(self.axes)):
            z_num = self.slice_nums[num]

            # background FA map
            self.imshow_list = []

            # loop through images
            for img_num, image in enumerate(self.image_data_list):
                # vmin and vmax, which must be consistent across the figures
                if hasattr(self, 'vmin_list'):
                    vmin = self.vmin_list[img_num]
                    has_vmin = True
                else:
                    has_vmin = False

                if hasattr(self, 'vmax_list'):
                    vmax = self.vmax_list[img_num]
                    has_vmax = True
                else:
                    has_vmax = False

                image_d = self.get_slice(image, z_num)

                if hasattr(self, 'alpha_list'):
                    alpha = self.alpha_list[img_num]
                else:
                    alpha = 1

                if hasattr(self, 'cmap_list'):
                    cmap = self.cmap_list[img_num]
                else:
                    cmap = 'autumn'


                if has_vmin and has_vmax:
                    img = ax.imshow(
                        image_d,
                        cmap=cmap,
                        vmin=vmin,
                        vmax=vmax,
                        alpha=alpha)
                elif has_vmin and has_vmax == False:
                    img = ax.imshow(
                        image_d,
                        cmap=cmap,
                        vmin=vmin,
                        alpha=alpha)
                elif has_vmax and has_vmin == False:
                    img = ax.imshow(
                        image_d,
                        cmap=cmap,
                        vmax=vmax,
                        alpha=alpha)
                else:
                    img = ax.imshow(
                        image_d,
                        cmap=cmap,
                        alpha=alpha)
                self.imshow_list.append(img)
            ax.axis('off')

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
    """TBSS related figure"""
    def __init__(self, template='enigma', **kwargs):
        """Requires template input"""
        # define template
        if template.lower() == 'enigma':
            # set enigma related attributes
            Enigma.__init__(self)
        elif template.lower() == 'fsl':
            # set FSL related attributes
            Fsl.__init__(self)
        else:
            self.template_fa_loc = kwargs.get('template_FA')
            self.template_skeleton_loc = kwargs.get('template_skeleton')

        # load FA and skeleton mask templates
        self.template_fa_data = get_nifti_data(self.template_fa_loc)
        self.template_skeleton_data = get_nifti_data(self.template_skeleton_loc)
        self.template_skeleton_data = self.make_lt_one_transparent(
            self.template_skeleton_data)

        # register attributes given when initiating TbssFigure class
        Figure.__init__(self, **kwargs)

        # read data given when creating initiating TbssFigure
        # read in the list of self.background_files and self.image_files
        # if it exists
        self.read_data()
        self.get_slice_nums_non_zero_linspace()

        # for tbss stats map cbar_ticks
        
        if kwargs.get('tbss_filled') == True: #TBSS filled
            self.vmin_list = np.tile(0, len(self.image_data_list))
        else:
            self.vmin_list = np.tile(0.95, len(self.image_data_list))
        self.vmax_list = np.tile(1, len(self.image_data_list))

        self.cbar_ticks = [0.95, 1]

        self.images_mask_out_the_zero()
        self.loop_through_axes_draw_bg_tbss()
        self.annotate_with_z()

        self.loop_through_axes_draw_images()

    def create_figure_one_map(self):
        self.add_cbars_horizontal()
        self.fig.suptitle(self.title, y=0.95, fontsize=self.title_font_size)
        self.fig.savefig(self.output_file, dpi=self.dpi)#, bbox_inches='tight')

    def create_figure_two_maps_and_overlap(self):
        # estimate overlap
        self.get_overlap_between_maps()
        self.loop_through_axes_draw_overlap()
        self.add_cbars_horizontal()

        self.fig.suptitle(self.title, y=0.95, fontsize=self.title_font_size)
        self.fig.savefig(self.output_file, dpi=self.dpi)#, bbox_inches='tight')

class SimpleFigure(Figure):
    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)

        self.read_data(kwargs.get('volumes', None))

        self.get_slice_nums_non_zero_linspace()

        if hasattr(self, 'slice_num_lowest'):
            self.slice_nums = [int(x) for x in \
                np.linspace(self.slice_num_lowest,
                            self.slice_num_highest,
                            self.ncols * self.nrows)]
        else:
            pass
            # self.get_center(self.image_data_list[0])

        # remove negative
        self.alpha_list = [1]
        # self.cmap_list = ['coolwarm']
        self.cmap_list = ['gray']

        if not hasattr(self, 'vmin_list') and not hasattr(self, 'vmax_list'):
            percentile = kwargs.get('percentile', [5, 95])
            self.vmin_list = []
            self.vmax_list = []
            for image_data in self.image_data_list:
                self.vmin_list.append(
                        np.percentile(image_data, percentile[0]))
                self.vmax_list.append(np.percentile(image_data, percentile[1]))

        self.loop_through_axes_draw_images()
        self.annotate_with_z()

        self.cbar_titles = ['intensity']
        self.add_intensity_cbars_horizontal()

        self.fig.suptitle(self.title, y=0.90, fontsize=self.title_font_size)
        self.fig.savefig(self.output_file, dpi=self.dpi)  #, bbox_inches='tight')


class SimpleHistogram(Figure):
    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.read_data()

        # self.get_center(self.image_data_list[0])
        
        self.slice_nums = [int(x) for x in \
            np.linspace(self.slice_num_lowest, 
                        self.slice_num_highest, 
                        self.ncols * self.nrows)]

        # remove negative
        self.alpha_list = [1]
        self.cmap_list = ['coolwarm']

        self.loop_through_axes_draw_hist()
        self.annotate_with_z()

        plt.style.use('default')
        self.fig.suptitle(self.title, y=0.90, fontsize=self.title_font_size)
