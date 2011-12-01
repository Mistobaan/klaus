#!/usr/bin/env python
from setuptools import setup, find_packages
import glob

import os
req_file = 'requirements.txt'

install_requires = [ l.strip() for l in open(req_file,'r').readlines()]

if __name__ == "__main__":
    os.system('git submodule update --init')
    
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
