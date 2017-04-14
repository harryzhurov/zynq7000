#!/usr/bin/python3
# coding: utf-8

import sys
import os
import re
import getopt

from utils import *

#-------------------------------------------------------------------------------
title0 =\
'//******************************************************************************'   + os.linesep +\
'//*'                                                                                + os.linesep
title1 = '//*      '

title2 = 'Xilinx zynq7000 PS7 memory mapped registers header file'                   + os.linesep

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
def split_modules(text):
    return text.split('<====    ====>')
    
#-------------------------------------------------------------------------------
def split_regs(text):
    return  re.findall('-+>((?:.|\s)+?)<-+', text)
    
#-------------------------------------------------------------------------------
def parse_module(text):
 
    #---------------------------------------------------------------
    #
    #    Search patterns
    #   
    h1  = 'B\.\d+ +.+\((\w+)\) *\n'            # header 1
    baf = 'Base Address((?: +0x\w+ +\w+\n)+)'  # base address frame
    ba  = ' +0x\w+ +(\w+)\n'                   # base address
    sfx = '\nSuffixes +(.+)'                   # suffixes
    rsf = 'Register Summary((?:\n|.)+?)<'      # registers summary frame
    rdf = '<-+( +-+>(.|\n)+<-+) +'             # registers description frame
    
    #---------------------------------------------------------------
    #
    #    Parse module
    #
    #    Module name
    res = re.search(h1, text)
    if res:
        mname = res.group(1) 
    else:
        print('E: invalid module format, header not found')
        print('module contents: ') + text[:1000]
        sys.exit(1)
        
    #    Base address[es]
    res = re.search(baf, text)
    if res:
        baframe = res.group(1) 
    else:
        print('E: invalid module format, Base Address frame not found')
        print('module contents: ') + text[:1000]
        sys.exit(1)
    
    baddr = re.findall(ba, baframe)
    if not baddr:
        print('E: invalid Base Address frame format')
        print(baframe)
        sys.exit(1)
        
    #    Suffixes
    res = re.search(sfx, text)
    if res:
        suffixes = res.group(1).split()
    else:
        suffixes = None
    
    #    Register summary
    res = re.search(rsf, text)
    if res:
        regsum = res.group(1) 
    else:
        print('E: invalid module format, Register Summary frame not found')
        print('module contents: ') + text[:1000]
        sys.exit(1)
            
    #    Register description
    res = re.search(rdf, text)
    if res:
        regdescr = res.group(1) 
    else:
        print('E: invalid module format, Register Description frame not found')
        print('module contents: ') + text[:1000]
        sys.exit(1)
        
    #print(mname)
    #print(baddr)
    #print(suffixes)
    #print(regsum)
    #print(regdescr)
    
    return mname, baddr, suffixes, regsum, regdescr
    
#-------------------------------------------------------------------------------
def parse_regsum(text):
    main_pattern = '(\w+)\s+(0x[0-9a-fA-F]+)\s+(\d+)\s+(\w+)\s+(\w+)\s+([\w\s-]+)'
    
    lines = text.splitlines()
                       
    records = []
    
    fields       = None
    col1_pos     = 0
    col3_pos     = 0
    col4_pos     = 0
    col_last_pos = 0
    
    for i, l in enumerate(lines, start = 1):
        res = re.match('<-+>', l)
        if res:
            if fields:
                records.append(fields)
                fields = None
                
            records.append(['', '', '', '', '', ''])
            continue

        res = re.match(main_pattern, l)
        if res:
            if fields:
                records.append(fields)
            fields = list( res.groups() )
            fields[-1].strip()    
            col1_pos     = l.index(fields[1])
            col3_pos     = l.index(fields[3])
            col4_pos     = l.index(fields[4])
            col_last_pos = l.index(fields[-1])
        else:
            if not fields:
                continue
            else:
                if len( l.strip() ):
                    col0     = l[0:col1_pos].strip()
                    col3     = l[col3_pos:col4_pos].strip()
                    col_last = l[col_last_pos:].strip()

                    if len(col0):
                        fields[0] += col0

                    if len(col3):
                        fields[3] += col3
                        
                    if len(col_last):
                        fields[-1] += ' ' + col_last

                    if i == len(lines):
                        records.append(fields)
                else:
                    records.append(fields)
                    fields = None
                        
    return records
    
#-------------------------------------------------------------------------------
def parse_regdescr_table(text):

    main_pattern = '(\w+) +(\d+(?::\d+)*) +(\w+) +(\w+) +(.+)'

    lines = text.splitlines()

    table = []
    row   = []

    col_pos = []

    for i, l in enumerate(lines, start = 1):
        res = re.match(main_pattern, l)
        if res:
            if row:
                table.append(row)
                row = []

            items = res.groups()
            for i in items:
                row.append([i])
            for i in row:
                col_pos.append( l.index(i[0]) )

        else:
            if not row:
                continue

            col1 = l[:col_pos[1]].strip()
            col5 = l[col_pos[4]:].strip()
            if col1:
                row[0].append(col1)
            if col5:
                row[4].append(col5)

    if row:
        table.append(row)

    return table

