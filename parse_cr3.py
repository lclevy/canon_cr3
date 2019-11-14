# parse CR3 (and CR2) file format from Canon (@lorenzo2472)
# from https://github.com/lclevy/canon_cr3
# tested with Python 3.6.7
# about ISO Base file format : https://stackoverflow.com/questions/29565068/mp4-file-format-specification
# License is GPLv3 

import sys
from struct import unpack, Struct
from binascii import hexlify, unhexlify
from optparse import OptionParser
from collections import namedtuple, OrderedDict

def getShortBE(d, a):
 return unpack('>H',(d)[a:a+2])[0]

def getShortLE(d, a):
 return unpack('<H',(d)[a:a+2])[0]
 
def getLongBE(d, a):
 return unpack('>L',(d)[a:a+4])[0]

def getLongLE(d, a):
 return unpack('<L',(d)[a:a+4])[0]
 
def getLongLongBE(d, a):
 return unpack('>Q',(d)[a:a+8])[0]

class Jpeg:
  JPEG_SOI  =  0xffd8
  JPEG_APP1 =  0xffe1
  JPEG_DHT  =  0xffc4
  JPEG_DQT  =  0xffdb
  JPEG_SOF0 =  0xffc0
  JPEG_SOF3 =  0xffc3
  JPEG_SOS  =  0xffda
  JPEG_EOI  =  0xffd9

  def __init__(self, data):
    self.data = data
    val = getShortBE(self.data, 0)
    ptr = 0
    size = 0
    while val != Jpeg.JPEG_SOS:
      #print('%x' % val)
      if val == Jpeg.JPEG_SOI:
        pass
      elif val == Jpeg.JPEG_DHT:
        size = getShortBE(self.data, ptr+2)
      elif val == Jpeg.JPEG_SOF0 or val == Jpeg.JPEG_SOF3:  
        size = getShortBE(self.data, ptr+2)
        self.bits, self.high, self.wide, self.n_comp = Struct('>BHHB').unpack_from(data, ptr+4)
        print(self.bits, self.high, self.wide, self.n_comp)
      #print('size %x' % size)
      ptr += size+2
      val = getShortBE(self.data, ptr)  

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

    if not options.quiet and display:
      print( "{0}: (0x{1:x})".format(name, length) )
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
        for i in range(0, min(length,max)*typeLen, typeLen):
          print( '%hu '%( getShortLE(data2, i) ), end='' )
        if length>max:
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

