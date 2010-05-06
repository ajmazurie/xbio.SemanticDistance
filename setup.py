#!/usr/bin/env python

# 'python setup.py sdist' to generate the package, then
# 'easy_install SemanticDistance-x.x.tar.gz' to install it

from distutils.core import setup, Extension

setup(
	name = "SemanticDistance",
	version = "1.0b",
	author = "Aurelien Mazurie",
	author_email = "ajmazurie@oenone.net",
	url = "http://github.com/ajmazurie/SemanticDistance",
	download_url = "http://github.com/ajmazurie/SemanticDistance",
	license = "MIT/X11",

	packages = ["SemanticDistance"],
)