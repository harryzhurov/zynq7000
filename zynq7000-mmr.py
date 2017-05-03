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

title2 = 'Xilinx zynq7000 PS7 Memory Mapped Registers Header File'                   + os.linesep

title3 = \
'//*'                                                                                + os.linesep +\
'//*      Version 1.0'                                                               + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      Copyright (c) 2017, emb-lib Project Team'                                  + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      This file is part of the zynq7000 library project.'                        + os.linesep +\
'//*      Visit https://github.com/emb-lib/zynq7000 for new versions.'               + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      Permission is hereby granted, free of charge, to any person obtaining'     + os.linesep +\
'//*      a copy of this software and associated documentation files (the'           + os.linesep +\
'//*      "Software"), to deal in the Software without restriction, including'       + os.linesep +\
'//*      without limitation the rights to use, copy, modify, merge, publish,'       + os.linesep +\
'//*      distribute, sublicense, and/or sell copies of the Software, and to'        + os.linesep +\
'//*      permit persons to whom the Software is furnished to do so, subject to'     + os.linesep +\
'//*      the following conditions:'                                                 + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      The above copyright notice and this permission notice shall be included'   + os.linesep +\
'//*      in all copies or substantial portions of the Software.'                    + os.linesep +\
'//*'                                                                                + os.linesep +\
'//*      THE SOFTWARE  IS PROVIDED  "AS IS", WITHOUT  WARRANTY OF  ANY KIND,'       + os.linesep +\
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
    
    return mname, baddr, suffixes, regsum, regdescr
    
#-------------------------------------------------------------------------------
def parse_regsum(text):
    main_pattern = '(\w+)\s+(0x[0-9a-fA-F]+)\s+(\d+)\s+(\w+)\s+([\w:]+)\s+([\w\s-]+)'
    
    lines = text.splitlines()
                       
    records = []
    
    fields       = None
    col1_pos     = 0
    col3_pos     = 0
    col4_pos     = 0
    col_last_pos = 0
    
    for i, l in enumerate(lines, start = 1):
#       res = re.match('<-+>', l)
#       if res:
#           if fields:
#               res =  re.findall('\w+\:\s+(0x[0-9a-fA-F]+)', fields[4])
#               fields[4] = res if len(res) > 0 else [fields[4]]
#               records.append(fields)
#               fields = None
#
#           records.append(['', '', '', '', [], ''])
#           continue

        res = re.match(main_pattern, l)
        if res:
            if fields:
                rvals =  re.findall('\w+\:\s+(0x[0-9a-fA-F]+)', fields[4])
                fields[4] = rvals if len(rvals) > 0 else [fields[4]]
                records.append(fields)
                
            fields = list( res.groups() )
            fields[-1].strip()    
            col1_pos  = l.index(fields[1])
            col3_pos  = l.index(fields[3])
            col4_pos  = l.index(fields[4])
            col5_pos  = l.index(fields[5])
        else:
            if not fields:
                continue
            else:
                if len( l.strip() ):
                    col0  = l[0:col1_pos].strip()
                    col3  = l[col3_pos:col4_pos].strip()
                    col4  = l[col4_pos:col5_pos].strip()
                    col5  = l[col5_pos:].strip()

                    if len(col0):
                        fields[0] += col0

                    if len(col3):
                        fields[3] += col3
                        
                    if len(col4):
                        fields[4] += ' ' + col4
                        
                    if len(col5):
                        fields[5] += ' ' + col5

                    if i == len(lines):
                        rvals =  re.findall('\w+\:\s+(0x[0-9a-fA-F]+)', fields[4])
                        fields[4] = rvals if len(rvals) > 0 else [fields[4]]
                        records.append(fields)
                        fields = None
                else:
                    rvals =  re.findall('\w+\:\s+(0x[0-9a-fA-F]+)', fields[4])
                    fields[4] = rvals if len(rvals) > 0 else [fields[4]]
                    records.append(fields)
                    fields = None
                    
    return records
    
