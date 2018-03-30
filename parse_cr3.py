# parse CR3 file format from Canon (@lorenzo2472)
# from https://github.com/lclevy/canon_cr3
# samples from M50 camera here: http://www.photographyblog.com/reviews/canon_eos_m50_review/preview_images/
# about ISO Base file format : https://stackoverflow.com/questions/29565068/mp4-file-format-specification
# License is GPLv3 

import sys
from struct import unpack
from binascii import hexlify, unhexlify
from optparse import OptionParser

def getShortBE(d, a):
 return unpack('>H',(d)[a:a+2])[0]

def getLongBE(d, a):
 return unpack('>L',(d)[a:a+4])[0]

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
  for n in range( nbLine ):
    idx = getLongBE( d, 4+n*CTBO_LINE_LEN )
    offset = getLongLongBE( d, 4+4+n*CTBO_LINE_LEN )
    size = getLongLongBE( d, 4+4+8+n*CTBO_LINE_LEN )
    print('      %s%x %7x %7x' % (depth*'  ', idx, offset, size) )

def cncv(d, l, depth):    
  print('CNCV: {0} (0x{1:x})'.format(d, l) ) 

def cdi1(d, l, depth):    
  print('CDI1: (0x{:x})'.format(l) ) 
  print('      %s'% (depth*'  '),end='')
  for i in range(0,len(d), 2):
    print('%d,' % getShortBE(d, i),end='')
  print()  

def iad1(d, l, depth):    
  print('IAD1: (0x{:x})'.format(l) ) 
  #print(hexlify(d))
  print('      %s'% (depth*'  '),end='')
  for i in range(0,len(d), 2):
    print('%d,' % getShortBE(d, i),end='')
  print()  
  
def cmp1(d, l, depth):    
  print('CMP1: (0x{:x})'.format(l) ) 
  #print(hexlify(d))
  print('      %s'% (depth*'  '),end='')
  for i in range(0,len(d), 2):
    print('%d,' % getShortBE(d, i),end='')
  print()  
  
def craw(d, l, depth):
  print( "CRAW: (0x{0:x})".format(l) )
  w = getShortBE( d, 24 )
  h = getShortBE( d, 26 )
  bits = getShortBE( d, 26 )
  print('      %swidth=%d, height=%d' % (depth*'  ', w, h) )
  return (w,h)

def get_crx_hdr_line(d):
  v1 = getLongBE( d, 0 )
  v2 = getLongBE( d, 4 )
  v3 = getLongBE( d, 8 )
  return v1, v2, v3

CRX_HDR_LINE_LEN = 12  
def parse_crx(d, hdr_size):
  o = 0 #offset inside header
  o2 = hdr_size #offset inside compressed data
  t_ff01 = hdr_size #size accumulation per ff01 parts
  for i in range(2):
    v1 = getLongBE( d, o )
    if v1!= 0xff010008: 
      return
    v2 = getLongBE( d, o+4 )
    t_ff01 = t_ff01 + v2
    v_ff01 = v2    
    v3 = getLongBE( d, o+8 )
    print('%08x %08x %08x' % ( v1, v2, v3 ) )
    o = o + CRX_HDR_LINE_LEN  
    t_ff03 = 0
    for l in range(4):
      for j in range(2):
        r = get_crx_hdr_line(d[o:])
        print('  %08x %08x %08x' % ( r ) )
        if r[0]==0xff030008:
          print('    %s' % hexlify(d[o2:o2+32]) )
          o2 = o2 + r[1]
          t_ff03 = t_ff03 + r[1]
        o = o + CRX_HDR_LINE_LEN
    if t_ff03 != v_ff01: #accumulation of ff03/ff02 sizes must equals size in ff01 size field
      print('t_ff03 != v_ff01, %x %x' % (t_ff03, v_ff01))
  if t_ff01 != len(d): #accumulation of ff01 size + header must equals picture size        
    print('t_ff01 != len(d), %x %x'% (t_ff01, len(d)))
    
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
      count[ chunkName ] = 0
    else:  
      count[ chunkName ] = count[ chunkName ] +1
    if chunkName == b'trak':  #will keep stsz and co64 per trak
      trakName = 'trak%d' % count[b'trak']
      if trakName not in cr3:
        cr3[ trakName ] = dict()    
      
    if chunkName in tags: #dedicated parsing
      r = tags[chunkName](d[o+no:o+no +l-no], l, depth+1) #return results
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
    if chunkName == b'stsz' or chunkName == b'co64' or chunkName == b'CRAW':  #keep these values per trak
      trakName = 'trak%d' % count[b'trak']
      cr3[ trakName ][ chunkName ] = r
    elif chunkName == b'PRVW' or chunkName == b'THMB':
      cr3[ chunkName ] = *r, base+o+no+16 #save offset
    o += l  
  return o

parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-v", "--verbose", type="int", dest="verbose", help="verbose level", default=0)
parser.add_option("-x", "--extract", action="store_true", dest="extract", help="extract embedded images", default=False)
#parser.add_option("-d", "--dir", type="string", dest="directory", help="directory", default='')
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

if options.verbose>0:
  print('extracting jpeg (trak0) %dx%d from mdat... offset=0x%x, size=0x%x' % (cr3['trak0'][b'CRAW'][0],cr3['trak0'][b'CRAW'][1],
    cr3['trak0'][b'co64'], cr3['trak0'][b'stsz']) )
if options.extract:
  f=open('trak0.jpg','wb')
  f.write( data[cr3['trak0'][b'co64']:cr3['trak0'][b'co64']+cr3['trak0'][b'stsz'] ] )
  f.close()

if options.verbose>0:
  print('extracting SD crx (trak1) %dx%d from mdat... offset=0x%x, size=0x%x' % (cr3['trak1'][b'CRAW'][0],cr3['trak1'][b'CRAW'][1],
    cr3['trak1'][b'co64'], cr3['trak1'][b'stsz']) )
sd_crx = data[cr3['trak1'][b'co64']:cr3['trak1'][b'co64']+cr3['trak1'][b'stsz'] ]
if options.extract:
  f=open('trak1.crx','wb')
  f.write( sd_crx )
  f.close()
if options.verbose>1:
  parse_crx( sd_crx, 0x70 ) #small crx has header size = 0x70

if options.verbose>0:
  print('extracting HD crx (trak2) %dx%d from mdat... offset=0x%x, size=0x%x' % (cr3['trak2'][b'CRAW'][0],cr3['trak2'][b'CRAW'][1],
    cr3['trak2'][b'co64'], cr3['trak2'][b'stsz']) )
hd_crx = data[cr3['trak2'][b'co64']:cr3['trak2'][b'co64']+cr3['trak2'][b'stsz'] ]
if options.extract:
  f=open('trak2.crx','wb')
  f.write( hd_crx )
  f.close()
if options.verbose>1:  
  parse_crx( hd_crx, 0xd8 )