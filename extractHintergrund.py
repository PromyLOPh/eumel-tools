#!/usr/bin/env python3

"""
Extract EUMEL Hintergrund floppy disk image. Known to work only with version
1.8 images.
"""

import os
from enum import IntEnum, unique
from operator import attrgetter

from eumel import pagesize

from construct import Struct, Const, Padding, PaddedString, Int8ul, Int16ul, \
        Int24ul, Int32ul, Flag, Computed, this, Array, BitStruct, Bitwise, \
        BitsInteger, Embedded, Nibble, Sequence, Enum

hgIdent = Struct(
    "signature" / Const(b"EUMEL-"),
    "version" / PaddedString(6, "ascii"),
    Padding(1),
    "isShutup" / Int8ul * "true if value is 0", # XXX
    "bootCount" / Int16ul,
    Padding(0x24) * "undocumented",
    "_hgblocks2" / Int16ul,
    Padding(0x50) * "unknown/undocumented",
    "_hgblocks" / Int16ul,
    "_plusident" / Int16ul,
    "isPlus" / Computed(this._hgblocks == 1 and this._plusident == 0),
    "blocks" / Computed(this._hgblocks if this.isPlus else this._hgblocks2), # XXX: this is not correct
    ) * "First block of Hintergrund"

blockref = Struct(
    "value" / Int24ul,
    "control" / Int8ul,
    )

anchor = Struct(
    Const(b"\xff"*4),
    "akttab" / blockref,
    "clorX" / blockref,
    Const(b"\xff"*4*3),
    "taskRoot" / blockref,
    Const(b"\xff"*4),
    ) * "System anchor block"

