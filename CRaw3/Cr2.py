'''
parses CR2 files using TiffIfd and Jpeg classes
'''

from CRaw3.TiffIfd import TiffIfd
from CRaw3.Jpeg import Jpeg

class Cr2:
  def __init__(self, data, length, name):
    self.ifd_list = dict()
    self.data = data
    
    ifd_num = 0
    #IFD 0 has header
    self.ifd_list[ ifd_num ] = TiffIfd( data, length, 0, '0', False, True, True )
    
    if TiffIfd.TIFF_EXIF in self.ifd_list[ 0 ].ifd:    
      offset = self.ifd_list[ 0 ].ifd[TiffIfd.TIFF_EXIF].value
      self.ifd_list[ TiffIfd.TIFF_EXIF ] = TiffIfd( data[offset:], length, offset, '%x' % TiffIfd.TIFF_EXIF, False, False, True )
    if TiffIfd.TIFF_MAKERNOTE in self.ifd_list[ TiffIfd.TIFF_EXIF ].ifd:    
      offset = self.ifd_list[ TiffIfd.TIFF_EXIF ].ifd[TiffIfd.TIFF_MAKERNOTE].value
      self.ifd_list[ TiffIfd.TIFF_MAKERNOTE ] = TiffIfd( data[offset:], length, offset, '%x' % TiffIfd.TIFF_MAKERNOTE, False, False, True )
    if TiffIfd.TIFF_GPS in self.ifd_list[ 0 ].ifd:    
      offset = self.ifd_list[ 0 ].ifd[TiffIfd.TIFF_GPS].value
      self.ifd_list[ TiffIfd.TIFF_GPS ] = TiffIfd( data[offset:], length, offset, '%x' % TiffIfd.TIFF_GPS, False, False, True )
    #other IFD has no header
    while self.ifd_list[ ifd_num ].next != 0:
      next = self.ifd_list[ ifd_num ].next 
      ifd_num += 1
      self.ifd_list[ ifd_num ] = TiffIfd( data[next:], length, next, '%d' % ifd_num, False, False, True )
      
  def display(self):
    for key, ifd in self.ifd_list.items():
      print('0x%x:' % key)
      ifd.display()
      
  def extract_pic0(self, filename): #full size, jpg
    offset = self.ifd_list[ 0 ].ifd[ TiffIfd.TIFF_EXIF_PreviewImageStart ].value
    length = self.ifd_list[ 0 ].ifd[ TiffIfd.TIFF_EXIF_PreviewImageLength ].value      
    f = open(filename, 'wb')
    f.write( self.data[offset:offset+length] )
    f.close()

  def extract_pic1(self, filename): #thumbnail, jpg
    offset = self.ifd_list[ 1 ].ifd[ TiffIfd.TiffIfd.TIFF_EXIF_ThumbnailOffset ].value
    length = self.ifd_list[ 1 ].ifd[ TiffIfd.TiffIfd.TIFF_EXIF_ThumbnailLength ].value      
    f = open(filename, 'wb')
    f.write( self.data[offset:offset+length] )
    f.close()
    
  def extract_pic2(self, filename): #saved as .ppm, (RGB 16bits, little endian). no WB, no scaling
    offset = self.ifd_list[ 2 ].ifd[ TiffIfd.TIFF_EXIF_PreviewImageStart ].value
    length = self.ifd_list[ 2 ].ifd[ TiffIfd.TIFF_EXIF_PreviewImageLength ].value      
    width = self.ifd_list[ 2 ].ifd[ TiffIfd.TIFF_EXIF_ImageWidth ].value
    height = self.ifd_list[ 2 ].ifd[ TiffIfd.TIFF_EXIF_ImageHeight ].value
    out = open(filename, 'w')
    print ('P3\n%d %d' % (width, height), file=out)
    print ('%s' % (1<<14), file=out)
    pic = Struct('<%dH'%(3*width*height)).unpack_from(self.data[offset:offset+length], 0)
    index = 0
    for y in range(height):
      for x in range(width):
        print ('%4d %4d %4d ' % (pic[index], pic[index+1], pic[index+2]), end='', file=out)
        index += 3
      print(file=out)
    out.close()    
    return width, height
  
  def get_lossless_info(self):
    offset = self.ifd_list[ 3 ].ifd[ TiffIfd.TIFF_EXIF_StripOffsets ].value
    length = self.ifd_list[ 3 ].ifd[ TiffIfd.TIFF_EXIF_StripByteCounts ].value    
    self.jpg = Jpeg( self.data[offset:offset+length] )
    
  def get_model_id(self):
    return self.ifd_list[ TiffIfd.TIFF_MAKERNOTE ].ifd[ TiffIfd.TIFF_MAKERNOTE_MODELID ].value
    
  def get_model_name(self):
    offset = self.ifd_list[ 0 ].ifd[ TiffIfd.TIFF_EXIF_Model ].value
    length = self.ifd_list[ 0 ].ifd[ TiffIfd.TIFF_EXIF_Model ].length
    return self.data[ offset: offset+length-1 ]