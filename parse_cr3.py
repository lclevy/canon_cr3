# parse CR3 file format from Canon (@lorenzo2472)
# from https://github.com/lclevy/canon_cr3
# samples from M50 camera here: http://www.photographyblog.com/reviews/canon_eos_m50_review/preview_images/, 
#   https://download.dpreview.com/canon_eosm50/M50_C-Raw_DPReview.zip
# CRM sample: http://www.4kshooters.net/2017/10/04/canon-c200-raw-footage-workflow-free-samples-for-download/
# about ISO Base file format : https://stackoverflow.com/questions/29565068/mp4-file-format-specification
# License is GPLv3 

import sys
from struct import unpack, Struct
from binascii import hexlify, unhexlify
from optparse import OptionParser


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

def ftyp(d, l, depth):
  major_brand = d[:4]
  minor_version = getLongBE(d, 4)
  compatible_brands = []
  for e in range( (l-(4*4))//4 ):
    compatible_brands.append( d[8+e*4:8+e*4+4] )
  print( "ftyp: major_brand={0}, minor_version={1}, {2} (0x{3:x})".format(major_brand,minor_version,compatible_brands, l )  )
  
def moov(d, l, depth):
  print('moov: (0x%x)'%l)

def uuid(d, l, depth):
  uuidValue = d[:16]
  print('{1}uuid: {0} (0x{2:x})'.format(hexlify(uuidValue), '', l))

def stsz(d, l, depth):
  version = getLongBE(d, 0)
  size = getLongBE(d, 4)
  count = getLongBE(d, 8)
  print( "stsz: version={0}, size=0x{1:x}, count={2} (0x{3:x})".format(version,size,count,l )  )
  return size
  
def co64(d, l, depth):
  version = getLongBE(d, 0)
  count = getLongBE(d, 4)
  size = getLongLongBE(d, 8)
  print( "co64: version={0}, size=0x{1:x}, count={2} (0x{3:x})".format(version,size,count, l )  )
  return size

def prvw(d, l, depth):
  w = getShortBE(d, 0xe-8)
  h = getShortBE(d, 0x10-8)
  jpegSize = getLongBE(d, 0x14-8)
  f = open("prvw.jpg","wb")
  f.write(d[0x18-8:0x18-8+jpegSize])
  f.close()
  print( "PRVW: width={0}, height={1}, jpeg_size=0x{2:x} (0x{3:x})".format( w, h, jpegSize, l )  )
  return w, h, jpegSize
  
def thmb(d, l, depth):
  w = getShortBE(d, 0xc-8)
  h = getShortBE(d, 0xe-8)
  jpegSize = getLongBE(d, 0x10-8)
  f = open("thmb.jpg","wb")
  f.write(d[0x18-8:0x18-8+jpegSize])
  f.close()
  print( "THMB: width={0}, height={1}, jpeg_size=0x{2:x} (0x{3:x})".format( w, h, jpegSize, l )  )
  return w, h, jpegSize
  
CTBO_LINE_LEN = 20  
def ctbo(d, l, depth):
  print( "CTBO: (0x{0:x})".format(l) )
  nbLine = getLongBE( d, 0 )
  offsetList = {}
  for n in range( nbLine ):
    idx = getLongBE( d, 4+n*CTBO_LINE_LEN )
    offset = getLongLongBE( d, 4+4+n*CTBO_LINE_LEN )
    size = getLongLongBE( d, 4+4+8+n*CTBO_LINE_LEN )
    print('      %s%x %7x %7x' % (depth*'  ', idx, offset, size) )
    offsetList[idx] = ( offset, size )
  return offsetList  
    

def cncv(d, l, depth):    
  print('CNCV: {0} (0x{1:x})'.format(d, l) ) 
  return d[:]

def cdi1(d, l, depth):    
  print('CDI1: (0x{:x})'.format(l) ) 
  if options.verbose>0:
    print('      %s'% (depth*'  '),end='')
    for i in range(0, 4, 2):
      print('%d,' % getShortBE(d, i),end='')
    print()  

def iad1(d, l, depth):    
  print('IAD1: (0x{:x})'.format(l) ) 
  '''if options.verbose>0:
    print('      %s'% (depth*'  '),end='')
    for i in range(0,len(d), 2):
      print('%d,' % getShortBE(d, i),end='')
    print()  '''

#offset does start after name, thus +8 when including size (long) and name (4*char)	
def cmp1(d, l, depth):    
  print('CMP1: (0x{:x})'.format(l) ) 
  w = getLongBE( d, 8 ) #16 in format description (readme.md)
  h = getLongBE( d, 12 )
  slice_w = getLongBE( d, 16 )
  crx_header_size = getLongBE( d, 28 )
  #print(w, h, slice_w, crx_header_size)
  return (w, h, slice_w, crx_header_size)	
  
def craw(d, l, depth):
  print( "CRAW: (0x{0:x})".format(l) )
  w = getShortBE( d, 24 )
  h = getShortBE( d, 26 )
  bits = getLongBE( d, 72 )
  print('      %swidth=%d, height=%d, bits=%d' % (depth*'  ', w, h, bits) )
  return (w,h)

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

def tiff_print_value(d, l, base, type, tl, val, max):
  typeLen = tiffTypeLen[type-1] 
  data2 = d[ val: val+min(tl,max)*typeLen ]
  if type == TIFF_TYPE_UCHAR or type == TIFF_TYPE_STRING:
    if tl < 5:
      print('%x'%val)
    else:  
      zero = data2.find(b'\x00')
      if zero!=-1:
        data2 = d[ val: val+zero ]
      print(data2)
  elif type == TIFF_TYPE_USHORT:
    if tl == 1:
      print('%hu'%val)
    else:
      for i in range(0, min(tl,max)*typeLen, typeLen):
        print( '%hu '%( getShortLE(data2, i) ), end='' )
      if tl>max:
        print('...')
      else:
        print()      
  elif type == TIFF_TYPE_ULONG:
    if tl == 1:
      print('%lu'%val)
    else:
      for i in range(0, min(tl,max)*typeLen, typeLen):
        print( '%lu '%( getLongLE(data2, i) ), end='' )
      if tl>max:
        print('...')
      else:
        print()  
  elif type == TIFF_TYPE_BYTESEQ:
    if tl < 5:
      print()    
    else:
      if tl>max:
        print(hexlify(data2), '...')
      else:
        print(hexlify(data2))
  elif type == TIFF_TYPE_URATIONAL:
    print('%lu / %lu' % ( getLongLE(data2, 0), getLongLE(data2, 4) ) )
  elif type == TIFF_TYPE_URATIONAL:
    print('%ld / %ld' % ( getLongLE(data2, 0), getLongLE(data2, 4) ) )
  else:
    print()  
  
S_IFD_ENTRY_REC = Struct('<HHLL')  
def tiff(d, l, depth, base, name):
  ifd = dict()
  print( "{0}: (0x{1:x})".format(name, l) )
  order = d[0:2]
  if order!=b'II':
    return
  marker = getShortLE( d, 2 )
  if marker != 0x2a:
    return  
  ptr = getShortLE( d, 4 )
  n = getShortLE( d, ptr )
  ptr = ptr + 2
  for i in range(n):
    tag, type, length, val = S_IFD_ENTRY_REC.unpack_from( d[ptr:ptr+S_IFD_ENTRY_REC.size] )
    if options.verbose>1:
      print( "      %s 0x%06lx %5d/0x%-4x %9s(%d)*%-6ld %9lu/0x%-lx, " % (depth*'  ', base+ptr,tag,tag,tiffTypeNames[type-1],type,length,val,val), end='' )
      tiff_print_value( d, l, 8, type, length, val, 20)
    ifd[tag]=(base+ptr,type,length,val)  
    ptr = ptr + S_IFD_ENTRY_REC.size
  return base, ifd  

def ctmd(d, l, depth, base, name):
  list = []
  print('CTMD: (0x{:x})'.format(l) ) 
  nb = getLongBE( d, 8 )
  if options.verbose>1:
    print('     %s %d' % (depth*'  ',nb))
  for i in range(nb):
    type = getLongBE( d, 12+i*8 )
    size = getLongBE( d, 16+i*8 )
    list.append( (type, size) )
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
    v2 = getLongBE( d, offset+4 ) #total of next ff03 group
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
    print('ff01 %08x %d ' % (ff01[0], ff01[1]) )
    in_ff01 = 0
    for ff02 in ff01[2]: #r
      print('  ff02 %08x %d %x %x %07x' % (ff02[0], ff02[1], ff02[2],ff02[3],ff02[4]) )
      in_ff02 = 0
      for ff03 in ff02[5]: #r
        print('    ff03 %08x %d %x %02x %05x' % (ff03[0], ff03[1], ff03[2], ff03[3], ff03[4]) )
        print('      %s (%x)' % (hexlify(d[dataOffset:dataOffset+32]), base+dataOffset) )
        dataOffset = dataOffset + ff03[0]
        in_ff02 = in_ff02 + ff03[0]
      if in_ff02 != ff02[0]:
        print('in_ff02 != ff02[0], %x != %x' % (in_ff02, ff02[0]) )      
      in_ff01 = in_ff01 + ff02[0]
    if in_ff01 != ff01[0]:
      print('in_ff01 != ff01[0], %x != %x' % (in_ff01, ff01[0]) )
  if dataOffset!=len(d):
    print('dataOffset!=len(d), %x %x' % (dataOffset, len(d)) )  
    
tags = { b'ftyp':ftyp, b'moov':moov, b'uuid':uuid, b'stsz':stsz, b'co64':co64, b'PRVW':prvw, b'CTBO':ctbo, b'THMB':thmb, b'CNCV':cncv,
         b'CDI1':cdi1, b'IAD1':iad1, b'CMP1':cmp1, b'CRAW':craw }  

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
def parse(d, base, depth):
  o = 0
  print('base=%x'%base)
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
      r = tags[chunkName](d[o+no:o+no +l-no], l, depth+1) #return results
    elif chunkName in { b'CMT1', b'CMT2', b'CMT3', b'CMT4' }:
      r = tiff( d[o+no:o+no +l-no], l, depth+1, base+o+no, chunkName )
      cr3[ chunkName ] = r
    elif chunkName == b'CTMD':
      r = ctmd( d[o+no:o+no +l-no], l, depth+1, base+o+no, chunkName )
      cr3[ chunkName ] = r
    else:
      print( '%s %s (0x%x)' % ( repr(chunkName), hexlify(d[o+no:o+no +dl-no]), l )  ) #default
       
    if chunkName in { b'moov', b'trak', b'mdia', b'minf', b'dinf', b'stbl' }: #requires inner parsing, just after the name
      parse( d[o+no:o+no +l-no], base+o+no, depth+1)
    elif chunkName == b'uuid':  #inner parsing at specific offsets after name
      uuidValue = d[o+no:o+no +UUID_LEN] #it depends on uuid values
      if uuidValue == unhexlify('85c0b687820f11e08111f4ce462b6a48'):
        parse(d[o+no+UUID_LEN:o+no+UUID_LEN +l-no-UUID_LEN], base+o+no+UUID_LEN, depth+1)
      if uuidValue == unhexlify('eaf42b5e1c984b88b9fbb7dc406e4d16'):
        parse(d[o+no+UUID_LEN+8:o+no+UUID_LEN+8 +l-no-8-UUID_LEN], base+o+no+UUID_LEN+8, depth+1)
    elif chunkName in innerOffsets: #it depends on chunkName
      start = o+no+innerOffsets[chunkName]
      end = start +l-no-innerOffsets[chunkName]
      parse( d[start:end], start, depth+1 )
      
    #post processing  
    if chunkName == b'stsz' or chunkName == b'co64' or chunkName == b'CRAW' or chunkName == b'CMP1':  #keep these values per trak
      trakName = 'trak%d' % count[b'trak']
      cr3[ trakName ][ chunkName ] = r
    elif chunkName == b'CNCV' or chunkName == b'CTBO':  
      cr3[ chunkName ] = r
    elif chunkName == b'PRVW' or chunkName == b'THMB':
      cr3[ chunkName ] = *r, base+o+no+16 #save offset
    o += l  
  return o

def getTiffTagData(name, tag):
  tagEntry = cr3[name][1][tag]  
  #print( 'tagEntry', tagEntry )
  base = cr3[name][0]
  type = tagEntry[1]
  length = tagEntry[2]
  val = tagEntry[3]
  size = tiffTypeLen[type-1]*length
  tagInfoData = data[ base+val: base+val+size ]
  return tagInfoData, tagEntry

def trakData(trak):
  return data[ cr3[trak][b'co64']:cr3[trak][b'co64']+cr3[trak][b'stsz'] ]

def parseCTMD():
  #in trak4/'CTMD' (stored in cr3[b'CTMD']), we have types and size of CMTD records, but CMTD data is in 'mdat' section
  ctmd_data = trakData( 'trak4' )  
  ctmd_offset = 0
  file_offset = cr3['trak4'][b'co64']
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
        r = tiff( ctmd_record[ record_offset+8: ], payload_size, 1, 0, b'CTMD%d_0x%x'%(record_type, payload_tag) )
        ctmd_tiff[ payload_tag ] =  (file_offset+ctmd_offset+record_offset, payload_size, payload_tag, r)  
        record_offset += payload_size
      ctmd_records[type] = (size, type, file_offset+ctmd_offset, ctmd_tiff)  #store context and TIFF entries		
    else:
      if options.verbose:
        print('%d 0x%x 0x%x' % (int(record_type), record_size, file_offset+ctmd_offset))
        print('  ',hexlify(ctmd_record))
      ctmd_records[type] = (size, type, file_offset+ctmd_offset) #do not store content, but type, size and pointer for later processing
    ctmd_offset += size
  return ctmd_records	
  
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

offset = parse(data, 0, 0)
print('%05x:'%offset)
#print( count )

if options.verbose>1:  
  print(cr3)
"""for k, v in cr3.items():
  for k2, v2 in v.items():
    print('%s, %s, %x' % (k, k2, v2) )"""


if cr3[b'CNCV'].find(b'CanonCRM')>=0:
  print('CRM')
  video = data[ cr3[b'CTBO'][3][0]+0x50: cr3[b'CTBO'][3][0]+cr3[b'CTBO'][3][1]-0x50]
  if options.verbose>2:  
    parse_crx( video, cr3[b'CTBO'][3][0]+0x50 )  
elif cr3[b'CNCV'].find(b'CanonCR3')>=0:
  print('CR3')
  if options.extract:
    if options.verbose>0:
      print('extracting jpeg (trak1) %dx%d from mdat... offset=0x%x, size=0x%x' % (cr3['trak1'][b'CRAW'][0],cr3['trak1'][b'CRAW'][1],
        cr3['trak1'][b'co64'], cr3['trak1'][b'stsz']) )
    jpeg = trakData( 'trak1' )    
    f=open('trak1.jpg','wb')
    f.write( jpeg )
    f.close()
  
  sd_crx = trakData( 'trak2' )
  if options.extract:
    if options.verbose>0:
      print('extracting SD crx (trak2) %dx%d from mdat... offset=0x%x, size=0x%x' % (cr3['trak2'][b'CRAW'][0],cr3['trak2'][b'CRAW'][1],
        cr3['trak2'][b'co64'], cr3['trak2'][b'stsz']) )
    f=open('trak2.crx','wb')
    f.write( sd_crx )
    f.close()
  if options.verbose>2:
    parse_crx( sd_crx, cr3['trak2'][b'co64'] ) #small crx has header size = 0x70

  hd_crx = trakData( 'trak3' )
  if options.extract:
    if options.verbose>0:
      print('extracting HD crx (trak3) %dx%d from mdat... offset=0x%x, size=0x%x' % (cr3['trak3'][b'CRAW'][0],cr3['trak3'][b'CRAW'][1],
        cr3['trak3'][b'co64'], cr3['trak3'][b'stsz']) )
    f=open('trak3.crx','wb')
    f.write( hd_crx )
    f.close()
    
  if options.verbose>2:  
    parse_crx( hd_crx, cr3['trak3'][b'co64'] )

  if 'trak5' in cr3: #dual pixel trak 
    dp_crx = trakData( 'trak5' )
    if options.extract:
      if options.verbose>0:
        print('extracting DP crx (trak5) %dx%d from mdat... offset=0x%x, size=0x%x' % (cr3['trak5'][b'CRAW'][0],cr3['trak5'][b'CRAW'][1],
          cr3['trak5'][b'co64'], cr3['trak5'][b'stsz']) )
      f=open('trak5.crx','wb')
      f.write( hd_crx )
      f.close()
  
  ctmd = parseCTMD()  
  print("CTMD parsing example")
  #generic way to list CTMD entries
  for entry in [1, 3, 7, 8]:
    ctmd_record = ctmd[ entry ]
    record_size = ctmd_record[0]
    record_type = ctmd_record[1]
    record_offset = ctmd_record[2]
    print('offset=0x%x, size=%d, type=%d: ' % (record_offset, record_size, record_type ), end='' ) 
    if len(ctmd_record)>3: #TIFF
      print('list')
      for subdir_tag, tiff_subdir in ctmd_record[3].items():
        offset, payload_size, payload_tag, entries = tiff_subdir
        print('  0x%04x: size=%d tag=0x%x offset_base=%x' % (offset, payload_size, payload_tag, entries[0]) )
        for tag, ifd_entry in entries[1].items():
          entry_offset, entry_type, entry_len, entry_value = ifd_entry
          print( '    0x%04x: %5d/0x%-4x %d*%d %d/0x%x' % (entry_offset, tag, tag, entry_type, entry_len, entry_value, entry_value ) )
    else: #not TIFF
      ctmd_data = data[ record_offset: record_offset+record_size] #we do not know how to parse it
      print('%s' % hexlify(ctmd_data) )

  #now we want raw data of TIFF entry 0x4016, in subdir 0x927c, in CTMD record #7. We know it is type=4=long, little endian 32 bits
  record_subdirs = ctmd[ 7 ][3]
  subdir = record_subdirs[ 0x927c ][3] # (offset, list)
  subdir_offset = record_subdirs[ 0x927c ][0]
  entry_offset, entry_type, entry_len, entry_value = subdir[1][ 0x4016 ]
  data_offset = subdir_offset+8+entry_value #TIFF_BASE is 8 bytes after TIFF subdir
  for i in range(data_offset, data_offset+4*entry_len, 4):
    print ('%d ' % getLongLE(data, i), end='' )
  print()  
  
  
  TIFF_CMT3_SENSORINFO = 0xe0  
  TIFF_CMT3_CAMERASETTINGS = 1
  TIFF_CAMERASETTINGS_QUALITY_RAW = 4
  TIFF_CAMERASETTINGS_QUALITY_CRAW = 7
  TIFF_CMT3_MODELID = 0x10
  TIFF_CMT1_MODEL = 0x110

  #get sensor characteristics
  sensorInfoData, sensorInfoEntry = getTiffTagData( b'CMT3', TIFF_CMT3_SENSORINFO )  
  #for each TIFF entry, we have (offset, type, length, value). If value is a pointer, we use getTiffTagData() to get the content
  sensorInfoList = [ getShortLE(sensorInfoData, i) for i in range( 0, sensorInfoEntry[2], tiffTypeLen[sensorInfoEntry[1]-1] ) ]
  SensorWidth = sensorInfoList[1]
  SensorHeight = sensorInfoList[2]
  SensorLeftBorder = sensorInfoList[5]
  SensorTopBorder = sensorInfoList[6]
  SensorRightBorder = sensorInfoList[7]
  SensorBottomBorder = sensorInfoList[8]

  #get camera settings to find if it is a craw (lossy) or raw (lossless)
  cameraSettingsData, cameraSettingsEntry = getTiffTagData( b'CMT3', TIFF_CMT3_CAMERASETTINGS )  
  cameraSettingsList = [ getShortLE(cameraSettingsData, i) for i in range( 0, cameraSettingsEntry[2], tiffTypeLen[cameraSettingsEntry[1]-1] ) ]
  if cameraSettingsList[3]==TIFF_CAMERASETTINGS_QUALITY_CRAW:
    print('craw')
  elif cameraSettingsList[3]==TIFF_CAMERASETTINGS_QUALITY_RAW:
    print('raw')
  else:
    print('cameraSettingsList[3]=%d'%cameraSettingsList[3]) 

  #get model name and model Id
  modelIdEntry = cr3[b'CMT3'][1][TIFF_CMT3_MODELID] 
  modelData, modelEntry = getTiffTagData( b'CMT1', TIFF_CMT1_MODEL )  
  print(modelData[:modelEntry[2]-1]) #use length value (modelEntry[2]) of TIFF entry for model
  modelId = modelIdEntry[3]
  if options.model:
 	  # modelId, SensorWidth, SensorHeight, CrxBigW, CrxBigH, CrxBigSliceW, CrxSmallW, CrwSmallH, JpegBigW, JpegBigH, JpegPrvwW, JpegPrvwH
    print('0x%08x, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d' % (modelId, SensorWidth, SensorHeight, cr3['trak3'][b'CRAW'][0],cr3['trak3'][b'CRAW'][1], 
	  cr3['trak3'][b'CMP1'][2],
	  cr3['trak2'][b'CRAW'][0],cr3['trak2'][b'CRAW'][1], cr3['trak1'][b'CRAW'][0],cr3['trak1'][b'CRAW'][1], cr3[b'PRVW'][0], cr3[b'PRVW'][1]) )

else:
  print('unknown codec')
  sys.exit()  