class Ctmd:
  S_CTMD_INDEX_HEADER = Struct('>LLL')
  S_CTMD_INDEX_ENTRY = Struct('>LL')
  NT_CTMD_INDEX_ENTRY = namedtuple('ctmd_index_entry', 'type size')

  def __init__(self, data, length, base, name): #parse the index, common to all ctmd in mdat if more than one (rolls)
    self.index_list = []
    _, _, nb = Ctmd.S_CTMD_INDEX_HEADER.unpack_from( data, 0)
    for i in range(nb):
      type, size = Ctmd.S_CTMD_INDEX_ENTRY.unpack_from( data, Ctmd.S_CTMD_INDEX_HEADER.size + i*Ctmd.S_CTMD_INDEX_ENTRY.size)
      entry = Ctmd.NT_CTMD_INDEX_ENTRY( type, size )
      self.index_list.append( entry )

  S_CTMD_RECORD_HEADER = Struct('<LHBBHH')  
  NT_CTMD_RECORD = namedtuple('ctmd_record', 'size type offset content')
  CTMD_TIFF_TYPES = [ 7, 8, 9 ]
  S_CTMD_TIFF_HEADER = Struct('<LL')  #record size, tag id

  CTMD_TYPE_TIMESTAMP = 1
  S_CTMD_TIMESTAMP = Struct('<HHBBBBBB')
  NT_CTMD_TIMESTAMP = namedtuple('ctmd_timestamp', 'y mo d h m s ms')
  CTMD_TYPE_FOCAL = 4
  S_CTMD_FOCAL = Struct('<HH')
  NT_CTMD_FOCAL = namedtuple('ctmd_focal', 'num denum')
  CTMD_TYPE_EXPOSURE = 5
  S_CTMD_EXPOSURE = Struct('<HHHHL')
  NT_CTMD_EXPOSURE = namedtuple('ctmd_exposure', 'f_num f_denum expo_num expo_denum iso')

  def parse(self, data ):
    self.ctmd_list = OrderedDict()
    pic_num = 0
    for file_offset, ctmd_size in zip( cr3['trak4'][b'co64'], cr3['trak4'][b'stsz'] ): #for all pictures in roll
      ctmd_data = data[ file_offset: file_offset+ctmd_size ]  
      ctmd_offset = 0
      ctmd_records = dict()
      for type, size in self.index_list: #contains type and size
        ctmd_record = ctmd_data[ ctmd_offset: ctmd_offset+size ]
        record_size, record_type, _, _, _, _ = Ctmd.S_CTMD_RECORD_HEADER.unpack_from( ctmd_record, 0)
        if record_size!=size or record_type!=type:
          print('warning CMDT type:%d/%d size:0x%x/0x%x' % (type, record_type, size, record_size ) )
        if record_type in Ctmd.CTMD_TIFF_TYPES:
          record_offset = Ctmd.S_CTMD_RECORD_HEADER.size #inside the record
          ctmd_tiff = dict()
          while record_offset < record_size:
            payload_size, payload_tag = Ctmd.S_CTMD_TIFF_HEADER.unpack_from( ctmd_record, record_offset )
            tiff = TiffIfd( ctmd_record[ record_offset+Ctmd.S_CTMD_TIFF_HEADER.size: ], payload_size, file_offset+ctmd_offset+record_offset+Ctmd.S_CTMD_TIFF_HEADER.size, b'CTMD%d_0x%x'%(record_type, payload_tag), False) 
            ctmd_tiff[ payload_tag ] =  (file_offset+ctmd_offset+record_offset, payload_size, payload_tag, (record_offset+Ctmd.S_CTMD_TIFF_HEADER.size, tiff) )  
            record_offset += payload_size
          ctmd_records[type] = Ctmd.NT_CTMD_RECORD(size, type, file_offset+ctmd_offset, ctmd_tiff)  #store context and TIFF entries		
        else:
          if record_type == Ctmd.CTMD_TYPE_TIMESTAMP:
            _, y, mo, d, h, m, s, ms = Ctmd.S_CTMD_TIMESTAMP.unpack_from( ctmd_record, Ctmd.S_CTMD_RECORD_HEADER.size )
            ctmd_records[type] = Ctmd.NT_CTMD_RECORD( size, type, file_offset+ctmd_offset, Ctmd.NT_CTMD_TIMESTAMP( y, mo, d, h, m, s, ms ) )
          elif record_type == Ctmd.CTMD_TYPE_EXPOSURE:
            f_num, f_denum, expo_num, expo_denum, iso = Ctmd.S_CTMD_EXPOSURE.unpack_from( ctmd_record, Ctmd.S_CTMD_RECORD_HEADER.size )
            ctmd_records[type] = Ctmd.NT_CTMD_RECORD( size, type, file_offset+ctmd_offset, Ctmd.NT_CTMD_EXPOSURE ( f_num, f_denum, expo_num, expo_denum, iso ) )   
          elif record_type == Ctmd.CTMD_TYPE_FOCAL:
            num, denum = Ctmd.S_CTMD_FOCAL.unpack_from( ctmd_record, Ctmd.S_CTMD_RECORD_HEADER.size )
            ctmd_records[type] = Ctmd.NT_CTMD_RECORD( size, type, file_offset+ctmd_offset, Ctmd.NT_CTMD_FOCAL ( num, denum ) )
          else:        
            ctmd_records[type] = Ctmd.NT_CTMD_RECORD( size, type, file_offset+ctmd_offset, None) #do not store content, but type, size and pointer for later processing
        ctmd_offset += size
      self.ctmd_list[ pic_num ] =  ctmd_records  
      pic_num += 1      
    return self.ctmd_list	

  def display(self):
    for pic_num, ctmd in self.ctmd_list.items():
      #generic way to list CTMD entries
      for ctmd_record in ctmd.values():
        print('offset=0x%x, size=%d, type=%d: ' % (ctmd_record.offset, ctmd_record.size, ctmd_record.type ), end='' ) 
        if ctmd_record.type in Ctmd.CTMD_TIFF_TYPES: #TIFF
          print('list')
          for subdir_tag, tiff_subdir in ctmd_record.content.items():
            offset, payload_size, payload_tag, entries = tiff_subdir
            print('  0x%04x: size=%d tag=0x%x offset_base=%x' % (offset, payload_size, payload_tag, entries[0]) )
            entries[1].display( 1 )  
        else: #not TIFF
          if ctmd_record.type in [ Ctmd.CTMD_TYPE_TIMESTAMP, Ctmd.CTMD_TYPE_EXPOSURE, Ctmd.CTMD_TYPE_FOCAL ]:
            print( ctmd_record.content )
          else:
            ctmd_data = data[ ctmd_record.offset: ctmd_record.offset+ctmd_record.size] #we do not know how to parse it
            print('%s' % hexlify(ctmd_data) )
      

