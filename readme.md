# Describing the Canon Raw v3 (CR3) file format #

version: 19mar2018 

Laurent Clévy (@Lorenzo2472)

other contributors are welcome!



### Table of contents ###

  * [Introduction](#introduction)

  * [C-Raw-codec](#about-c-raw-codec)
  * [About Cinema RAW Light codec](#about-cinema-raw-Light-codec)
  * [CR3 file Structure](#cr3-file-Structure)
  * [Canon tags description](#canon-tags-description)
      * [THMB Thumbnail](#thmb-(thumbnail)) 
      * [CTBO](#ctbo)
      * [PRVW (Preview)](#prvw-(preview))
  * [Crx codec structures](#crx-codec-structures)





## Introduction ##

The Canon CR3 format is mainly based on the ISO Base Media File Format (ISO/IEC 14496-12), with custom tags. Some tags contains TIFF structures (like IFDs, Makernotes...)

Phil Harvey, the author of ExifTool, already identified some custom tags: [Canon CR3 tags](https://sno.phy.queensu.ca/~phil/exiftool/TagNames/Canon.html#uuid "Canon CR3 tags")

Canon Raw v2 is described here: http://lclevy.free.fr/cr2/ and Canon CRW here: https://sno.phy.queensu.ca/~phil/exiftool/canon_raw.html



#### About C-RAW codec

"Supports the next-generation CR3 RAW format and the new C-RAW compression format. The C – RAW format is 40% smaller in file size than conventional RAW, and it corresponds to in – camera RAW development and digital lens optimizer"

See this related patent : http://patents.com/us-20170359471.html, US Patent 20170359471 (December 14th, 2017)

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

#### About Cinema RAW Light codec

"Cinema RAW Light does not record in the frame-by-frame file structure of a traditional RAW format. Instead, using a **proprietary format developed by Canon**, the RAW information is compiled into a single Canon RAW Movie file, or .CRM.

Once a Canon RAW Movie is recorded, it then needs to be unpacked in one of two ways. The first and more traditional route would be utilizing an updated version of Canon’s RAW Development Software. At its core, this software allows for the unpacking, modification, and debayering of Cinema RAW Light files. Modification is the key phrase here, as we have the opportunity to modify the parameters by which our footage is debayered. EOS C200 captures its RAW information in a proprietary RAW Gamut and RAW Gamma. This data needs to be taken from their RAW spaces, and conformed into one of the many gamma curves or color spaces to begin the post-production process."

http://www.learn.usa.canon.com/resources/articles/2017/eos-c200-post-production-brief.shtml

```
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'Canon-C200-Raw.CRM':
  Metadata:
    major_brand     : crx
    minor_version   : 1
    compatible_brands: crx isom
    creation_time   : 2017-10-01T22:04:43.000000Z
    timecode        : 18:28:18;24
  Duration: 00:00:49.05, start: 0.000000, bitrate: 26049 kb/s
    Stream #0:0(eng): Video: none (CRAW / 0x57415243), none, 4096x2160, 993500 kb/s, 59.94 fps, 59.94 tbr, 60k tbn, 60k tbc (default)
    Metadata:
      creation_time   : 2017-10-01T22:04:43.000000Z
    Stream #0:1(eng): Audio: pcm_s16be (twos / 0x736F7774), 48000 Hz, mono, s16, 768 kb/s (default)
    Metadata:
      creation_time   : 2017-10-01T22:04:43.000000Z
    Stream #0:2(eng): Audio: pcm_s16be (twos / 0x736F7774), 48000 Hz, mono, s16, 768 kb/s (default)
    Metadata:
      creation_time   : 2017-10-01T22:04:43.000000Z
    Stream #0:3(eng): Audio: pcm_s16be (twos / 0x736F7774), 48000 Hz, mono, s16, 768 kb/s (default)
    Metadata:
      creation_time   : 2017-10-01T22:04:43.000000Z
    Stream #0:4(eng): Audio: pcm_s16be (twos / 0x736F7774), 48000 Hz, mono, s16, 768 kb/s (default)
    Metadata:
      creation_time   : 2017-10-01T22:04:43.000000Z
    Stream #0:5(eng): Data: none (tmcd / 0x64636D74), 1 kb/s (default)
    Metadata:
      creation_time   : 2017-10-01T22:04:43.000000Z
      timecode        : 18:28:18;24
    Stream #0:6(eng): Data: none (CTMD / 0x444D5443), 774 kb/s (default)
    Metadata:
      creation_time   : 2017-10-01T22:04:43.000000Z
```




## CR3 file Structure ##
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

   - picture #2 (1624x1080, craw preview)

   - picture #3 (main, 6888x4056, craw main image)

   - metadata (TIFF like)

      ​

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
00000004 0000000000000000 0000000000000000 no lossless raw ?
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

### mdat_picture2 (crx codec)

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

### mdat_picture3 (crx codec)

size=0x201ef28

```
0x546c70:  ff010008 00ff40b8 00000000 ff020008    ......@......... 
0x546c80:  00405528 08000000 ff030008 00405528    .@U(.........@U(
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



## crx codec structures

(using canon_eos_m50_02.cr3, by analysing hex data)

small picture 1624x1080

```
picture data size = 0x1cbc40
 7b5c0 + 70600 + 70640 + 6f9d0 == 1cbbd0
crx header (size=0x70)
0x37b030:  ff010008 001cbbd0 00000000             size after header is 0x1cbbd0
           ff020008 0007b5c0 08000000             subpic#0, size is 7b5c0
           ff030008 0007b5c0 00200001 
           ff020008 00070600 18000000             subpic#1
0x37b060:  ff030008 00070600 00200002 
           ff020008 00070640 28000000             subpic#2
           ff030008 00070640 00200006 
           ff020008 0006f9d0 38000000             subpic#3
0x37b090:  ff030008 0006f9d0 00200006 
           00000000 
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
0x2565b80:  f8dfd549 a2c4f792 ddc72efe 2c9a7435    ...I........,.t5
0x2565b90:  f8000000 00000000 
                              18000000 01000000    546d48 + ff40b8 + 102ad98 = 2565B98 (end of subpic#1.3)
```



## References ##

- ISO base media file format : [ISO/IEC 14496-12:2015](http://http://standards.iso.org/ittf/PubliclyAvailableStandards/c068960_ISO_IEC_14496-12_2015.zip "ISO IEC 14496-12:2015")

- MP4 file format : [ISO/IEC 14496-14:2003](http://jchblog.u.qiniudn.com/doc/ISO_IEC_14496-14_2003-11-15.pdf "ISO/IEC 14496-14:2003")

- [ISO 14496-1 Media Format](http://xhelmboyx.tripod.com/formats/mp4-layout.txt "ISO 14496-1 Media Format")

- Canon DPP 4.8.20 supports M50 CR3: [DPP](http://support-sg.canon-asia.com/contents/SG/EN/0200544802.html "DPP")

	 Cimena RAW Development 2.1 for windows supports CRM movie format :  [Cinema Raw](https://www.usa.canon.com/internet/portal/us/home/support/details/cameras/cinema-eos/eos-c200?tab=drivers_downloads	"Cinema Raw")

- Discussions about CR3 format: 
  - [rawspeed](https://github.com/darktable-org/rawspeed/issues/121)

  - [Exiv2](https://github.com/Exiv2/exiv2/issues/236)




## CR3 samples (from M50 camera)

Files canon_eos_m50_02.cr3, canon_eos_m50_06.cr3, canon_eos_m50_10.cr3, canon_eos_m50_23.cr3 can be downloaded from:

http://www.photographyblog.com/reviews/canon_eos_m50_review/preview_images/

See exiftool directory for outputs of "exiftool(-k).exe" -v3 -H -a  canon_eos_m50_*.cr3
[exiftool02.txt](exiftool/exiftool02.txt)

See ffmpeg directory for outputs of "ffmpeg -i"
[ffmpeg02.txt](ffmpeg/ffmpeg02.txt)
