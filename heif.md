

# Inside Canon High Efficiency Image File format

04nov2022



Samples:

- Special thanks to Damon Lynch for 1DX Mark III HEIF and CR3 HDR samples.
- Thanks to Michel Lesoinne for R5 HEIF and CR3 HDR samples
- Thanks to Gordon Laing from Cameralabs for R6 HEIF



### Introduction

Canon released the 1DX Mark III camera with the ability to store HDR pictures in HEIF file format. Such pictures have 10 bits per color depth. HDR PQ must be enabled in settings. Filename extension is .HIF

HEIF container is ISO base file format (ISO/IEC 14496-12) and defined mainly in ISO/IEC 23008-12. Compression details (like HEVCDecoderConfigurationRecord) are defined in ISO/IEC 14496-15

Canon is using the "heix" major type, derived "grid" image for tiling and embeds "Exif" metadata (Exif, GPS and Makernotes) in "mdat" section. 



### Structure (1DX Mark III)

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



### Example (1DX Mark III)

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



Properties are numbered inside 'ipco' container, starting with 1. Property #1 is 'hvcC', property #2 is 'ispe', ... property #0x10 is 'irot'.

'ipma' links each item with their properties, for example dimension ('ispe') of main image (**0x0001**) is property #5 (ispe: v0 flags:000000 5472x3648) , because of **0x0001**:0x04/0, **0x05**/0, 0x06/1 association list.



### EOS R5

```
00000:ftyp: major_brand=b'heix', minor_version=0, [b'mif1', b'heix'] (0x18)
00018:b'meta' b'000000000000002168646c72000000000000000070696374' (0x611)
00024:  hdlr: b'pict' (0x21)
00045:  uuid: b'85c0b687820f11e08111f4ce462b6a48' (0x3e)
0005d:    CNCV: b'CanonHEIF001/10.00.00/00.00.00' (0x26)
00083:  b'dinf' b'0000001c6472656600000000000000010000000c75726c20' (0x24)
0008b:    b'dref' b'00000000000000010000000c75726c2000000001' (0x1c)
00010:      b'url ' b'00000001' (0xc)
000a7:  pitm: v0, flags:000000 0x0001
000b5:  b'iinf' b'00000000000b00000015696e666502000000000100006772' (0x10a)
0009f:    infe: v2, flags:000000 0x0001 0x0000 b'grid'
000b4:    infe: v2, flags:000001 0x0100 0x0000 b'hvc1'
000c9:    infe: v2, flags:000001 0x0101 0x0000 b'hvc1'
000de:    infe: v2, flags:000001 0x0102 0x0000 b'hvc1'
000f3:    infe: v2, flags:000001 0x0103 0x0000 b'hvc1'
00108:    infe: v2, flags:000001 0x0104 0x0000 b'hvc1'
0011d:    infe: v2, flags:000001 0x0105 0x0000 b'hvc1'
00132:    infe: v2, flags:000000 0x0200 0x0000 b'hvc1'
00147:    infe: v2, flags:000000 0x0201 0x0000 b'hvc1'
0015c:    infe: v2, flags:000001 0x0300 0x0000 b'Exif'
00171:    infe: v2, flags:000001 0x0301 0x0000 b'mime' b'application/rdf+xml\x00\x00'
001bf:  b'iref' b'000000000000001864696d67000100060100010101020103' (0x5c)
001a7:    dimg: 0x0001 6 0x100,0x101,0x102,0x103,0x104,0x105,
001bf:    thmb: id=0x200
001cd:    thmb: id=0x201
001db:    cdsc: id=0x300
001e9:    cdsc: id=0x301
0021b:  b'iprp' b'000002ec6970636f000000b1687663430124080000009d20' (0x33e)
00223:    b'ipco' b'000000b1687663430124080000009d200000000099f000fc' (0x2ec)
0022b:      hvcC: (0xb1)
              v1 24 8000000 b'9d2000000000' lvl=153, seg=0 para=0 chrF=4:2:2 lum=10 chr=10, fr=0, f, n=3
                type=0xa0 n=1:len=0x16,
                type=0xa1 n=1:len=0x66,
                type=0xa2 n=1:len=0x7,
002dc:      ispe: v0 flags:000000 4096x1856
002f0:      colr: b'nclx' 9 10 9 80
00303:      pixi: 3, 10 10 10
00313:      ispe: v0 flags:000000 8192x5464
00327:      b'irot' b'01' (0x9)
00330:      hvcC: (0xaf)
              v1 4 8000000 b'9d2000000000' lvl=60, seg=0 para=0 chrF=4:2:2 lum=10 chr=10, fr=0, f, n=3
                type=0xa0 n=1:len=0x16,
                type=0xa1 n=1:len=0x64,
                type=0xa2 n=1:len=0x7,
003df:      ispe: v0 flags:000000 320x214
003f3:      colr: b'nclx' 9 10 9 80
00406:      pixi: 3, 10 10 10
00416:      b'irot' b'01' (0x9)
0041f:      hvcC: (0xb0)
              v1 24 8000000 b'9d2000000000' lvl=120, seg=0 para=0 chrF=4:2:2 lum=10 chr=10, fr=0, f, n=3
                type=0xa0 n=1:len=0x16,
                type=0xa1 n=1:len=0x65,
                type=0xa2 n=1:len=0x7,
004cf:      ispe: v0 flags:000000 1620x1080
004e3:      colr: b'nclx' 9 10 9 80
004f6:      pixi: 3, 10 10 10
00506:      b'irot' b'01' (0x9)
0050f:    ipma:
            0x0001:0x04/0, 0x05/0, 0x06/1,
            0x0100:0x01/1, 0x02/1, 0x03/1,
            0x0101:0x01/1, 0x02/1, 0x03/1,
            0x0102:0x01/1, 0x02/1, 0x03/1,
            0x0103:0x01/1, 0x02/1, 0x03/1,
            0x0104:0x01/1, 0x02/1, 0x03/1,
            0x0105:0x01/1, 0x02/1, 0x03/1,
            0x0200:0x07/1, 0x08/1, 0x09/1, 0x0a/0, 0x0b/1,
            0x0201:0x0c/1, 0x0d/1, 0x0e/1, 0x0f/0, 0x10/1,
00559:  idat: 8192x5464
00569:  iloc: v1 flags:000000 params:4400 count:11
          0001 0001 00000000 00000008
          0100 0000 0007ce00 002d6e18
          0101 0000 00353c18 002e8284
          0102 0000 0063be9c 0031a0db
          0103 0000 00955f77 002ffa46
          0104 0000 00c559bd 002e2c96
          0105 0000 00f38653 002b048f
          0200 0000 00008000 00006821
          0201 0000 0000f600 0006d7f3
          0300 0000 00000800 000076fb
          0301 0000 0000ea00 00000c00
00629:b'mdat' b'000000000000000000000000000000000000000000000000' (0x11e84b9)
end of parsing offset: 0x11e8ae2:
HEIF
Main 0x0001 at offset 0x000000 (size=0x8) b'grid' (8192x5464)
Tile 0x0100 at offset 0x07ce00 (size=0x2d6e18) b'hvc1' (4096x1856)
Tile 0x0101 at offset 0x353c18 (size=0x2e8284) b'hvc1' (4096x1856)
Tile 0x0102 at offset 0x63be9c (size=0x31a0db) b'hvc1' (4096x1856)
Tile 0x0103 at offset 0x955f77 (size=0x2ffa46) b'hvc1' (4096x1856)
Tile 0x0104 at offset 0xc559bd (size=0x2e2c96) b'hvc1' (4096x1856)
Tile 0x0105 at offset 0xf38653 (size=0x2b048f) b'hvc1' (4096x1856)
b'Exif' at 0x800 (size=0x76fb)
b'thmb' id=0x200 at offset 0x008000 (size 0x6821) b'hvc1' (320x214)
b'thmb' id=0x201 at offset 0x00f600 (size 0x6d7f3) b'hvc1' (1620x1080)
modelId=0x80000421
sensorInfo(w=8352, h=5586, lb=144, tb=112, rb=8335, bb=5575)
```