#-------------------------------------------------------------------------------
def parse_regdescr_table(text):

    main_pattern = '(\w+) +(\d+(?::\d+)*) +([\w,]+) +(\w+) +(.+)'

    lines = text.splitlines()

    table   = []
    row     = []
    col_pos = []

    for l in lines:
        res = re.match(main_pattern, l)
        if res:
            if row:
                table.append(row)
                row     = []
                col_pos = []

            items = res.groups()
            for i in items:
                row.append([i])
                
            for pos in res.regs[1:]:
                col_pos.append( pos[0] )
                
        else:
            if not row:
                continue

            col0 = l[          :col_pos[1]].strip()
            col2 = l[col_pos[2]:col_pos[3]].strip()
            col4 = l[col_pos[4]:].strip()
            if col0:
                row[0].append(col0)
            if col2:
                row[2].append(col2)
            if col4:
                row[4].append(col4)

    if row:
        table.append(row)

    return table

#-------------------------------------------------------------------------------
def parse_regdescr(text):

    table_header = 'Field Name +Bits +Type +Reset Value +Description\n'
    main_pattern = '(?P<Header>Register \(\w+\**\) \w+\**)\s+(?P<Info>Name.+)(?P<Details>Register +\w+.+Details.+?)'+ table_header + '(?P<Bits>.+)'

    res = re.search(main_pattern, text, re.DOTALL)
    
    if not res:
        print(text)

    header  = res.groupdict()['Header'].strip()
    info    = res.groupdict()['Info'].strip()
    details = res.groupdict()['Details'].strip()
    bittext = res.groupdict()['Bits'].strip()
    
    res = re.match('Register +\((\w+\**)\) +(\w+\**)', header)
    modname = res.groups()[0]
    regname = res.groups()[1]
    modname = modname[:-1] + '_' if re.match('.+\*', modname) else ''
    regname = regname[:-1] + '_' if re.match('.+\*', regname) else ''

    header  = re.sub('\*', '', header)
    info    = re.sub('\n\n+', '\n', info)
    details = re.sub('\n\n+', '\n', details)
        
    bittables = re.split(table_header, bittext)
    bittable = []
    for bt in bittables:
        bittable += parse_regdescr_table(bt)
    
    bitdata = []
    for item in bittable:
        bname   = ''.join(item[0])
        bname   = re.sub('\(.+\)', '', bname)
        bname   = re.sub('([a-z])([A-Z])', '\g<1>' + '_' + '\g<2>', bname)
        if bname != 'reserved':
            bname   = (modname + regname + bname).upper()
        bnum    = item[1][0]
        btype   = ''.join(item[2])
        bresval = item[3][0]
        bdescr  = item[4]
        bitdata.append([bname, bnum, btype, bresval, bdescr])
    
    return header, info, details, bitdata, bittables

