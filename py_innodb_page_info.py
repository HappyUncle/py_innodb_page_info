#! /usr/bin/env python
# encoding=utf-8

import os
from sys import argv

# Start of the data on the page
FIL_PAGE_DATA = 38

FIL_PAGE_SPACE_OR_CHKSUM = 0 # checksum
FIL_PAGE_OFFSET = 4  # page offset inside space
FIL_PAGE_PREV = 8
FIL_PAGE_NEXT = 12
FIL_PAGE_LSN = 16
FIL_PAGE_TYPE = 24  # File page type
FIL_PAGE_FILE_FLUSH_LSN = 26
FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID = 34


# Types of an undo log segment */
TRX_UNDO_INSERT = 1
TRX_UNDO_UPDATE = 2

# On a page of any file segment, data may be put starting from this offset
FSEG_PAGE_DATA = FIL_PAGE_DATA

# The offset of the undo log page header on pages of the undo log
TRX_UNDO_PAGE_HDR = FSEG_PAGE_DATA

#https://github.com/mysql/mysql-server/blob/7ed30a748964c009d4909cb8b4b22036ebdef239/storage/innobase/include/page0types.h
PAGE_N_DIR_SLOTS = 0
PAGE_LEVEL = 26  # level of the node in an index tree; the leaf level is the level 0 */
PAGE_INDEX_ID = 28  # Index ID

# https://github.com/mysql/mysql-server/blob/8.0/storage/innobase/include/fil0fil.h#L1203
innodb_page_type = {
    '0000': u'Freshly Allocated Page',
    '0002': u'Undo Log Page',
    '0003': u'File Segment inode',
    '0004': u'Insert Buffer Free List',
    '0005': u'Insert Buffer Bitmap',
    '0006': u'System Page',
    '0007': u'Transaction system Page',
    '0008': u'File Space Header',
    '0009': u'extend description page',
    '000a': u'Uncompressed BLOB Page',
    '000b': u'1st compressed BLOB Page',
    '000c': u'Subsequent compressed BLOB Page',
    '000d': u'In old tablespaces, garbage in FIL_PAGE_TYPE is replaced with this value when flushing pages',
    '0015': u'Rollback Segment Array pag',
    '0016': u'Index pages of uncompressed LOB',
    '0017': u'Data pages of uncompressed LOB',
    '0018': u'The first page of an uncompressed LOB',
    '45bf': u'B-tree Node',
    '45be': u'R-tree Node',
    '45bd': u'Tablespace SDI Index page',  # MySQL8.0 Serialized Dictionary Information Page
}

innodb_page_direction = {
    '0000': 'Unknown(0x0000)',
    '0001': 'Page Left',
    '0002': 'Page Right',
    '0003': 'Page Same Rec',
    '0004': 'Page Same Page',
    '0005': 'Page No Direction',
    'ffff': 'Unkown2(0xffff)'
}

INNODB_PAGE_SIZE = 1024 * 16  # InnoDB Page 16K
VARIABLE_FIELD_COUNT = 1
NULL_FIELD_COUNT = 0


class myargv(object):
    def __init__(self, argv):
        self.argv = argv
        self.parms = {}
        self.tablespace = ''

    def parse_cmdline(self):
        argv = self.argv
        if len(argv) == 1:
            print 'Usage: python py_innodb_page_info.py [OPTIONS] tablespace_file'
            print 'For more options, use python py_innodb_page_info.py -h'
            return 0
        while argv:
            if argv[0][0] == '-':
                if argv[0][1] == 'h':
                    self.parms[argv[0]] = ''
                    argv = argv[1:]
                    break
                if argv[0][1] == 'v':
                    self.parms[argv[0]] = ''
                    argv = argv[1:]
                else:
                    self.parms[argv[0]] = argv[1]
                    argv = argv[2:]
            else:
                self.tablespace = argv[0]
                argv = argv[1:]
        if self.parms.has_key('-h'):
            print'Get InnoDB Page Info'
            print 'Usage: python py_innodb_page_info.py [OPTIONS] tablespace_file\n'
            print 'The following options may be given as the first argument:'
            print '-h        help '
            print '-o output put the result to file'
            print '-t number thread to anayle the tablespace file'
            print '-v        verbose mode'
            return 0
        return 1


def mach_read_from_n(page, start_offset, length):
    ret = page[start_offset:start_offset + length]
    return ret.encode('hex')

def mach_read_from_n_dec(page, start_offset, length):
    ret = page[start_offset:start_offset + length]
    return int(ret.encode('hex'), 16)

def get_innodb_page_type(myargv):
    f = file(myargv.tablespace, 'rb')
    fsize = os.path.getsize(f.name) / INNODB_PAGE_SIZE
    ret = {}
    for i in range(fsize):
        page = f.read(INNODB_PAGE_SIZE)
        page_checksum = mach_read_from_n(page, FIL_PAGE_SPACE_OR_CHKSUM, 4)
        page_offset = mach_read_from_n(page, FIL_PAGE_OFFSET, 4)
        page_prev = mach_read_from_n(page, FIL_PAGE_PREV, 4)
        page_next = mach_read_from_n(page, FIL_PAGE_NEXT, 4)
        page_lsn = mach_read_from_n_dec(page, FIL_PAGE_LSN, 8)
        page_type = mach_read_from_n(page, FIL_PAGE_TYPE, 2)
        page_lsn_flush = mach_read_from_n_dec(page, FIL_PAGE_FILE_FLUSH_LSN, 8)
        page_belongs = mach_read_from_n(page, FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID, 4)

        if myargv.parms.has_key('-v'):
            sss = "checksum %s, offset %s, prev %s, next %s, lsn %8s, flush lsn %8s, belongs %s, type <%s>" % \
                  (page_checksum, page_offset, page_prev, page_next, page_lsn, page_lsn_flush, page_belongs, innodb_page_type[page_type])
            if page_type == '45bf':
                page_slot_no = mach_read_from_n_dec(page, PAGE_N_DIR_SLOTS, 2)
                page_level = mach_read_from_n_dec(page, FIL_PAGE_DATA + PAGE_LEVEL, 2)
                index_id = mach_read_from_n_dec(page, FIL_PAGE_DATA + PAGE_INDEX_ID, 8)
                sss = "%s, slot %8s, level <%s>, index_id <%s>" % (sss, page_slot_no, page_level, index_id)
            print sss
        if not ret.has_key(page_type):
            ret[page_type] = 1
        else:
            ret[page_type] = ret[page_type] + 1
    print "----------------------------------------------"
    print "Total number of page: %d:" % fsize
    for type in ret:
        print "%s: %s" % (innodb_page_type[type], ret[type])


if __name__ == '__main__':
    myargv = myargv(argv)
    if myargv.parse_cmdline() == 0:
        pass
    else:
        get_innodb_page_type(myargv)
