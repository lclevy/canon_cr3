
from struct import Struct
from collections import namedtuple
from binascii import hexlify

class Crx:    

  def __init__(self, base, data, cmp1):
    self.base = base
    self.data = data
    self.cmp1 = cmp1
    self.tiles = dict()
    self.planes = dict()
    self.subbands = dict()
    
  S_CRXSUBBAND = Struct('>HHLL')
  NT_CRXSUBBAND = namedtuple('crx_subband', 'index offset size supportsPartial quantValue val_19bits')
  SUBBAND_MARKER = 0xff03

  def parse_subband(self, d, ptotal, tindex, pindex):
  
    offset = 0
    dataOffset = self.planes[tindex][pindex].offset 
    
    while dataOffset < self.planes[tindex][pindex].offset + ptotal: #stay in current plane data
      sign, length, sb_size, val = Crx.S_CRXSUBBAND.unpack_from(d, offset)
      #print('    %8x %d %8x %8x' % (sign, length, sb_size, val))
      if sign!= Crx.SUBBAND_MARKER or length!=8: 
        print('error: sign != Crx.SUBBAND_MARKER or length != 8')
        return
      sb_index        = (val & 0xf0000000)>>28
      supportsPartial = (val & 0x08000000)>>27
      quantValue      = (val & 0x07f80000)>>19
      _19bits = (val & 0x0007ffff)
      
      if tindex not in self.subbands:
        self.subbands[tindex] = dict()
      if pindex not in self.subbands[tindex]:
        self.subbands[tindex][pindex] = dict()
      self.subbands[tindex][pindex][sb_index] = Crx.NT_CRXSUBBAND(sb_index, dataOffset, sb_size, supportsPartial, quantValue, _19bits )  
      
      offset = offset + Crx.S_CRXSUBBAND.size
      dataOffset = dataOffset + sb_size
      
    n_subbands = len(self.subbands[tindex][pindex])    
    if self.cmp1.wl>0 and n_subbands!=10 or self.cmp1.wl==0 and n_subbands!=1:
      print('error: self.cmp1.wl>0 and n_subbands!=10 or self.cmp1.wl==0 and n_subbands!=1')

    return n_subbands

  S_CRXPLANE = Struct('>HHLL')
  NT_CRXPLANE = namedtuple('crx_plane', 'index offset size supportsPartial roundedBits')
  PLANE_MARKER = 0xff02
  
  def parse_plane(self, d, ttotal, tindex):
  
    offset = 0
    dataOffset = self.tiles[tindex].offset
    
    while dataOffset < self.tiles[tindex].offset + ttotal:    
      sign, length, psize, val = Crx.S_CRXPLANE.unpack_from(d, offset)
      #print('  %8x %d %8x %8x' % (sign, length, psize, val))
      if sign != Crx.PLANE_MARKER or length != 8:
        print('error: sign != Crx.PLANE_MARKER or length != 8')
        return
      pindex            = (val & 0xf0000000)>>28
      supportsPartial  = (val & 0x08000000)>>27
      roundedBits      = (val & 0x06000000)>>25
      res              = (val & 0x01ffffff)
      
      if tindex not in self.planes:
        self.planes[tindex] = dict()
      self.planes[tindex][pindex] = Crx.NT_CRXPLANE(pindex, dataOffset, psize, supportsPartial, roundedBits )
      
      offset = offset + Crx.S_CRXPLANE.size
      
      n_subbands = self.parse_subband( d[offset:], psize, tindex, pindex)
      
      if psize != sum( [ self.subbands[tindex][pindex][c].size for c in range(n_subbands) ] ):
        print('error: size(plane) != sum( inner subbands)')

      offset += (n_subbands*Crx.S_CRXSUBBAND.size)
      dataOffset += psize

    return len(self.planes[tindex])
    
  S_CRXTILE = Struct('>HHLH2s')
  NT_CRXTILE = namedtuple('crx_tile', 'index offset size')
  TILE_MARKER = 0xff01
    
  def parse_tile(self):
  
    offset = 0 #offset inside header
    dataOffset = self.base + self.cmp1.hsize

    while offset+Crx.S_CRXTILE.size <= self.cmp1.hsize: #header size from cmp1, bug in Canon code: for small crx, header size in cmp1 is 4 bytes too big for parsing
      sign, length, tsize, tindex, _ = Crx.S_CRXTILE.unpack_from(self.data, offset)
      #print('%8x %d %8x %d' % (sign, length, tsize, tindex))
      if sign != Crx.TILE_MARKER or length != 8:   #r3 craw, r5m2 craw
        print('not supported: 0x%08x, sign (0x%04x) != Crx.TILE_MARKER or length (%d) != 8' % (self.base+offset, sign, length))
        return
      self.tiles[tindex] = Crx.NT_CRXTILE(tindex, dataOffset, tsize)
      offset = offset + Crx.S_CRXTILE.size
      if self.cmp1.wl > 0:
        n_subband = 10
      else:
        n_subband = 1
      n_plane = self.parse_plane(self.data[offset:], tsize, tindex)
      if tsize != sum( [ self.planes[tindex][c].size for c in range(n_plane) ] ):
        print('error: size(tile) != sum( inner planes)')

      offset = offset + (((n_subband*Crx.S_CRXSUBBAND.size)+Crx.S_CRXPLANE.size)*n_plane)
      dataOffset += tsize

    return offset

  def display_tiles(self):
    for v in self.tiles.values():
      print('%d 0x%08x 0x%08x' % (v.index, v.offset, v.size) )     

  def display_planes(self):
    for k, v in self.planes.items():
      for v2 in v.values():
        print('%d 0x%08x 0x%08x %d %d %d' % (k, v2.offset, v2.size, v2.index, v2.supportsPartial, v2.roundedBits) )     
        
  def display_subbands(self):
    for k, v in self.subbands.items():
      for k2, v2 in v.items():
        for v3 in v2.values():
          print('%d %d %d 0x%08x 0x%08x %d %02d %d' % (k, k2, v3.index, v3.offset, v3.size, v3.supportsPartial, v3.quantValue, v3.val_19bits) )   
          print('%s' % hexlify(self.data[v3.offset-self.base:v3.offset+64-self.base]))          
