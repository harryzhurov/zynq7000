#!/usr/bin/python3
# coding: utf-8

import sys
import os
import re
import getopt

#-------------------------------------------------------------------------------
title0 =\
'//******************************************************************************'   + os.linesep +\
'//*'                                                                                + os.linesep
title1 = '//*      '

title2 = 'Xilinx zynq7000 peripheral memory mapped registers header file'            + os.linesep

title3 = \
'//*'                                                                                + os.linesep +\
'//*      Version 1.0'                                                               + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      Copyright (c) 2017, emb-lib Project Team'                                  + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      This file is part of the zynq7000 library project.'                        + os.linesep +\
'//*      Visit https://github.com/emb-lib/zynq7000 for new versions.'               + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      Permission is hereby granted, free of charge, to any person'               + os.linesep +\
'//*      obtaining  a copy of this software and associated documentation'           + os.linesep +\
'//*      files (the "Software"), to deal in the Software without restriction,'      + os.linesep +\
'//*      including without limitation the rights to use, copy, modify, merge,'      + os.linesep +\
'//*      publish, distribute, sublicense, and/or sell copies of the Software,'      + os.linesep +\
'//*      and to permit persons to whom the Software is furnished to do so,'         + os.linesep +\
'//*      subject to the following conditions:'                                      + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      The above copyright notice and this permission notice shall be included'   + os.linesep +\
'//*      in all copies or substantial portions of the Software.'                    + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,'           + os.linesep +\
'//*      EXPRESS  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF'       + os.linesep +\
'//*      MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.'    + os.linesep +\
'//*      IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY'      + os.linesep +\
'//*      CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,'      + os.linesep +\
'//*      TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH'             + os.linesep +\
'//*      THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'                + os.linesep +\
'//*'                                                                                + os.linesep +\
'//------------------------------------------------------------------------------'   + os.linesep


#-------------------------------------------------------------------------------
def read_file(fname):
    with open(fname, 'rb') as f:
        b = f.read()
    
    return b.decode()
    
#-------------------------------------------------------------------------------
def write_file(fname, data):
    with open(fname, 'wb') as f:
        f.write(data.encode('utf-8'))
        
#-------------------------------------------------------------------------------
def namegen(fullpath, ext):
    basename = os.path.basename(fullpath)
    name     = os.path.splitext(basename)[0]
    return name + os.path.extsep + ext
#-------------------------------------------------------------------------------
def parse(text):
    main_pattern = '(\w+)\s+(0x[0-9a-fA-F]+)\s+(\d+)\s+(\w+)\s+(0x[0-9a-fA-F]+)\s+([\w\s-]+)'
    
    lines = text.splitlines()
        
    mname = lines[0].split()[0]
    baddr = lines[1].split()[0]
                       
    records = []
    
    fields = None
    col1_pos = 0
    col_last_pos = 0
    
    for i, l in enumerate(lines, start = 1):
        res = re.match('<-+>', l)
        if res:
            records.append([''])
            continue

        res = re.match(main_pattern, l)
        if res:
            if fields:
                records.append(fields)
            fields = list( res.groups() )
            fields[-1].strip()    
            col1_pos     = l.index(fields[1])
            col_last_pos = l.index(fields[-1])
        else:
            if not fields:
                continue
            else:
                if len( l.strip() ):
                    col0     = l[0:col1_pos].strip()
                    col_last = l[col_last_pos:].strip()

                    if len(col0):
                        fields[0] += col0

                    if len(col_last):
                        fields[-1] += ' ' + col_last

                    if i == len(lines):
                        records.append(fields)
                else:
                    records.append(fields)
                    fields = None
                        
    return records, mname, baddr
    
#-------------------------------------------------------------------------------
def generate_output(records, name, style, mod_name, base_addr):
    
    max_name_len = 0
    for r in records:
        if len( r[0] ) > max_name_len:
            max_name_len = len( r[0])
    
    sout  = title0
    sout += title1 + title2
    sout += title1 + os.linesep
    sout += title1 + 'Module name: ' + mod_name + os.linesep
    sout += title3 + os.linesep
    sout += '#ifndef ' + mod_name + '_H'  + os.linesep
    sout += '#define ' + mod_name + '_H'  + os.linesep*2
    sout += \
'//------------------------------------------------------------------------------' + os.linesep + \
'//'                                                                               + os.linesep + \
'//     Registers'                                                                 + os.linesep + \
'//'                                                                               + os.linesep

    if style == 'macro':
        prefix = '#define '
        prefix2 = '  ('
        suffix = ')'
    elif style == 'intptr':
        prefix = 'const uintptr_t '
        prefix2 = ' = '
        suffix = ';'
    else:                            # enum
        prefix = '    '
        prefix2 = ' =  '
        suffix = ','
        
    s0 = len(prefix) - len('//')
    s1 = max_name_len - len('Name') + len(' = ')
    s2 = len(mod_name) + len(' + 0x00000000; // ')
    s3 = len('  ') 
    s4 = len('  ')
    s5 = len('   ')

    sout += '//' + s0*' ' + 'Name' + s1*' ' + 'Address' + s2*' ' + 'Width' + s3*' ' + 'Type' + s4*' ' + 'Reset Value' + s5*' ' + 'Description' + os.linesep
     
    if style == 'enum':
        sout += 'enum T' + mod_name + os.linesep
        sout += '{' + os.linesep
                      
    for idx, r in enumerate(records, start=1):
        if style == 'enum' and idx == len(records):
            suffix = ' '
            
        if r[0]:
            #               Name                                        Address                     Width           Type         Reset Value    Description
            sout += prefix + r[0] + (max_name_len - len(r[0]))*' ' + prefix2 + base_addr + ' + ' + r[1] + suffix + ' //  ' + r[2] + 4*' ' + r[3] + 3*' ' + r[4] + 4*' ' + r[5]  + os.linesep
        else:
            sout += os.linesep
        
    if style == 'enum':
        sout += '};' + os.linesep
        
    sout += '//------------------------------------------------------------------------------' + os.linesep
        
    sout +=  os.linesep + '#endif // ' + mod_name + '_H'  + os.linesep
    return sout        

#-------------------------------------------------------------------------------

optlist, infiles = getopt.gnu_getopt(sys.argv[1:], 's:o:')

if not infiles:
    print('\n Usage: ug585.py [options] txt_file')
    print('     where options:')
    print('        -s - style: macro, intptr or enum, default intptr')
    print('        -o - output path, if ommited then the current path is used')
    sys.exit(0)


style  = 'intptr'
opath  = os.getcwd()

for i in optlist:
    if i[0] == '-s':
        style = i[1]
    elif i[0] == '-o':
        opath = i[1]

infile = infiles[0]
text   = read_file(infile)

records, mod_name, base_addr = parse(text)
out = generate_output(records, 'slon', style, mod_name, base_addr)

outfile = namegen(infile, 'h')

write_file(opath + os.sep + outfile, out)

#print(opath + os.sep + outfile)

#-------------------------------------------------------------------------------

