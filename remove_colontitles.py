#!/usr/bin/python3


import sys
import re
from utils import *


strin = read_file(sys.argv[1])

pattern = '\s+Zynq-7000 AP SoC Technical Reference Manual\s+www\.xilinx\.com\s+Send Feedback\s+\d+\s+UG585 \(v1\.11\) September 27, 2016\s+.+\s+'

strout = re.sub(pattern, '\n', strin)

write_file('slon.txt', strout)

