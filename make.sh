#!/usr/bin/env bash
cd libs/cxx/ && python3 setup.py build
cp -r $(pwd)/build/lib*/*.so $(pwd)/../
rm -rf build/
rm -rf *.c
cd ../../