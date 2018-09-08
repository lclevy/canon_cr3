# Describing the Canon Raw v3 (CR3) file format #

version: 8sep2018 

by Laurent Clévy (@Lorenzo2472)



Contributors: 

- Phil Harvey (https://www.sno.phy.queensu.ca/~phil/exiftool/): CTMD, File structure





### Table of contents ###

  * [Introduction](#introduction)
    * [Cinema Raw Lite](#cimena-raw-movie-(CRM))
  * [CR3 file Structure](#cr3-file-Structure)
  * [parse_cr3.py](#parse_cr3.py)
  * [Canon tags description](#canon-tags-description)
    * [THMB Thumbnail](#thmb-(thumbnail)) 
    * [CTBO](#ctbo)
    * [PRVW (Preview)](#prvw-(preview))
    * [CTMD (Canon Timed Metadata)](#ctmd-(canon-timed-metadata))
  * [Crx codec structures](#crx-codec-structures)
    * [Lossless compression (raw)](#lossless-compression-(raw))
    * [Lossy compression (craw)](#lossy-compression-(craw))
* [Crx compression](#crx-compression)
* [Samples](#samples)





## Introduction ##

The Canon CR3 format is mainly based on the ISO Base Media File Format (ISO/IEC 14496-12), with custom tags, and the new 'crx' codec. Some tags contains TIFF structures (like IFDs, Makernotes...)

Phil Harvey, the author of ExifTool, already identified some custom TIFF tags: [Canon CR3 tags](http://https://sno.phy.queensu.ca/~phil/exiftool/TagNames/Canon.html#uuid "Canon CR3 tags")

Canon Raw v2 is described here: http://lclevy.free.fr/cr2/ and Canon CRW here: https://sno.phy.queensu.ca/~phil/exiftool/canon_raw.html

The CR3 file format and its new crx codec support both lossless 'raw' and lossy 'craw' compressions. CR2, the TIFF based format is no more used by the M50 or EOSR, even with lossless 'raw' compression. 

'craw' means 'compact raw'.

The Cinema Raw Light file format with extension .crm, also uses the crx codec.

#### Cimena Raw Movie (CRM)

Cinema Raw Light (from C200) file format is very similar to CR3, and also uses the crx codec.
CNCV value is 'CanonCRM0001/02.09.00/00.00.00'
```
> python parse_cr3.py -v 2 A003C013_170923CU_CANON.CRM
filesize 0x21a36e70
00000:ftyp: major_brand=b'crx ', minor_version=1, [b'crx ', b'isom'] x18)
00018:moov: (0x4120) 00020:  uuid: b'85c0b687820f11e08111f4ce462b6a48' (0x2a80) 
00038:    CNCV: b'CanonCRM0001/02.09.00/00.00.00' (0x26)
0005e:   b'CCTP' b'000000000000000000000001000000184343445400000000' 0x2c)
0003a:      b'CCDT' b'00000000000000000000000000000001' (0x18)
...
```

See http://learn.usa.canon.com/resources/articles/2017/eos-c200-post-production-brief.shtml



## CR3 file Structure ##

- **ftyp**: File Type Box

- **moov** : container box whose sub‐boxes define the metadata for a presentation 
  - **uuid** = 85c0b687 820f 11e0 8111 f4ce462b6a48
    - **CNCV** (Canon Compressor Version). "CanonCR3_001/00.09.00/00.00.00"

    - **CCTP** (Canon Compressor Table Pointers?). 

      - **CCDT** (?, 16 bytes). 

          00000000 00000010 00000000 00000001 (flags and index ?)

      - **CCDT** (?, 16 bytes). 

          00000000 00000001 00000000 00000002

      - **CCDT** (?, 16 bytes). 

          00000000 00000000 00000000 00000003

    - **CTBO** (Canon Trak b Offsets?)

    - free
    - **CMT1** (Canon Metadata in TIFF format, Exif IFD0)

    - **CMT2** (Canon Metadata in TIFF format, Exif ExifIFD)

    - **CMT3** (Canon Metadata in TIFF format, Canon Makernotes)

    - **CMT4** (Canon Metadata in TIFF format, Exif GPS IFD)

    - **THMB** (Thumbnail image in jpeg format)

      - size=160x120

  - **mvhd** (Movie Header)

  - **trak** (Track, embedded jpeg)

    - **tkhd** (Track Header)
    - **mdia** (Media)
      - **mdhd** (Media Header)
      - **hdlr** (Handler, type='vide')
      - **minf** (Media Information container)
        - **vmhd** (Video Media Header)
        - **dinf** (Data information box)
          - **dref** (Data Reference box)
        - **stbl** (Sample table box)
          - **stsd** (Sample descriptions, codec types, init...)
            - **CRAW** (size=0x70)
              - W=6000, H=4000, D=24bit
              - **JPEG** (size=0xc)
              - **free**
          - **stts** (decoding, time-to-sample)
          - **stsc** (sample-to-chunk, partial data offset info)
          - **stsz** (sample sizes, framing)
            - size of jpeg picture #1 in mdat
          - **free**
          - **co64** : pointer to picture #1 inside mdat

  - **trak** (sd crx)

    - **tkhd**
    - **mdia**
      - **mdhd**
      - **hdlr** (type='vide')
      - **minf**
        - **vmhd**
        - **dinf**
          - **dref**
        - **stbl**
          - **stsd**
            - **CRAW** (size=0xd4)
              - W=1624, H=1080, BitDepth=24
              - **CMP1** (size=0x3c)
              - **CDI1** (size=0x34)
                - **IAD1** (size=0x28)
              - **free**
          - **stts**
          - **stsc**
          - **stsz** : size of picture #2 in mdat
          - **free**
          - **co64** : pointer to picture #2 in mdat

  - **trak** (hd image in crx)

    - **tkhd**
    - **mdia**
      - **mdhd**
      - **hdlr** (type='vide')
      - **minf**
        - **vmhd**
        - **dinf**
          - **dref**
        - **stbl**
          - **stsd**
            - **CRAW** (size=0xe4)
              - W=6288, H=4056, bitDepth=24
              - **CMP1** (size=0x3c)
              - **CDI1** (size=0x44)
                - **IAD1** (size=0x38)
              - **free**
          - **stts**
          - **stsc**
          - **stsz** : size of picture #3 in mdat
          - **free**
          - **co64** : pointer to picture #3 in mdat

  - **trak** (metadata at end of mdat)

    - **tkhd**
    - **mdia**
      - **mdhd**
      - **hdlr** (type='meta')
      - **minf**
        - **nmhd**
        - **dinf**
          - **dref**
        - **stbl**
          - **stsd**
            - **CTMD** (size=0x4c)
          - **stts**
          - **stsc**
          - **stsz** : size of metadata in mdat
          - **free**
          - **co64** : pointer to metadata in mdat

- **uuid** = be7acfcb 97a9 42e8 9c71 999491e3afac (xpacket data)

- **uuid** = eaf42b5e 1c98 4b88 b9fb b7dc406e4d16 (preview data)
  - **PRVW**
    - jpeg (1620x1080)

- **mdat** (main data)

  - picture #1 (6000x4000, jpeg)

  - picture #2 (1624x1080, crx preview)

  - picture #3 (main, 6888x4056, crx main image)

  - Canon Timed Metadata, CTMD tags below 

    ​


## parse_cr3.py

This experimental tool allows to:

* parse Canon Raw v3 file structure
* display some Canon tags content
* extract the 3 jpeg pictures: THMB, PRVW and "mdat1"
* extract the 2 crx pictures: "mdat2" and "mdat3". Compression schemes (lossless and lossy) are unknown 
  * display first 32 bytes of each image subparts (both 'raw'/lossless and 'craw'/lossy)

Examples of output [here](output/)



## Canon tags description

### THMB (Thumbnail) 

from **uuid** = 85c0b687 820f 11e0 8111 f4ce462b6a48

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | long   | 1                   | size of this tag            |
| 4            | char   | 4                   | "THBM"                      |
| 8            | long   | 1                   | unknown, value = 0          |
| 12/0xc       | short  | 1                   | width (160)                 |
| 14/0xe       | short  | 1                   | height (120)                |
| 16/0x10      | long   | 1                   | jpeg image size (jpeg_size) |
| 20/0x14      | long   | 1                   | unknown, value = 0x00010000 |
| 24/0x18      | byte[] | stored at offset 16 | jpeg_data = ffd8ffdb...ffd9 |
| 24+jpeg_size | byte[] | ?                   | padding to next 4 bytes?    |
|              | long   | 1                   | ?                           |

### CTBO 

(using canon_eos_m50_02.cr3)

```
00000004 
00000001 0000000000006b88 0000000000010018 (offset and size of xpacket uuid)
00000002 0000000000016ba0 0000000000056d90 (offset and size of preview uuid)
00000003 000000000006d930 00000000025022b8 (offset and size of mdat)
00000004 0000000000000000 0000000000000000 ?
```

### PRVW (Preview) 

from **uuid** = eaf42b5e 1c98 4b88 b9fb b7dc406e4d16

size = 1620x1080

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | long   | 1                   | size of this tag            |
| 4            | char   | 4                   | "PRVW"                      |
| 8            | long   | 1                   | unknown, value = 0          |
| 12/0xc       | short  | 1                   | ? value = 1                 |
| 14/0xe       | short  | 1                   | width (1620)                |
| 16/0x10      | short  | 1                   | height (1080)               |
| 18/0x12      | short  | 1                   | ? value = 1                 |
| 20/0x14      | long   | 1                   | jpeg_size                   |
| 24/0x18      | byte[] | stored at offset 20 | jpeg_data = ffd8ffdb...ffd9 |
| 24+jpeg_size | byte[] | ?                   | padding to next 4 bytes?    |

### CTMD (Canon Timed MetaData)

(at end of mdat area)
Each CTMD record has this format (little-endian byte order):

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | long   | 1                   | record size (N)             |
| 4            | short  | 1                   | record type (1,3,4,5,7,8,9) |
| 6            | byte[] | 6                   | unknown                     |
| 12           | byte[] | N-12                | payload                     |

CTMD record type 1 payload (time stamp):

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | short  | 1                   | unknown                     |
| 2            | short  | 1                   | year                        |
| 4            | byte   | 1                   | month                       |
| 5            | byte   | 1                   | day                         |
| 6            | byte   | 1                   | hour                        |
| 7            | byte   | 1                   | minute                      |
| 8            | byte   | 1                   | second                      |
| 9            | byte   | 1                   | 1/100 seconds               |
| 10           | byte[] | 2                   | unknown                     |

CTMD record type 3 payload (unknown):

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | byte[] | 4                   | unknown                     |

CTMD record type 4 payload (focal-length info):

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | short  | 1                   | focal length numerator      |
| 2            | short  | 1                   | focal length denominator    |
| 4            | byte[] | 8                   | unknown                     |

CTMD record type 5 payload (exposure info):

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | short  | 1                   | F-number numerator          |
| 2            | short  | 1                   | F-number denominator        |
| 4            | short  | 1                   | exposure time numerator     |
| 6            | short  | 1                   | exposure time denominator   |
| 8            | long   | 1                   | ISO speed rating            |
| 12           | byte[] | 16                  | unknown                     |

CTMD record type 7, 8 and 9 payload (Exif info):

This is a block of Exif records.  Each Exif record has this format:

| Offset | type   | size | content                                    |
| ------ | ------ | ---- | ------------------------------------------ |
| 0      | long   | 1    | record size (N)                            |
| 4      | long   | 1    | tag ID (0x8769=ExifIFD, 0x927c=MakerNotes) |
| 8      | byte[] | N-8  | TIFF-format metadata                       |

### mdat_picture1 (lossy jpeg)

```
>python parse_cr3.py -v 2 canon_eos_m50_02.cr3
...
06451:            CRAW: (0x70)
                    width=6000, height=4000
064ab:              b'JPEG' b'00000000' (0xc)
064b7:              b'free' b'0000' (0xa)
064c1:          b'stts' b'00000000000000010000000100000001' (0x18)
064d9:          b'stsc' b'0000000000000001000000010000000100000001' (0x1c)
064f5:          stsz: version=0, size=0x30d6ef, count=1 (0x14)
06509:          b'free' b'00000000000000' (0xf)
06518:          co64: version=0, size=6d940, count=1 (0x18)
...
extracting jpeg (trak0) 6000x4000 from mdat... offset=0x6d940, size=0x30d6ef
```

### mdat_picture2 (crx codec)

this file is compressed lossless

```
>python parse_cr3.py canon_eos_m50_02.cr3
...
06635:            CRAW: (0xd4)
                    width=1624, height=1080
0668f:              CMP1: (0x3c)
066cb:              CDI1: (0x34)
066d7:                IAD1: (0x28)
066ff:              b'free' b'0000' (0xa)
06709:          b'stts' b'00000000000000010000000100000001' (0x18)
06721:          b'stsc' b'0000000000000001000000010000000100000001' (0x1c)
0673d:          stsz: version=0, size=0x1cbc40, count=1 (0x14)
06751:          b'free' b'00000000000000' (0xf)
06760:          co64: version=0, size=37b030, count=1 (0x18)
...
extracting SD crx (trak1) 1624x1080 from mdat... offset=0x37b030, size=0x1cbc40
ff01 001cbbd0 0
  ff02 0007b5c0 0 1 0 0000000
    ff03 0007b5c0 0 0 04 00001
      b'00000000002027a5000004000f03e0347565417b810ded0ef68019d59085af6a' (37b0a0)
  ff02 00070600 1 1 0 0000000
    ff03 00070600 0 0 04 00002
      b'00000000002028ff00000a6000680ccecfdd76905615eb87c07047a8e10bb5a4' (3f6660)
  ff02 00070640 2 1 0 0000000
    ff03 00070640 0 0 04 00006
      b'00000000002028d500000000004001800880baa0035a513e5a91891b50050ad5' (466c60)
  ff02 0006f9d0 3 1 0 0000000
    ff03 0006f9d0 0 0 04 00006
      b'0000000000202cab0000020002a2b7747063b83a27ff1625fb4d52b4c41823e5' (4d72a0)
```

### mdat_picture3 (crx codec)

this file is compressed lossless

```
>python parse_cr3.py -v 2 canon_eos_m50_02.cr3
...
0687d:            CRAW: (0xe4)
                    width=6288, height=4056
068d7:              CMP1: (0x3c)
06913:              CDI1: (0x44)
0691f:                IAD1: (0x38)
06957:              b'free' b'0000' (0xa)
06961:          b'stts' b'00000000000000010000000100000001' (0x18)
06979:          b'stsc' b'0000000000000001000000010000000100000001' (0x1c)
06995:          stsz: version=0, size=0x201ef28, count=1 (0x14)
069a9:          b'free' b'00000000000000' (0xf)
069b8:          co64: version=0, size=546c70, count=1 (0x18)
...
extracting HD crx (trak2) 6288x4056 from mdat... offset=0x546c70, size=0x201ef28
ff01 00ff40b8 0
  ff02 00405528 0 1 0 0000000
    ff03 00405528 0 0 04 00006
      b'0000000000202e45000000000040039226003b15c982d276151ca7cef3aa0b22' (546d48)
  ff02 003fc8a8 1 1 0 0000000
    ff03 003fc8a8 0 0 04 00003
      b'0000000000202fbd000000000040016000000000e801b88ac3590cd6c022df4d' (94c270)
  ff02 003fc6e8 2 1 0 0000000
    ff03 003fc6e8 0 0 04 00005
      b'0000000000202f9d0000000002000000000a80110bf884163afc8d3d28f76fe1' (d48b18)
  ff02 003f5c00 3 1 0 0000000
    ff03 003f5c00 0 0 04 00000
      b'0000000000202f6100000000004003ae0000000062a9c1c8002b0471075d0a2d' (1145200)
ff01 0102ad98 1
  ff02 0040cb88 0 1 0 0000000
    ff03 0040cb88 0 0 04 00006
      b'0000000000202f6b0000000000a0064e819b8854c64481e72f454f50a3242ab2' (153ae00)
  ff02 0040eb50 1 1 0 0000000
    ff03 0040eb50 0 0 04 00006
      b'0000000000202feb00000000004003c20000000000800b68026fcbbd264dfba5' (1947988)
  ff02 0040ed48 2 1 0 0000000
    ff03 0040ed48 0 0 04 00002
      b'0000000000202fa10001c00001b0034367370ac4dec63b510ad0e2415a17c15f' (1d564d8)
  ff02 00400978 3 1 0 0000000
    ff03 00400978 0 0 04 00007
      b'00000000002031db000000000040062400000001b0005e43835fa07a05efb670' (2165220)
```

### mdat_metadata (CTMD records)

size=0xa04c

```
0x2565b90:                    18000000 01000000    ................
0x2565ba0:  00010000 0000e207 02150c01 1c010000    ................
0x2565bb0:  10000000 03000000 00010000 ffffffff    ................
0x2565bc0:  18000000 04000000 0001ffff 2d000100    ............-...
0x2565bd0:  ffffffff ffffffff 28000000 05000000    ........(.......
0x2565be0:  0001ffff 3f000a00 01005000 00320000    ....?.....P..2..
....
0x256fbc0:  00000000 0002b006 00009800 94042600    ..............&.
0x256fbd0:  6d004d00 01000001 ff070100 00000100    m.M.............
0x256fbe0:  05000000 00000000                      ........        
```

This is a block of CTMD (Canon Timed MetaData) records.



## crx codec structures

### Lossless compression (raw)

(using canon_eos_m50_02.cr3, by analysing hex data)

small picture 1624x1080 (preview in DPP)

```
picture data size = 0x1cbc40
 7b5c0 + 70600 + 70640 + 6f9d0 == 1cbbd0
crx header (size=0x6c +4)
0x37b030:  ff010008 001cbbd0 00000000             size after header is 0x1cbbd0
           ff020008 0007b5c0 08000000             subpic#0, size is 7b5c0
           ff030008 0007b5c0 00200001             
           ff020008 00070600 18000000             subpic#1
0x37b060:  ff030008 00070600 00200002 
           ff020008 00070640 28000000             subpic#2
           ff030008 00070640 00200006 
           ff020008 0006f9d0 38000000             subpic#3
0x37b090:  ff030008 0006f9d0 00200006             
           00000000                               <-- 4 bytes here
0x37b0a0:  00000000 002027a5 00000400 0f03e034    start of subpic#0 (37b030+70)
0x37b0b0:  7565417b 810ded0e f68019d5 9085af6a  
...
0x3f6650:  4f6c6b49 8492d816 083817c6 75908c00    
0x3f6660:  00000000 002028ff 00000a60 00680cce    37b0a0 + 7b5c0 = 3f6660 (start of subpic#1)
0x3f6670:  cfdd7690 5615eb87 c07047a8 e10bb5a4    
...
0x466c50:  a8417683 15413023 3427d483 0ee80000    
0x466c60:  00000000 002028d5 00000000 00400180    3f6660 + 70600 = 466c60 (start of subpic#2)
0x466c70:  0880baa0 035a513e 5a91891b 50050ad5    
...
0x4d7290:  e9ae1d2b 7739005b 6a900000 00000000    
0x4d72a0:  00000000 00202cab 00000200 02a2b774    466c60 + 70640 = 4d72a0 (start of subpic#3)
0x4d72b0:  7063b83a 27ff1625 fb4d52b4 c41823e5    4d72a0 + 6f9d0 = 546C70
...
0x546c60:  86bbe446 05c21456 bdbc0000 00000000    end of subpic#3
0x546c70:  ff010008 00ff40b8 00000000 ff020008    4d72a0 + 6f9d0 = 546C70 = 37b030 + 70 + 1cbbd0
```

big picture 6888x4056

The first ff01 section is the left slice, the second one is the right slice. Inside each ff01 section, it seems the first ff02 is for red, the second and third for green, the 4th for blue: the bayer RGGB pattern.

```
picture data size = 0x201ef28
 405528 + 3fc8a8 + 3fc6e8 + 3f5c00 = ff40b8 (size of subpic#0, with 4 parts)
crx header (size=0xd8)
0x546c70:  ff010008 00ff40b8 00000000             
           ff020008 00405528 08000000             subpic#0.0, size=405528
           ff030008 00405528 00200006 
           ff020008 003fc8a8 18000000             1
0x546ca0:  ff030008 003fc8a8 00200003 
           ff020008 003fc6e8 28000000             2
           ff030008 003fc6e8 00200005 
           ff020008 003f5c00 38000000             3
0x546cd0:  ff030008 003f5c00 00200000

 40cb88 + 40eb50 + 40ed48 + 400978 = 102ad98
ff40b8 + 102ad98 = 201EE50 (+d8 = 201ef28)
0x546cda:  ff010008 0102ad98 00010000             102ad98 is size of subpic #1, with 4 parts
           ff020008 0040cb88 08000000             subpic#1.0, size=40cb88
           ff030008 0040cb88 00200006    
0x546d00:  ff020008 0040eb50 18000000             1
           ff030008 0040eb50 00200006 
           ff020008 0040ed48 28000000             2
           ff030008 0040ed48 00200002    
0x546d30:  ff020008 00400978 38000000             3
           ff030008 00400978 00200007           
           
0x546d48:  00000000 00202e45 00000000 00400392 26003b15. 546c70 + D8 = 546d48 (subpic#0.0)
...
0x94c260:  0aa2e833 1e531992 29880000 00000000    
0x94c270:  00000000 00202fbd 00000000 00400160    546d48 + 405528 = 94c270 (subpic#0.1)
0x94c280:  00000000 e801b88a c3590cd6 c022df4d    
...
0x153adf0:  11419c8e b2bfd253 391bfc04 4a709fe8    
0x153ae00:  00000000 00202f6b 00000000 00a0064e   546d48 + ff40b8 = 153ae00 (subpic#1.0)  
0x153ae10:  819b8854 c64481e7 2f454f50 a3242ab2    
...
0x1947970:  f4aa562c 85eb7223 44cc5405 1b8411b0    
0x1947980:  22800000 00000000 
                              00000000 00202feb   153ae00 + 40cb88 = 1947988 (subpic#1.1)
0x1947990:  00000000 004003c2 00000000 00800b68    
...
0x1d564c0:  4e418e60 561af160 20d8964b c866ac81    
0x1d564d0:  7e800000 00000000 
                              00000000 00202fa1   1947988 + 40eb50 = 1D564D8 (subpic#1.2)
0x1d564e0:  0001c000 01b00343 67370ac4 dec63b51    
...
0x2565b80:  f8dfd549 a2c4f792 ddc72efe 2c9a7435    
0x2565b90:  f8000000 00000000 
                              18000000 01000000    546d48 + ff40b8 + 102ad98 = 2565B98 (end of subpic#1.3)
```

### Lossy compression (craw)

Lossy compression data always has 10 "ff03 parts" for one "ff02 part", and not only one like lossless. 

```
extracting SD crx (trak1) 1624x1080 from mdat... offset=0x20ee31, size=0x85200
ff01 00084fe0 0
  ff02 00020328 0 1 0 0000000
    ff03 00001918 0 0 04 00006
      b'0000000000203ac318425ef6a542510989082c844a24481516268485b225d0a8' (20f051)
    ff03 00001538 1 0 04 00003
      b'00ef1e8849731d5028b2248b391413212c401b04595d7d65018054ad899137a8' (210969)
    ff03 000016b0 2 0 04 00006
      b'67ac484c922e025e55034962865cc8168e0b2636db2efa9341cb403a227bea08' (211ea1)
    ff03 00001610 3 0 04 00007
      b'01fde185a0795dd7b0d0906d0400e2a1272113c64072af1a0423259919531043' (213551)
    ff03 00003308 4 0 10 00005
      b'575d1afb5a4fdb3999ac9249a7a724dcdbe6c7ac550a8849158fa42a0a8f3f05' (214b61)
    ff03 000037f8 5 0 10 00000
      b'f65dfb9eddf5ebc65fda716792792f13236f93ab9d0da2a66fe4e37673ecc360' (217e69)
    ff03 00002a10 6 0 16 00004
      b'fdc31c95bc733fbcea678e9bdaf96ce7cf19361939cffb935c924eceb35c9cd9' (21b661)
    ff03 00006878 7 0 1a 00004
      b'faff6f8ff667774f2f87aaf3efb70f0f971dfb93fa4e1ff1e5ddefc3d5aaf4e7' (21e071)
    ff03 00007688 8 0 1a 00006
      b'ffd370f971feb3d5fb7cf9bd5cbabc5e2f470f7f272ede5efe3cb4de5d3d387c' (2248e9)
    ff03 00003408 9 0 20 00004
      b'fffffe50e39d0b80fce7d0be73aa736749784ffef5cdb85765fe99f00e45c238' (22bf71)
  ff02 00021928 1 1 0 0000000
    ff03 00001af0 0 0 04 00006
      b'000000000020394b00104132249729a435ef6b9ef72443204463319422958ac5' (22f379)
    ff03 00001678 1 0 04 00005
      b'0a6883f1002cd95ea0b644ff25597844d9312c0bcf70c05d7feb07285981cbda' (230e69)
...
extracting HD crx (trak2) 6288x4056 from mdat... offset=0x294031, size=0xadee70
ff01 0053a758 0
  ff02 0012bd60 0 1 0 0000000
    ff03 00009780 0 0 04 00001
      b'0000000000203bf754548c25d64922a4b02f9152a62bad34996ae57486444a97' (294469)
    ff03 00009440 1 0 04 00005
      b'24491267014147941584993c11f743c48190d21403e911b16dae44ab02b5ea90' (29dbe9)
    ff03 00009580 2 0 04 00001
      b'42dca2f8184a44d6d1e530f224d421705a691e92fe785962ddb421544d91f460' (2a7029)
    ff03 0000a018 3 0 04 00003
      b'900912b17668800484f28051f6da010f193d6404a64412f1d0844dfc0e49be80' (2b05a9)
    ff03 00019fb0 4 0 10 00007
      b'24fabde49a599f7d59e48636fbe277ea5656286792e77df97eafa71c477d3cca' (2ba5c1)
    ff03 00019f08 5 0 10 00007
      b'd9f7efb3cf7c5e6f657652dfb7678d72f4ef73efc8d8def9df9f6778f8d3abfd' (2d4571)
    ff03 00016fe0 6 0 16 00002
      b'cc9f39379d6e4bfeed9dbd799ae27c924e27e5f138cce3c712ffad993b713c92' (2ee479)
    ff03 00043de8 7 0 1a 00000
      b'e7fff83eaf83c4f5be27d3707cb794eae273fbdef774f7babc6e379374eb9f0f' (305459)
    ff03 00044458 8 0 1a 00000
      b'fcfe1e9ff3777fc1d3ee4f5791f13cee1f1cf37897376f77be5c5f8fd1e47e27' (349241)
    ff03 00032b30 9 0 20 00006
      b'fffffe3ef2d7e23e867873923fd2a7077e6af9b9f9a0fe101c357c2cff11ef88' (38d699)
  ff02 001564e8 1 1 0 0000000
    ff03 0000a450 0 0 04 00007
      b'0000000000203bfb8bd2e14b8d29ea1d4e44a5245288ae9e920897254d543eb2' (3c01c9)
    ff03 0000a2d0 1 0 04 00000
      b'856125e24305a8250d1d0264c962528c61815243203fca07638d24bc92ccff88' (3ca619)
    ff03 0000a1f8 2 0 04 00000
      b'02a0c6c90295148640ce38242da344a42a0301e08a590a38c3062183068550c0' (3d48e9)
    ff03 0000abc0 3 0 04 00007
      b'0b6a02013ba24444cda4ff15c8a0017662435a35c4ac22d088448825c03b68f1' (3deae1)
    ff03 0001cd60 4 0 10 00006
      b'933e6f6737f7d7a9ce79f8f59f2a9dfe273aebefeb3f6f9e526efc3d27e1d729' (3e96a1)
    ff03 0001cc00 5 0 10 00003
      b'5f7d5debeef9b6dffaefbdbbc25b7df25f3ddc6eb7977bb97dcd95b3e57f3939' (406401)
    ff03 00019928 6 0 16 00005
      b'5b3cf3f26faf69cfebd7f0ebac9ea9f89fa499e3e9d3a70ed3fcbae9e5cb8797' (423001)
    ff03 0004e3e8 7 0 1a 00002
      b'fffebfe778de6fc94f1ba5ddf13a7f0df02e5f96e02fdb3d1be03e21dcfd7b26' (43c929)
    ff03 0004eca0 8 0 1a 00003
      b'fff6ffd8e2f43defdf7dffa1f9ce9fcd779e2bc87e93c1725f3e739dae474fb5' (48ad11)
    ff03 0003cd00 9 0 20 00000
      b'ffffffffffe1001a04ae0d7019c13836b86e171dd8e35d1c1e6e2e2ead93e2dc' (4d99b1)
  ff02 001560b8 2 1 0 0000000
    ff03 0000a400 0 0 04 00007
      b'0000000000203bffd356922a9bf4a0553ed6a4bd0f21465d34b0b591935aa44b' (5166b1)
      ...     
ff01 005a42e0 1
  ff02 001479e8 0 1 0 0000000
    ff03 0000a6c8 0 0 04 00003
      b'0000000000203bfdd44e9d3c288938a1f5094259326591dc2649eb23146aa150' (7cebc1)
    ff03 000098b0 1 0 04 00004
      b'0ff9c1090abe0c55d1060a325080f4938299b388b2c489fcb24bd1449142ac0b' (7d9289)
    ff03 00009fe0 2 0 04 00005
      b'05690a9c062624c4b90ee18521e8504d3c0a5b49c06432052929ab4d03469621' (7e2b39)
    ff03 0000a548 3 0 04 00007
      b'091fb2004c9ca75277a32874ee547407af2919a012548cf82a4071ae9991243d' (7ecb19)
    ff03 0001ace0 4 0 10 00005
      b'cda4fa3a55764993accf73b267bbce4ce6431c9242542a33be670a8e4934d55b' (7f7061)
    ff03 0001bd28 5 0 10 00003
      b'ff34de7365b9c9e737fe5dce3e9738e2ebbfadf5591ab7cdbd4a772b8bf9f971' (811d41)
    ff03 00018610 6 0 16 00000
      b'6e72ee92b3d992ef9ebec9ffa4e3cf59c750d1b9fb71eb64e7ddc9bdbdf9f1c7' (82da69)
    ff03 00049ab8 7 0 1a 00005
      b'b93febfebfcf39be4fd0c9e6e178f8bb5fe6ee8e7f4b9feeecb8f07cba3f2f57' (846079)
    ff03 0004dbc8 8 0 1a 00002
      b'ffe5e9f0faffa7cde0f3ef373fafc4df1f5eebe6fe97b5c7c3f03ddf03b393f7' (88fb31)
    ff03 00038eb0 9 0 20 00004
      b'bfffffe6de6dff859cd1c6ffe4638c1f103feb8b844f859e7ee2fd59e82f0773' (8dd6f9)
  ff02 00171bc0 1 1 0 0000000
    ff03 0000b3d0 0 0 04 00007
      b'0000000000203bff49c50f29364bda42f24d315e94389f49344a0c34a53d284d' (9165a9)
    ff03 0000a4d8 1 0 04 00006
      b'9485285994031256284b80c2395024bd2692216f2f0d25fd852e45051e79b349' (921979)
    ...  
```

### ff01 header format
| Offset | type  | size | content                                                      |
| ------ | ----- | ---- | ------------------------------------------------------------ |
| 0      | short | 1    | ff01                                                         |
| 2      | short | 1    | 8 (size)                                                     |
| 4      | long  | 1    | size of ff01 data. One ff01 for small picture, two ff01 for big picture |
| 8      | bits | 4    | counter (0 to 1)                                                    |

### ff02 header format
| Offset in bytes | type  | size | content                                                      |
| --------------- | ----- | ---- | ------------------------------------------------------------ |
| 0               | short | 1    | ff02                                                         |
| 2               | short | 1    | 8 (size)                                                     |
| 4               | long  | 1    | size of ff02 data. Sum of ff02 data equals size of parent ff01 |
| 8               | bits  | 4    | counter (always 0 to 3). c                                   |
| 8+4bits         | bits  | 1    | flag (f)                                                     |
| 8+5bits         | bits  | 2    | 2bits value (x)                                              |

last long format is (in bits): ccccfxx0 00000000 00000000 00000000

### ff03 header format

| Offset  | type  | size  | content                                                      |
| ------- | ----- | ----- | ------------------------------------------------------------ |
| 0       | short | 1     | ff03                                                         |
| 2       | short | 1     | 8 (size)                                                     |
| 4       | long  | 1     | size of ff03 data. Sum of ff03 data equals size of parent ff02 |
| 8       | bits  | 4     | counter (0 to 9 for lossy/craw, only one for lossless/raw). c |
| 8+4bits | bits  | 1     | flag (f)                                                     |
| 8+5bits | bits  | 3+4+1 | 8 bits value (3 right most bits of byte#8 + 5 left most bits of byte#9). x |
| 9+5bits | bits  | 3+16  | 19 bits value (3 right most bits of byte#9 + 16 bits at offset 10). Substracted to size at offset 4. Likely to compute exact meanful bits at end of the encoded stream, as size is rounded to 8 bits (observed values are 0 to 7). y |

last long format is (in bits): ccccfxxx xxxxxyyy yyyyyyyy yyyyyyyy



## Crx compression

This Canon patent https://patents.google.com/patent/US20160323602A1/en describes a 3 levels Wavelet transform and Adapting Rice encoding.

*"FIG. 7A explains an example in which wavelet transform is executed three times. LL**1**, HL**1**, LH**1**, and HH**1** represent the subbands of decomposition level **1**, LL**2**, HL**2**, LH**2**, and HH**2** represent the subbands of decomposition level **2**, and LL**3**, HL**3**, LH**3**, and HH**3** represent the subbands of decomposition level **3**.*
*Note that a transform target of wavelet transform from the second time is subband LL obtained by immediately preceding wavelet transform, so subbands LL**1** and LL**2** are omitted, and subband LL obtained by last wavelet transform remains. Also, the horizontal and vertical resolutions of, for example, HL**2** are half those of HL**1**. Subband LH indicates a horizontal-direction frequency characteristic (a horizontal-direction component) of a local region to which wavelet transform is applied. Likewise, subband HL indicates a* *vertical-direction frequency characteristic (a vertical-direction component), and subband HH indicates an oblique-direction frequency characteristic (an oblique-direction component). Subband LL is a* *low-frequency component. An integer-type 5/3 filter is used in wavelet transform of this embodiment, but the present invention is not limited to this. It is also possible to use another wavelet transform filter* such as a real-type 9/7 filter used in JPEG2000 (ISO/IEC15444|ITU-T T. 800) as an international standard. In addition, the processing unit of wavelet transform can be either a line or image."

It is very likely the ten ff03 sections of lossy cr3 are LL1, HL1, LH1, HH1, HL2, LH2, HH2, HL3, LH3 and HH3, and lossless cr3 unique ff03 sections is LL1.

*"The procedure of Golomb-Rice coding is as follows"*

Each time, the first ff03 section is starting with b'00000000002', in bits 00000000 00000000 00000000 00000000 00000000 001, which is 42 in unary coding

for canon_eos_m50_02.cr3, 

small image, 

first LL data over 4 (for Red data ?) is b'00000000002027a5000004000f03e0347565417b810ded0ef68019d59085af6a', which decodes to:

00000000 00000000 00000000 00000000 00000000 001 = 42

00000 00100111 10100101 = 10149 (21 next bits)

for second FF03 (G1) : b'00000000002028ff00000', 

42 and 10495 (00000 00101000 11111111)

...





## References ##

- ISO base media file format : [ISO/IEC 14496-12:2015](http://http://standards.iso.org/ittf/PubliclyAvailableStandards/c068960_ISO_IEC_14496-12_2015.zip "ISO IEC 14496-12:2015")
- MP4 file format : [ISO/IEC 14496-14:2003](http://jchblog.u.qiniudn.com/doc/ISO_IEC_14496-14_2003-11-15.pdf "ISO/IEC 14496-14:2003")
- [ISO 14496-1 Media Format](http://xhelmboyx.tripod.com/formats/mp4-layout.txt "ISO 14496-1 Media Format")
- Software support:
   - Canon DPP 4.8.20 supports M50 CR3: [DPP](http://support-sg.canon-asia.com/contents/SG/EN/0200544802.html "DPP")
   - Adobe DNG Encoder 10.3 : [DNG Encoder](https://supportdownloads.adobe.com/detail.jsp?ftpID=6321)
   - Cinema RAW Development 2.1 for windows supports CRM movie format :  [Cinema Raw](https://www.usa.canon.com/internet/portal/us/home/support/details/cameras/cinema-eos/eos-c200?tab=drivers_downloads	"Cinema Raw")
   - EDSDK 3.8.0 (Canon)



## Samples 

#### CR3 from M50 camera

- Files canon_eos_m50_02.cr3, canon_eos_m50_06.cr3, canon_eos_m50_10.cr3, canon_eos_m50_23.cr3 can be downloaded from:

  http://www.photographyblog.com/reviews/canon_eos_m50_review/preview_images/ (only lossless raw)

  See exiftool directory for outputs of "exiftool(-k).exe" -v3 -H -a  canon_eos_m50_*.cr3
  [exiftool02.txt](exiftool/exiftool02.txt)

  See ffmpeg directory for outputs of "ffmpeg -i"
  [ffmpeg02.txt](ffmpeg/ffmpeg02.txt)


- From DPReview: IMG_0482.CR3 (raw), IMG_0483.CR3 (craw)...

  https://download.dpreview.com/canon_eosm50/M50_C-Raw_DPReview.zip (including lossy c-raw)

#### CR3 from EOSR (lossless)

- https://www.photographyblog.com/reviews/canon_eos_r/preview_images/
- https://www.dpreview.com/samples/5691884265/canon-eos-r-sample-gallery-updated-with-raw-conversions

#### CRM samples (from C200)

http://www.4kshooters.net/2017/10/04/canon-c200-raw-footage-workflow-free-samples-for-download/



