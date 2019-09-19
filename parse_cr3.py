# parse CR3 file format from Canon (@lorenzo2472)
# from https://github.com/lclevy/canon_cr3
# tested with Python 3.6.7
# about ISO Base file format : https://stackoverflow.com/questions/29565068/mp4-file-format-specification
# License is GPLv3 

import sys
from struct import unpack, Struct
from binascii import hexlify, unhexlify
from optparse import OptionParser
from collections import namedtuple

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

def ftyp(b, d, l, depth):
  major_brand = d[:4]
  minor_version = getLongBE(d, 4)
  compatible_brands = []
  for e in range( (l-(4*4))//4 ):
    compatible_brands.append( d[8+e*4:8+e*4+4] )
  print( "ftyp: major_brand={0}, minor_version={1}, {2} (0x{3:x})".format(major_brand,minor_version,compatible_brands, l )  )
  
def moov(b, d, l, depth):
  print('moov: (0x%x)'%l)

def uuid(b, d, l, depth):
  uuidValue = d[:16]
  print('{1}uuid: {0} (0x{2:x})'.format(hexlify(uuidValue), '', l))

S_STSZ = Struct('>BBBBLL') #size==12

def stsz(b, d, l, depth):
  version, f1, f2, f3, size, count = S_STSZ.unpack_from(d, 0) #count is always 1, even if table is empty (size 0x14)
  flags = f1<<16 | f2<<8 | f3
  size_list = []
  print( "stsz: version={0}, size=0x{1:x}, count={2} (0x{3:x})\n      {4}".format(version, size, count, l, depth*'  '), end='' )
  if size!=0:
    for s in range(count):
      size_list.append( size )  
  else: 
    for s in range(count):
      sample_size = getLongBE(d, 12+s*4)
      size_list.append( sample_size )
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
  print( "co64: version={0}, count={1} (0x{2:x})\n      {3}".format(version, count, l, depth*'  ' ), end=''  )
  for s in offset_list:
    print('0x%x ' % s, end='')
  print()  
  return offset_list
  
def prvw(b, d, l, depth):
  S_PRVW = Struct('>LHHHHL')
  NT_PRVW = namedtuple('prvw', 'w h size')
  _, _, w, h, _, jpegSize = S_PRVW.unpack_from(d, 0)
  _prvw = NT_PRVW( w, h, jpegSize)
  if options.extract:
    f = open("prvw.jpg","wb")
    f.write(d[0x18-8:0x18-8+jpegSize])
    f.close()
  print( "PRVW: width={0}, height={1}, jpeg_size=0x{2:x} (0x{3:x})".format( w, h, jpegSize, l )  )
  return _prvw
  
def thmb(b, d, l, depth):
  S_THMB = Struct('>LHHLHH')
  NT_THMB = namedtuple('thmb', 'w h size')
  _, w, h, jpegSize, _, _ = S_THMB.unpack_from(d, 0)
  _thmb = NT_THMB( w, h, jpegSize)
  if options.extract:
    f = open("thmb.jpg","wb")
    f.write(d[0x18-8:0x18-8+jpegSize])
    f.close()
  print( "THMB: width={0}, height={1}, jpeg_size=0x{2:x} (0x{3:x})".format( w, h, jpegSize, l )  )
  return _thmb
  
CTBO_LINE_LEN = 20  
def ctbo(b, d, l, depth):
  S_CTBO_LINE = Struct('>LQQ')
  NT_CTBO_LINE = namedtuple('ctbo_line', 'index offset size')
  nbLine = getLongBE( d, 0 )
  offsetList = {}
  for n in range( nbLine ):
    idx, offset, size = S_CTBO_LINE.unpack_from( d, 4 + n*S_CTBO_LINE.size ) 
    _ctbo_line = NT_CTBO_LINE( idx, offset, size )
    print('      %s%x %7x %7x' % (depth*'  ', idx, offset, size) )
    offsetList[idx] = _ctbo_line
  return offsetList  
    

def cncv(b, d, l, depth):    
  print('CNCV: {0} (0x{1:x})'.format(d, l) ) 
  return d[:]

def cdi1(b, d, l, depth):    
  print('CDI1: (0x{:x})'.format(l) ) 
  if options.verbose>0:
    print('      %s'% (depth*'  '),end='')
    for i in range(0, 4, 2):
      print('%d,' % getShortBE(d, i),end='')
    print()  

def iad1(b, d, l, depth):    
  print('IAD1: (0x{:x})'.format(l) ) 
  '''if options.verbose>0:
    print('      %s'% (depth*'  '),end='')
    for i in range(0,len(d), 2):
      print('%d,' % getShortBE(d, i),end='')
    print()  '''

#offset does start after name, thus +8 when including size (long) and name (4*char)	
def cmp1(b, d, l, depth):    
  S_CMP1 = Struct('>HHHHLLLLBBBBL') 
  NT_CMP1 = namedtuple('cmp1', 'iw ih tw th d p cfa extra wl b35 hsize')
  print('CMP1: (0x{:x})'.format(l) ) 
  _, size, version, _, iw, ih, tw, th, _32, _33, _34, b35, hsize = S_CMP1.unpack_from(d, 0)
  bits = int(_32)
  planes = int(_33)>>4
  cfa = int(_33)&0xf
  extra = int(_34)>>4
  wavelets = int(_34)&0xf
  cmp = NT_CMP1(iw, ih, tw, th, bits, planes, cfa, extra, wavelets, b35, hsize)
  #print(cmp)

  return cmp	
  
def craw(b, d, l, depth):
  S_CRAW = Struct('>LL16sHHHHHHLH32sHHHH')
  NT_CRAW = namedtuple('craw', 'w h bits')
  print( "CRAW: (0x{0:x})".format(l) )
  _, _, _, w, h, _, _, _, _, _, _, _, bits, _, _, _ = S_CRAW.unpack_from(d, 0)
  #print(S_CRAW.unpack_from(d, 0))
  _craw = NT_CRAW( w, h, bits)
  #print(_craw)
  '''w = getShortBE( d, 24 )
  h = getShortBE( d, 26 )
  bits = getLongBE( d, 72 )'''
  print('      %swidth=%d, height=%d, bits=%d' % (depth*'  ', w, h, bits) )
  return _craw

def cnop(b, d, l, depth):
  print( "CNOP: (0x{0:x})".format(l) )
  return

class TiffIfd:
  #class for Tiff IFD (Canon kind)
  
  TIFF_CMT3_SENSORINFO = 0xe0  
  TIFF_CMT3_CAMERASETTINGS = 1
  TIFF_CAMERASETTINGS_QUALITY_RAW = 4
  TIFF_CAMERASETTINGS_QUALITY_CRAW = 7
  TIFF_CMT3_MODELID = 0x10
  TIFF_CMT1_MODEL = 0x110
  
  TIFF_MAKERNOTE = 0x927c
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
  tiffTypeNames = [ "uchar", "string", "ushort", "ulong", "urational", "char", "byteseq", "short", "long", "rational", "float4", "float8" ]

  S_IFD_ENTRY_REC = Struct('<HHLL')  
  NT_IFD_ENTRY = namedtuple('ifd_entry', 'offset tag type length value')

  def __init__(self, data, length, base, name, display=True):
    self.data = data
    self.length = length
    self.base = base
    self.name = name
    
    self.ifd = dict()
    if display:
      print( "{0}: (0x{1:x})".format(name, length) )
    self.order = data[0:2] #for a future MM compatible version ?
    if self.order!=b'II': #should raise exception
      print('order!=II')
      return
    marker = getShortLE( data, 2 )
    if marker != 0x2a:
      print('marker != 0x2a')
      return  
    ptr = getShortLE( data, 4 )
    n = getShortLE( data, ptr )
    ptr = ptr + 2
    for i in range(n):
      tag, type, length, val = TiffIfd.S_IFD_ENTRY_REC.unpack_from( data[ptr:ptr+TiffIfd.S_IFD_ENTRY_REC.size] )
      ifd_entry = TiffIfd.NT_IFD_ENTRY( self.base+ptr, tag, type, length, val )
      self.ifd[ tag ] = ifd_entry  
      ptr = ptr + TiffIfd.S_IFD_ENTRY_REC.size
      if self.base+ptr > self.base+self.length:
        print('base+ptr > base+length !')
   
  '''def ifd(self):
    return self.ifd'''

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
  
  def display( self, depth):
    for entry in self.ifd.values():
      print( "     %s 0x%06lx %5d/0x%-4x %9s(%d)*%-6ld %9lu/0x%-lx, " % (depth*'  ', entry.offset, entry.tag , entry.tag, TiffIfd.tiffTypeNames[entry.type-1],entry.type,entry.length,entry.value,entry.value), end='' )
      self.print_entry( entry.type, entry.length, entry.value, 20)
 
#CTMD INDEX, content is in mdat
def ctmd(d, l, depth, base, name):
  S_CTMD_INDEX_ENTRY = Struct('>LL')
  NT_CTMD_INDEX_ENTRY = namedtuple('ctmd_index_entry', 'type size')
  list = []
  print('CTMD: (0x{:x})'.format(l) ) 
  nb = getLongBE( d, 8 )
  if options.verbose>1:
    print('     %s %d' % (depth*'  ',nb))
  for i in range(nb):
    type = getLongBE( d, 12+i*8 )
    size = getLongBE( d, 16+i*8 )
    entry = NT_CTMD_INDEX_ENTRY( type, size )
    #list.append( (type, size) )
    list.append( entry )
    if options.verbose>1:
      print('       %s %d 0x%x' % (depth*'  ',type, size) )
  return list
    
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
      tiff = TiffIfd( d[o+no:o+no +l-no], l, base+o+no, chunkName )
      cr3[ chunkName ] = ( base+o+no, tiff.ifd )
      if options.verbose>1:
        tiff.display( depth+1 ) 


    elif chunkName == b'CTMD':
      r = ctmd( d[o+no:o+no +l-no], l, depth+1, base+o+no, chunkName )
      cr3[ chunkName ] = r 
    else:
      print( '%s %s (0x%x)' % ( repr(chunkName), hexlify(d[o+no:o+no +dl-no]), l )  ) #default
       
    if chunkName in { b'moov', b'trak', b'mdia', b'minf', b'dinf', b'stbl' }: #requires inner parsing, just after the name
      parse( offset+o+no, d[o+no:o+no +l-no], base+o+no, depth+1)
    elif chunkName == b'uuid':  #inner parsing at specific offsets after name
      uuidValue = d[o+no:o+no +UUID_LEN] #it depends on uuid values
      if uuidValue == unhexlify('85c0b687820f11e08111f4ce462b6a48'):
        parse(offset+o+no+UUID_LEN, d[o+no+UUID_LEN:o+no+UUID_LEN +l-no-UUID_LEN], base+o+no+UUID_LEN, depth+1)
      elif uuidValue == unhexlify('eaf42b5e1c984b88b9fbb7dc406e4d16'):
        parse(offset+o+no+UUID_LEN+8, d[o+no+UUID_LEN+8:o+no+UUID_LEN+8 +l-no-8-UUID_LEN], base+o+no+UUID_LEN+8, depth+1)
      elif uuidValue == unhexlify('5766b829bb6a47c5bcfb8b9f2260d06d') or uuidValue == unhexlify('210f1687914911e4811100242131fce4'):  
        parse(offset+o+no+UUID_LEN, d[o+no+UUID_LEN:o+no+UUID_LEN +l-no-UUID_LEN], base+o+no+UUID_LEN, depth+1)
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
      cr3[ chunkName ] = r, base+o+no+16 #save offset
    elif chunkName == b'uuid':
      if uuidValue == unhexlify('210f1687914911e4811100242131fce4'):
        cr3[ uuidValue ] = o #save offset    
    o += l  
  return o

def getTiffTagData(name, tag):
  tagEntry = cr3[name][1][tag]  
  #print(tagEntry)
  base = cr3[name][0]
  #print(base)
  size = TiffIfd.tiffTypeLen[tagEntry.type-1] * tagEntry.length
  tagInfoData = data[ base+tagEntry.value: base+tagEntry.value+size ]
  return tagInfoData, tagEntry

S_CTMD_RECORD = Struct('<HHLL')  
NT_CTMD_RECORD = namedtuple('ctmd_record', 'size type offset content')

def parseCTMD():
  #in trak4/'CTMD' (stored in cr3[b'CTMD']), we have types and size of CMTD records, but CMTD data is in 'mdat' section
  ctmd_list = []
  for file_offset, ctmd_size in zip( cr3['trak4'][b'co64'], cr3['trak4'][b'stsz'] ):
    ctmd_data = data[ file_offset: file_offset+ctmd_size ]  
    ctmd_offset = 0
    #file_offset = cr3['trak4'][b'co64'][0]
    ctmd_records = dict()
    for type, size in cr3[b'CTMD']: #contains type and size
      ctmd_record = ctmd_data[ ctmd_offset: ctmd_offset+size ]
      record_size = getLongLE( ctmd_record, 0 )
      record_type = getShortLE( ctmd_record, 4 )
      if record_size!=size or record_type!=type:
        print('warning CMDT type:%d/%d size:0x%x/0x%x' % (type, record_type, size, record_size ) )
      if record_type in [ 7, 8, 9 ]:
        record_offset = 12 #inside the record
        ctmd_tiff = dict()
        while record_offset < record_size:
          payload_size = getLongLE( ctmd_record[ record_offset: ], 0 )
          payload_tag = getLongLE( ctmd_record[ record_offset: ], 4 )
          tiff = TiffIfd( ctmd_record[ record_offset+8: ], payload_size, record_offset+8, b'CTMD%d_0x%x'%(record_type, payload_tag), False) 
          ctmd_tiff[ payload_tag ] =  (file_offset+ctmd_offset+record_offset, payload_size, payload_tag, (record_offset+8, tiff.ifd) )  
          record_offset += payload_size
        ctmd_records[type] = NT_CTMD_RECORD(size, type, file_offset+ctmd_offset, ctmd_tiff)  #store context and TIFF entries		
      else:
        '''if options.verbose>1:
          print('%d 0x%x 0x%x' % (int(record_type), record_size, file_offset+ctmd_offset))
          print('  ',hexlify(ctmd_record))'''
        ctmd_records[type] = NT_CTMD_RECORD(size, type, file_offset+ctmd_offset, None) #do not store content, but type, size and pointer for later processing
      ctmd_offset += size
    ctmd_list.append( ctmd_records )  
  return ctmd_list	

def displayCTMD(ctmd_list):
  print("CTMD parsing example")
  for ctmd in ctmd_list:
    #generic way to list CTMD entries
    for entry in [1, 3, 7, 8]:
      ctmd_record = ctmd[ entry ]
      print('offset=0x%x, size=%d, type=%d: ' % (ctmd_record.offset, ctmd_record.size, ctmd_record.type ), end='' ) 
      if ctmd_record.type in [ 7, 8, 9 ]: #TIFF
        print('list')
        for subdir_tag, tiff_subdir in ctmd_record.content.items():
          offset, payload_size, payload_tag, entries = tiff_subdir
          print('  0x%04x: size=%d tag=0x%x offset_base=%x' % (offset, payload_size, payload_tag, entries[0]) )
          for tag, ifd_entry in entries[1].items():
            #entry_offset, entry_type, entry_len, entry_value = ifd_entry
            #print( '    0x%04x: %5d/0x%-4x %d*%d %d/0x%x' % (entry_offset, tag, tag, entry_type, entry_len, entry_value, entry_value ) )
            print( '    0x%04x: %5d/0x%-4x %d*%d %d/0x%x' % (ifd_entry.offset, tag, tag, ifd_entry.type, ifd_entry.length, ifd_entry.value, ifd_entry.value ) )
      else: #not TIFF
        ctmd_data = data[ ctmd_record.offset: ctmd_record.offset+ctmd_record.size] #we do not know how to parse it
        print('%s' % hexlify(ctmd_data) )
  
parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-v", "--verbose", type="int", dest="verbose", help="verbose level", default=0)
parser.add_option("-x", "--extract", action="store_true", dest="extract", help="extract embedded images", default=False)
parser.add_option("-m", "--model", action="store_true", dest="model", help="display model info", default=False)
(options, args) = parser.parse_args()

f = open(args[0], 'rb')
data = f.read()
filesize = f.tell()
f.close()
print( 'filesize 0x%x' % filesize)

offset = parse(0, data, 0, 0)
print('%05x:'%offset)


if cr3[b'CNCV'].find(b'CanonCRM')>=0:
  print('CRM')
  video = data[ cr3[b'CTBO'][3][0]+0x50: cr3[b'CTBO'][3][0]+cr3[b'CTBO'][3][1]-0x50]
  if options.verbose>2:  
    parse_crx( video, cr3[b'CTBO'][3][0]+0x50 )  
elif cr3[b'CNCV'].find(b'CanonCR3')>=0:
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
  
  ctmd = parseCTMD()  
  if options.verbose>1:
    displayCTMD( ctmd )
  #print(cr3)

  #now we want raw data of TIFF entry 0x4016, in subdir TIFF_MAKERNOTE, in CTMD record #7. We know it is type=4=long, little endian 32 bits
  record_subdirs = ctmd[0][ 7 ][3] #first CTMD, type 7
  subdir = record_subdirs[ TiffIfd.TIFF_MAKERNOTE ][3] # (offset, list)
  subdir_offset = record_subdirs[ TiffIfd.TIFF_MAKERNOTE ][0]
  #entry_offset, entry_type, entry_len, entry_value = subdir[1][ 0x4016 ]
  ifd_entry = subdir[1][ TiffIfd.TIFF_CANON_VIGNETTING_CORR2 ]
  data_offset = subdir_offset + 8 + ifd_entry.value #TIFF_BASE is 8 bytes after TIFF subdir
  for i in range(data_offset, data_offset + TiffIfd.tiffTypeLen[ifd_entry.type-1]*ifd_entry.length, TiffIfd.tiffTypeLen[ifd_entry.type-1]):
    print ('%d ' % getLongLE(data, i), end='' )
  print()  


  NT_SENSOR_INFO = namedtuple('sensorInfo','w h lb tb rb bb')
  #get sensor characteristics
  sensorInfoData, sensorInfoEntry = getTiffTagData( b'CMT3', TiffIfd.TIFF_CMT3_SENSORINFO )  
  #for each TIFF entry, we have (offset, type, length, value). If value is a pointer, we use getTiffTagData() to get the content
  sensorInfoList = [ getShortLE(sensorInfoData, i) for i in range( 0, sensorInfoEntry.length, TiffIfd.tiffTypeLen[sensorInfoEntry.type-1] ) ]
  #print(sensorInfoList)
  _, SensorWidth, SensorHeight, _, _, SensorLeftBorder, SensorTopBorder, SensorRightBorder, SensorBottomBorder = sensorInfoList
  sensorInfo = NT_SENSOR_INFO( SensorWidth, SensorHeight, SensorLeftBorder, SensorTopBorder, SensorRightBorder, SensorBottomBorder )
  print(sensorInfo)
  #print(SensorWidth, SensorHeight, SensorLeftBorder, SensorTopBorder, SensorRightBorder, SensorBottomBorder)
  
  #get camera settings to find if it is a craw (lossy) or raw (lossless)
  cameraSettingsData, cameraSettingsEntry = getTiffTagData( b'CMT3', TiffIfd.TIFF_CMT3_CAMERASETTINGS )  
  cameraSettingsList = [ getShortLE(cameraSettingsData, i) for i in range( 0, cameraSettingsEntry.length, TiffIfd.tiffTypeLen[cameraSettingsEntry.type-1] ) ]
  if cameraSettingsList[3]==TiffIfd.TIFF_CAMERASETTINGS_QUALITY_CRAW:
    print('craw')
  elif cameraSettingsList[3]==TiffIfd.TIFF_CAMERASETTINGS_QUALITY_RAW:
    print('raw')
  else:
    print('cameraSettingsList[3]=%d'%cameraSettingsList[3]) 

  #get model name and model Id
  modelIdEntry = cr3[b'CMT3'][1][TiffIfd.TIFF_CMT3_MODELID] 
  modelData, modelEntry = getTiffTagData( b'CMT1', TiffIfd.TIFF_CMT1_MODEL )  
  print(modelData[:modelEntry.length-1]) #use length value (modelEntry[2]) of TIFF entry for model
  modelId = modelIdEntry.value
  #print(cr3[b'PRVW'])
  if options.model:
 	  # modelId, SensorWidth, SensorHeight, CrxBigW, CrxBigH, CrxBigSliceW, CrxSmallW, CrwSmallH, JpegBigW, JpegBigH, JpegPrvwW, JpegPrvwH
    print('0x%08x, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d' % (modelId, SensorWidth, SensorHeight, cr3['trak3'][b'CRAW'].w,cr3['trak3'][b'CRAW'].h, 
	  cr3['trak3'][b'CMP1'].tw,
	  cr3['trak2'][b'CRAW'].h,cr3['trak2'][b'CRAW'].w, cr3['trak1'][b'CRAW'].h,cr3['trak1'][b'CRAW'].w, cr3[b'PRVW'][0].w, cr3[b'PRVW'][0].h) )

  #print cmp1 for each crx track     
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