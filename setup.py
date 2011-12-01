#!/usr/bin/env python
from setuptools import setup, find_packages
import glob

import os
req_file = 'requirements.txt'

install_requires = [ l.strip() for l in open(req_file,'r').readlines()]

if __name__ == "__main__":
    if os.system('git submodule update --init'):

        with open('./nano/nano.py','r') as fdin:
            with open('./klaus/nano/__init__.py','w') as fdout:
                fdout.write(fdin.read())

    setup(name='klaus',
          version='0.1',
          description='The first Git web viewer that Just Works',
          author='',
          author_email='',
          url='https://github.com/jonashaag/klaus',
          license='BSD',
          include_package_data=True,
          packages = find_packages('.'),
          package_data={'': ['*.*']},      
          scripts=glob.glob('scripts/*'),
          # Put your dependencies here...
          install_requires=install_requires,
    )          
