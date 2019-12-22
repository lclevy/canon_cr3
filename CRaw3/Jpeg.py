'''
parses main info from lossless Jpeg (ITU-T81)

'''

from struct import unpack, Struct

def getShortBE(d, a):
 return unpack('>H',(d)[a:a+2])[0]


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
      