#-------------------------------------------------------------------------------
def parse_regdescr(text):

    table_header = 'Field Name +Bits +Type +Reset Value +Description\n'
    main_pattern = '(?P<Header>Register \(\w+\) \w+)\s+(?P<Info>Name.+)(?P<Details>Register +\w+ +Details.+?)'+ table_header + '(?P<Bits>.+)'

    res = re.search(main_pattern, text, re.DOTALL)

    header  = res.groupdict()['Header'].strip()
    info    = res.groupdict()['Info'].strip()
    details = res.groupdict()['Details'].strip()
    bittext = res.groupdict()['Bits'].strip()
    
    
    info    = re.sub('\n\n+', '\n', info)
    details = re.sub('\n\n+', '\n', details)
        
    bittables = re.split('table_header', bittext)
    bittable = []
    for bt in bittables:
        bittable += parse_regdescr_table(bt)
    
    bitdata = []
    for item in bittable:
        bname   = ''.join(item[0])
        bname   = re.sub('\(.+\)', '', bname).upper()
        bnum    = item[1][0]
        btype   = item[2][0]
        bresval = item[3][0]
        bdescr  = item[4]
        bitdata.append([bname, bnum, btype, bresval, bdescr])
    
    return header, info, details, bitdata

#-------------------------------------------------------------------------------
def generate_output(regdata, style, mod_name, base_addrs, reg_suffixes, regdetails):
    
    sout  = title0
    sout += title1 + title2
    sout += title1 + os.linesep
    sout += title1 + 'Module name: ' + mod_name + os.linesep
    sout += title3 + os.linesep
    sout += '#ifndef ' + mod_name + '_H'  + os.linesep
    sout += '#define ' + mod_name + '_H'  + os.linesep*2
    sout += '#include <pmodmap.h>' + os.linesep*2
    sout += \
    '//------------------------------------------------------------------------------' + os.linesep + \
    '//'                                                                               + os.linesep + \
    '//     Registers'                                                                 + os.linesep + \
    '//'                                                                               + os.linesep + \
    '//------------------------------------------------------------------------------' + os.linesep 
    
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

    for ba_idx, base_addr in enumerate(base_addrs):
        
        max_name_len = 0
        max_type_len = 0
        reg_suffix   = reg_suffixes[ba_idx]
        
        suffix_sep = '' if reg_suffix.isdigit() or len(reg_suffix) == 0 else '_'
        
        for r in regdata:
            #print(r)
            reg_name_len = len( r[0] + suffix_sep + reg_suffix)
            if reg_name_len > max_name_len:
                max_name_len = reg_name_len
                
            type_len = len(r[3])
            if type_len > max_type_len:
                max_type_len = type_len
                
        baddr = base_addr + '_ADDR'
        sout += '//' + os.linesep + '//    ' + mod_name + suffix_sep + reg_suffix + ' MMRs' + os.linesep + '//' + os.linesep
        
        #-----------------------------------------------------------------------
        s0 = len(prefix) - len('//')
        s1 = max_name_len - len('Name') + len(' = ')
        s2 = len( prefix2 + baddr + ' + 0x00000000' + suffix ) - len('Address')
        s3 = 3 
        s4 = 2 if max_type_len <= 2 else max_type_len
        s5 = len('   ')
        #-----------------------------------------------------------------------
        sout += '//' + s0*' ' + 'Name' + s1*' ' + 'Address' + s2*' ' + 'Width' + s3*' ' +\
                'Type' + s4*' ' + 'Reset Value' + s5*' ' + 'Description' + os.linesep
         
        if style == 'enum':
            sout += 'enum T' + mod_name + suffix_sep + reg_suffix + os.linesep
            sout += '{' + os.linesep
                          
        sfx = suffix
        for idx, r in enumerate(regdata, start=1):
            if style == 'enum' and idx == len(regdata):
                sfx = ' '
                
            if r[0]:
                if len(reg_suffixes[ba_idx]):
                    reg_name = r[0] + suffix_sep + reg_suffix
                else:
                    reg_name = r[0]
                    
                reg_name = reg_name.upper()
                    
                if len(r[2]) < 2:
                    r[2] = ' ' + r[2]
                    
                if len(r[3]) < max_type_len:
                    r[3] += (max_type_len - len(r[3]))*' '
                    
                if len(r[4]) < 10:
                    r[4] += ( 10-len(r[4]) )*' '
                #                   Name                                                 Address                                     Width         Type        Reset Value       Description
                sout += prefix + reg_name + (max_name_len - len(reg_name))*' ' + prefix2 + baddr + ' + ' + r[1] + sfx + ' //  ' + r[2] + 4*' ' + r[3] + 4*' ' + r[4] + 4*' ' + r[5]  + os.linesep
            else:
                sout += os.linesep
            
        if style == 'enum':
            sout += '};' + os.linesep
            
        sout += '//------------------------------------------------------------------------------' + os.linesep
        
        
    for reg in regdetails:
        sout += os.linesep +'//------------------------------------------------------------------------------' + os.linesep
        sout += '//' + os.linesep
        sout += '// ' + reg[0] + os.linesep  # header
        sout += '//' + os.linesep

        info    = re.sub('^', '// ', reg[1], flags=re.MULTILINE)  
        details = re.sub('^', '// ', reg[2], flags=re.MULTILINE)  
        
        sout += info    + os.linesep
        sout += '//' + os.linesep
        sout += details + os.linesep
        
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

mods_raw = split_modules(text)
mods = []
for m in mods_raw:
    #mods.append( parse_module(m) )   # result: mname, baddr, suffixes, regsum, regdescr
    mname, baddr, rsuffixes, regsum, regdescr = parse_module(m)
    regdata = parse_regsum(regsum)
    regbits_raw = split_regs(regdescr)
    regdetails  = [parse_regdescr(x) for x in regbits_raw]
    #print(regdetails)
    out = generate_output(regdata, style, mname, baddr, rsuffixes, regdetails)
    print(out)
    

#records, mod_names, base_addrs, reg_suffixs = parse_regsum(text)
#out = generate_output(regdata, style, mname, baddr, rsuffixes)

#outfile = namegen(infile, 'h')

#write_file(opath + os.sep + outfile, out)

#print(opath + os.sep + outfile)

#-------------------------------------------------------------------------------

