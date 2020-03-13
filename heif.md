

# Canon High Efficiency Image File format

13mar2020



Samples:

- Special thanks to Damon Lynch for 1DX Mark III HEIF and CR3 HDR samples.



### Introduction

Canon released the 1DX Mark III camera with the ability to store HDR pictures in HEIF file format. Such pictures have 10 bits per color depth.

HEIF is based on ISO base file format (ISO/IEC 14496-12) and defined mainly in ISO/IEC 23008-12.

Canon is using the "heix" major type, derived "grid" image for tiling and embeds "Exif" metadata (Exif, GPS and Makernotes) in "mdat" section. 



### Structure

- ftyp (major='heix')
- meta
  - hdlr (handler = 'pict')
  - uuid: b'85c0b687820f11e08111f4ce462b6a48'
    - CNCV: **b'CanonHEIF001/10.00.00/00.00.00'**
  - pitm (primary item)
  - iinf (item info box)
    - infe (info entry)
    - infe
    - ...
  - iref (item references box)
    - dimg (derived image)
    - thmb (thumbnail)
    - thmb
    - cdsc (content description)
    - cdsc
  - iprp (item properties box)
    - ipco (item properties container)
      - hvcC (HEVC configuration)
      - ispe (Image spatial extents = width and height )
      - colr (colour information)
      - pixi (pixel information)
      - irot (image rotation)
      - hvcC
      - ...
    - ipma (item property association)
  - idat (item data, = width and height for main image)
- mdat (main data)
  - id=0x300 (Exif / TIFF metadata)
  - id=0x301 (xpacket)
  - id=0x200 (thumbnail) 320x214
  - id=0x201 (preview) 1620x1080
  - ids=0x100, ..., 0x103 : (4 tiles of main image)



### Example

