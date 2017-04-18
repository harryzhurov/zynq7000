#!/bin/sh

./zynq7000-mmr.py -o out/intptr $1
./zynq7000-mmr.py -o out/enum  -s enum $1
./zynq7000-mmr.py -o out/macro -s macro $1
