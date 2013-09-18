hasher
======

Efficient hashing of multiple files

Features
========

* Low memory usage: reads each file one block at a time

* Reads each file only once while running multiple hashing algorithms

* Uses worker threads to do multiple files at once

* Provides a command line interface and a reusable object/module

Usage
=====

    usage: hasher [-h] [-t N] [--tab] FILENAME [FILENAME ...]
    
    positional arguments:
      FILENAME           one or more files to hash
    
    optional arguments:
      -h, --help         show this help message and exit
      -t N, --threads N  maximum number of threads (default: 8)
      --tab              tab separated

See Also
========

* [The Case for Learning Python® for Malware Analysis](http://www.cloudshield.com/blog/advanced-malware/the-case-for-learning-python-for-malware-analysis/), CloudShield Blog

Legal
=====

    Copyright © 2013 by Nick Jensen
    
    This module is free software; you may redistribute it and/or modify it
    under the terms of the GNU GPLv3.

