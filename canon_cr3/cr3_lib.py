'''
parse CR3 file format from Canon (@lorenzo2472)
from https://github.com/lclevy/canon_cr3

License is GPLv3

This file is part of canon_cr3.

cannon_cr3 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

canon_cr3 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with cannon_cr3. If not, see <http://www.gnu.org/licenses/>.


'''

from struct import unpack, Struct
from binascii import unhexlify, hexlify

class Cr3FileParser:

    def __init__(self, filepath):
        self.cr3 = dict()
        self.count = dict()
        self._thumbnail_data = None
        self._preview_image = None
        self.NAMELEN = 4
        self.SIZELEN = 4
        self.UUID_LEN = 16
        self.CTBO_LINE_LEN = 20
        self.S_IFD_ENTRY_REC = Struct('<HHLL')
        self.innerOffsets = {b'CRAW': 0x52, b'CCTP': 12, b'stsd': 8, b'dref': 8, b'CDI1': 4}
        self.tags = {b'ftyp': self.ftyp, b'moov': self.moov, b'uuid': self.uuid, b'stsz': self.stsz, b'co64': self.co64, b'PRVW': self.prvw,
                     b'CTBO': self.ctbo, b'CNCV': self.cncv, b'CDI1': self.cdi1, b'IAD1': self.iad1, b'CMP1': self.cmp1, b'CRAW': self.craw,
                     b'THMB': self.thmb}
        self.file_path = filepath
        with open(filepath, 'rb') as f:
            self._file_contents = f.read()
            self.filesize = f.tell()
        self.offsets = self._parse(self._file_contents, 0, 0)

    def get_short_be(self, d, a):
        return unpack('>H', (d)[a:a + 2])[0]

    def get_short_le(self, d, a):
        return unpack('<H', (d)[a:a + 2])[0]

    def get_long_be(self, d, a):
        return unpack('>L', (d)[a:a + 4])[0]

    def get_long_le(self, d, a):
        return unpack('<L', (d)[a:a + 4])[0]

    def get_long_long_be(self, d, a):
        return unpack('>Q', (d)[a:a + 8])[0]

    def thmb(self, d, l, depth):
        w = self.get_short_be(d, 0xc - 8)
        h = self.get_short_be(d, 0xe - 8)
        jpegSize = self.get_long_be(d, 0x10 - 8)
        self._thumbnail_data = d[0x18 - 8:0x18 - 8 + jpegSize]
        return w, h, jpegSize

    def craw(self, d, l, depth):
        w = self.get_short_be(d, 24)
        h = self.get_short_be(d, 26)
        bits = self.get_long_be(d, 72)
        return (w, h)

    def cmp1(self, d, l, depth):
        w = self.get_long_be(d, 8)  # 16 in format description (readme.md)
        h = self.get_long_be(d, 12)
        slice_w = self.get_long_be(d, 16)
        crx_header_size = self.get_long_be(d, 28)
        # print(w, h, slice_w, crx_header_size)
        return (w, h, slice_w, crx_header_size)

    def iad1(self, d, l, depth):
        pass

    def cdi1(self, d, l, depth):
        pass

    def cncv(self, d, l, depth):
        return d[:]

    def tiff(self, d, l, depth, base, name):
        ifd = dict()
        order = d[0:2]
        if order != b'II':
            return
        marker = self.get_short_le(d, 2)
        if marker != 0x2a:
            return
        ptr = self.get_short_le(d, 4)
        n = self.get_short_le(d, ptr)
        ptr = ptr + 2
        for i in range(n):
            tag, type, length, val = self.S_IFD_ENTRY_REC.unpack_from(d[ptr:ptr + self.S_IFD_ENTRY_REC.size])
            ifd[tag] = (base + ptr, type, length, val)
            ptr = ptr + self.S_IFD_ENTRY_REC.size
        return base, ifd

    def ctmd(self, d, l, depth, base, name):
        list = []
        nb = self.get_long_be(d, 8)
        for i in range(nb):
            type = self.get_long_be(d, 12 + i * 8)
            size = self.get_long_be(d, 16 + i * 8)
            list.append((type, size))
        return list

    def ctbo(self, d, l, depth):
        nbLine = self.get_long_be(d, 0)
        offsetList = {}
        for n in range(nbLine):
            idx = self.get_long_be(d, 4 + n * self.CTBO_LINE_LEN)
            offset = self.get_long_long_be(d, 4 + 4 + n * self.CTBO_LINE_LEN)
            size = self.get_long_long_be(d, 4 + 4 + 8 + n * self.CTBO_LINE_LEN)
            offsetList[idx] = (offset, size)
        return offsetList

    def prvw(self, d, l, depth):
        w = self.get_short_be(d, 0xe - 8)
        h = self.get_short_be(d, 0x10 - 8)
        jpegSize = self.get_long_be(d, 0x14 - 8)
        self._preview_image = d[0x18 - 8:0x18 - 8 + jpegSize]
        return w, h, jpegSize

    def co64(self, d, l, depth):
        version = self.get_long_be(d, 0)
        count = self.get_long_be(d, 4)
        size = self.get_long_long_be(d, 8)
        return size

    def stsz(self, d, l, depth):
        version = self.get_long_be(d, 0)
        if l==0x14:
          size = self.get_long_be(d, 4)
          count = self.get_long_be(d, 8)
        else:  #0x18
          size = self.get_long_be(d, 12)
          count = self.get_long_be(d, 8)
        return size

    def uuid(self, d, l, depth):
        uuidValue = d[:16]

    def ftyp(self, d, l, depth):
        major_brand = d[:4]
        minor_version = self.get_long_be(d, 4)
        compatible_brands = []
        for e in range((l - (4 * 4)) // 4):
            compatible_brands.append(d[8 + e * 4:8 + e * 4 + 4])

    def moov(self, d, l, depth):
        pass

    def _trak_data(self, trak):
        return self._file_contents[self.cr3[trak][b'co64']:self.cr3[trak][b'co64'] + self.cr3[trak][b'stsz']]

    def _parse(self, d, base, depth):

        o = 0
        while o < len(d):
            l = self.get_long_be(d, o)
            chunkName = d[o + self.SIZELEN:o + self.SIZELEN + self.NAMELEN]
            no = self.SIZELEN + self.NAMELEN  # next offset to look for data
            if l == 1:
                l = self.get_long_long_be(d, o + self.SIZELEN + self.NAMELEN)
                no = self.SIZELEN + self.NAMELEN + 8
            dl = min(32, l)  # display length

            if chunkName not in self.count:  # enumerate atom to create unique ID
                self.count[chunkName] = 1
            else:
                self.count[chunkName] = self.count[chunkName] + 1
            if chunkName == b'trak':  # will keep stsz and co64 per trak
                trakName = 'trak%d' % self.count[b'trak']
                if trakName not in self.cr3:
                    self.cr3[trakName] = dict()

            if chunkName in self.tags:  # dedicated parsing
                r = self.tags[chunkName](d[o + no:o + no + l - no], l, depth + 1)  # return results
            elif chunkName in {b'CMT1', b'CMT2', b'CMT3', b'CMT4'}:
                r = self.tiff(d[o + no:o + no + l - no], l, depth + 1, base + o + no, chunkName)
                self.cr3[chunkName] = r
            elif chunkName == b'CTMD':
                r = self.ctmd(d[o + no:o + no + l - no], l, depth + 1, base + o + no, chunkName)
                self.cr3[chunkName] = r

            if chunkName in {b'moov', b'trak', b'mdia', b'minf', b'dinf', b'stbl'}:  # requires inner parsing, just after the name
                self._parse(d[o + no:o + no + l - no], base + o + no, depth + 1)
            elif chunkName == b'uuid':  # inner parsing at specific offsets after name
                uuidValue = d[o + no:o + no + self.UUID_LEN]  # it depends on uuid values
                if uuidValue == unhexlify('85c0b687820f11e08111f4ce462b6a48'):
                    self._parse(d[o + no + self.UUID_LEN:o + no + self.UUID_LEN + l - no - self.UUID_LEN], base + o + no + self.UUID_LEN, depth + 1)
                if uuidValue == unhexlify('eaf42b5e1c984b88b9fbb7dc406e4d16'):
                    self._parse(d[o + no + self.UUID_LEN + 8:o + no + self.UUID_LEN + 8 + l - no - 8 - self.UUID_LEN],
                               base + o + no + self.UUID_LEN + 8, depth + 1)
            elif chunkName in self.innerOffsets:  # it depends on chunkName
                start = o + no + self.innerOffsets[chunkName]
                end = start + l - no - self.innerOffsets[chunkName]
                self._parse(d[start:end], start, depth + 1)

            # post processing
            if chunkName == b'stsz' or chunkName == b'co64' or chunkName == b'CRAW' or chunkName == b'CMP1':  # keep these values per trak
                trakName = 'trak%d' % self.count[b'trak']
                self.cr3[trakName][chunkName] = r
            elif chunkName == b'CNCV' or chunkName == b'CTBO':
                self.cr3[chunkName] = r
            elif chunkName == b'PRVW' or chunkName == b'THMB':
                self.cr3[chunkName] = *r, base + o + no + 16  # save offset
            o += l
        return o


class CmtdDataParser(Cr3FileParser):

    def __init__(self, filepath):
        super().__init__(filepath)
        self.TIFF_TYPE_UCHAR = 1
        self.TIFF_TYPE_STRING = 2
        self.TIFF_TYPE_USHORT = 3
        self.TIFF_TYPE_ULONG = 4
        self.TIFF_TYPE_URATIONAL = 5
        self.TIFF_TYPE_CHAR = 6
        self.TIFF_TYPE_BYTESEQ = 7
        self.TIFF_TYPE_SHORT = 8
        self.TIFF_TYPE_LONG = 9
        self.TIFF_TYPE_RATIONAL = 10
        self.TIFF_TYPE_FLOAT4 = 11
        self.TIFF_TYPE_FLOAT8 = 12

        self.TIFF_CMT3_SENSORINFO = 0xe0
        self.TIFF_CMT3_CAMERASETTINGS = 1
        self.TIFF_CAMERASETTINGS_QUALITY_RAW = 4
        self.TIFF_CAMERASETTINGS_QUALITY_CRAW = 7
        self.TIFF_CMT3_MODELID = 0x10
        self.TIFF_CMT1_MODEL = 0x110

        self.tiffTypeLen = [1, 1, 2, 4, 4 + 4, 1, 1, 2, 4, 4 + 4, 4, 8]
        self.tiffTypeNames = ["uchar", "string", "ushort", "ulong", "urational", "char", "byteseq", "short", "long", "rational", "float4", "float8"]
        self._parse_ctmd()


    def _sensor_characteristics(self):
        # get sensor characteristics
        sensorInfoData, sensorInfoEntry = self.getTiffTagData(b'CMT3', self.TIFF_CMT3_SENSORINFO)
        # for each TIFF entry, we have (offset, type, length, value). If value is a pointer, we use getTiffTagData() to get the content
        sensor_info_list = [self.get_short_le(sensorInfoData, i) for i in range(0, sensorInfoEntry[2], self.tiffTypeLen[sensorInfoEntry[1] - 1])]
        return sensor_info_list

    def parseCTMD(self):
        # in trak4/'CTMD' (stored in cr3[b'CTMD']), we have types and size of CMTD records, but CMTD data is in 'mdat' section
        ctmd_data = self._trak_data('trak4')
        ctmd_offset = 0
        file_offset = self.cr3['trak4'][b'co64']
        ctmd_records = dict()
        for type, size in self.cr3[b'CTMD']:  # contains type and size
            ctmd_record = ctmd_data[ctmd_offset: ctmd_offset + size]
            record_size = self.get_long_le(ctmd_record, 0)
            record_type = self.get_short_le(ctmd_record, 4)
            if record_size != size or record_type != type:
                print('warning CMDT type:%d/%d size:0x%x/0x%x' % (type, record_type, size, record_size))
            if record_type in [7, 8, 9]:
                record_offset = 12  # inside the record
                ctmd_tiff = dict()
                while record_offset < record_size:
                    payload_size = self.get_long_le(ctmd_record[record_offset:], 0)
                    payload_tag = self.get_long_le(ctmd_record[record_offset:], 4)
                    r = self.tiff(ctmd_record[record_offset + 8:], payload_size, 1, 0, b'CTMD%d_0x%x' % (record_type, payload_tag))
                    ctmd_tiff[payload_tag] = (file_offset + ctmd_offset + record_offset, payload_size, payload_tag, r)
                    record_offset += payload_size
                ctmd_records[type] = (size, type, file_offset + ctmd_offset, ctmd_tiff)  # store context and TIFF entries
            else:
                ctmd_records[type] = (size, type, file_offset + ctmd_offset)  # do not store content, but type, size and pointer for later processing
            ctmd_offset += size
        return ctmd_records

    def getTiffTagData(self, name, tag):

        tagEntry = self.cr3[name][1][tag]
        # print( 'tagEntry', tagEntry )
        base = self.cr3[name][0]
        type = tagEntry[1]
        length = tagEntry[2]
        val = tagEntry[3]
        size = self.tiffTypeLen[type - 1] * length
        tagInfoData = self._file_contents[base + val: base + val + size]
        return tagInfoData, tagEntry

    def _parse_ctmd(self):
        ctmd = self.parseCTMD()
        # generic way to list CTMD entries
        for entry in [1, 3, 7, 8]:
            ctmd_record = ctmd[entry]
            record_size = ctmd_record[0]
            record_type = ctmd_record[1]
            record_offset = ctmd_record[2]
            if len(ctmd_record) > 3:  # TIFF
                for subdir_tag, tiff_subdir in ctmd_record[3].items():
                    offset, payload_size, payload_tag, entries = tiff_subdir
                    for tag, ifd_entry in entries[1].items():
                        entry_offset, entry_type, entry_len, entry_value = ifd_entry
            else:  # not TIFF
                ctmd_data = self._file_contents[record_offset: record_offset + record_size]  # we do not know how to parse it

        # now we want raw data of TIFF entry 0x4016, in subdir 0x927c, in CTMD record #7. We know it is type=4=long, little endian 32 bits
        record_subdirs = ctmd[7][3]
        subdir = record_subdirs[0x927c][3]  # (offset, list)
        subdir_offset = record_subdirs[0x927c][0]
        entry_offset, entry_type, entry_len, entry_value = subdir[1][0x4016]
        data_offset = subdir_offset + 8 + entry_value  # TIFF_BASE is 8 bytes after TIFF subdir




            # get model name and model Id
        modelIdEntry = self.cr3[b'CMT3'][1][self.TIFF_CMT3_MODELID]
        modelData, modelEntry = self.getTiffTagData(b'CMT1', self.TIFF_CMT1_MODEL)
        modelId = modelIdEntry[3]


