'''
This file is part of cannon_cr3.

cannon_cr3 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

cannon_cr3 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with cannon_cr3. If not, see <http://www.gnu.org/licenses/>.
'''

from canon_cr3.cr3_lib import Cr3FileParser, CmtdDataParser


class CanonCraw:
    '''Class to represent the Cannon Compressed Raw setting'''
    def __repr__(self):
        return 'Cannon Craw'


class CanonRaw:
    def __repr__(self):
        '''Class to represent the Cannon Raw setting'''
        return 'Cannon Raw'


class Image(Cr3FileParser):
    '''This class is to act as the API to extract the specific Image data out of the cr3 file'''

    @property
    def jpeg_image(self):
        return self._trak_data('trak1')

    @property
    def hd_crx_image(self):
        return self._trak_data('trak3')

    @property
    def sd_crx_image(self):
        return self._trak_data('trak2')

    @property
    def dual_pixel_crx_image(self):
        if 'trak5' in self.cr3:  # dual pixel trak
            return self._trak_data('trak5')
        return None

    @property
    def thumbnail_image(self):
        return self._thumbnail_data

    @property
    def preview_image(self):
        return self._preview_image


class CmtdData(CmtdDataParser):

    '''This class is to act as the API to extract the specific CMTD data out of the cr3 file'''

    @property
    def camera_model(self):
        modelData, modelEntry = self.getTiffTagData(b'CMT1', self.TIFF_CMT1_MODEL)
        return modelData[:modelEntry[2] - 1].decode()  # use length value (modelEntry[2]) of TIFF entry for model

    @property
    def sensor_width(self):
        return self._sensor_characteristics()[1]

    @property
    def sensor_height(self):
        return self._sensor_characteristics()[2]

    @property
    def sensor_left_border(self):
        return self._sensor_characteristics()[5]

    @property
    def sensor_top_border(self):
        return self._sensor_characteristics()[6]

    @property
    def sensor_right_border(self):
        return self._sensor_characteristics()[7]

    @property
    def sensor_bottom_border(self):
        return self._sensor_characteristics()[8]

    @property
    def quality_type(self):
        # get camera settings to find if it is a craw (lossy) or raw (lossless)
        camera_settings_data, camera_settings_entry = self.getTiffTagData(b'CMT3', self.TIFF_CMT3_CAMERASETTINGS)
        camera_settings_list = [self.get_short_le(camera_settings_data, i)
                              for i in range(0, camera_settings_entry[2], self.tiffTypeLen[camera_settings_entry[1] - 1])]

        if camera_settings_list[3] == self.TIFF_CAMERASETTINGS_QUALITY_CRAW:
            return CanonCraw()
        elif camera_settings_list[3] == self.TIFF_CAMERASETTINGS_QUALITY_RAW:
            return CanonRaw()
        else:
            return 'camera_settings_list[3]=%d' % camera_settings_list[3]