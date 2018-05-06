# Describing the Canon Raw v3 (CR3) file format #

version:6may2018 

by Laurent Clévy (@Lorenzo2472)



Contributors: 

- Phil Harvey (https://www.sno.phy.queensu.ca/~phil/exiftool/): CTMD, File structure





### Table of contents ###

  * [Introduction](#introduction)
    * [C-Raw-compression](#about-c-raw-compression)
    * [Cinema Raw Lite](#cimena-raw-movie-(CRM))
  * [CR3 file Structure](#cr3-file-Structure)
  * [parse_cr3.py](#parse_cr3.py)
  * [Canon tags description](#canon-tags-description)
    * [THMB Thumbnail](#thmb-(thumbnail)) 
    * [CTBO](#ctbo)
    * [PRVW (Preview)](#prvw-(preview))
    * [CTMD](#CTMD)
  * [Crx codec structures](#crx-codec-structures)
    * [Lossless compression (raw)](#lossless-compression-(raw))
    * [Lossy compression (craw)](#lossy-compression-(craw))
* [Samples](#samples)





## Introduction ##

The Canon CR3 format is mainly based on the ISO Base Media File Format (ISO/IEC 14496-12), with custom tags, and the new 'crx' codec. Some tags contains TIFF structures (like IFDs, Makernotes...)

Phil Harvey, the author of ExifTool, already identified some custom TIFF tags: [Canon CR3 tags](http://https://sno.phy.queensu.ca/~phil/exiftool/TagNames/Canon.html#uuid "Canon CR3 tags")

Canon Raw v2 is described here: http://lclevy.free.fr/cr2/ and Canon CRW here: https://sno.phy.queensu.ca/~phil/exiftool/canon_raw.html

The CR3 file format and its new crx codec support both lossless 'raw' and lossy 'craw' compressions. CR2, the TIFF based format is not used by the M50, even with lossless 'raw' compression. 

'craw' means 'compact raw'.

The Cinema Raw Light file format with extension .crm, also used the crx codec.

#### About C-RAW compression

"Supports the next-generation CR3 RAW format and the new C-RAW compression format. The C – RAW format is 40% smaller in file size than conventional RAW, and it corresponds to in – camera RAW development and digital lens optimizer"

```[mov,mp4,m4a,3gp,3g2,mj2 @ 0000000000140640] Could not find codec parameters for stream 0 (Video: none (CRAW / 0x57415243), none, 6000x4000, 25606 kb/s): unknown codec
> ffmpeg.exe -i canon_eos_m50_02.cr3
Consider increasing the value for the 'analyzeduration' and 'probesize' options
[mov,mp4,m4a,3gp,3g2,mj2 @ 0000000000140640] Could not find codec parameters for stream 1 (Video: none (CRAW / 0x57415243), none, 1624x1080, 15065 kb/s): unknown codec
Consider increasing the value for the 'analyzeduration' and 'probesize' options
[mov,mp4,m4a,3gp,3g2,mj2 @ 0000000000140640] Could not find codec parameters for stream 2 (Video: none (CRAW / 0x57415243), none, 6288x4056, 269449 kb/s): unknown codec
Consider increasing the value for the 'analyzeduration' and 'probesize' options`
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'canon_eos_m50_02.cr3':
  Metadata:
    major_brand     : crx
    minor_version   : 1
    compatible_brands: crx isom
    creation_time   : 2018-02-21T12:01:28.000000Z
  Duration: 00:00:01.00, start: 0.000000, bitrate: 314040 kb/s
    Stream #0:0(eng): Video: none (CRAW / 0x57415243), none, 6000x4000, 25606 kb/s, 1 fps, 1 tbr, 1 tbn, 1 tbc (default)

    Metadata:
      creation_time   : 2018-02-21T12:01:28.000000Z
    Stream #0:1(eng): Video: none (CRAW / 0x57415243), none, 1624x1080, 15065 kb/s, 1 fps, 1 tbr, 1 tbn, 1 tbc (default)
    
    Metadata:
      creation_time   : 2018-02-21T12:01:28.000000Z
    Stream #0:2(eng): Video: none (CRAW / 0x57415243), none, 6288x4056, 269449 kb/s, 1 fps, 1 tbr, 1 tbn, 1 tbc (default)    
    Metadata:
      creation_time   : 2018-02-21T12:01:28.000000Z
    Stream #0:3(eng): Data: none (CTMD / 0x444D5443), 328 kb/s (default)
    Metadata:
      creation_time   : 2018-02-21T12:01:28.000000Z
```

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

See this related patent : http://patents.com/us-20170359471.html, US Patent 20170359471 (December 14th, 2017)



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
    - **CMT1** (Canon Metadata? Exif IFD0)

    - **CMT2** (Canon Metadata? Exif ExifIFD)

    - **CMT3** (Canon Makernotes)

    - **CMT4** (Canon Metadata? Exif GPS IFD)

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

  - metadata, CTMD tags below 

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

### CTMD  ###

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
ff010008 001cbbd0 00000000
  ff020008 0007b5c0 08000000
  ff030008 0007b5c0 00200001
    b'00000000002027a5000004000f03e0347565417b810ded0ef68019d59085af6a'
  ff020008 00070600 18000000
  ff030008 00070600 00200002
    b'00000000002028ff00000a6000680ccecfdd76905615eb87c07047a8e10bb5a4'
  ff020008 00070640 28000000
  ff030008 00070640 00200006
    b'00000000002028d500000000004001800880baa0035a513e5a91891b50050ad5'
  ff020008 0006f9d0 38000000
  ff030008 0006f9d0 00200006
    b'0000000000202cab0000020002a2b7747063b83a27ff1625fb4d52b4c41823e5'
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
ff010008 00ff40b8 00000000
  ff020008 00405528 08000000
  ff030008 00405528 00200006
    b'0000000000202e45000000000040039226003b15c982d276151ca7cef3aa0b22'
  ff020008 003fc8a8 18000000
  ff030008 003fc8a8 00200003
    b'0000000000202fbd000000000040016000000000e801b88ac3590cd6c022df4d'
  ff020008 003fc6e8 28000000
  ff030008 003fc6e8 00200005
    b'0000000000202f9d0000000002000000000a80110bf884163afc8d3d28f76fe1'
  ff020008 003f5c00 38000000
  ff030008 003f5c00 00200000
    b'0000000000202f6100000000004003ae0000000062a9c1c8002b0471075d0a2d'
ff010008 0102ad98 00010000
  ff020008 0040cb88 08000000
  ff030008 0040cb88 00200006
    b'0000000000202f6b0000000000a0064e819b8854c64481e72f454f50a3242ab2'
  ff020008 0040eb50 18000000
  ff030008 0040eb50 00200006
    b'0000000000202feb00000000004003c20000000000800b68026fcbbd264dfba5'
  ff020008 0040ed48 28000000
  ff030008 0040ed48 00200002
    b'0000000000202fa10001c00001b0034367370ac4dec63b510ad0e2415a17c15f'
  ff020008 00400978 38000000
  ff030008 00400978 00200007
    b'00000000002031db000000000040062400000001b0005e43835fa07a05efb670'
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

This is a block of CTMD (Canon Timed MetaData?) records.



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
           ff030008 0007b5c0 00200001             maybe huffman table#1 ?
           ff020008 00070600 18000000             subpic#1
0x37b060:  ff030008 00070600 00200002 
           ff020008 00070640 28000000             subpic#2
           ff030008 00070640 00200006 
           ff020008 0006f9d0 38000000             subpic#3
0x37b090:  ff030008 0006f9d0 00200006             maybe huffman table#6 ?
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

Lossy compression data has several ff03 parts for one ff02 part, and not only one like lossless. Maybe 020 flags means 'lossless' ?

```
extracting SD crx (trak1) 1624x1080 from mdat... offset=0x47ed3a, size=0xe7ce0
ff01 000e7ac0 0
  ff02 00047530 0 8 000000
    ff03 00001ad0 0 020 0004
      b'0000000000202853000000000040022c04013978f459560227cfa438f5a72c8a'
    ff03 00001b28 0 020 0001
      b'000000000020003400c209d688378fb8998b85343bc752ed1d8026de4f707e4d'
    ff03 00001a48 0 020 0005
      b'000000000020003d0008f803168631b974d0649a5e7b943609ea693241e5b37b'
    ff03 00001d00 0 020 0000
      b'0000000000200045401000dd30f0852dd802532094165d84974f624aa7ec6b5a'
    ff03 00005930 0 080 0001
      b'0000100d67019c69d23e5c853366f27135741d0245f3d953d572310700c6ca24'
    ff03 00005618 0 080 0006
      b'000000000082200846ba6558dd305631b60e24b3844945801b41056e01fcced2'
    ff03 00005238 0 0b0 0003
      b'8011145009b5de28abadca409b6d6ca512c489f31ee258f40aae94df47a00000'
    ff03 00011450 0 0d0 0006
      b'40039eb077e00050809b4604f4247da1b83ad7f0286a10840457b9d241b9463e'
    ff03 00010a70 0 0d0 0003
      b'0299300d10367205cb7880301168033b297af6219600ac9b8e53a0ee4ab83241'
    ff03 0000e7b0 1 100 0004
      b'244d1d8a6a038894485843ceef502ce668d03900e9684bf40136946d65abb2f4'
  ff02 00036f68 1 8 000000
    ff03 000017a8 0 020 0001
      b'0000000000202ce50000000000400154b00d12311d2e952d7188aacbb522891e'
    ff03 000017e8 0 020 0005
      b'00011003bf434a007752ada689c6d6251bf83282121512b5a0a02e25885279f5'
    ff03 00001760 0 020 0000
      b'0000000000804e3233109986e4e3a552238cf407af9284d76e5a61a2bcf19e90'
    ff03 000019e8 0 020 0007
      b'0000000000200031101403740d0ca82e001331241a9ebbafbd43012a5e5b1c90'
    ff03 00004a48 0 080 0007
      b'400000029c034c82813af2ebdbcd168dba1a8003148442645046ac63cac0f369'
    ff03 000049b8 0 080 0004
      b'020028002b3ee6d2aba4a20b63cb29fe118d71e4047e02374e23c2a2eba00000'
    ff03 000043c8 0 0b0 0003
      b'000f61b0fa1573995dcc0a51502207802164225640250affe8be335db0008dab'
    ff03 0000ca10 0 0d0 0002
      b'c030f2a60a45e521325a0b36d42b2007995bb2c334a08af30058f600d17c2130'
    ff03 0000d1d8 0 0d0 0006
      b'41c0a24c8ab02a62d44cce8dd890d98b68a18300590989238000c3a000c0bb92'
    ff03 00009ae0 1 100 0006
      b'33299c3971c81b0d0f1496d03572456d650a84a184950b71438b3470c93e87b1'
  ff02 00036798 2 8 000000
    ff03 000017c8 0 020 0005
      b'0000000000202cd50000000000400169c0142274264278ad8762aa67bd2e70ae'
    ff03 000017f8 0 020 0004
      b'90000201ccf41a77e1ce4709c6d5a16660c58003c4aad8ca165c5a3c5b515963'
    ff03 00001738 0 020 0002
      b'080108e83aa1988bfa8ad774c6f87e1abc6bb4d6394f3c121cfe7192e84980cf'
    ff03 000019e8 0 020 0002
      b'0080003d403733e3cca50641a1c0c1a9a58d32486257e69150d4587e4aa5e4a0'
    ff03 00004b50 0 080 0002
      b'0414400000000008000d8ac100da6a91f015000319daaaf77faf500588d8bbc7'
    ff03 00004870 0 080 0007
      b'000028c116c31a72f2c2f09528312ce3adcf5f20cb74013b8148b1d7b3c3c419'
    ff03 00004398 0 0b0 0000
      b'03808853ec5d83d01bc9b02e79baf13008256b29a6aa7f0a6c02500346820e75'
    ff03 0000d490 0 0d0 0006
      b'4428cea0374d02e8af5f3481ae00024d427378d1b09533abd1d440721610a00d'
    ff03 0000c438 0 0d0 0000
      b'20513ed600ffb4324235f0a941e4268b8822c9036a092112294181d7c0344b1c'
    ff03 00009698 1 100 0005
      b'4991284c360452ea0c14d14d434f4a2bc93fa4d862941371092b0ba6e80fd149'
  ff02 00032e90 3 8 000000
    ff03 00001718 0 020 0001
      b'0000000000202db70000000000400175601834ec99ade1f488ce4a598f00715e'
    ff03 00001728 0 020 0000
      b'0008041a0a50f3c50be37664b1a9f54fe030818be7c8cb480d0508a2147ffcbf'
    ff03 000016c0 0 020 0004
      b'043304093c2fe60cd568d1cff4f70fdcb0c4aa00aa991040e58902f4e42fc536'
    ff03 00001948 0 020 0003
      b'000000000801ce4801ad356b8919001a2fa994bea0213d89fe32371bd8006281'
    ff03 00004748 0 080 0005
      b'000ea1036d603ce851a946407dc8d092bbeb54309759f996c0800334840214ab'
    ff03 00004668 0 080 0000
      b'0002261960cbb06fcc7c04ca8001a4af35ae5acef30740fa08e2059c8200334b'
    ff03 000040a8 0 0b0 0002
      b'0000c300acce3d40e00560a5fd4009e88058604ecd2e439483607f81bc81082b'
    ff03 0000bf90 0 0d0 0000
      b'496029fc8126c48d45516dbc23ed5809689468444a8806906227e5151ae58dbe'
    ff03 0000be00 0 0d0 0000
      b'92390b2eff4498904555402ba8b424e40a2cb3591ac44d10ca2b1895e048b115'
    ff03 00008460 1 100 0003
      b'434a44f8590fa15b81eb4292544a42b2ba5416ac329303219b3a64f4e8528ca2'
extracting HD crx (trak2) 6288x4056 from mdat... offset=0x566a1a, size=0x123eee0
ff01 009619b8 0
  ff02 0028f0c0 0 8 000000
    ff03 0000e858 0 020 0006
      b'00000000002030450000031f1c4b02ad610585f0d2c36b8608d727a89368514f'
    ff03 0000ec80 0 020 0006
      b'00000000002000360603d38b395eb9b2796b68aaa024e95b57cbe97141c11502'
    ff03 0000e5e0 0 020 0005
      b'000000000020003201408de14a738efac94a7fcd52e214e8203df2350707e4a0'
    ff03 0000f840 0 020 0000
      b'000040000000003445811deb8f04a509c0612c9eb281f6018f46a34c2a892c71'
    ff03 00032ae8 0 080 0001
      b'0000055803d04237139dc5b460547188c0ee5c6b999f213257002f1ea34a62bf'
    ff03 00031508 0 080 0001
      b'008a083ba638b694b18b30f2b9f4019cff1034ba319a012f8bce814105c1d019'
    ff03 0002ee18 0 0b0 0002
      b'000140492045292b4ba0e5687000001018857764a3d80224a235dc40a2c41242'
    ff03 000a1780 0 0d0 0000
      b'0123623e2d79000bf5f906c252a288a53770a4a33a64198241490e0680013501'
    ff03 000993d0 0 0d0 0001
      b'0d09a81f03727d482ab0bb0214360d8c07943160c6ca1ddbb2fd4f008b206115'
    ff03 00086470 1 100 0004
      b'00bb5089703b62b7517711cc980e9ea02405241150461332fc0d2013c01fed48'
  ff02 0024b608 1 8 000000
    ff03 0000d608 0 020 0003
      b'0000000000202ff90835b0e29f9795095b3cc3242bfb7ebbb4795acc64d9217c'
    ff03 0000d908 0 020 0003
      b'0000000082e70062e2859544410551c980f3b8a02c00064a1e70e7a24c9ec596'
    ff03 0000d470 0 020 0000
      b'00218560ae95a01139127a4cbeb78325d533ff2689a32a95107296432fa0b89f'
    ff03 0000e718 0 020 0005
      b'00000000002000db00000014195548a118bd2772626443cb8008947dc6e87bcd'
    ff03 0002cd30 0 080 0002
      b'880047128c85c60054509b5fd00a2586908206e904c443066158e1157eebc80d'
    ff03 0002cea0 0 080 0004
      b'4000023345650a70a5a05adae2645676f491c06816516319e3198e48009e83c4'
    ff03 0002a4f0 0 0b0 0001
      b'8000291816f0b412922417e0c61bf4b981eda8032cdd47c2831d645035bfec50'
    ff03 0008dc58 0 0d0 0007
      b'801864e820e4784eac891082fa034d3ac2220b0a150c906408a10a531c577522'
    ff03 0008a388 0 0d0 0002
      b'48834442e172ff58491b0789d532c8a02d9a910a1068547e42e4e866eb8ca34e'
    ff03 00078ad0 1 100 0001
      b'86021775f19701264b0554223da22481c581b51d154462b0cc2855e3b01f5d09'
  ff02 0024afc8 2 8 000000
    ff03 0000d5c8 0 020 0000
      b'0000000000203009000626ab59e3620865a041d709b51a0c824f1ce96673a286'
    ff03 0000d8f0 0 020 0004
      b'000000800051bb0b8fd83cb672c0712a223228a55c007430f029eef57320fef3'
    ff03 0000d428 0 020 0001
      b'00000e1600ce8100164f4010ed52a637dd2140bb8be3c1c329f17e813ed4d92d'
    ff03 0000e718 0 020 0007
      b'000000000020002e000010d0a1b09d9dfd55d5ae2059fa34210542aa274b13a6'
    ff03 0002ce90 0 080 0003
      b'00180b06d7ab090962b27620033cf2deb12b659c3257e92c5fc8a54a0c8a8071'
    ff03 0002ccc0 0 080 0002
      b'221500369041884a3eb00b014a10a2967d502175b02a3a911ba4fc015e0abfc3'
    ff03 0002a3c0 0 0b0 0007
      b'00008499002f5dd049d94e2407033281f83b0a6b417d4fbec662869ac4934708'
    ff03 0008ded8 0 0d0 0007
      b'4a8060002593bc8d9e76645f59b141f021068276a0139162c99132b2151b06c4'
    ff03 00089e38 0 0d0 0005
      b'601218bc8a6444ce2674c0d605608e846e25c19c10d71599d11a0cb60b5a058b'
    ff03 000789b0 1 100 0002
      b'210ec0f000ae66b12052871893135dfd40a736a809d02b444d30a80a4906e121'
  ff02 0023c328 3 8 000000
    ff03 0000d048 0 020 0001
      b'0000000000202fd161cdfc102f7182659b1f2cdcd84f9ac9627b420850efe341'
    ff03 0000d2d0 0 020 0005
      b'00000000c00000000c4b45c91504c8e7016b4e083d79973a9dfa27c68b5aef0b'
    ff03 0000cf08 0 020 0006
      b'0000108d384a606b3d084c0225d29a79a980014af4a4b98bf80dacd382185214'
    ff03 0000e1d8 0 020 0000
      b'0000000000200054002809118809933f5cd460adc4928bc3236da0117a4d364a'
    ff03 0002b070 0 080 0004
      b'100431144a0009f9870d9fb5ea3c806f60085afe487b7a9c07a130878d6c9dcc'
    ff03 0002b558 0 080 0003
      b'000000000205625fc5a0f902abe82c0cd08c560b694edbac56e842707dfa40c0'
    ff03 00028f20 0 0b0 0001
      b'00502344c8ee812c00086202e38d7afcc2905cb2090071d0610610586a68e534'
    ff03 000892f8 0 0d0 0000
      b'000a7749612b09cc5d2a1504926e7e9be118a56d5f1c021e46c7279bb3c68131'
    ff03 00086f80 0 0d0 0002
      b'0044adc49ee22ba5f284db7314c3a24e1484ec32d0bf4ec1e621203a0df66a19'
    ff03 000777d0 1 100 0003
      b'11225c504cf044dbe682054322526e498006928062801f4d40e641a32f80de32'
ff01 008dd0f0 1
  ff02 00276f98 0 8 000000
    ff03 0000ddf0 0 020 0003
      b'000000000020301900372c0920aaa1023e176f12a2a5dadac7ea0e3e259bb51d'
    ff03 0000e160 0 020 0006
      b'00000000002000355071b4a00007912b68016cf3e6c0d235a5d001fe1739f46f'
    ff03 0000dbf0 0 020 0000
      b'000000000020002c0c0d360a13e9d26884fd20b5d982d636bba5751003c8117d'
    ff03 0000ef20 0 020 0006
      b'0000000000200038000000002b4c01d927879b480302f6170ed43fc41bebc434'
    ff03 0002f3e0 0 080 0004
      b'800000042283f6ddc5a7d8a0b802b2f8036ae14b72434910989ecb0260373109'
    ff03 0002f320 0 080 0004
      b'00751145176c124a6504ed42abe7a979add5ea4b75c0d490db11b1ac28154474'
    ff03 0002d340 0 0b0 0007
      b'00456c874c0aa0a5e329e801a2f602656a6c0295d01e01123d54f7346c981a5c'
    ff03 00098ef8 0 0d0 0002
      b'001810aa6251e85505870f23d60b07fd5542db65c410d2646894480f05410c73'
    ff03 00094df8 0 0d0 0001
      b'0004c44a83257a2437edc87e2741687c8754c746c3effee320408b46dd31c145'
    ff03 00084e08 1 100 0004
      b'888989e08506377cd46cbaa2644167ba3a035228421121c117d1440be5f14611'
  ff02 00224e60 1 8 000000
    ff03 0000c840 0 020 0007
      b'000000000020300500dd6c625044688b95022ef43cdd6c62a02013b274c9498b'
    ff03 0000cab0 0 020 0004
      b'00000010e3f2dcc011450000e78e551c266bc75bc04a22f0581d6eaf37cbaa1c'
    ff03 0000c6b8 0 020 0001
      b'0000000000200048204e2406a48e0e3452442895e01a9ff46975c66c1a980880'
    ff03 0000da48 0 020 0004
      b'000000200000d7246070307371d12f18700133b9afeea2644fe23ce1f03adabb'
    ff03 00029200 0 080 0006
      b'0460173011502016ab802d40417c5620a0a928c77aeb9833854189a7120e0921'
    ff03 00029b68 0 080 0002
      b'00005900423c9d1012401e05d98a1c6119fbc558d505f33cecd90d100008480e'
    ff03 00027c48 0 0b0 0004
      b'816208b4a0d625d4e0865102c80452e4a2c0f4440625bb271b7566b588e945c8'
    ff03 00083320 0 0d0 0004
      b'1000731688c74b824f0c33977c883e56848858598093290943aa00c0d4c9822a'
    ff03 000818f0 0 0d0 0000
      b'002d4457151a4bfb1312ad017d2393410bbe4a3ea456919a67021095fc25202a'
    ff03 000724b0 1 100 0000
      b'002ac9036889061325053d70a2885b2219be223257b3097ad11899532438133f'
  ff02 00224d60 2 8 000000
    ff03 0000c828 0 020 0004
      b'0000000000202ff10e3327425ec2938b9f284cb26c41230c887ad8d682ced345'
    ff03 0000ca70 0 020 0004
      b'00000000806ffc4b18e0013fff0d029a98b1330a5d6dbb80db3844b163cc5160'
    ff03 0000c698 0 020 0004
      b'0000000000200048000e35013fb122640017aa13642d0b63d4ba4565d406f663'
    ff03 0000da38 0 020 0005
      b'00000000002000da00000001419dc14f9fccb07a5a464a4afdea45071f6bfc8d'
    ff03 00029310 0 080 0001
      b'0008aec1a68e2292d6c9c708214408cfdc14a25ea7d4180021131784a3f43346'
    ff03 00029b80 0 080 0003
      b'003c312a2e600091204f489209828117c7d4de38a6ef2db033dcba044cd0c20a'
    ff03 00027bb0 0 0b0 0002
      b'0000003b0691ee01f03cdbe8442b18088e92974ea8007dd05e428af838027395'
    ff03 00083548 0 0d0 0007
      b'20a166ceae248f08688a0920ee0ac0883de8087c85670028420954304c957b06'
    ff03 00081628 0 0d0 0001
      b'040b2b2888ee89a196406cf553687a02a80fdd150024488269849101ef104c59'
    ff03 00072448 1 100 0002
      b'8018166d9ba6584f643468a090b494105141660a19137aa00baf8070fb0ec658'
  ff02 0021c598 3 8 000000
    ff03 0000c2a8 0 020 0006
      b'0000000000202fd10000a2579f1296e0295e2d886bc696228097ea504c641057'
    ff03 0000c528 0 020 0003
      b'000000000020004e0ea03525c07f0c1f024873ac1e3a729defe5b8a95674585b'
    ff03 0000c260 0 020 0007
      b'000601e30000c6191a8018204a147887292d8cce30a181d48622de06c9c2d0e9'
    ff03 0000d6b0 0 020 0002
      b'000000000020003101134dc07dfd60040b47eb83067491e2888cb26af548fc04'
    ff03 00028278 0 080 0002
      b'0000000000b9400c5a0133d19fbf10be14934bf7655ac7d0d7461c4bb948037f'
    ff03 000288c8 0 080 0006
      b'8000000000100016102df80158825da220059ae8218f0d8b70d349193a07d35a'
    ff03 00026d10 0 0b0 0001
      b'00038edcc0441856426da3f5858a248a2957e0075f39b91d43385f659c4aec0b'
    ff03 00080fa0 0 0d0 0006
      b'80910a7e2a7ee101c38a4b59542cc7807f9864541900a157812d7657ea5214a8'
    ff03 0007ffa0 0 0d0 0006
      b'00390dfc1a19240c4dcca0723767ac30a00050fcc4d005964680c62e20a4da56'
    ff03 00071d28 1 100 0007
      b'21803d16c8b187b22bff4c12f93da0a0c86e84d0b17748811c3b821296b0e12d' 
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

## References ##

- ISO base media file format : [ISO/IEC 14496-12:2015](http://http://standards.iso.org/ittf/PubliclyAvailableStandards/c068960_ISO_IEC_14496-12_2015.zip "ISO IEC 14496-12:2015")
- MP4 file format : [ISO/IEC 14496-14:2003](http://jchblog.u.qiniudn.com/doc/ISO_IEC_14496-14_2003-11-15.pdf "ISO/IEC 14496-14:2003")
- [ISO 14496-1 Media Format](http://xhelmboyx.tripod.com/formats/mp4-layout.txt "ISO 14496-1 Media Format")
- Software support:
   - Canon DPP 4.8.20 supports M50 CR3: [DPP](http://support-sg.canon-asia.com/contents/SG/EN/0200544802.html "DPP")
   - Adobe DNG Encoder 10.3 : [DNG Encoder](https://supportdownloads.adobe.com/detail.jsp?ftpID=6321)
   	 Cinema RAW Development 2.1 for windows supports CRM movie format :  [Cinema Raw](https://www.usa.canon.com/internet/portal/us/home/support/details/cameras/cinema-eos/eos-c200?tab=drivers_downloads	"Cinema Raw")
   - EDSDK 3.8.0 (Canon)
- Discussions about CR3 format: 
  - [Rawspeed](https://github.com/darktable-org/rawspeed/issues/121)

  - [Exiv2](https://github.com/Exiv2/exiv2/issues/236)




## Samples 

#### CR3 (from M50 camera)

- Files canon_eos_m50_02.cr3, canon_eos_m50_06.cr3, canon_eos_m50_10.cr3, canon_eos_m50_23.cr3 can be downloaded from:

  http://www.photographyblog.com/reviews/canon_eos_m50_review/preview_images/ (only lossless raw)

  See exiftool directory for outputs of "exiftool(-k).exe" -v3 -H -a  canon_eos_m50_*.cr3
  [exiftool02.txt](exiftool/exiftool02.txt)

  See ffmpeg directory for outputs of "ffmpeg -i"
  [ffmpeg02.txt](ffmpeg/ffmpeg02.txt)


- From DPReview: IMG_0482.CR3 (raw), IMG_0483.CR3 (craw)...

  https://download.dpreview.com/canon_eosm50/M50_C-Raw_DPReview.zip (including lossy c-raw)



#### CRM samples (from C200)

http://www.4kshooters.net/2017/10/04/canon-c200-raw-footage-workflow-free-samples-for-download/