R5 has 6 tiles (0x100 to 0x105).

### EOS R6

```
HEIF
Main 0x0001 at offset 0x000000 (size=0x8) b'grid' (5472x3648)
Tile 0x0100 at offset 0x0e2400 (size=0xe930d) b'hvc1' (2752x1856)
Tile 0x0101 at offset 0x1cb70d (size=0x185da1) b'hvc1' (2752x1856)
Tile 0x0102 at offset 0x3514ae (size=0x2fa74b) b'hvc1' (2752x1856)
Tile 0x0103 at offset 0x64bbf9 (size=0x2febe6) b'hvc1' (2752x1856)
b'Exif' at 0x600 (size=0x76fb)
b'thmb' id=0x200 at offset 0x007e00 (size 0xbd76) b'hvc1' (320x214)
b'thmb' id=0x201 at offset 0x014800 (size 0xcdaaa) b'hvc1' (1620x1080)
modelId=0x80000453
sensorInfo(w=5568, h=3708, lb=84, tb=50, rb=5555, bb=3697)
```

### Canon cameras creating HEIF images

| modelId | name | releaseData | sensorSize | sensorType | ImageProc |
| ------- | ---- | ----------- | ---------- | ---------- | --------- |
| 0x80000428 | EOS 1DX Mark III | 01/2020 | FF | CMOS |Digic X |
| 0x80000453 | EOS R6 | 07/2020 | FF | CMOS |Digic X |
| 0x80000421 | EOS R5 | 07/2020 | FF | CMOS |Digic X |
| 0x80000450 | EOS R3 | 09/2021 | FF | BSI-CMOS |Digic X |
| 0x80000465 | EOS R10 | 05/2022 | APS-C | CMOS |Digic X |
| 0x80000464 | EOS R7 | 05/2022 | FF | CMOS |Digic X |
| 0x80000481 | EOS R6 Mark II | 11/2022 | FF | CMOS |Digic X |

### Reference documents

- ISO/IEC 14496-12 (ISO Base media file format) : https://mpeg.chiariglione.org/standards/mpeg-4/iso-base-media-file-format/text-isoiec-14496-12-5th-edition


- ISO/IEC 23008-12:2017: HEIF : https://standards.iso.org/ittf/PubliclyAvailableStandards/c066067_ISO_IEC_23008-12_2017.zip

- WD2 of ISO/IEC 14496-15 2013/AMD1 Enhanced support of HEVC and MVC+D : https://mpeg.chiariglione.org/standards/mpeg-4/carriage-nal-unit-structured-video-iso-base-media-file-format/wd-isoiec-14496

- Nokia HEIF site:  https://nokiatech.github.io/heif/technical.html

  

### Other links

- Apple WWDC 2017 HEIF (jun 2017) : https://developer.apple.com/videos/play/wwdc2017/513/


- Monkey takes a .heic (oct 2017): http://cheeky4n6monkey.blogspot.com/2017/10/monkey-takes-heic.html
- Exiftool, Quicktime, HEVCConfig tag : https://exiftool.org/TagNames/QuickTime.html#HEVCConfig



### Related patents

- Description of image composition with HEVC still image file format, https://patents.google.com/patent/US10298947B2/

- Encapsulating images with vendor and proprietary information in a file, UK Patent Application 2573096, https://patentimages.storage.googleapis.com/9d/d2/93/55a2f022504d12/GB2573096A.pdf

