
from struct import Struct, unpack
from collections import namedtuple, OrderedDict
from binascii import hexlify

def getShortLE(d, a):
 return unpack('<H',(d)[a:a+2])[0]

def getLongLE(d, a):
 return unpack('<L',(d)[a:a+4])[0]
  
 
class TiffIfd:
  #class for Tiff IFD (Canon kind)
  
  TIFF_EXIF_Model = 0x110
  TIFF_EXIF_PreviewImageStart = 0x111
  TIFF_EXIF_PreviewImageLength = 0x117
  TIFF_EXIF_ImageHeight = 0x101
  TIFF_EXIF_ImageWidth = 0x100
  TIFF_EXIF_ThumbnailOffset = 0x201
  TIFF_EXIF_ThumbnailLength = 0x202
  TIFF_EXIF_StripOffsets = 0x111
  TIFF_EXIF_StripByteCounts = 0x117
  
  TIFF_MAKERNOTE_SENSORINFO = 0xe0  
  TIFF_MAKERNOTE_CAMERASETTINGS = 1
  TIFF_MAKERNOTE_DUST_DELETE_DATA = 0x97
  TIFF_MAKERNOTE_ROLLINFO = 0x403f
  TIFF_CAMERASETTINGS_QUALITY_RAW = 4
  TIFF_CAMERASETTINGS_QUALITY_CRAW = 7
  TIFF_MAKERNOTE_MODELID = 0x10
  
  TIFF_MAKERNOTE = 0x927c
  TIFF_EXIF = 0x8769
  TIFF_GPS = 0x8825
  TIFF_CANON_VIGNETTING_CORR2 = 0x4016
    
  TIFF_TYPE_UCHAR = 1  
  TIFF_TYPE_STRING = 2
  TIFF_TYPE_USHORT = 3
  TIFF_TYPE_ULONG =  4 
  TIFF_TYPE_URATIONAL =  5 
  TIFF_TYPE_CHAR =  6 
  TIFF_TYPE_BYTESEQ = 7
  TIFF_TYPE_SHORT = 8 
  TIFF_TYPE_LONG =  9 
  TIFF_TYPE_RATIONAL =  10 
  TIFF_TYPE_FLOAT4 =  11 
  TIFF_TYPE_FLOAT8 =  12   

  tiffTypeLen = [ 1, 1, 2, 4, 4+4, 1, 1, 2, 4, 4+4, 4, 8 ]
  tiffTypeStr = [ 'B', 's', 'H', 'L', 'L', 'c', 'c', 'h', 'l', 'l', 'l', 'q' ] #use with caution, might not always work. Will not with rational
  tiffTypeNames = [ "uchar", "string", "ushort", "ulong", "urational", "char", "byteseq", "short", "long", "rational", "float4", "float8" ]

  S_IFD_ENTRY_REC = Struct('<HHLL')  
  NT_IFD_ENTRY = namedtuple('ifd_entry', 'offset tag type length value')

  def __init__(self, data, length, base, name, display=True, has_header=True, get_next=False):
    self.data = data
    self.length = length
    self.base = base
    self.name = name
    self.ifd = dict()
    self.next = 0

    '''if not options.quiet and display:
      print( "{0}: (0x{1:x})".format(name, length) )'''
    if has_header:  
      #4949 2A00 08000000  
      self.order = data[0:2] #for a future MM compatible version ?
      if self.order!=b'II': #should raise exception
        print('order!=II')
        return
      marker = getShortLE( data, 2 )
      if marker != 0x2a:
        print('marker != 0x2a')
        return
      ptr = getShortLE( data, 4 ) #8
    else:
      ptr = 0    
      
    n = getShortLE( data, ptr )
    ptr = ptr + 2
    for i in range(n):
      tag, type, length, val = TiffIfd.S_IFD_ENTRY_REC.unpack_from( data[ptr:ptr+TiffIfd.S_IFD_ENTRY_REC.size] )
      ifd_entry = TiffIfd.NT_IFD_ENTRY( self.base+ptr, tag, type, length, val )
      self.ifd[ tag ] = ifd_entry  
      ptr = ptr + TiffIfd.S_IFD_ENTRY_REC.size
      if self.base+ptr > self.base+self.length:
        print('base+ptr > base+length !')
    if get_next:
      self.next =  getLongLE( data, ptr )   

  def print_entry(self, type, length, val, max):
    #we should verify this is access after self.base+self.length in self.data
    typeLen = TiffIfd.tiffTypeLen[type-1] 
    data2 = self.data[ val: val+min(length,max)*typeLen ]
    if type == TiffIfd.TIFF_TYPE_UCHAR or type == TiffIfd.TIFF_TYPE_STRING:
      if length < 5:
        print('%x'%val)
      else:  
        zero = data2.find(b'\x00')
        if zero!=-1:
          data2 = self.data[ val: val+zero ]
        print(data2)
    elif type == TiffIfd.TIFF_TYPE_USHORT:
      if length == 1:
        print('%hu'%val)
      else:
        if length*typeLen > 4: #do not fit in long (tag 0x404b)
          for i in range(0, min(length,max)*typeLen, typeLen):
            print( '%hu '%( getShortLE(data2, i) ), end='' )
        if length > max:
          print('...')
        else:
          print()      
    elif type == TiffIfd.TIFF_TYPE_ULONG:
      if length == 1:
        print('%lu'%val)
      else:
        for i in range(0, min(length,max)*typeLen, typeLen):
          print( '%lu '%( getLongLE(data2, i) ), end='' )
        if length>max:
          print('...')
        else:
          print()  
    elif type == TiffIfd.TIFF_TYPE_BYTESEQ:
      if length < 5:
        print()    
      else:
        if length>max:
          print(hexlify(data2), '...')
        else:
          print(hexlify(data2))
    elif type == TiffIfd.TIFF_TYPE_URATIONAL:
      print('%lu / %lu' % ( getLongLE(data2, 0), getLongLE(data2, 4) ) )
    elif type == TiffIfd.TIFF_TYPE_URATIONAL:
      print('%ld / %ld' % ( getLongLE(data2, 0), getLongLE(data2, 4) ) )
    else:
      print()  
  
  def display( self, depth=0):
    for entry in self.ifd.values():
      print( "     %s 0x%06lx %5d/0x%-4x %9s(%d)*%-6ld %9lu/0x%-lx, " % (depth*'  ', entry.offset, entry.tag , entry.tag, TiffIfd.tiffTypeNames[entry.type-1],entry.type,entry.length,entry.value,entry.value), end='' )
      self.print_entry( entry.type, entry.length, entry.value, 20)