```
00000:ftyp: major_brand=b'heix', minor_version=0, [b'mif1', b'heix'] (0x18)
00018:b'meta' b'000000000000002168646c72000000000000000070696374' (0x5b7)
00024:  hdlr: b'pict' (0x21)
00045:  uuid: b'85c0b687820f11e08111f4ce462b6a48' (0x3e)
0005d:    CNCV: b'CanonHEIF001/10.00.00/00.00.00' (0x26)
00083:  b'dinf' b'0000001c6472656600000000000000010000000c75726c20' (0x24)
0008b:    b'dref' b'00000000000000010000000c75726c2000000001' (0x1c)
00010:      b'url ' b'00000001' (0xc)
000a7:  pitm: v0, flags:000000 0x0001
000b5:  b'iinf' b'00000000000900000015696e666502000000000100006772' (0xe0)
0009f:    infe: v2, flags:000000 0x0001 0x0000 b'grid'
000b4:    infe: v2, flags:000001 0x0100 0x0000 b'hvc1'
000c9:    infe: v2, flags:000001 0x0101 0x0000 b'hvc1'
000de:    infe: v2, flags:000001 0x0102 0x0000 b'hvc1'
000f3:    infe: v2, flags:000001 0x0103 0x0000 b'hvc1'
00108:    infe: v2, flags:000000 0x0200 0x0000 b'hvc1'
0011d:    infe: v2, flags:000000 0x0201 0x0000 b'hvc1'
00132:    infe: v2, flags:000001 0x0300 0x0000 b'Exif'
00147:    infe: v2, flags:000001 0x0301 0x0000 b'mime' b'application/rdf+xml\x00\x00'
00195:  b'iref' b'000000000000001464696d67000100040100010101020103' (0x58)
0017d:    dimg: 0x0001 4 0x100,0x101,0x102,0x103,
00191:    thmb: id=0x200
0019f:    thmb: id=0x201
001ad:    cdsc: id=0x300
001bb:    cdsc: id=0x301
001ed:  b'iprp' b'000002ec6970636f000000b1687663430124080000009d20' (0x332)
001f5:    b'ipco' b'000000b1687663430124080000009d200000000099f000fc' (0x2ec)
001fd:      b'hvcC' b'0124080000009d200000000099f000fcfefafa00000f03a0' (0xb1)
002ae:      ispe: v0 flags:000000 2752x1856
002c2:      colr: b'nclx' 9 10 9 80
002d5:      pixi: 3, 10 10 10
002e5:      ispe: v0 flags:000000 5472x3648
002f9:      b'irot' b'00' (0x9)
00302:      b'hvcC' b'0104080000009d20000000003cf000fcfefafa00000f03a0' (0xaf)
003b1:      ispe: v0 flags:000000 320x214
003c5:      colr: b'nclx' 9 10 9 80
003d8:      pixi: 3, 10 10 10
003e8:      b'irot' b'00' (0x9)
003f1:      b'hvcC' b'0124080000009d200000000078f000fcfefafa00000f03a0' (0xb0)
004a1:      ispe: v0 flags:000000 1620x1080
004b5:      colr: b'nclx' 9 10 9 80
004c8:      pixi: 3, 10 10 10
004d8:      b'irot' b'00' (0x9)
004e1:    ipma:
            0x0001:0x04/0, 0x05/0, 0x06/1,
            0x0100:0x01/1, 0x02/1, 0x03/1,
            0x0101:0x01/1, 0x02/1, 0x03/1,
            0x0102:0x01/1, 0x02/1, 0x03/1,
            0x0103:0x01/1, 0x02/1, 0x03/1,
            0x0200:0x07/1, 0x08/1, 0x09/1, 0x0a/0, 0x0b/1,
            0x0201:0x0c/1, 0x0d/1, 0x0e/1, 0x0f/0, 0x10/1,
0051f:  idat: 5472x3648
0052f:  iloc: v1 flags:000000 params:4400 count:9
          0001 0001 00000000 00000008
          0100 0000 00073800 0013e911
          0101 0000 001b2111 0015b044
          0102 0000 0030d155 00171b29
          0103 0000 0047ec7e 0017a058
          0200 0000 00006000 00006ac0
          0201 0000 0000d800 00065ee7
          0300 0000 00000600 00005899
          0301 0000 0000cc00 00000c00
005cf:b'mdat' b'000000000000000000000000000000000000000000000000' (0x5f8707)
HEIF
Main 0x0001 at offset 0x000000 (size=0x8) b'grid' (5472x3648)
Tile 0x0100 at offset 0x073800 (size=0x13e911) b'hvc1' (2752x1856)
Tile 0x0101 at offset 0x1b2111 (size=0x15b044) b'hvc1' (2752x1856)
Tile 0x0102 at offset 0x30d155 (size=0x171b29) b'hvc1' (2752x1856)
Tile 0x0103 at offset 0x47ec7e (size=0x17a058) b'hvc1' (2752x1856)
b'Exif' at 0x600 (size=0x5899)
b'thmb' id=0x200 at offset 0x006000 (size 0x6ac0) b'hvc1' (320x214)
b'thmb' id=0x201 at offset 0x00d800 (size 0x65ee7) b'hvc1' (1620x1080)
modelId=0x80000428
```



Properties are numbered inside 'ipco' container, starting with 1. Properties #1 if 'hvcC', property #2 is 'ispe', ... property #0x10 is 'irot'.

'ipma' links item and their properties, for example dimension ('ispe') of main image (**0x0001**) is property #5 (ispe: v0 flags:000000 5472x3648) , because of **0x0001**:0x04/0, **0x05**/0, 0x06/1 association list.



### References documents

- ISO/IEC 14496-12 (ISO Base media file format) : https://mpeg.chiariglione.org/standards/mpeg-4/iso-base-media-file-format/text-isoiec-14496-12-5th-edition


- ISO/IEC 23008-12:2017: HEIF : https://standards.iso.org/ittf/PubliclyAvailableStandards/c066067_ISO_IEC_23008-12_2017.zip




https://nokiatech.github.io/heif/technical.html

### Other links

Apple WWDC 2017 HEIF (jun 2017) : https://developer.apple.com/videos/play/wwdc2017/513/

Monkey takes a .heic (oct 2017): http://cheeky4n6monkey.blogspot.com/2017/10/monkey-takes-heic.html



### Related patents

- Description of image composition with HEVC still image file format, https://patents.google.com/patent/US10298947B2/

- Encapsulating images with vendor and proprietary information in a file, UK Patent Application 2573096, https://patentimages.storage.googleapis.com/9d/d2/93/55a2f022504d12/GB2573096A.pdf

