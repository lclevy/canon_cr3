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

from unittest import TestCase
from cannon_cr3 import Image

test_file = '../samples/IMG_0482_raw.CR3'


class TestImageAPI(TestCase):

    def setUp(self):
        self.img = Image(test_file)

    def test_returns_jpg_image_data(self):
        jpg_image = self.img.jpeg_image
        # first 5 bits
        self.assertEqual(b'\xff\xd8\xff\xdb\x00', jpg_image[:5])
        # last 5 bits
        self.assertEqual(b'\xab\x85\xcf\xff\xd9', jpg_image[-5:])

    def test_returns_hd_crx_image(self):
        hd_crx = self.img.hd_crx_image
        # first 5 bits
        self.assertEqual(b'\xff\x01\x00\x08\x00', hd_crx[:5])
        # last 5 bits
        self.assertEqual(b'\x8e\xde\x8e@\x00', hd_crx[-5:])
        # proper size
        self.assertEqual(22914744, len(hd_crx))

    def test_returns_sd_crx_image(self):
        sd_crx = self.img.sd_crx_image
        # first 5 bits
        self.assertEqual(b'\xff\x01\x00\x08\x00', sd_crx[:5])
        # last 5 bits
        self.assertEqual(b'\x00\x00\x00\x00\x00', sd_crx[-5:])
        # proper size
        self.assertEqual(1290224, len(sd_crx))

    def test_returns_dual_pixel_crx(self):
        dp_crx = self.img.dual_pixel_crx_image
        # first 5 bits
        self.assertEqual(None, dp_crx)
        # last 5 bits
        self.assertEqual(None, dp_crx)

    def test_returns_thumbnail(self):
        thm = self.img.thumbnail_image
        # first 5 bits
        self.assertEqual(b'\xff\xd8\xff\xdb\x00', thm[:5])
        # last 5 bits
        self.assertEqual(b'\xd6\xa7s\xff\xd9', thm[-5:])
        # proper size
        self.assertEqual(11958, len(thm))

    def test_returns_preview(self):
        prv = self.img.preview_image
        # first 5 bits
        self.assertEqual(b'\xff\xd8\xff\xdb\x00', prv[:5])
        # last 5 bits
        self.assertEqual(b'\x17/\x99\xff\xd9', prv[-5:])
        # proper size
        self.assertEqual(265125, len(prv))
