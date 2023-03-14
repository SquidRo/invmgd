#!/bin/bash

PKG_NAM=`sed -n -e "s/ *app_name *= *['\"]\([^']*\)['\"][ ]*/\1/p" misc/setup.py`
PKG_VER=`sed -n -e "s/ *version *= *['\"]\([^']*\)['\"][ ]*,/\1/p" misc/setup.py`

cd build

python3 setup.py --command-packages=stdeb.command debianize

tar czvf ../${PKG_NAM}_${PKG_VER}.orig.tar.gz .

cp postinst debian/python3-${PKG_NAM}.postinst

dpkg-buildpackage
