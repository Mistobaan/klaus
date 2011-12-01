#!/usr/bin/env python
from setuptools import setup, find_packages
import glob

import os

from functools import partial
here = partial(os.path.join, os.path.dirname(__file__) or './')

req_file = here('requirements.txt')
install_requires = [ l.strip() for l in open(req_file,'r').readlines()]

if __name__ == "__main__":
    if os.system('cd %s && git submodule update --init' % here('')):

        with open( here('nano/nano.py') ,'r') as fdin:
            try:
                os.mkdir( here('klaus/nano/') )
            except:
                pass
            with open( here('klaus/nano/__init__.py'),'w') as fdout:
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
