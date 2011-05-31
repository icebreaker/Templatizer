#!/usr/bin/env python
from distutils.core import setup
import templatizer

setup(
	name='templatizer',
	version='%d.%d.%d' % templatizer.__version__,
	description=templatizer.__description__,
	author=templatizer.__author__,
	scripts=['bin/templatizer'],
	py_modules=['templatizer'],
	classifiers=[
		'Development Status :: 1 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: FSF Approved :: GPL License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Utilities'
    ],
)
