#!/bin/sh

./zynq7000-mmr.py -o $2/const $1
./zynq7000-mmr.py -o $2/enum  -s enum $1
./zynq7000-mmr.py -o $2/macro -s macro $1