def getIfd(name, details): # details is dict with 'picture', 'type', 'tag'
  if name in { b'CMT1', b'CMT2', b'CMT3', b'CMT4', b'CMTA' }:
    return cr3[name][1]
  elif name== b'CTMD':   
    if 'picture' in details:
      pic_num = details[ 'picture' ]
    else:
      pic_num = 0   
    ctmd = cr3[b'CTMD'].ctmd_list[ pic_num ]  
    if 'type' in details:
      if details[ 'type' ] in Ctmd.CTMD_TIFF_TYPES:
        for ctmd_record in ctmd.values():
          if ctmd_record.type == details[ 'type' ]:
            for subdir_tag, tiff_subdir in ctmd_record.content.items():
              offset, payload_size, payload_tag, entries = tiff_subdir
              if details[ 'tag' ] == payload_tag:
                return entries[1]
  return None                 
    
#CTMD INDEX, content is in mdat
def ctmd(d, l, depth, base, name):
  if not options.quiet:
    print('CTMD: (0x{:x})'.format(l) ) 
  _ctmd = Ctmd(d, l, base, name) #parse index
  if options.verbose>0:
    print('     %s %d' % (depth*'  ',len(_ctmd.index_list)))
  for i in _ctmd.index_list:
    if options.verbose>0:
      print('       %s %d 0x%x' % (depth*'  ',i.type, i.size) )
  return _ctmd

