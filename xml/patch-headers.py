#! /usr/bin/env python
#
# Copyright (c) 2005  Joerg Wunsch
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# * Neither the name of the copyright holders nor the names of
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# $Id$
#

import os, sys, time, types, re

from types import *

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from Descparser import *
from Atmel2libc import *

home = os.environ['HOME']

xmls = home + "/src/jtagII/xml/Partdescriptionfiles"
headers = home + "/src/avr-libc/include/avr"

docfilename = "vectortable.dox"

# Mapping between header name and device name.  In case of a header
# name that covers more than one device, the device names form a tuple
# where the device with the largest feature set is listed as the first
# one.
table = {
    "io1200.h": "AT90S1200",
    "io2313.h": "AT90S2313",
    "io2323.h": "AT90S2323",
    "io2333.h": "AT90S2333",
    "io2343.h": "AT90S2343",
    # no XML files
    #"io43u32x.h": "AT43USB320",
    #"io43u35x.h": "AT43USB355",
    "io4414.h": "AT90S4414",
    "io4433.h": "AT90S4433",
    "io4434.h": "AT90S4434",
    # no XML file
    #"io76c711.h": "AT76C711",
    "io8515.h": "AT90S8515",
    # no XML file
    #"io8534.h": "AT90C8534",
    "io8535.h": "AT90S8535",
    "io86r401.h": "AT86RF401",
    "io90pwmx.h": ("AT90PWM3", "AT90PWM2"),
    # no XML file
    #"ioat94k.h": "AT94k",
    "iocan128.h": "AT90CAN128",
    "iom103.h": "ATmega103",
    "iom128.h": "ATmega128",
    #"iom1280.h" => "iomxx0_1.h"
    #"iom1281.h" => "iomxx0_1.h"
    "iom16.h": "ATmega16",
    "iom161.h": "ATmega161",
    "iom162.h": "ATmega162",
    "iom163.h": "ATmega163",
    #"iom164.h" => "iomxx4.h"
    "iom165.h": "ATmega165",
    #"iom168.h" => "iomx8.h"
    "iom169.h": "ATmega169",
    "iom32.h": "ATmega32",
    "iom323.h": "ATmega323",
    "iom325.h": "ATmega325",
    "iom3250.h": "ATmega3250",
    "iom329.h": "ATmega329",
    "iom3290.h": "ATmega3290",
    #"iom48.h" => "iomx8.h"
    "iom64.h": "ATmega64",
    #"iom640.h" => "iomxx0_1.h"
    #"iom644.h" => "iomxx4.h"
    "iom645.h": "ATmega645",
    "iom6450.h": "ATmega6450",
    "iom649.h": "ATmega649",
    "iom6490.h": "ATmega6490",
    "iom8.h": "ATmega8",
    "iom8515.h": "ATmega8515",
    "iom8535.h": "ATmega8535",
    #"iom88.h" => "iomx8.h"
    "iomx8.h": ("ATmega168", "ATmega48", "ATmega88"),
    "iomxx0_1.h": ("ATmega640", "ATmega1280", "ATmega1281"),
    "iomxx4.h": ("ATmega324", "ATmega164", "ATmega644"),
    "iotn11.h": "ATtiny11",
    "iotn12.h": "ATtiny12",
    "iotn13.h": "ATtiny13",
    "iotn15.h": "ATtiny15",
    "iotn22.h": "ATtiny22",
    "iotn2313.h": "ATtiny2313",
    #"iotn25.h" => "iotnx5.h"
    "iotn26.h": "ATtiny26",
    "iotn28.h": "ATtiny28",
    #"iotn45.h" => "iotnx5.h"
    #"iotn85.h" => "iotnx5.h"
    "iotnx5.h": "ATtiny45",
}

def create_tabs (string):
    "Create a number of tabs according to the length of string"
    x = ''
    lim = (32 - len(string) + 7) / 8
    if lim <= 0:
        lim = 1
    for i in range(0, lim):
        x += "\t"
    return x


parser = make_parser ()

handler = DescHandler ()
parser.setContentHandler (handler)

