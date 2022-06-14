# Describing the Canon Raw v3 (CR3) file format #

##### version: 24may2022 

by Laurent Clévy (@Lorenzo2472)



##### Wanted samples:

- R3 heif
- R10 craw and heif
- R7 craw, dpraw or heif




##### Contributors: 

- Phil Harvey (https://www.sno.phy.queensu.ca/~phil/exiftool/): CTMD, File structure
- Alexey Danilchenko (https://github.com/Alexey-Danilchenko): CMP1, CRX open source decoder
- Daniel "cytrinox" Vogelbacher: IAD1
- Mark Reid : extended header in CMP1

  

##### Thanks for samples to:

- Mark McClelland for EOS R samples (www.instagram.com/mcclellandphoto)
- Kostiantyn for M6 Mark II roll sample
- Aaron Seilis for R5 samples (raw, craw, dpraw)
- Mathias / Matze for R5 samples (jpeg, heif, craw, raw)
- Gordon Laing / Cameralabs for R6 (heif)
- Väinö Leppänen for R6 (craw, heif)
- piratenpanda for R5 dust samples (heif, raw, version 3)
- Kitor for R dust samples
- oguruma1218 for a lot of R3 raw and craw !





### Table of contents ###

  * [Introduction](#introduction)
  * [CR3 file Structure](#cr3-file-Structure)
  * [parse_cr3.py](#parse_cr3.py)
  * [Canon tags description](#canon-tags-description)
    * [THMB (Thumbnail)](#thmb-(thumbnail)) 
    * [CNCV](#cncv)
    * [CCTP](#cctp) 
    * [CCDT](#ccdt) 
    * [CTBO](#ctbo)
    * [PRVW (Preview)](#prvw-(preview))
    * [CRAW](#craw) 
    * [JPEG](#jpeg) 
    * [CMP1](#cmp1)
    * [IAD1](#iad1)
    * [CDI1](#cdi1) 
    * [CTMD (Canon Timed Metadata)](#ctmd-(canon-timed-metadata))
    * [MDAT (main data)](#mdat-(main-data))
  * [HDR](#hdr) tags description
      * [CISZ](#CISZ)
      * [IMGD](#IMGD)
      * [GRID](#GRID)
  * [Crx codec structures](#crx-codec-structures)
    * [Lossless compression (raw)](#lossless-compression-(raw))
    * [Lossy compression (craw)](#lossy-compression-(craw))
* [Crx compression](#crx-compression)
* [Samples](#samples)
* [Example Usage](#example-usage)





## Introduction ##

The Canon CR3 format is based the ISO Base Media File Format (ISO/IEC 14496-12), with custom tags, and the Canon 'crx' codec: a mix of JPEG-LS (Rice-Golomb + RLE coding) and JPEG-2000 (LeGall 5/3 DWT + quantification). Some tags contains TIFF structures : IFDs, Makernotes.

Phil Harvey, the author of ExifTool, already identified some custom TIFF tags: [Canon CR3 tags](https://sno.phy.queensu.ca/~phil/exiftool/TagNames/Canon.html#uuid "Canon CR3 tags")

Canon Raw v2 is described here: http://lclevy.free.fr/cr2/ and Canon CRW here: https://sno.phy.queensu.ca/~phil/exiftool/canon_raw.html

The CR3 file format and its new CRX codec support both lossless 'raw' and lossy 'craw' compressions. CR2, the TIFF based format is no more used by the M50 or EOSR, even with lossless 'raw' compression. 

The CRX codec has been reverse engineered by Alexey Danilchenko, implemented in FastRawViewer 1.5.1 and source code was released in october 2019, see https://github.com/LibRaw/LibRaw/blob/master/src/decoders/crx.cpp

'craw' means 'compact raw'. The CR3 format also supports dual pixel pictures, sequence of images ("roll" created using Raw burst mode) and movie (CRM).

Roll files (CSI_*.CR3) can contains up to 70 pictures (from M6 Mark II, G7X Mark II). Extracted pictures have encoding type 3, likely YCrCb format and 10 bits  (see https://github.com/LibRaw/LibRaw/blob/master/src/decoders/crx.cpp#L1710). Using Sony BSI sensor.

Starting with 1DX Mark III, Canon is using an additional file format to store 10 bits HDR pictures : HEIF, see https://github.com/lclevy/canon_cr3/blob/master/heif.md. CR3 can also store HDR images (with HEVC), see HDR section below.



The overall structure of a CR3 picture file is (dimensions are for EOS R): 

- 'moov' container 
  - uuid=85c0b687 820f 11e0 8111 f4ce462b6a48
    - track1 = full size jpeg (6000x4000)
    - track2 = small definition raw image (1624x1080)
    - track3 = high definition raw image (6888x4546)
    - track4 = Canon Timed Metadata
    - track5 = dual pixel picture (delta?, 6888x4546)
- uuid=be7acfcb 97a9 42e8 9c71 999491e3afac (xpacket data)
- uuid=eaf42b5e 1c98 4b88 b9fb b7dc406e4d16 (preview data, jpeg 1620x1080)
  - PRVW, jpeg picture
- uuid=5766b829 bb6a 47c5 bcfb 8b9f2260d06d (in roll)
  - CMTA
- mdat (main data)
  - picture(s) from track1
  - picture(s) from track2
  - picture(s) from track3
  - Canon Timed Metadata
  - picture(s) from track5 (dual pixel)
- uuid=210f1687 9149 11e4 8111 00242131fce4 (optional data, in roll)
  - CNOP






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

            size of jpeg picture #1 in mdat
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

  - picture #3 ( 6888x4056, crx main image)

  - Canon Timed Metadata, CTMD tags below 

  - picture #5 (6888x4056, dual pixel delta image)



## parse_cr3.py ##

This experimental tool allows to:

* parse Canon Raw v3, and CR2 file structure
* display TIFF tags and Canon Timed Metadata content
* for each roll:
  * extract the jpeg pictures: THMB, PRVW and "mdat"
  * extract the sd, hd and dual pictures from 'mdat' 
    * display first 32 bytes of each image subparts (both 'raw'/lossless and 'craw'/lossy)

Examples of output [here](output/)



## Canon tags description

values are in big endian



### THMB (Thumbnail) 

from **uuid** = 85c0b687 820f 11e0 8111 f4ce462b6a48



| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | long   | 1                   | size of this tag            |
| 4            | char   | 4                   | "THMB"                      |
| 8            | byte   | 1                   | likely version, value=0 or 1    |
| 9            | bytes  | 3                   | likely flags, value = 0          |



for version 0:

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 12/0xc       | short  | 1                   | width (160)                 |
| 14/0xe       | short  | 1                   | height (120)                |
| 16/0x10      | long   | 1                   | jpeg image size (jpeg_size) |
| 20/0x14      | short   | 1                   | unknown, value = 1 |
| 22/0x16      | short   | 1                   | unknown, value = 0 |
| 24/0x18      | byte[] | stored at offset 16 | jpeg_data = ffd8ffdb...ffd9 |
| **24+jpeg_size** | byte[] | ?                   | padding to next 4 bytes?    |
|              | long   | 1                   | ?                           |



for version 1:

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 12/0xc       | short  | 1                   | width (160)                 |
| 14/0xe       | short  | 1                   | height (120)                |
| 16/0x10      | long   | 1                   | jpeg image size (jpeg_size) |

### CNCV ### 
likely CaNon Codec Version

| Offset       | type   | size        | content                     |
| ------------ | ------ | ----------- | --------------------------- |
| 0            | long   | 1           | size of this tag. 0x26        |
| 4            | char   | 4           | "CNCV" |
| 8            | char   | 30          | version string |

Observed values for version string:
- "Canon**HEIF001/10**.00.**01**/00.00.00" for R6 FW 1.2.0 (with b'miaf' and b'MiHA')
- "Canon**HEIF001/10**.00.00/00.00.00" for HEIF of 1DX Mark III, R5 and R6 FW 1.0
- "Canon**CR3_003/00.10**.00/00.00.00" for R6 (craw with HDR preview), R5 (craw HDR, FW 1.2.0)
- "Canon**CR3_002/00.10**.00/00.00.00" for 1DX Mark III (craw w/ HDR FW 1.0) and R5 (craw/craw HDR FW 1.0)
- "CanonCR3_001/**00.11**.00/00.00.00" for R7 and R10 (raw with FW 1.0.1)
- "CanonCR3_001/**00.10**.00/00.00.00" for 1DX Mark III (raw/craw FW 1.0) , EOS R5 (raw) and R6 (craw/raw) 
- "CanonCR3_001/01.09.00/**01**.00.00" for raw burst mode roll (containing several pictures in burst mode)
- "CanonCR3_001/**01**.09.00/00.00.00" for SX70 HS, G5 Mark II and G7 Mark III 
- "CanonCR3_001/**00**.09.00/00.00.00" for EOS R, EOS RP, M50, 250D, 90D, M6 Mark II, M200, M50m2 and 250D
- "CanonCR**M0001**/**02**.09.00/00.00.00" for CRM movies


### CCTP ### 

size=0x5c for 3 CCDT lines, 0x74 for 4 lines (dual pixel). 

| Offset       | type   | size        | content                     |
| ------------ | ------ | ----------- | --------------------------- |
| 0            | long   | 1           | size of this tag            |
| 4            | char   | 4           | "CCTP". Canon CR3 trak pointers? |
| 8            | long   | 1           | 0      |
| 12           | long   | 1           | 1      |
| 16           | long   | 1           | number of CCDT lines. 3, or 4 for dual pixel |

3 CCDT lines are included.

### CCDT ### 

| Offset       | type   | size        | content                     |
| ------------ | ------ | ----------- | --------------------------- |
| 0            | long   | 1           | size of this tag. 0x18        |
| 4            | char   | 4           | "CCDT". Canon CR3 definition of tracks ? |
| 8            | longlong   | 1           | image type? |
| 16            | long   | 1           | 0 or 1 for dual pixel |
| 20            | long   | 1           | Trak index. 1, 2, 3 or 5 |

type values:

- 2 for trak#1 (JPEG_BIG)
- 1 for trak#2 (CRX_SMALL)
- 0 for trak#3 (CRX_BIG)
- 4 for trak#5 dual pixel second image (CRX_DUAL)



### CTBO ###

| Offset       | type   | size        | content                     |
| ------------ | ------ | ----------- | --------------------------- |
| 0            | long   | 1           | size of this tag. 0x5c       |
| 4            | char   | 4           | "CTBO". Canon tracks base offsets ? |
| 8            | long   | 1           | number of records. 4 |

for each records (20 bytes):


| Offset       | type   | size        | content                     |
| ------------ | ------ | ----------- | --------------------------- |
| 0            | long   | 1           | index|
| 4            | longlong   | 1           | offset |
| 12            | longlong   | 1           | size |

Records are:
1. xpacket
2. preview
3. mdat (main data)
4. ? size and offset are 0
5. uuid: b'5766b829bb6a47c5bcfb8b9f2260d06d', containing CMTA



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

### CRAW ###

see also https://sno.phy.queensu.ca/~phil/exiftool/TagNames/QuickTime.html#ImageDesc

CRAW is derived from ISOBMFF SampleEntry box.

| Offset | type  | size | content                                 |
| ------ | ----- | ---- | --------------------------------------- |
| 0      | long   | 1           | size of this tag.        |
| 4      | bytes | 4    | "CRAW"                                  |
| 8      | byte[] | 6    | 0. SampleEntry.reserved                |
| 12      | ushort | 1    | 1. SampleEntry.data_reference_index   |
| 16     | bytes?| 16?  | 0                                       |
| 32     | short | 1    | width                                   |
| 34     | short | 1    | height                                  |
| 36     | short | 2    | 0048 0000. XResolution. (72.0) in fixed point |
| 40     | short | 2    | 0048 0000. YResolution. (72.0)          |
| 44     | long? | 1    | 0                                       |
| 48     | short | 1    | 1                 |
| 50     | bytes? | 32? | 0. CompressorName ?                     |
| 82     | short | 1    | bits depth. 24                 |
| 84     | short? | 1    |ffff. -1?                 |
| 86     | short | 1    | 3. flags ? 3 for Jpeg, 1 for craw/raw |
| 88     | short | 1    | 0 for jpeg. 1 for craw/raw |

CRAW contains 
+ either JPEG (jpeg). Size=0x3c
+ or CMP1 and CDI1 (raw) .

sizes:
+ 0x3c for jpeg
+ 0xd4 for small raw, because IAD1 size is 0x28
+ 0xe4 for big raw, because IAD1 size id 0x38

### JPEG ###

| Offset | type  | size | content                                 |
| ------ | ----- | ---- | --------------------------------------- |
| 0      | long   | 1           | size of this tag. 0xc       |
| 4      | char   | 4           | "JPEG"|
| 8      | long  | 1    | 0               |

### CMP1 (Compression?) ###

Thanks to Alexey Danilchenko for his contributions (bytes 10 to 36): 

"In terms of CRX decoder this CMP1 is essentially image header for encoded image (exists for each image track). Decoder uses CMP1 data to decode image track."

| Offset | type  | size | content                                 |
| ------ | ----- | ---- | --------------------------------------- |
| 0      | long   | 1           | size of this tag. 0x3c       |
| 4      | char   | 4           | "CMP1"|
| 8      | short? | 1   | -1 ?            |
| 10 | short | 1 | 0x30 - size of the image header to follow |
| 12 | short | 1 | version - always 0x100 for current CR3 (major.minor version in bytes?) |
| 14 | bytes | 2 | 00 00 |
| 16      | long  | 1    | image width                            |
| 20     | long  | 1    | image height                           |
| 24     | long  | 1    | tile width (image width /2 for big picture) |
| 28     | long  | 1    | tile height                             |
| 32     | bytes | 4    | bits per sample - usually 14 |
| 33 | bits | 4 | number of planes - 4 for RGGB |
| 33+4bits | bits | 4 | CFA layout - only valid where number of planes > 1. 0:RGGB, 1:GRBG, 2:GBRG, 3:BGGR. Seen 1 for small, 0 for big (raw or craw) |
| 34 | bits | 4 | encoding type. Always 0 for raw and craw, 3 for raw extracted from roll burst |
| 34+4bits | bits | 4 | number of wavelet levels (set for wavelet compressed image). 0 for raw, 3 for craw |
| 35 | bit | 1 | 1 = image has more than one tile horizontally  (set for wavelet compressed image). Seen 1 for craw big, 0 otherwise |
| 35+1bit | bit | 1 | 1 = image has more than one tile vertically (set for wavelet compressed image). Always 0 |
| 35+2bits | bits | 6 | unused in current version - always 0 |
| 36     | long  | 1    | mdat track header size (mdat bitstream data starts following that header). raw small = 0x70, raw big   = 0xd8, craw small = 0x220, craw big   = 0x438 |
| 40     | bit   | 1    | 1 = has extended header, has extended header size |
| 40+1bit | bits | 7    | ? 0                                     |
| 41     | byte  | 1    | ? 0                                     |
| 42     | short | 1    | ? 0                                     |
| 44     | bytes | 16   | ? plane count (4) times "01 01 00 00"   |
| 60     | long  | 1    | extended header size, only present and everything after if extended header bit set |
| 64     | bit   | 1    | ? always seems to be 1                  |
| 64+1bit | bit  | 1    | 1 = has median bit depth                |
| 64+2bits | bits | 6   | ? 0                                     |
| 65     | byte  | 1    | ? 0                                     |
| 66     | short | 1    | ? 0                                     |
| 68     | long  | 6    | ? 6 items                               |
| 92     | byte  | 1    | median bit depth, usually 14, only present if has median bit set. an alternative bit depth to use with type 3 encoding when combining intermediate buffers |

### CDI1 (Canon Dimensions?) ###

size = sizeof(IAD1) + 12

CDI1 is a ISOBMFF FullBox, containing other boxes

| Offset | type  | size | content                                 |
| ------ | ----- | ---- | --------------------------------------- |
| 0      | long   | 1           | size of this tag. 0x3c       |
| 4      | char   | 4           | "CDI1"|
| 8      | byte | 1    | FullBox Version       |
| 9 | bytes[] | 3 | FullBox flags |

### IAD1 (Image Area Dimensions ?) ###

Size=0x28 for small picture, 0x38 for big picture. All values are in big endian

| Offset | type  | size | content (EOS R full size)              | cropped image (x1.6) |
| ------ | ----- | ---- | -------------------------------------- | -------------------- |
| 0      | short | 1    | 0                                      |                      |
| 2      | short | 1    | 0                                      |                      |
| 4      | short | 1    | image width (6888 with EOS R)          | 4352                 |
| 6      | short | 1    | image height (4546 with EOS R)         | 2850                 |
| 8      | short | 1    | 1                                      |                      |
| 10/0xa | short | 1    | 0 (small), 2 (big) = flag for sliced ? |                      |
| 12     | short | 1    | 1                                      |                      |
| 14     | short | 1    | 0                                      |                      |

Small image (1024x1080)

| Offset | type  | size | content (no crop)                     | cropped                       |
| ------ | ----- | ---- | -------------------------------------- | -------------------------------------- |
| 16     | short | 1    | 1 | **3** |
| 18     | short | 1    | 0 | 0 |
| 20     | short | 1    | width -4 (1620)                        | **1622**               |
| 22     | short | 1    | height (1079)                   | 1079               |
| 24     | short | 1    | 0                                      | 0                                     |
| 26     | short | 1    | 0                                      | 0                                     |
| 28     | short | 1    | width -1 (1623)                        | 1623                    |
| 30     | short | 1    | height -1 (1079)                       | 1079                |

Big image (dimensions example is for EOS R)

| Offset | type  | size | content (full size)                             | cropped (x1.6) |
| ------ | ----- | ---- | ----------------------------------------------- | -------------- |
| 16     | short | 1    | crop left offset (sensorInfo[5]) = 156          | 164            |
| 18     | short | 1    | crop top offset (sensorInfo[6]) = 158           | 158            |
| 20     | short | 1    | crop right offset (sensorInfo[7]) = 6875        | 4339           |
| 22     | short | 1    | crop bottom offset (sensorInfo[8]) = 4537       | 2841           |
| 24     | short | 1    | left optical black left offset = 0              |                |
| 26     | short | 1    | left optical black top offset = 0               |                |
| 28     | short | 1    | left optical black right offset = 143           | 151            |
| 30     | short | 1    | left optical black bottom offset = 4545         | 2849           |
| 32     | short | 1    | top optical black left offset = 144             | 152            |
| 34     | short | 1    | top optical black top offset = 0                |                |
| 36     | short | 1    | top optical black right offset = 6887           | 4351           |
| 38     | short | 1    | top optical black bottom offset = 45            | 45             |
| 40     | short | 1    | active area left offset = 144                   | 152            |
| 42     | short | 1    | active area top offset = 46                     | 46             |
| 44     | short | 1    | active area right offset = 6887                 | 4351           |
| 46     | short | 1    | active area bottom offset = 4545                | 2849           |

Values are given as offsets (from zero), so you must + 1 if you want the amount of pixels.

*active area* is the rectangle containing valid pixel data. It has same meaning as ActiveArea DNG tag.
These values sometimes are not accurate, especially in 1.6x crop files. The bottom or right offsets are
sometimes few pixels overflowing the width/height of raw image. Maybe a glitch in the firmware.

*crop* is the rectangle for the recommended crop. The dimension is usually exactly the size of the
official camera resolution and full size JPEGs.


### CMTA (Canon Metadata in Tiff)

With roll CR3.

Tiff tag 0x4047, byteseq, size = 583576

unknown content

### CNOP (Canon Optional data)

unknown content



### CTMD (Canon Timed MetaData)



1. #### Inside trak#4:



| Offset | type  | size | content                                |
| ------ | ----- | ---- | -------------------------------------- |
| 0      | long   | 1           | size of this tag. 0x4c       |
| 4      | char   | 4           | "CTMD"|
| 8      | long   | 1           | 0|
| 12      | long   | 1           | 1|
| 16      | long   | 1           | number of CTMD records. example= 7|
| 20      | records[]   | stored at 16           | |

For each record (size=8 bytes):

| Offset | type  | size | content                                |
| ------ | ----- | ---- | -------------------------------------- |
| 0      | long   | 1           | type. 1,3,4,5,7,8 or 9|
| 4      | long   | 1           | size|





2. #### At end of mdat area:


Contribution by Phil Harvey



##### Each CTMD record has this format (little-endian byte order):

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------- |
| 0            | long   | 1                   | record size (N)        |
| 4            | short  | 1                   | record type (1,3,4,5,7,8 or 9) |
| 6            | byte | 1                   | 0 for non TIFF types, 1 for TIFF                  |
| 7            | byte | 1                   | 0 for non TIFF types, 1 for TIFF               |
| 8            | short | 1                   | 1                     |
| 10            | short | 1                   | unknown. value is 0 (types 1,3) or -1 (types 4,5,7,8,9) |
| 12           | byte[] | N-12                | payload                     |



##### CTMD record type 1 payload (time stamp):

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

##### CTMD record type 3 payload (unknown):

| Offset | type | size | content                |
| ------ | ---- | ---- | ---------------------- |
| 0      | long | 1    | unknown. -1 if empty ? |

##### CTMD record type 4 payload (focal-length info):

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | short  | 1                   | focal length numerator      |
| 2            | short  | 1                   | focal length denominator    |
| 4            | byte[] | 8                   | unknown                     |

##### CTMD record type 5 payload (exposure info):

| Offset       | type   | size                | content                     |
| ------------ | ------ | ------------------- | --------------------------- |
| 0            | short  | 1                   | F-number numerator          |
| 2            | short  | 1                   | F-number denominator        |
| 4            | short  | 1                   | exposure time numerator     |
| 6            | short  | 1                   | exposure time denominator   |
| 8            | long   | 1                   | ISO speed rating            |
| 12           | byte[] | 16                  | unknown                     |

##### CTMD record type 7, 8 and 9 payload (Exif info):

This is a block of Exif records.  Each Exif record has this format:

| Offset | type   | size | content                                    |
| ------ | ------ | ---- | ------------------------------------------ |
| 0      | long   | 1    | record size (N)                            |
| 4      | long   | 1    | tag ID (0x8769=ExifIFD, 0x927c=MakerNotes) |
| 8      | byte[] | N-8  | TIFF-format metadata                       |

### CMT3

#### tag 0x97 (Dust Delete Data)

M50 use version 1, see http://lclevy.free.fr/cr2/#ddd

#### tag 0x403f (Roll Info)

```
00740:    b'CMT3': (0xe70)
...
            0x000986 16447/0x403f     ulong(4)*3           3620/0xe24, 12 15 36 
```

12 is tag length (4*3), 15 is the current picture (#16 in DPP), 36 is the number of images in the roll.



## MDAT (main data)

The MDAT section contains 4 or 5 parts:

1. a fullsize, lossy jpeg version of picture(s) 
2. a small version of picture(s) in raw or craw (1624x1080)
3. a fullsize version, in raw or craw 
4. data for CTMD (Canon Time Metada)
5. for dual pixel (delta?) picture(s), in raw or craw  



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
```
offset=0x2565b98, size=24, type=1: ctmd_timestamp(y=2018, mo=2, d=21, h=12, m=1, s=28, ms=1)
offset=0x2565bb0, size=16, type=3: b'100000000300000000010000ffffffff'
offset=0x2565bc0, size=24, type=4: ctmd_focal(num=45, denum=1)
offset=0x2565bd8, size=40, type=5: ctmd_exposure(f_num=63, f_denum=10, expo_num=1, expo_denum=80, iso=12800)
```



## HDR

CR3 files storing HDR pictures contains HEVC data and metadata. Such files are created by 1DX Mark III.

"THMB" and "CRAW" entries contains Canon specific tags and HEVC metadata.

Example values are for 1DX Mark III.

HDR images in CR3 are stored in 4:2:2 sub-sampling and 10bits, based on 'hvcC' and 'pixi' content.

### Canon HEVC like tags

#### CISZ

likelike "Canon Image SiZe". Inside THMB or CRAW metadata.
| Offset | type   | size | content                                    |
| ------ | ------ | ---- | ------------------------------------------ |
| 0      | long   | 1    | size (0x14)                            |
| 4      | char[] | 4    | "CISZ" |
| 8      | byte | 1  | likely version                       |
| 9      | bytes | 3  | likely flags                       |
| 12/0xc | short | 1  | width ? (320 for THMB)                       |
| 16/0x10| short | 1  | height ? (320 for THMB)                    |


#### IMGD

IMaGe Data. Inside THMB or CRAW metadata.
| Offset | type   | size | content                                    |
| ------ | ------ | ---- | ------------------------------------------ |
| 0      | long   | 1    | size (N bytes)                            |
| 4      | char[] | 4    | "IMGD" |
| 8      | long  | 1  | inner size1 (N-12)                       |
| 12      | long | 1  | inner size2 (N-16)                       |
| 16/0x10| bytes[] | 1  | height ? (x0140 for THMB)                    |
| 16+inner size2|  |   | end of image data                    |

#### GRID

Inside CRAW metadata. To describe number and size of tiles.

| Offset | type   | size | content                                    |
| ------ | ------ | ---- | ------------------------------------------ |
| 0      | long   | 1    | size (0x18)                            |
| 4      | char[] | 4    | "GRID" |
| 8      | byte | 1  | likely version                       |
| 9      | bytes | 3  | likely flags                       |
| 12/0xc | long | 1  | number of tiles (4)     |
| 16/0x10| long | 1  | unknown, value is 0x00000101                |
| 20/0x14| short | 1  | width (5472)                    |
| 22/0x16| short | 1  | height (3648)                    |

For main CRAW image, GRID dimensions are 5472x3648 and CISZ dimensions are 2752x1856, likely for each of 4 tiles. But 2752 x 2 = 5504 (not 5472), and 1856 x 2 = 3712 (not 3648). This must be for black level measurement on the borders.

For THMB (thumbnail) image, THMB dimensions are 320x214, whereas CISZ dimensions are 320x320.



### Standard HEVC tags

"pixi", "colr" and "hvcC" tags are used, see https://github.com/lclevy/canon_cr3/blob/master/heif.md and related ISO standards.



### Example

```
python parse_cr3.py -v 1 93FG5559.CR3
filesize 0x17dbc58
00000:ftyp: major_brand=b'crx ', minor_version=1, [b'crx ', b'isom'] (0x18)
00018:moov: (0xacf0)
00020:  uuid: b'85c0b687820f11e08111f4ce462b6a48' (0xa310)
00038:    CNCV: b'CanonCR3_002/00.10.00/00.00.00' (0x26)
0005e:    b'CCTP' b'000000000000000100000003000000184343445400000000' (0x5c)
0003a:      b'CCDT' b'00000000000000200000000000000001' (0x18)
00052:      b'CCDT' b'00000000000000010000000000000002' (0x18)
0006a:      b'CCDT' b'00000000000000000000000000000003' (0x18)
000ba:    CTBO: (0x70)
            1    ad08   10018
            2   1ad20   66388
            3   811f0 175aa68
            4       0       0
            5       0       0
0012a:    b'free' b'000000000000' (0xe)
00138:    b'CMT1': (0x208)
00340:    b'CMT2': (0x608)
00948:    b'CMT3': (0x2608)
02f50:    b'CMT4': (0x808)
03758:    THMB: version=1, width=320, height=214, size=0x6bc0 (0x6bd8)
03770:      CISZ: v0 320x320
03784:      hvcC: (0xaf)
              v1 4 8000000 b'9d2000000000' lvl=60, seg=0 para=0 chrF=4:2:2 lum=10 chr=10, fr=0, f, n=3
                type=0xa0 n=1:len=0x16,
                type=0xa1 n=1:len=0x64,
                type=0xa2 n=1:len=0x7,
03833:      colr: b'nclx' 9 10 9 80
03846:      pixi: 3, 10 10 10
03856:      b'IMGD' b'00006ac000006abc2601ac18c0f9558525640207952fbd1c' (0x6acc)
0a330:  b'mvhd' b'00000000da72f103da72f103000000010000000100010000' (0x6c)
0a39c:  b'trak' b'0000005c746b686400000007da72f103da72f10300000001' (0x2f4)
0a3a4:    b'tkhd' b'00000007da72f103da72f103000000010000000000000001' (0x5c)
0a400:    b'mdia' b'000000206d64686400000000da72f103da72f10300000001' (0x290)
0a408:      b'mdhd' b'00000000da72f103da72f103000000010000000115c70000' (0x20)
0a428:      hdlr: b'vide' (0x21)
0a449:      b'minf' b'00000014766d686400000001000000000000000000000024' (0x247)
0a451:        b'vmhd' b'000000010000000000000000' (0x14)
0a465:        b'dinf' b'0000001c6472656600000000000000010000000c75726c20' (0x24)
0a46d:          b'dref' b'00000000000000010000000c75726c2000000001' (0x1c)
00010:            b'url ' b'00000001' (0xc)
0a489:        b'stbl' b'000001807374736400000000000000010000017043524157' (0x207)
0a491:          b'stsd' b'000000000000000100000170435241570000000000000001' (0x180)
00010:            CRAW: (0x170)
                    width=5472, height=3648, bits=24
0005a:              b'HEVC' b'000000010000001847524944000000000000000400000101' (0x10c)
0000c:                GRID: v0 n=4 5472x3648
00024:                CISZ: v0 2752x1856
00038:                hvcC: (0xb1)
                        v1 24 8000000 b'9d2000000000' lvl=153, seg=0 para=0 chrF=4:2:2 lum=10 chr=10, fr=0, f, n=3
                          type=0xa0 n=1:len=0x16,
                          type=0xa1 n=1:len=0x66,
                          type=0xa2 n=1:len=0x7,
000e9:                colr: b'nclx' 9 10 9 80
000fc:                pixi: 3, 10 10 10
00166:              b'free' b'0000' (0xa)
0a611:          b'stts' b'00000000000000010000000100000001' (0x18)
0a629:          b'stsc' b'0000000000000001000000010000000100000001' (0x1c)
```





## CRX codec structures

update: the following is true codec version starting with "**CanonCR3_001**". With "CanonCR3_002", tile start with marker 0xff11, plane with 0xff12 and subband with 0xff13 (seen with 1DX Mark III craw).

### Lossless compression (raw)

(using canon_eos_m50_02.cr3, by analysing hex data)

small picture 1624x1080 (preview in DPP)

```
picture data size = 0x1cbc40
 7b5c0 + 70600 + 70640 + 6f9d0 == 1cbbd0
crx header (size=0x6c +4)
0x37b030:  ff010008 001cbbd0 00000000             size after header is 0x1cbbd0
           ff020008 0007b5c0 08000000             plane#0, size is 7b5c0
           ff030008 0007b5c0 00200001             
           ff020008 00070600 18000000             plane#1
0x37b060:  ff030008 00070600 00200002 
           ff020008 00070640 28000000             plane#2
           ff030008 00070640 00200006 
           ff020008 0006f9d0 38000000             plane#3
0x37b090:  ff030008 0006f9d0 00200006             
           00000000                               <-- 4 bytes here
0x37b0a0:  00000000 002027a5 00000400 0f03e034    start of plane#0 (37b030+70) 
...
0x3f6650:  4f6c6b49 8492d816 083817c6 75908c00    
0x3f6660:  00000000 002028ff 00000a60 00680cce    37b0a0+7b5c0= 3f6660 (start of plane#1)
0x3f6670:  cfdd7690 5615eb87 c07047a8 e10bb5a4    
...
0x466c50:  a8417683 15413023 3427d483 0ee80000    
0x466c60:  00000000 002028d5 00000000 00400180    3f6660+70600= 466c60 (start of plane#2)
0x466c70:  0880baa0 035a513e 5a91891b 50050ad5    
...
0x4d7290:  e9ae1d2b 7739005b 6a900000 00000000    
0x4d72a0:  00000000 00202cab 00000200 02a2b774    466c60+70640= 4d72a0 (start of plane#3)
0x4d72b0:  7063b83a 27ff1625 fb4d52b4 c41823e5    4d72a0+6f9d0 = 546C70
...
0x546c60:  86bbe446 05c21456 bdbc0000 00000000    end of plane#3
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

### Tile header format
| Offset | type  | size | content (codec v1 / v2)                                      |
| ------ | ----- | ---- | ------------------------------------------------------------ |
| 0      | short | 1    | ff01 / ff11                                                  |
| 2      | short | 1    | 8 (size)  / 16              |
| 4      | long  | 1    | size of ff01 data. v1: One tile for small picture, two tiles for big picture<br />v2 : one tile for small and big pictures |
| 8      | bits | 4    | counter (0 to 1)                                                    |

### Plane header format 
| Offset in bytes | type  | size | content (v1 / v2)                                            |
| --------------- | ----- | ---- | ------------------------------------------------------------ |
| 0               | short | 1    | ff02 / ff12                                                  |
| 2               | short | 1    | 8 (size)                                                     |
| 4               | long  | 1    | size of plane data. Sum of plane data equals size of parent tile |
| 8               | bits  | 4    | counter (always 0 to 3). c for RGGB components               |
| 8+4bits         | bits  | 1    | supportsPartial flag (f)                                     |
| 8+5bits         | bits  | 2    | RoundedBits (x)                                              |

last long format is (in bits): ccccfxx0 00000000 00000000 00000000

### Subband header format (LL3 HL3... HH1)

| Offset  | type  | size  | content (v1 / v2)                                            |
| ------- | ----- | ----- | ------------------------------------------------------------ |
| 0       | short | 1     | ff03 / ff13                                                  |
| 2       | short | 1     | 8 (size) / 16                                                |
| 4       | long  | 1     | size of subband data. Sum of subband data equals size of parent plane data |
| 8       | bits  | 4     | counter (0 to 9 for lossy/craw, only one for lossless/raw). c |
| 8+4bits | bits  | 1     | supportsPartial  flag (f)                                    |
| 8+5bits | bits  | 3+4+1 | quantValue (3 right most bits of byte#8 + 5 left most bits of byte#9). x |
| 9+5bits | bits  | 3+16  | 19 bits value (3 right most bits of byte#9 + 16 bits at offset 10). Substracted to size at offset 4. Likely to compute exact meanful bits at end of the encoded stream, as size is rounded to 8 bits (observed values are 0 to 7). y |

last long format is (in bits): ccccfxxx xxxxxyyy yyyyyyyy yyyyyyyy



## Crx compression

### Raw (lossless)

Lossless CR3 (and LL3) subbands are encoded using Golomb-Rice, Run length mode and Median Edge Detection prediction, similarly to JPEG-LS (ITU T.87). Crx uses <u>Adaptive</u> Golomb-Rice coding.

JPEG-LS:

![https://github.com/lclevy/canon_cr3/blob/master/jpeg_ls_encoder.png](https://github.com/lclevy/canon_cr3/blob/master/jpeg_ls_encoder.png)

in Canon patent:

![https://patentimages.storage.googleapis.com/31/86/a3/30120d794684a5/US20160323602A1-20161103-D00000.png](https://patentimages.storage.googleapis.com/31/86/a3/30120d794684a5/US20160323602A1-20161103-D00000.png)



### C-Raw (lossy)

Crx lossy type is close to JPEG-2000 : using Le Gall 5/3 wavelet transformation, which is lossless. Canon uses  quantification (loss of information ) to compress better. DWT coefficients are then encoded using Adaptive Rice-Golomb and RLE, like in lossless mode.



This Canon patent https://patents.google.com/patent/US20160323602A1/en describes a 3 levels Wavelet transform and Adapting Rice encoding.

*"FIG. 7A explains an example in which wavelet transform is executed three times. LL**1**, HL**1**, LH**1**, and HH**1** represent the subbands of decomposition level **1**, LL**2**, HL**2**, LH**2**, and HH**2** represent the subbands of decomposition level **2**, and LL**3**, HL**3**, LH**3**, and HH**3** represent the subbands of decomposition level **3**.*
*Note that a transform target of wavelet transform from the second time is subband LL obtained by immediately preceding wavelet transform, so subbands LL**1** and LL**2** are omitted, and subband LL obtained by last wavelet transform remains. Also, the horizontal and vertical resolutions of, for example, HL**2** are half those of HL**1**. Subband LH indicates a horizontal-direction frequency characteristic (a horizontal-direction component) of a local region to which wavelet transform is applied. Likewise, subband HL indicates a* *vertical-direction frequency characteristic (a vertical-direction component), and subband HH indicates an oblique-direction frequency characteristic (an oblique-direction component). Subband LL is a* *low-frequency component. An integer-type 5/3 filter is used in wavelet transform of this embodiment, but the present invention is not limited to this. It is also possible to use another wavelet transform filter* such as a real-type 9/7 filter used in JPEG2000 (ISO/IEC15444|ITU-T T. 800) as an international standard. In addition, the processing unit of wavelet transform can be either a line or image."

Subband data (0xff03) of lossy CR3 are LL3, HL3, LH3, HH3, HL2, LH2, HH2, HL1, LH1 and HH1. 



![FIGS. 7A and 7B are views for explaining the concept of subband division by wavelet transform, and an example of a code to be generated](https://patentimages.storage.googleapis.com/a5/2f/24/6f36c0f3fdfe5f/US20160323602A1-20161103-D00007.png)





## References ##

- ISO base media file format : [ISO/IEC 14496-12:2015](https://mpeg.chiariglione.org/standards/mpeg-4/iso-base-media-file-format/text-isoiec-14496-12-5th-edition "ISO IEC 14496-12:2015")
- MP4 file format : [ISO/IEC 14496-14:2003](https://mpeg.chiariglione.org/standards/mpeg-4/mp4-file-format "ISO/IEC 14496-14:2003")
- ITU-T Rec T.87 / ISO 14495-1 (JPEG-LS, 1998) : https://www.itu.int/rec/T-REC-T.87/en
- ITU-T Rec T.800 / ISO 15444 (JPEG 2000, 1996) : https://www.itu.int/rec/T-REC-T.800-201511-S/en
- [ISO 14496-1 Media Format](http://xhelmboyx.tripod.com/formats/mp4-layout.txt "ISO 14496-1 Media Format")
- Software support:
   - Canon DPP 4.8.20 supports M50 CR3: [DPP](http://support-sg.canon-asia.com/contents/SG/EN/0200544802.html "DPP")
   - Adobe DNG Encoder 10.3 : [DNG Encoder](https://supportdownloads.adobe.com/detail.jsp?ftpID=6321)
   - Cinema RAW Development 2.1 for windows supports CRM movie format :  [Cinema Raw](https://www.usa.canon.com/internet/portal/us/home/support/details/cameras/cinema-eos/eos-c200?tab=drivers_downloads	"Cinema Raw")
   - EDSDK 3.8.0 (Canon)
   - FastRawViewer 1.5.1 (libraw CR3 support by Alexey Danilchenko). 
     - https://github.com/LibRaw/LibRaw/blob/master/src/decoders/crx.cpp
   - Darktable (11may2021)
     - https://github.com/darktable-org/rawspeed/pull/271 (Daniel "cytrinox" Vogelbacher)
   - DNGLab (Daniel "cytrinox" Vogelbacher)
     - https://github.com/dnglab/dnglab/tree/main/rawler/src/decompressors/crx (16aug2021)



### Cameras creating CR3 / CRX images

| modelId | name | releaseData | sensorSize | sensorType | ImageProc |
| ------- | ---- | ----------- | ---------- | ---------- | --------- |
| 0x00000412 | EOS M50 / Kiss M | 04/2018 | APS-C | CMOS | Digic 8 |
| 0x80000424 | EOS R                      |09/2018| FF| CMOS| Digic 8 |
| 0x00000805 | PowerShot SX70 HS | 09/2018| 1/2.3"| BSI-CMOS|Digic 8 |
| 0x80000433 | EOS RP | 02/2019 | FF | CMOS |Digic 8 |
| 0x80000436 | EOS Rebel SL3 / 250D / Kiss X10 | 04/2019 | APS-C | CMOS |Digic 8 |
| 0x00000804 | Powershot G5 X Mark II | 07/2019 | 1" | BSI-CMOS |Digic 8 |
| 0x00000808 | PowerShot G7 X Mark III | 07/2019 | 1" | BSI-CMOS |Digic 8 |
| 0x00000811 | EOS M6 Mark II  | 08/2019 | APS-C | CMOS |Digic 8 |
| 0x80000437 | EOS 90D | 08/2019 | APS-C | CMOS |Digic 8 |
| 0x00000812 | EOS M200 | 09/2019 | APS-C | CMOS |Digic 8 |
| 0x80000428 | EOS 1DX Mark III | 01/2020 | FF | CMOS |Digic X |
| 0x80000435 | 850D / T8i / Kiss X10i | 02/2020 | APS-C | CMOS |Digic 8 |
| 0x80000453 | EOS R6 | 07/2020 | FF | CMOS |DigicX |
| 0x80000421 | EOS R5 | 07/2020 | FF | CMOS |DigicX |
| 0x80000468 | EOS M50 Mark II / Kiss M2 | 10/2020 | APS-C | CMOS |Digic8 |
| 0x80000450 | EOS R3 | 09/2021 | FF | BSI-CMOS |DigicX |
| 0x80000464 | EOS R7 | 05/2022 | APS-C | CMOS |DigicX |
| 0x80000465 | EOS R10 | 05/2022 | APS-C | CMOS |DigicX |


## Samples 

http://www.photographyblog.com, https://raw.pixls.us/data/Canon, https://www.dpreview.com, https://www.imaging-resource.com

### CRM samples (from C200)

http://www.4kshooters.net/2017/10/04/canon-c200-raw-footage-workflow-free-samples-for-download/

