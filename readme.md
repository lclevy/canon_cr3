# Describing the Canon Raw v3 (CR3) file format #

Laurent Clévy (@Lorenzo2472)

other contributors are welcome!



## Introduction ##

The Canon CR3 format is mainly based on the ISO base media file format (ISO/IEC 14496-12), with custom tags. Some tags contains TIFF structures (like IFDs, Makernotes...)

Phil Harvey, the author of ExifTool, already identified some custom tags: [Canon CR3 tags](http://https://sno.phy.queensu.ca/~phil/exiftool/TagNames/Canon.html#uuid "Canon CR3 tags")




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

        - **CTBO**

            - free
            - **CMT1** (Exif)
            - **CMT2** (Exif)
            - **CMT3** (Canon Makernotes)
            - **CMT4**
            - **THMB** (Thumbnail image in jpeg format)

 - **mvhd** (Movie Header)

 - **trak** (Track)
     - **tkhd** (Track Header)
     - **mdia** (Media)
       - **mdhd** (Media Header)
       - **hdlr** (Handler)
       - **minf** (Media Information container)
         - **vmhd**
         - **dinf**
           - **dref**
           - **url**
         - **stbl**
           - **stsd**
             - **CRAW**
               - jpeg
               - free
           - **stts**
           - **stsc**
           - **stsz**
           - **free**
           - **CO64** : pointer to picture #1 inside mdat

 - **trak**

    - ...
    - co64 : pointer to picture #2 in mdat

 - **trak**

    - ...
    - co64 : pointer to picture #3 in mdat

 - **trak**

    - ...
    - co64 : pointer to metadata in mdat

- **uuid** = be7acfcb 97a9 42e8 9c71 999491e3afac (xpacket data)

- **uuid** = eaf42b5e 1c98 4b88 b9fb b7dc406e4d16 (preview data)
   - PRVW

- **mdat** (main image data)

   - picture #1 (6000x4000, jpeg ?)

   - picture #2 (1624x1080, preview ?)

   - picture #3 (main, 6888x4056, lossy raw?)

   - metadata (TIFF like)

      ​

## Canon tags description

### CTBO

00000004 
00000001 00000000 00006b88 00000000 00010018 (offset and size of xpacket uuid)
00000002 00000000 00016ba0 00000000 00056d90 (offset and size of preview uuid)
00000003 00000000 0006d930 00000000 025022b8 (offset and size of mdat)
00000004 00000000 00000000 00000000 00000000 no lossy raw ?



## References ##

- ISO base media file format : [ISO/IEC 14496-12:2015](http://http://standards.iso.org/ittf/PubliclyAvailableStandards/c068960_ISO_IEC_14496-12_2015.zip "ISO IEC 14496-12:2015")

http://l.web.umkc.edu/lizhu/teaching/2016sp.video-communication/ref/mp4.pdf
http://jchblog.u.qiniudn.com/doc/ISO_IEC_14496-14_2003-11-15.pdf
http://xhelmboyx.tripod.com/formats/mp4-layout.txt

Discussion about CR3 format: https://github.com/darktable-org/rawspeed/issues/121

## CR3 samples

http://img.photographyblog.com/reviews/canon_eos_m50/photos/canon_eos_m50_01.cr3