print "Converting XML files:"
for header in table.keys():
    try:
        xmlfile = table[header] + ".xml"
        basedev = table[header]
    except TypeError:
        # in case we've got a tuple of device names
        xmlfile = table[header][0] + ".xml"
        basedev = ", ".join(table[header])
    inputxml = xmls + "/" + xmlfile
    outputxml = xmlfile

    if os.access(xmlfile, os.F_OK):
        continue

    sys.stdout.write(basedev + "... ")

    parser1 = Xml2Obj()
    root = parser1.Parse(inputxml)

    tradheader = HeaderToVec()
    tradheader.Read(headers + "/" + header)

    savedstdout = sys.stdout
    sys.stdout = open(outputxml, "w")
    dump_header (root)
    dump_memory_sizes (root)
    dump_vectors (root, tradheader)
    dump_ioregs (root)
    dump_boot_info (root)
    dump_footer (root)
    sys.stdout.close()
    sys.stdout = savedstdout

    print "done."

r = re.compile(r'#\s*define\s+(SIG_[A-Z0-9_]+)\s+_VECTOR[(](\d+)[)]')
print "Patching headers:"
docs = {}
nlist = table.keys()
nlist.sort()
for header in nlist:
    devname = table[header]
    try:
        xmlfile = devname + ".xml"
        basedev = devname
    except TypeError:
        # in case we've got a tuple of device names
        xmlfile = devname[0] + ".xml"
        basedev = ", ".join(devname)
    hfile = headers + "/" + header

    sys.stdout.write(basedev + "... ")

    #parser = Xml2Obj()
    parser.parse (open (xmlfile))

    lastline = ''
    h = open(hfile)
    newh = open(header, "w")
    for line in h:
        m = r.match(line)
        if m != None:
            key = m.group(2)
            ele = parser.getContentHandler().dev.interrupts[key]
#            if lastline.find(ele.description.data) >= 0:
            if 1:
                if len(ele.description.data) > 0:
                    newh.write("/* " + ele.description.data + " */\n")
                newh.write("#define " + ele.sig_name.data +
                           create_tabs(ele.sig_name.data) +
                           "_VECTOR(" + key + ")\n")
                for x in ele.alt_name.data:
                    newh.write("#define " + x +
                               create_tabs(x) + "_VECTOR(" + key + ")\n\n")
                try:
                    if type(devname) is TupleType:
                        for d in devname:
                            docs[ele.sig_name.data][2].append(d)
                    else:
                        docs[ele.sig_name.data][2].append(devname)
                except KeyError:
                    if type(devname) is TupleType:
                        docs[ele.sig_name.data] = (ele.alt_name.data,
                                                   ele.description.data,
                                                   [])
                        for d in devname:
                            docs[ele.sig_name.data][2].append(d)
                    else:
                        docs[ele.sig_name.data] = (ele.alt_name.data,
                                                   ele.description.data,
                                                   [devname])
            else:
                newh.write(line)
        else:
            newh.write(line)
        lastline = line
    newh.close()
    print "done."

# Try to find the name of the person running this script.
user = 'The avr-libc developer group.'
if os.name == 'posix':
    import pwd
    gecos=pwd.getpwnam(os.getlogin())[4]
    x = gecos.split(',')[0]
    if re.match('^[A-Z][a-z]* [A-Z][a-z]*', x):
        # if at least two capitalized words are present, trust that
        user = x

sys.stdout.write("Writing documentation to " + docfilename + "... ")
savedstdout = sys.stdout
sys.stdout = open(docfilename, "w")

print """/* Note: this file has been automatically generated. */
/* DO NOT EDIT, or your changes WILL BE LOST! */

/* Copyright (c) %d %s
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   * Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.

   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.

   * Neither the name of the copyright holders nor the names of
     contributors may be used to endorse or promote products derived
     from this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
   ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE. */
""" % (time.localtime()[0], user)

print '''
/** \\addtogroup avr_interrupts

@{

\\anchor avr_signames
<small>
<table border="3">
  <tr>
    <td width="20%"><strong>Vector name</strong></td>
    <td width="20%"><strong>Old vector name</strong></td>
    <td width="20%"><strong>Description</strong></td>
    <td width="40%"><strong>Applicable for device</strong></td>
  </tr>
'''

vecs = docs.keys()
vecs.sort()
for vecname in vecs:
    x = docs[vecname]
    nlines = len(x[2])
    print '  <tr>'
    print '    <td>' + vecname + '</td>'
    try:
        print '    <td>' + x[0] + '</td>'
    except TypeError:
        print '    <td>' + ', '.join(x[0]) + '</td>'
    print '    <td>' + x[1] + '</td>'
    print '    <td>' + ', '.join(x[2]) + '</td>'
    print '  </tr>'

print """</table>
</small>

@}*/
"""

sys.stdout.close()
sys.stdout = savedstdout

print "done."