#to parse Canon CR3 ISO Base File format 
def ftyp(b, d, l, depth):
  major_brand = d[:4]
  minor_version = getLongBE(d, 4)
  compatible_brands = []
  for e in range( (l-(4*4))//4 ):
    compatible_brands.append( d[8+e*4:8+e*4+4] )
  if not options.quiet:
    print( "ftyp: major_brand={0}, minor_version={1}, {2} (0x{3:x})".format(major_brand,minor_version,compatible_brands, l )  )
  
def moov(b, d, l, depth):
  if not options.quiet:
    print('moov: (0x%x)'%l)

def uuid(b, d, l, depth):
  uuidValue = d[:16]
  if not options.quiet:
    print('{1}uuid: {0} (0x{2:x})'.format(hexlify(uuidValue), '', l))
  return uuidValue  

def stsz(b, d, l, depth):
  S_STSZ = Struct('>BBBBLL') #size==12
  version, f1, f2, f3, size, count = S_STSZ.unpack_from(d, 0) 
  flags = f1<<16 | f2<<8 | f3
  size_list = []
  if size!=0:
    for s in range(count):
      size_list.append( size )  
  else: 
    for s in range(count):
      sample_size = getLongBE(d, 12+s*4)
      size_list.append( sample_size )
  if not options.quiet:
    print( "stsz: version={0}, size=0x{1:x}, count={2} (0x{3:x})\n      {4}".format(version, size, count, l, depth*'  '), end='' )
    for s in size_list:
      print('0x%x ' % s, end='')
    print()  
  return size_list
  
def co64(b, d, l, depth):
  version = getLongBE(d, 0)
  count = getLongBE(d, 4)
  offset_list = []
  for o in range(count):
    offset_list.append( getLongLongBE(d, 8+o*8) )
  if not options.quiet:
    print( "co64: version={0}, count={1} (0x{2:x})\n      {3}".format(version, count, l, depth*'  ' ), end=''  )
    for s in offset_list:
      print('0x%x ' % s, end='')
    print()  
  return offset_list
  
S_PRVW = Struct('>LHHHHL')
def prvw(b, d, l, depth):
  NT_PRVW = namedtuple('prvw', 'w h size')
  _, _, w, h, _, jpegSize = S_PRVW.unpack_from(d, 0)
  _prvw = NT_PRVW( w, h, jpegSize)
  if not options.quiet:
    print( "PRVW: width={0}, height={1}, jpeg_size=0x{2:x} (0x{3:x})".format( w, h, jpegSize, l )  )
  return _prvw
  
S_THMB = Struct('>LHHLHH')
def thmb(b, d, l, depth):
  NT_THMB = namedtuple('thmb', 'w h size')
  _, w, h, jpegSize, _, _ = S_THMB.unpack_from(d, 0)
  _thmb = NT_THMB( w, h, jpegSize)
  if not options.quiet:
    print( "THMB: width={0}, height={1}, jpeg_size=0x{2:x} (0x{3:x})".format( w, h, jpegSize, l )  )
  return _thmb
  
CTBO_LINE_LEN = 20  
def ctbo(b, d, l, depth):
  if not options.quiet:
    print( 'CTBO: (0x{0:x})'.format(l) )
  S_CTBO_LINE = Struct('>LQQ')
  NT_CTBO_LINE = namedtuple('ctbo_line', 'index offset size')
  nbLine = getLongBE( d, 0 )
  offsetList = {}
  for n in range( nbLine ):
    idx, offset, size = S_CTBO_LINE.unpack_from( d, 4 + n*S_CTBO_LINE.size ) 
    _ctbo_line = NT_CTBO_LINE( idx, offset, size )
    if not options.quiet:
      print('      %s%x %7x %7x' % (depth*'  ', _ctbo_line.index, _ctbo_line.offset, _ctbo_line.size) )
    offsetList[idx] = _ctbo_line
  return offsetList  
    

def cncv(b, d, l, depth):    
  if not options.quiet:
    print('CNCV: {0} (0x{1:x})'.format(d, l) ) 
  return d[:]

def cdi1(b, d, l, depth):    
  if not options.quiet:
    print('CDI1: (0x{:x})'.format(l) ) 
  if options.verbose>0:
    print('      %s'% (depth*'  '),end='')
    for i in range(0, 4, 2):
      print('%d,' % getShortBE(d, i),end='')
    print()  

def iad1(b, d, l, depth):    
  if not options.quiet:
    print('IAD1: (0x{:x})'.format(l) ) 
  if options.verbose>0:
    print('      %s'% (depth*'  '),end='')
    for i in range(0,len(d), 2):
      print('%d,' % getShortBE(d, i),end='')
    print()  

#offset does start after name, thus +8 when including size (long) and name (4*char)	
def cmp1(b, d, l, depth):    
  S_CMP1 = Struct('>HHHHLLLLBBBBL') 
  NT_CMP1 = namedtuple('cmp1', 'iw ih tw th d p cfa extra wl b35 hsize')
  if not options.quiet:
    print('CMP1: (0x{:x})'.format(l) ) 
  _, size, version, _, iw, ih, tw, th, _32, _33, _34, b35, hsize = S_CMP1.unpack_from(d, 0)
  bits = int(_32)
  planes = int(_33)>>4
  cfa = int(_33)&0xf
  extra = int(_34)>>4
  wavelets = int(_34)&0xf
  cmp = NT_CMP1(iw, ih, tw, th, bits, planes, cfa, extra, wavelets, b35, hsize)
  return cmp	
  
def craw(b, d, l, depth):
  S_CRAW = Struct('>LL16sHHHHHHLH32sHHHH')
  NT_CRAW = namedtuple('craw', 'w h bits')
  _, _, _, w, h, _, _, _, _, _, _, _, bits, _, _, _ = S_CRAW.unpack_from(d, 0)
  #print(S_CRAW.unpack_from(d, 0))
  _craw = NT_CRAW( w, h, bits)
  #print(_craw)
  if not options.quiet:
    print( "CRAW: (0x{0:x})".format(l) )
    print('      %swidth=%d, height=%d, bits=%d' % (depth*'  ', w, h, bits) )
  return _craw

def cnop(b, d, l, depth):
  if not options.quiet:
    print( "CNOP: (0x{0:x})".format(l) )
  return

    
CRX_HDR_LINE_LEN = 12  

def parse_ff03(d, total):
  offset = 0
  ff03_list = []
  while total > 0:
    v1 = getLongBE( d, offset )
    if v1!= 0xff030008: 
      return
    v2 = getLongBE( d, offset+4 ) 
    v3 = getLongBE( d, offset+8 )
    c     = (v3 & 0xf0000000)>>28
    f     = (v3 & 0x08000000)>>27
    val8  = (v3 & 0x07f80000)>>19
    val13 = (v3 & 0x0007ffff)
    #print('    %08x %08x %08x'%(v1,v2,v3))
    #print('    %08x %08x %d %x %02x %05x'%(v1,v2,c,f,val8,val13))
    total = total - v2
    offset = offset + CRX_HDR_LINE_LEN
    ff03_list.append( (v2,c,f,val8,val13) )
  return offset, ff03_list  

def parse_ff02(d, total):
  offset = 0
  ff02_list = []
  while total > 0:    
    v1 = getLongBE( d, offset )
    if v1!= 0xff020008: 
      return
    _ff02 = dict()  
    v2 = getLongBE( d, offset+4 ) #total of next ff03 group
    v3 = getLongBE( d, offset+8 )
    c     = (v3 & 0xf0000000)>>28
    f     = (v3 & 0x08000000)>>27
    val2  = (v3 & 0x06000000)>>25
    res     = (v3 & 0x01ffffff)
    #print('  %08x %08x %08x'%(v1,v2,v3))
    #print('  %08x %08x %d %x %x %07x'%(v1,v2,c,f,val2, r))
    total = total - v2
    offset = offset + CRX_HDR_LINE_LEN
    delta, r = parse_ff03(d[offset:], v2)
    ff02_list.append( (v2,c,f,val2,res,r) )
    offset = offset + delta
  return offset, ff02_list  
  
#header size can be retrieved from CMP1     
def parse_crx(d, base):
  offset = 0 #offset inside header
  dataOffset = 0
  v1 = getLongBE( d, offset )
  ff01_list = []  
  while v1 == 0xff010008: 
    #print('offset=%x'%offset)
    v2 = getLongBE( d, offset+4 ) #total of next ff02 group
    v3 = getLongBE( d, offset+8 )
    i = (v3 & 0xff0000)>>16
    #print('  %08x %08x %08x'%(v1,v2,v3))
    offset = offset + CRX_HDR_LINE_LEN
    delta, r = parse_ff02(d[offset:], v2)
    ff01_list.append( (v2,i,r) )
    #print('delta %x'%delta)
    offset = offset + delta
    v1 = getLongBE( d, offset )
  #print('%x' % offset)
  if len(ff01_list)<2:
    dataOffset = offset + 4
  else:  
    dataOffset = offset
  for ff01 in ff01_list:
    if options.verbose>1:
      print('ff01 %08x %d ' % (ff01[0], ff01[1]) )
    in_ff01 = 0
    for ff02 in ff01[2]: #r
      if options.verbose>1:
        print('  ff02 %08x %d %x %x %07x' % (ff02[0], ff02[1], ff02[2],ff02[3],ff02[4]) )
      in_ff02 = 0
      for ff03 in ff02[5]: #r
        if options.verbose>1:
          print('    ff03 %08x %d %x %02x %05x' % (ff03[0], ff03[1], ff03[2], ff03[3], ff03[4]) )
          print('      %s (%x)' % (hexlify(d[dataOffset:dataOffset+32]), base+dataOffset) )
        dataOffset = dataOffset + ff03[0]
        in_ff02 = in_ff02 + ff03[0]
      if in_ff02 != ff02[0]:
        print('in_ff02 != ff02[0], %x != %x' % (in_ff02, ff02[0]) )      
      in_ff01 = in_ff01 + ff02[0]
    if in_ff01 != ff01[0]:
      print('in_ff01 != ff01[0], %x != %x' % (in_ff01, ff01[0]) )

    if options.verbose>1:
      print('end: 0x%x' % (dataOffset+base))    
  return dataOffset+base, dataOffset
  
tags = { b'ftyp':ftyp, b'moov':moov, b'uuid':uuid, b'stsz':stsz, b'co64':co64, b'PRVW':prvw, b'CTBO':ctbo, b'THMB':thmb, b'CNCV':cncv,
         b'CDI1':cdi1, b'IAD1':iad1, b'CMP1':cmp1, b'CRAW':craw, b'CNOP':cnop }  

innerOffsets = { b'CRAW': 0x52, b'CCTP':12, b'stsd':8, b'dref':8, b'CDI1':4 }         
         
count = dict()
#keep important values
cr3 = dict()

NAMELEN = 4
SIZELEN = 4
UUID_LEN = 16
#base for this atom (length will be added to this base)
#o = offset inside
#no = next offset after name and length 
def parse(offset, d, base, depth):
  o = 0
  #print('base=0x%x offset=0x%x'% (base, offset))
  while o < len(d):
    l = getLongBE(d, o)
    chunkName = d[o+SIZELEN:o+SIZELEN+NAMELEN]
    no = SIZELEN+NAMELEN #next offset to look for data
    if l==1:
      l = getLongLongBE(d, o+SIZELEN+NAMELEN)
      no = SIZELEN+NAMELEN+8
    dl = min(32, l) #display length
    if not options.quiet:
      print( '%05x:%s' % (base+o, depth*'  '), end=''  )
    
    if chunkName not in count: #enumerate atom to create unique ID
      count[ chunkName ] = 1
    else:  
      count[ chunkName ] = count[ chunkName ] +1
    if chunkName == b'trak':  #will keep stsz and co64 per trak
      trakName = 'trak%d' % count[b'trak']
      if trakName not in cr3:
        cr3[ trakName ] = dict()    
      
    if chunkName in tags: #dedicated parsing
      r = tags[chunkName](base, d[o+no:o+no +l-no], l, depth+1) #return results
    elif chunkName in { b'CMT1', b'CMT2', b'CMT3', b'CMT4', b'CMTA' }:
      tiff = TiffIfd( d[o+no:o+no +l-no], l, base+o+no, chunkName, False )
      cr3[ chunkName ] = ( base+o+no, tiff )
      if options.verbose>1:
        tiff.display( depth+1 ) 
    elif chunkName == b'CTMD':
      r = ctmd( d[o+no:o+no +l-no], l, depth+1, base+o+no, chunkName )
      cr3[ chunkName ] = r 
    else:
      if not options.quiet:
        print( '%s %s (0x%x)' % ( repr(chunkName), hexlify(d[o+no:o+no +dl-no]), l )  ) #default
       
    if chunkName in { b'moov', b'trak', b'mdia', b'minf', b'dinf', b'stbl' }: #requires inner parsing, just after the name
      parse( offset+o+no, d[o+no:o+no +l-no], base+o+no, depth+1)
    elif chunkName == b'uuid':  #inner parsing at specific offsets after name
      uuidValue = d[ o+no: o+no +UUID_LEN ] #it depends on uuid values
      if uuidValue == unhexlify('85c0b687820f11e08111f4ce462b6a48') or uuidValue == unhexlify('5766b829bb6a47c5bcfb8b9f2260d06d') or uuidValue == unhexlify('210f1687914911e4811100242131fce4'):
        parse(offset+o+no+UUID_LEN, d[o+no+UUID_LEN:o+no+UUID_LEN +l-no-UUID_LEN], base+o+no+UUID_LEN, depth+1)
      elif uuidValue == unhexlify('eaf42b5e1c984b88b9fbb7dc406e4d16'):
        parse(offset+o+no+UUID_LEN+8, d[o+no+UUID_LEN+8:o+no+UUID_LEN+8 +l-no-8-UUID_LEN], base+o+no+UUID_LEN+8, depth+1)
    elif chunkName in innerOffsets: #it depends on chunkName
      start = o+no+innerOffsets[chunkName]
      end = start +l-no-innerOffsets[chunkName]
      parse( offset+start, d[start:end], start, depth+1 )
      
    #post processing  
    if chunkName == b'stsz' or chunkName == b'co64' or chunkName == b'CRAW' or chunkName == b'CMP1':  #keep these values per trak
      trakName = 'trak%d' % count[b'trak']
      cr3[ trakName ][ chunkName ] = r
    elif chunkName == b'CNCV' or chunkName == b'CTBO':  
      cr3[ chunkName ] = r
    elif chunkName == b'PRVW' or chunkName == b'THMB':
      cr3[ chunkName ] = base+o+no, r  #save chunk offset
    elif chunkName == b'uuid':
      if uuidValue == unhexlify('210f1687914911e4811100242131fce4'):
        cr3[ uuidValue ] = o #save offset    
    o += l  
  return o

  
parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-v", "--verbose", type="int", dest="verbose", help="verbose level", default=0)
parser.add_option("-x", "--extract", action="store_true", dest="extract", help="extract embedded images", default=False)
parser.add_option("-m", "--model", action="store_true", dest="model", help="display model info", default=False)
parser.add_option("-q", "--quiet", action="store_true", dest="quiet", help="do not display CR3 tree", default=False)
parser.add_option("-c", "--ctmd", action="store_true", dest="display_ctmd", help="display CTMD", default=False)
parser.add_option("-p", "--picture", type="int", dest="pic_num", help="specific picture, default is 0", default=0)
(options, args) = parser.parse_args()

if options.verbose>0:
  options.quiet = False

f = open(args[0], 'rb')
data = f.read()
filesize = f.tell()
f.close()
if options.verbose>0:
  print( 'filesize 0x%x' % filesize)
  
if data[4:12]==b'ftypcrx ':
  offset = parse(0, data, 0, 0)
  if options.verbose>0:
    print('end of parsing offset: %05x:'%offset)
elif data[:4]==b'II*\x00' and data[8:12]==b'CR\x02\x00':
  print('CR2')
  cr2 = Cr2( data, filesize, 'cr2' )
  if options.verbose>1:
    cr2.display()
  if options.extract:
    cr2.extract_pic0('ifd0.jpg')
    cr2.extract_pic1('ifd1.jpg')
    cr2.extract_pic2('ifd2.ppm')
  print('modelId = 0x%x' % cr2.get_model_id() ) 
  print('modelName = %s' % cr2.get_model_name() ) 
  cr2.get_lossless_info()
  sys.exit()
    
if cr3[b'CNCV'].find(b'CanonCRM')>=0:
  if options.verbose>0:
    print('CRM')
  video = data[ cr3[b'CTBO'][3][0]+0x50: cr3[b'CTBO'][3][0]+cr3[b'CTBO'][3][1]-0x50]
  if options.verbose>2:  
    parse_crx( video, cr3[b'CTBO'][3][0]+0x50 )  
elif cr3[b'CNCV'].find(b'CanonCR3')>=0:
  if options.verbose>0:
    print('CR3')
  if options.extract:
    trak_list = [ 'trak1' ,'trak2', 'trak3', 'trak5' ]
    trak_msg = [ 'jpg%02d.jpg', 'sd%02d_crx.bin', 'hd%02d_crx.bin', 'dp%02d_crx.bin' ] 
    for trak, msg in zip(trak_list, trak_msg):
      if trak in cr3:
        for offset, size, index in zip( cr3[trak][b'co64'], cr3[trak][b'stsz'], range( len(cr3[trak][b'co64']) ) ):
          filename = msg % (index)
          if options.verbose>0:
            print('extracting %s (%s) %dx%d from mdat... offset=0x%x, size=0x%x (ends at 0x%x)' % ( filename, trak, cr3[trak][b'CRAW'][0], cr3[trak][b'CRAW'][1], offset, size, offset+size) )
          picture = data[ offset: offset+size ] 
          f = open( filename,'wb' )
          f.write( picture )
          f.close()
    if b'THMB' in cr3:      
      offset = cr3[b'THMB'][0]
      jpegSize = cr3[b'THMB'][1].size
      f = open('thmb.jpg','wb')
      f.write( data[ offset+S_THMB.size: offset+S_THMB.size+jpegSize ])
      f.close()  
    if b'PRVW' in cr3:
      offset = cr3[b'PRVW'][0]
      jpegSize = cr3[b'PRVW'][1].size
      f = open('prvw.jpg','wb')
      f.write( data[ offset+S_PRVW.size: offset+S_PRVW.size+jpegSize ] )
      f.close()

  _ctmd = cr3[b'CTMD']  
  _ctmd.parse( data )  
  if options.display_ctmd:
    _ctmd.display( )
    
  #print(cr3)


  #now we want raw data of TIFF entry 0x4016 (TIFF_CANON_VIGNETTING_CORR2), in subdir TIFF_MAKERNOTE, in CTMD record #7. We know it is type=4=long, little endian 32 bits
  ctmd_makernote7 = getIfd( b'CTMD', { 'type':7, 'tag':TiffIfd.TIFF_MAKERNOTE } ) #picture 0 by default
  if TiffIfd.TIFF_CANON_VIGNETTING_CORR2 in ctmd_makernote7.ifd:
    vignetting_corr2 = ctmd_makernote7.ifd[ TiffIfd.TIFF_CANON_VIGNETTING_CORR2 ]
    r = Struct('<%dL' % vignetting_corr2.length).unpack_from( data, ctmd_makernote7.base+vignetting_corr2.value )
  if options.verbose>1:
    print(r)

  cmt3 = getIfd( b'CMT3', None )
  if TiffIfd.TIFF_MAKERNOTE_ROLLINFO in cmt3.ifd: # only in CSI_* files (raw burst mode)
    rollInfoTag = cmt3.ifd[ TiffIfd.TIFF_CMT3_ROLLINFO ]
    #print( rollInfoTag )
    length, current, total = Struct('<%d%s' % (rollInfoTag.length, TiffIfd.tiffTypeStr[rollInfoTag.type-1])).unpack_from( data, cmt3.base+rollInfoTag.value )
    #exif IFD for current picture in the roll
    ifd = getIfd( b'CTMD', { 'picture':current, 'type':7, 'tag':TiffIfd.TIFF_MAKERNOTE } )
    ifd.display()
    
  NT_SENSOR_INFO = namedtuple('sensorInfo','w h lb tb rb bb')
  sensorInfo = cmt3.ifd[ TiffIfd.TIFF_MAKERNOTE_SENSORINFO ]
  _, SensorWidth, SensorHeight, _, _, SensorLeftBorder, SensorTopBorder, SensorRightBorder, SensorBottomBorder, *_ = Struct('<%d%s' % (sensorInfo.length, TiffIfd.tiffTypeStr[sensorInfo.type-1])).unpack_from( data, cmt3.base+sensorInfo.value )
  sensorInfo = NT_SENSOR_INFO( SensorWidth, SensorHeight, SensorLeftBorder, SensorTopBorder, SensorRightBorder, SensorBottomBorder )
  if options.verbose>1:
    print(sensorInfo)
  
  #get camera settings to find if it is a craw (lossy) or raw (lossless)
  cameraSettings = cmt3.ifd[ TiffIfd.TIFF_MAKERNOTE_CAMERASETTINGS ]
  cameraSettingsList = Struct('<%d%s' % (cameraSettings.length, TiffIfd.tiffTypeStr[cameraSettings.type-1])).unpack_from( data, cmt3.base+cameraSettings.value )
  if options.verbose>0:
    if cameraSettingsList[3]==TiffIfd.TIFF_CAMERASETTINGS_QUALITY_CRAW:
      print('craw')
    elif cameraSettingsList[3]==TiffIfd.TIFF_CAMERASETTINGS_QUALITY_RAW:
      print('raw')
    else:
      print('cameraSettingsList[3]=%d'%cameraSettingsList[3]) 

  #get model name and model Id
  modelId = cmt3.ifd[ TiffIfd.TIFF_MAKERNOTE_MODELID ].value 
  if options.verbose>1:
    print('modelId: 0x%x' % modelId)

  cmt1 = getIfd( b'CMT1', None )
  modelNameEntry = cmt1.ifd[ TiffIfd.TIFF_EXIF_Model ]
  modelName = Struct('<%ds' % (modelNameEntry.length-1) ).unpack_from( data, cmt1.base+modelNameEntry.value ) [0]
  if options.verbose>0:
    print(modelName) #use length value (modelEntry[2]) of TIFF entry for model

  if TiffIfd.TIFF_MAKERNOTE_DUST_DELETE_DATA in cmt3.ifd:
    dustDeleteData = cmt3.ifd[ TiffIfd.TIFF_MAKERNOTE_DUST_DELETE_DATA ]
    dddData = data[ cmt3.base+dustDeleteData.value: cmt3.base+dustDeleteData.value+dustDeleteData.length ]
    S_DDD_V1 = Struct('<BBHHHHHHHHHHHBBBBBBBBBB')     # http://lclevy.free.fr/cr2/#ddd
    NT_DDD = namedtuple('ddd', 'version lensinfo av po count focal lensid w h rw rh pitch lpfdist toff boff loff roff y mo d ho mi diff')
    S_DUST = Struct('<HHBB')
    NT_DUST = namedtuple('dust', 'w h size')
    version = int( dddData[0] )
    if version==1:
      l = S_DDD_V1.unpack_from( dddData[:S_DDD_V1.size], 0)
      ddd = NT_DDD( *l )
      if options.verbose>1:
        print(ddd)
      for dust in range(ddd.count):
        w, h, size, _ = S_DUST.unpack_from( dddData[S_DDD_V1.size:], dust*S_DUST.size )
        if options.verbose>1:
          print( NT_DUST(w, h, size) ) 
          # for EOS R, version 2?

  if options.model:
 	  # modelId, SensorWidth, SensorHeight, CrxBigW, CrxBigH, CrxBigSliceW, CrxSmallW, CrwSmallH, JpegBigW, JpegBigH, JpegPrvwW, JpegPrvwH
    print('0x%08x, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d' % (modelId, SensorWidth, SensorHeight, cr3['trak3'][b'CRAW'].w,cr3['trak3'][b'CRAW'].h, 
	  cr3['trak3'][b'CMP1'].tw,
	  cr3['trak2'][b'CRAW'].h,cr3['trak2'][b'CRAW'].w, cr3['trak1'][b'CRAW'].h,cr3['trak1'][b'CRAW'].w, cr3[b'PRVW'][1].w, cr3[b'PRVW'][1].h) )

  #print cmp1 for each crx track     
  if options.verbose>1:
    for t in ['trak2', 'trak3', 'trak5']:
      if t in cr3:
        print( t, cr3[ t ][b'CMP1'] )


  #to check for additionnal crx (raw burst roll). oops stored in stsz and co64
  '''
  if 'trak5' in cr3: #end of main CRX data
    crx_offset = cr3['trak5'][b'co64']+cr3['trak5'][b'stsz'][0]
  else:
    crx_offset = cr3['trak3'][b'co64']+cr3['trak3'][b'stsz'][0]
  crx_num = 0  
  while crx_offset < cr3['trak4'][b'co64']: #ends at CTMD 
    print('additionnal crx#%d at 0x%x, ' % (crx_num, crx_offset), end='')
    crx_offset, crx_size = parse_crx( data[crx_offset:], crx_offset)
    print('size= 0x%x' % crx_size)
    crx_num += 1
    '''


else:
  print('unknown codec')
  sys.exit()  