#-------------------------------------------------------------------------------
def generate_output(regdata, style, mod_name, base_addrs, reg_suffixes, regdetails):
    
    sout  = title0
    sout += title1 + title2
    sout += title1 + os.linesep
    sout += title1 + 'Module name: PS7_' + mod_name.upper() + os.linesep
    sout += title3 + os.linesep
    sout += '#ifndef PS7_' + mod_name.upper() + '_H'  + os.linesep
    sout += '#define PS7_' + mod_name.upper() + '_H'  + os.linesep*2
    sout += '#include <ps7modmap.h>' + os.linesep*2
    sout += \
    '//------------------------------------------------------------------------------' + os.linesep + \
    '//'                                                                               + os.linesep + \
    '//     Registers'                                                                 + os.linesep + \
    '//'                                                                               + os.linesep + \
    '//------------------------------------------------------------------------------' + os.linesep 
    
    if style == 'macro':
        prefix = '#define '
        prefix2 = '  ('
        suffix = 'UL)'
    elif style == 'const':
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
        reg_suffix   = reg_suffixes[ba_idx] if reg_suffixes else ''
        
        suffix_sep = '' if reg_suffix.isdigit() or len(reg_suffix) == 0 else '_'

        for r in regdata:
            reg_name_len = len( r[0] + suffix_sep + reg_suffix)
            if reg_name_len > max_name_len:
                max_name_len = reg_name_len
                
            type_len = len(r[3])
            if type_len > max_type_len:
                max_type_len = type_len
                
        baddr = base_addr.upper() + '_ADDR'
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
                          
        #print(regdata)
        sfx = suffix
        for idx, r in enumerate(regdata, start = 1):
            if style == 'enum' and idx == len(regdata):
                sfx = ' '
                
            if r[0]:
                if reg_suffixes:
                    if len(reg_suffixes[ba_idx]):
                        reg_name = r[0] + suffix_sep + reg_suffix
                    else:
                        reg_name = r[0]
                else:
                    reg_name = r[0]
                    
                reg_name = reg_name.upper()
                    
                addr_offset = r[1]
                rwidth = r[2]
                if len(r[2]) < 2:
                    rwidth = ' ' + r[2]
                    
                rtype = r[3]
                if len(r[3]) < max_type_len:
                      rtype = r[3] + (max_type_len - len(r[3]))*' '
                    
                resval = r[4][ba_idx] if len(r[4]) > 1 else r[4][0]
                if len(resval) < 10:
                     resval = resval + ( 10-len(resval) )*' '
                
                sout += prefix + reg_name + (max_name_len - len(reg_name))*' ' + prefix2 + baddr + ' + ' + addr_offset + sfx + \
                ' //  ' + rwidth + 4*' ' + rtype + 4*' ' + resval + 4*' ' + r[5]  + os.linesep
            else:
                sout += os.linesep
            
        if style == 'enum':
            sout += '};' + os.linesep
            
        sout += '//------------------------------------------------------------------------------' + os.linesep
        
        
    if style == 'macro':
        prefix2 = '  '
        suffix = ''
        
    for reg in regdetails:   # reg: list[ header, info, details, bitdata, bittables ]
        sout += os.linesep +'//------------------------------------------------------------------------------' + os.linesep
        sout += '//' + os.linesep
        sout += '// ' + reg[0] + os.linesep  # header
        sout += '//' + os.linesep

        regname = re.match('Name +(\w+) *\n', reg[1]).groups()[0]
        info    = re.sub('^', '// ', reg[1], flags=re.MULTILINE)  
        details = re.sub('^', '// ', reg[2], flags=re.MULTILINE)  
        
        sout += info + os.linesep
        sout += '//' + os.linesep
        sout += details + os.linesep
        sout += '//' + os.linesep
        
        bitrecs = []
        valuelen  = len('0x00000000') if style == 'const' else len('0x00000000UL')
        for row in reg[3]:                   # table row
            name  = row[0].upper()
            bits  = row[1]
            btype = row[2]
            rval  = row[3]
            descr = row[4]
            
            res = re.match('(\d+):*(\d+)*', bits)
            if not res:
                print('E: invalid bits number[s]: ' + bits)
            
            bitlist = res.groups()
            if bitlist[1] == None:
                bpos  = bitlist[0]
                bmask = '0x{:>08X}'.format(1 << int(bpos))
            else:
                bpos   = bitlist[1]
                brange = int(bitlist[0])-int(bpos) + 1
                bmask  = '0x{:>08X}'.format( (int('1'*brange, 2) ) << int(bpos))
            
            if not style == 'const':
                bmask += 'UL'
                bpos  += 'UL'
                
            bitrecs.append([ name, bmask, bpos, bits, btype, rval, descr])
        
        maxnamelen = 0
        for br in bitrecs:
            namelen = len(br[0])
            if namelen > maxnamelen:
                maxnamelen = namelen

        comment_offset = maxnamelen + valuelen + len('_MASK' + prefix + prefix2 + suffix) + 4
                    
        sfx = suffix
        if style == 'enum':
            sout += 'enum T' + regname.upper() + os.linesep
            sout += '{' + os.linesep
            
        for idx, br in enumerate(bitrecs, start = 1):
            if br[0] == 'RESERVED':
                sout += '// ' + br[0] + ' '*(comment_offset - len(br[0])) + 'Properties: ' + ('Bit: ' if br[3].find(':') == -1 else 'Bits: ') + br[3] + ', Type: ' + br[4] + ', Reset Value: ' + br[5] + os.linesep
            else:
                sout += ' '*comment_offset + '// Properties: ' + ('Bit: ' if br[3].find(':') == -1 else 'Bits: ') + br[3] + ', Type: ' + br[4] + ', Reset Value: ' + br[5] + os.linesep
                sout += prefix + br[0] + '_MASK' + ' '*(maxnamelen-len(br[0])) + prefix2 + br[1] + sfx +  ' '*4 +                         '// ' + (br[6][0] if len(br[6]) > 0 else '') + os.linesep
                if style == 'enum' and idx == len(bitrecs):
                    sfx = ' '
                sout += prefix + br[0] + '_BPOS' + ' '*(maxnamelen-len(br[0])) + prefix2 + br[2] + sfx +  ' '*(4+len(br[1])-len(br[2])) + '// ' + (br[6][1] if len(br[6]) > 1 else '') + os.linesep
                for d in br[6][2:]:
                    sout += ' '*comment_offset + '// ' + d + os.linesep
        
            sout += os.linesep
            
        if style == 'enum':
            sout += '};' + os.linesep
            
    sout +=  os.linesep + '#endif // PS7_' + mod_name.upper() + '_H'  + os.linesep*2
    return sout        

