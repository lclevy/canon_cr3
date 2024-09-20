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

from CRaw3.TiffIfd import TiffIfd
from CRaw3.Jpeg import Jpeg      
from CRaw3.Cr2 import Cr2      
from CRaw3.Crx import Crx
from CRaw3.Ctmd import Ctmd      
   

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
  _ctmd = Ctmd(d, l, base, name ) #parse index

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
  
if data[4:12]==b'ftypheix' or data[4:12]==b'ftypcrx ':
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
elif data[:4]==b'II*\x00':
  pass
  #tiff = Tiff( data, filesize, 'tiff' )

if b'CNCV' not in cr3:
  sys.exit() #heif parsing is broken yet   
    
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

  cr3[b'CTMD'].offsets = cr3['trak4'][b'co64']
  cr3[b'CTMD'].sizes = cr3['trak4'][b'stsz']
  
  _ctmd = cr3[b'CTMD']  
  _ctmd.parse( data )  
  if options.display_ctmd:
    _ctmd.display( )
    
  #print(cr3)


  #now we want raw data of TIFF entry 0x4016 (TIFF_CANON_VIGNETTING_CORR2), in subdir TIFF_MAKERNOTE, in CTMD record #7. We know it is type=4=long, little endian 32 bits
  ctmd_makernote7 = getIfd( b'CTMD', { 'type':7, 'tag':TiffIfd.TIFF_MAKERNOTE } ) #picture 0 by default
  if ctmd_makernote7 and TiffIfd.TIFF_CANON_VIGNETTING_CORR2 in ctmd_makernote7.ifd:
    vignetting_corr2 = ctmd_makernote7.ifd[ TiffIfd.TIFF_CANON_VIGNETTING_CORR2 ]
    r = Struct('<%dL' % vignetting_corr2.length).unpack_from( data, ctmd_makernote7.base+vignetting_corr2.value )
    if options.verbose>1:
      print(r)

  cmt3 = getIfd( b'CMT3', None )
  if cmt3 and TiffIfd.TIFF_MAKERNOTE_ROLLINFO in cmt3.ifd: # only in CSI_* files (raw burst mode)
    rollInfoTag = cmt3.ifd[ TiffIfd.TIFF_MAKERNOTE_ROLLINFO ]
    #print( rollInfoTag )
    length, current, total = Struct('<%d%s' % (rollInfoTag.length, TiffIfd.tiffTypeStr[rollInfoTag.type-1])).unpack_from( data, cmt3.base+rollInfoTag.value )
    #exif IFD for current picture in the roll
    ifd = getIfd( b'CTMD', { 'picture':current, 'type':7, 'tag':TiffIfd.TIFF_MAKERNOTE } )
    if ifd:   
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


  #crx header parsing
  if 'trak5' in cr3: #end of main CRX data
    trak = 'trak5'
  else:
    trak = 'trak3'
  big_crx = Crx( cr3[trak][b'co64'][0], data[ cr3[trak][b'co64'][0]:cr3[trak][b'co64'][0]+cr3[trak][b'stsz'][0] ], cr3[trak][b'CMP1'] )
  big_crx.parse_tile()
  if options.verbose>1:
    big_crx.display_tiles()
    big_crx.display_planes()    
    big_crx.display_subbands()    

  small_crx = Crx( cr3['trak2'][b'co64'][0], data[ cr3['trak2'][b'co64'][0]:cr3['trak2'][b'co64'][0]+cr3['trak2'][b'stsz'][0] ], cr3['trak2'][b'CMP1'] )
  small_crx.parse_tile()
  if options.verbose>1:
    small_crx.display_tiles()
    small_crx.display_planes()    
    small_crx.display_subbands()    


else:
  print('unknown codec')
  sys.exit()  