blockTable = Array(pagesize//blockref.sizeof(), blockref)

# XXX: skip const
segmentTable = Sequence (Const (2*blockref.sizeof ()*b'\xff'), Array (14, blockref))

drinfo = Struct(
    "count" / blockref * "Number of blocks/pages allocated",
    "blocks" / Array(3, blockref) * "Direct block references for page 1, 2 and 3",
    "blockTables" / Array (2, blockref) * "Block references to block tables",
    "segmentTables" / Array (2, blockref) * "Block references to segment tables, which refer to block tables",
    ) * "Dataspace descriptor"

# see src/devel/misc/unknown/src/XSTATUS.ELA
# EUMEL’s pcb function returns the 16 bit word at position (0x1e+2*<id>)%0x40
# i.e. module is pcb(23) → at offset 0x0c
pcb = Struct(
    "wstate" / Int32ul,
    "millis" / Int8ul,
    "unknown" / BitStruct (
        "unused" / Flag, # bit 7
        Padding(6),
        "comflag" / Flag, # bit 0
        ),
    "status" / Int8ul,
    "statusflags" / Int8ul * "unknown status flags",
    "pricnt" / Int8ul,
    "_icount" / Int16ul,
    "flags" / BitStruct( # XXX: embedding BitStruct is not possible
        "iserror" / Flag, # bit 7
        "disablestop" / Flag, # bit 6
        Padding(1),
        "arith" / Flag, # bit 4
        Padding(2),
        "_codesegment" / BitsInteger(2), # bits 0…1
        ),
    "icount" / Computed(this._icount | (this.flags._codesegment<<16)), # XXX: byte-swapping 18 bit int is not possible? is codesegment low/high bits of icount?
    "module" / Int16ul,
    "pbase" / Int8ul,
    "c8k" / Int8ul,
    "lbase" / Int16ul,
    "ltop" / Int16ul,
    "lsTop" / Int16ul,
    "heap" / BitStruct( # XXX: is this just a 16 bit pointer?
        "top" / BitsInteger(12), # XXX: incorrect byte order
        "segment" / Nibble, # bit 0…3
        ),
    Padding(4),
    "priclk" / Int8ul,
    "priv" / Int8ul,
    Padding(2),
    "linenr" / Int16ul, # ↓ See library/entwurf-systemdokumentation-1982.djvu section 2.4.13 (page 29)
    "errorline" / Int16ul,
    "errorcode" / Int16ul,
    "channel" / Int16ul,
    Padding(2), # XXX: sure about this padding?
    "prio" / Int16ul,
    "msgcode" / Int16ul,
    "msgds" / Int16ul,
    "taskid" / Int16ul,
    "version" / Int16ul,
    "fromid" / Int32ul,
    Padding(8) * "unknown",
    Padding(64) * "usually ff",
    ) * "Leitblock"
assert pcb.sizeof() == 4*drinfo.sizeof(), (pcb.sizeof(), drinfo.sizeof())

class CpuType (IntEnum):
    Z80 = 1
    INTEL8088 = 3
    M68K = 1024

urladerlink = Struct (
    "signature" / Const(b'EUMEL' + b' '*11),
    "blocks" / Int16ul,
    "hgver" / Int16ul,
    "cputype" / Enum (Int16ul, CpuType),
    "urver" / Int16ul,
    Padding (2),
    "shdvermin" / Int16ul,
    "shdvermax" / Int16ul,
    ) * "Urlader Linkleiste"

def copyblock (block, infd, outfd):
    if block == 0xffffff:
        written = outfd.write (b'\xff'*pagesize)
        assert written == pagesize
    else:
        infd.seek (block*pagesize, os.SEEK_SET)
        buf = infd.read (pagesize)
        assert len (buf) == pagesize
        written = outfd.write (buf)
        assert written == pagesize

def copyBlockTable (block, infd, outfd, skip=0):
    if block != 0xffffff:
        fd.seek (block*pagesize, os.SEEK_SET)
        for i, refl2 in enumerate (blockTable.parse_stream (infd)):
            if i >= skip:
                copyblock (refl2.value, fd, outfd)
    else:
        entries = (blockTable.sizeof()//blockref.sizeof())-skip
        outfd.write (b'\xff'*(pagesize*entries))

if __name__ == '__main__':
    import sys
    from struct import Struct, unpack

    with open (sys.argv[1], 'rb') as fd:
        # ident
        print (hgIdent.parse_stream (fd))
        fd.seek (0x1400, os.SEEK_SET)
        print (urladerlink.parse_stream (fd))

        fd.seek (pagesize)
        a = anchor.parse_stream (fd)

        # task root (level 1)
        fd.seek (a.taskRoot.value*pagesize)
        taskRoot = blockTable.parse_stream (fd)

        # task dataspaces(?) (level 2)
        for taskid, taskref in enumerate (taskRoot):
            if taskref.value == 0xffffff:
                continue
            print (f'task {taskid} is at {taskref.value} 0x{taskref.value*pagesize:x}')

            fd.seek (taskref.value*pagesize)
            dataspaces = blockTable.parse_stream (fd)

            for dsidhigh, dsref in enumerate (dataspaces):
                if dsref.value == 0xffffff:
                    continue
                print (f'\ttaskid {taskid} dsid {dsidhigh<<4} is at {dsref.value} 0x{dsref.value*pagesize:x}')

                # pcb and drinfo (level 3)
                fd.seek (dsref.value*pagesize)
                drinfoStart = 0
                if dsidhigh == 0:
                    p = pcb.parse_stream (fd)
                    print (f'\t+pcb taskid {p.taskid} version {p.version} icount {p.icount:x} arith {p.flags.arith} disablestop {p.flags.disablestop} iserror {p.flags.iserror} pbase {p.pbase:x} module {p.module}')
                    drinfoStart = 4
                print (f'\t\tdrinfo starting at {fd.tell():x}')
                for dsidlow in range (drinfoStart, 16):
                    dsid = dsidlow | dsidhigh << 4
                    d = drinfo.parse_stream (fd)
                    if d.count.value != 0xffffff and d.count.value != 0:
                        # pbt (page block table) 1/2 contain block refs for pages 0…127 and 128…256
                        # pst (page segment table) 1/2 contain block refs to page block tables for pages > 256
                        print (f'\t\tdrinfo {dsid} #{d.count.value} @ {[x.value for x in d.blocks]}, ind {[x.value for x in d.blockTables]}, ind2 {[x.value for x in d.segmentTables]}')

                        pos = fd.tell ()
                        with open (f'{taskid:04d}_{dsid:04d}.ds', 'wb') as outfd:
                            os.ftruncate (outfd.fileno(), 0)

                            # get the first three pages
                            for ref in d.blocks:
                                copyblock (ref.value, fd, outfd)

                            # indirect block refs (level 4a)
                            assert len (d.blockTables) == 2
                            # first four entries of first table are empty and must not be written!
                            copyBlockTable (d.blockTables[0].value, fd, outfd, 3)
                            copyBlockTable (d.blockTables[1].value, fd, outfd)

                            # segment tables (level 4b)
                            for segref in d.segmentTables:
                                if segref.value != 0xffffff:
                                    fd.seek (segref.value*pagesize, os.SEEK_SET)
                                    segtbl = segmentTable.parse_stream (fd)
                                    for ref in segtbl[1]:
                                        copyBlockTable (ref.value, fd, outfd)
                                else:
                                    outfd.write((14*128*pagesize)*b'\xff')

                            # 2*128 pages through block table, 2 segment tables with 14 refs to block tables each
                            expectedSize = (2*128+2*14*128)*pagesize
                            assert outfd.tell() == expectedSize, (outfd.tell(), expectedSize)
                    fd.seek (pos, os.SEEK_SET)

