klaus
=====
*a simple Git web viewer that Just Works™.* (beta quality)

Demo at http://klausdemo.lophus.org

|img1|_ |img2|_ |img3|_

.. |img1| image:: https://github.com/jonashaag/klaus/raw/master/assets/commit-view.thumb.gif
.. |img2| image:: https://github.com/jonashaag/klaus/raw/master/assets/tree-view.thumb.gif
.. |img3| image:: https://github.com/jonashaag/klaus/raw/master/assets/blob-view.thumb.gif

.. _img1: https://github.com/jonashaag/klaus/raw/master/assets/commit-view.gif
.. _img2: https://github.com/jonashaag/klaus/raw/master/assets/tree-view.gif
.. _img3: https://github.com/jonashaag/klaus/raw/master/assets/blob-view.gif


Installation
------------
::

   All the big messy refactory from jonashaag's fork was to be able to do this:

   virtualenv your-env
   source your-env/bin/activate
   pip install git+http://github.com/Mistobaan/klaus.git#egg=klaus


Usage
-----
Using the ``klaus`` script
..................................
::

   klaus --help
   klaus <host> <port> /path/to/repo1 [../path/to/repo2 [...]]

Example::

   klaus 127.0.0.1 8080 ../klaus ../nano ../bjoern

This will make klaus serve the *klaus*, *nano* and *bjoern* repos at
``127.0.0.1:8080`` using Python's built-in wsgiref_ server (or, if installed,
the bjoern_ server).

.. _wsgiref: http://docs.python.org/library/wsgiref.html
.. _bjoern: https://github.com/jonashaag/bjoern

Using a real server
...................
The ``klaus/application.py`` module contains a WSGI ``application`` object. 