#-------------------------------------------------------------------------------
def generate_common_header(mods):

    sout  = title0
    sout += title1 + title2
    sout += title1 + os.linesep
    sout += title1 + 'Common PS7 MMRs file' + os.linesep
    sout += title3 + os.linesep
    sout += '#ifndef PS7_MMRS_H' + os.linesep
    sout += '#define PS7_MMRS_H' + os.linesep*2
    sout += \
    '//------------------------------------------------------------------------------' + os.linesep

    for m in mods:
        sout += '#include <' + m + '>' + os.linesep
    
    sout += \
    '//------------------------------------------------------------------------------' + os.linesep 
    
    sout +=  os.linesep + '#endif // PS7_MMRS_H' + os.linesep
    return sout        
    
#-------------------------------------------------------------------------------

optlist, infiles = getopt.gnu_getopt(sys.argv[1:], 's:o:')

if not infiles:
    print('\n Usage: zynq7000-mmr.py [options] txt_file')
    print('     where options:')
    print('        -s - style: const, macro or enum, default const')
    print('        -o - output path, if ommited then the current path is used')
    sys.exit(0)

style  = 'const'
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
print('*'*80)
print('generating header files for style "' + style + '"' + os.linesep)
print('-'*80)
print('#   Module          Per Mod    Total     Bit Fields')
print('-'*80)
nmod    = 1
regs    = 0
regstot = 0
bfields = 0
for m in mods_raw:
    mname, baddr, rsuffixes, regsum, regdescr = parse_module(m)
    modnum  = '{:>2}'.format( nmod )
    print(modnum + '  ', mname, end='')
    nmod += 1
    regdata = parse_regsum(regsum)
    regbits_raw = split_regs(regdescr)
    regdetails  = [parse_regdescr(x) for x in regbits_raw]       # result: header, info, details, bitdata, bittables
    out = generate_output(regdata, style, mname, baddr, rsuffixes, regdetails)
    outfile = 'ps7' + mname.lower() + '.h'
    mods.append(outfile)
    if not os.path.exists(opath):
        os.makedirs(opath)
    write_file(opath + os.sep + outfile, out)
    regs_count_per_module = len(regdata)
    regs_count_total      = regs_count_per_module*(len(rsuffixes) if rsuffixes else 1)
    bitfields_count       = 0
    
    for idx, regdet in enumerate(regdetails):
        bitfields = regdet[3]
        for bf in bitfields:
            if i[0] != 'reserved':
                bitfields_count += 1
            
    regcnt_per_mod = str(regs_count_per_module)
    regcnt_total   = str(regs_count_total)
    bfcnt          = str(bitfields_count)
    
    regs     += regs_count_per_module
    regstot += regs_count_total
    bfields += bitfields_count
                
    print(' '*(16-len(mname))  +  regcnt_per_mod + ' '*(12-len(regcnt_per_mod)) + regcnt_total + ' '*(12-len(regcnt_total)) + bfcnt )
    
print('-'*80)
print(' Summary:' + ' '*(20-len(' Summary:'))  +  str(regs) + ' '*(12-len(str(regs))) + str(regstot) + ' '*(12-len(str(regstot))) + str(bfields) )
        
write_file(opath + os.sep + 'ps7mmrs.h', generate_common_header(mods)) 
    
print('*'*80)
print('')    

#-------------------------------------------------------------------------------
