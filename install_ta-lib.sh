#!/bin/bash

set -e

wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz || { echo "Error: wget failed"; exit 1; }
tar -xzf ta-lib-0.6.4-src.tar.gz || { echo "Error: extracting ta-lib archive failed"; exit 1; }
cd ta-lib-0.6.4 || { echo "Error: cd into ta-lib-0.6.4 failed"; exit 1; }

./configure --prefix=/usr || { echo "Error: configure failed"; exit 1; }
make || { echo "Error: make failed"; exit 1; }
sudo make install || { echo "Error: sudo make install failed"; exit 1; }

cd .. || { echo "Error: cd back to parent directory failed"; exit 1; }
rm -rf ta-lib-0.6.4 || { echo "Error: failed to remove ta-lib-0.6.4 directory"; exit 1; }
