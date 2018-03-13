# Describing the Canon Raw v3 (CR3) file format #

version: 13mar2018 

Laurent Clévy (@Lorenzo2472)

other contributors are welcome!



## Introduction ##

The Canon CR3 format is mainly based on the ISO Base Media File Format (ISO/IEC 14496-12), with custom tags. Some tags contains TIFF structures (like IFDs, Makernotes...)

Phil Harvey, the author of ExifTool, already identified some custom tags: [Canon CR3 tags](http://https://sno.phy.queensu.ca/~phil/exiftool/TagNames/Canon.html#uuid "Canon CR3 tags")

Canon Raw v2 is described here: http://lclevy.free.fr/cr2/ and Canon CRW here: https://sno.phy.queensu.ca/~phil/exiftool/canon_raw.html




## Structure ##
- **ftyp**: File Type Box

- **moov** : container box whose sub‐boxes define the metadata for a presentation 
    - **uuid** = 85c0b687 820f 11e0 8111 f4ce462b6a48
        - **CNCV** (Canon Compressor Version). "CanonCR3_001/00.09.00/00.00.00"

        - **CCTP** (Canon Compressor Table Pointers?). 00000000 00000001 00000003 (how many CCDT == 3 ?)

            - **CCDT** (?, 16 bytes). 

                00000000 00000010 00000000 00000001 (flags and index ?)

            - **CCDT** (?, 16 bytes). 

                00000000 00000001 00000000 00000002

            - **CCDT** (?, 16 bytes). 

                00000000 00000000 00000000 00000003

        - **CTBO** (Canon Trak b Offsets?)

            - free
            - **CMT1** (Canon Metadata? Exif)
            - **CMT2** (Canon Metadata? Exif)
            - **CMT3** (Canon Makernotes)
            - **CMT4** (Canon Metadata?)
            - **THMB** (Thumbnail image in jpeg format)
              - confirmed jpeg. size=160x120

 - **mvhd** (Movie Header)

 - **trak** (Track, embedded jpeg)
     - **tkhd** (Track Header)
     - **mdia** (Media)
       - **mdhd** (Media Header)
       - **hdlr** (Handler)
       - **minf** (Media Information container)
         - **vmhd** (Video Media Header)
         - **dinf** (Data information box)
           - **dref** (Data Reference box)
         - **stbl** (Sample table box)
           - **stsd** (Sample descriptions, codec types, init...)
             - **CRAW** (size=0x70)
               - W=6000, H=4000
               - **JPEG** (size=0xc)
               - **free**
           - **stts** (decoding, time-to-sample)
           - **stsc** (sample-to-chunk, partial data offset info)
           - **stsz** (sample sizes, framing)
             - size of picture #1 in mdat
           - **free**
           - **CO64** : pointer to picture #1 inside mdat

 - **trak** (big preview in c-raw?)

     - **tkhd**
     - **mdia**
         - **mdhd**
         - **hdlr**
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
                 - **stts**
                 - **stsc**
                 - **stsz** : size of picture #2 in mdat
                - **co64** : pointer to picture #2 in mdat

 - **trak** (main image in c-raw?)

     - **tkhd**
     - **mdia**
         - **mdhd**
         - **hdlr**
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
             - **stts**
             - **stsc**
             - **stsz** : size of picture #3 in mdat
            - **co64** : pointer to picture #3 in mdat

 - **trak** (metadata at end of mdat)

    - ...
    - **stsz** : size of metadata in mdat
    - **co64** : pointer to metadata in mdat

- **uuid** = be7acfcb 97a9 42e8 9c71 999491e3afac (xpacket data)

- **uuid** = eaf42b5e 1c98 4b88 b9fb b7dc406e4d16 (preview data)
   - **PRVW**
     - confirmed jpeg (1620x1080)

- **mdat** (main data)

   - picture #1 (6000x4000, jpeg)

   - picture #2 (1624x1080, lossy raw preview?)

   - picture #3 (main, 6888x4056, lossy raw?)

   - metadata (TIFF like)

      ​

## Canon tags description

### THBM (Thumbnail) 

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

### CTBO (using canon_eos_m50_02.cr3)

```
00000004 
00000001 00000000 00006b88 00000000 00010018 (offset and size of xpacket uuid)
00000002 00000000 00016ba0 00000000 00056d90 (offset and size of preview uuid)
00000003 00000000 0006d930 00000000 025022b8 (offset and size of mdat)
00000004 00000000 00000000 00000000 00000000 no lossless raw ?
```

### PRVW (Preview) 

from **uuid** = eaf42b5e 1c98 4b88 b9fb b7dc406e4d16

size = 1620x1008

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

### mdat_picture1 (confirmed jpeg)

size=0x30d6ef (from stsz)

6000x4000 pixels

```
0x06d940:  ffd8ffdb 00840006 04040604 04060604    
0x06d950:  06060606 080a110a 0a08080a 130f0f0c    
0x06d960:  11171519 17171517 15191d23 1f191b23    
0x06d970:  1b1b171f 2c1f2325 282a2a2a 191f2c30    
0x06d980:  2c283023 282a2801 0606060a 080a130a    
...
0x37b020:  03b0daaa 3185c13d a9d85276 3fffd900    
```

### mdat_picture2 (unknown compression)

size=0x1cbc40

```
0x37b030:  ff010008 001cbbd0 00000000 ff020008    ................ 
0x37b040:  0007b5c0 08000000 ff030008 0007b5c0    ................
0x37b050:  00200001 ff020008 00070600 18000000    . ..............
0x37b060:  ff030008 00070600 00200002 ff020008    ......... ......
0x37b070:  00070640 28000000 ff030008 00070640    ...@(..........@
0x37b080:  00200006 ff020008 0006f9d0 38000000    . ..........8...
0x37b090:  ff030008 0006f9d0 00200006 00000000    ......... ......
0x37b0a0:  00000000 002027a5 00000400 0f03e034    ..... '........4
0x37b0b0:  7565417b 810ded0e f68019d5 9085af6a    ueA{...........j
0x37b0c0:  95d4e700 cc0d744d 20d7c569 0af800b0    ......tM ..i....
...
0x546c30:  f1860b4a 31096b41 a64c0a0e f1b54760    ...J1.kA.L....G`
0x546c40:  74072f89 b1680333 16cb3c79 f9e98bc2    t./..h.3..<y....
0x546c50:  95a459a6 c0213203 37f136f1 b3711906    ..Y..!2.7.6..q..
0x546c60:  86bbe446 05c21456 bdbc0000 00000000    ...F...V........
```

### mdat_picture3 (unknown compression)

size=0x201ef28

```
0x546c70:  ff010008 00ff40b8 00000000 ff020008    ......@......... 
0x546c80:  00405528 08000000 ff030008 00405528    .@U(.........@U(
0x546c90:  00200006 ff020008 003fc8a8 18000000    . .......?......
0x546ca0:  ff030008 003fc8a8 00200003 ff020008    .....?... ......
0x546cb0:  003fc6e8 28000000 ff030008 003fc6e8    .?..(........?..
0x546cc0:  00200005 ff020008 003f5c00 38000000    . .......?\.8...
0x546cd0:  ff030008 003f5c00 00200000 ff010008    .....?\.. ......
0x546ce0:  0102ad98 00010000 ff020008 0040cb88    .............@..
0x546cf0:  08000000 ff030008 0040cb88 00200006    .........@... ..
0x546d00:  ff020008 0040eb50 18000000 ff030008    .....@.P........
0x546d10:  0040eb50 00200006 ff020008 0040ed48    .@.P. .......@.H
0x546d20:  28000000 ff030008 0040ed48 00200002    (........@.H. ..
0x546d30:  ff020008 00400978 38000000 ff030008    .....@.x8.......
0x546d40:  00400978 00200007 00000000 00202e45    .@.x. ....... .E
0x546d50:  00000000 00400392 26003b15 c982d276    .....@..&.;....v
0x546d60:  151ca7ce f3aa0b22 b35b3146 c2eb2d05    .......".[1F..-.
0x546d70:  c25fe658 d0c68c92 36b6c5f1 bf8df590    ._.X....6.......
0x546d80:  10e47ab2 5683714b 5ff10a75 65352000    ..z.V.qK_..ue5 .
....
0x2565b70:  bff1234a ce204824 8b54935d 5e0fc72d    ..#J. H$.T.]^..-
0x2565b80:  f8dfd549 a2c4f792 ddc72efe 2c9a7435    ...I........,.t5
0x2565b90:  f8000000 00000000 
```

### mdat_metadata (trak3)

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



## References ##

- ISO base media file format : [ISO/IEC 14496-12:2015](http://http://standards.iso.org/ittf/PubliclyAvailableStandards/c068960_ISO_IEC_14496-12_2015.zip "ISO IEC 14496-12:2015")
- MP4 file format : [ISO/IEC 14496-14:2003](http://jchblog.u.qiniudn.com/doc/ISO_IEC_14496-14_2003-11-15.pdf "ISO/IEC 14496-14:2003")
- [ISO 14496-1 Media Format](http://xhelmboyx.tripod.com/formats/mp4-layout.txt "ISO 14496-1 Media Format")

- Discussions about CR3 format: 
  - [rawspeed](https://github.com/darktable-org/rawspeed/issues/121)

  - [Exiv2](https://github.com/Exiv2/exiv2/issues/236)

    ​

## CR3 samples (from M50 camera)

Files canon_eos_m50_02.cr3, canon_eos_m50_06.cr3, canon_eos_m50_10.cr3, canon_eos_m50_23.cr3 can be downloaded from:

http://www.photographyblog.com/reviews/canon_eos_m50_review/preview_images/

See exiftool directory for outputs of "exiftool(-k).exe" -v3 -H -a  canon_eos_m50_**.cr3



