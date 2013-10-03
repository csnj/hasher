#!/usr/bin/env python
# coding: utf-8

"""
Efficient hashing of multiple files

Features:
* Low memory usage: reads each file one block at a time
* Reads each file only once while running multiple algorithms, including
  MD5, SHA1, SHA256, SHA512, byte histogram, Shannon entropy
* Uses worker threads to do multiple files at once
* Provides a command line interface and a reusable object/module

Exports:
  File ( filename, hashes, blocksize ):
    filename is a full or relative path to the file
    hashes is a list of the hashing algorithms,
      default: [md5, sha1, sha256, sha512]
    blocksize is the number of bytes to read from the file at once,
      default: 1024*1024 B => 1 MB
  Session ( filenames, hashes, blocksize, threads ):
    filenames is a list of full or relative paths to the files
    hashes is a list of the hashing algorithms,
      default: [md5, sha1, sha256, sha512]
    blocksize is the number of bytes to read from the file at once,
      default: 1024*1024 B => 1 MB
    threads is the number of files to process simultaneously
"""

import sys
import hashlib
import logging
import math

from Queue import Queue
from threading import Thread

log = logging.getLogger('hasher')
#log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

class File:
  """
  An instance represents a file to be hashed.
  """
  
  def __init__(self, filename,
               hashes=['md5', 'sha1', 'sha256', 'sha512'],
               blocksize=1024*1024, separator=','):
    """
    Initialize a File object and hashlib objects for each hashing
    algorithm.
    """
    self.filename = filename
    self.hashes = hashes
    self.blocksize = blocksize
    self.separator = separator
    self.result = 0
    self.report = filename
    self.size = 0
    self.histogram = [0] * 256
    self.entropy = 0.0
    self.ho = {}
    for h in self.hashes:
      self.ho[h] = hashlib.new(h)
  
  def hash(self, p=False):
    """
    Read the file in blocks, passing each block to each hashing algorithm.
    Saves the hashes' hexdigests in .result[hash] upon completion.
    Set p to force immediate printing of report lines.
    """
    if not self.result:
      fh = open(self.filename, 'rb')

      while 1:
        block = fh.read(self.blocksize)
        if not block:
          break

        # Hashes
        for h in self.hashes:
          self.ho[h].update(block)

        # Histogram
        for char in block:
          self.histogram[ord(char)] += 1

        # Size
        self.size += len(block)

      fh.close()

      # Entropy
      for f in self.histogram:
        if f > 0:
          freq = float(f) / self.size
          self.entropy += freq * math.log(freq, 2)
      self.entropy *= -1

      self.result = {}

    self.report += '%s%d' % (self.separator, self.size)
    for h in self.hashes:
      self.result[h] = self.ho[h].hexdigest()
      self.report += self.separator + self.result[h]
    #self.report += self.separator + '%s' % self.histogram
    self.report += self.separator + '%f' % self.entropy

    if p:
      print self.report
  
class Session:
  """
  An instance represents one or more files to be hashed.
  """
  
  def __init__(self, filenames,
               hashes=['md5', 'sha1', 'sha256', 'sha512'],
               blocksize=1024*1024, separator=',', threads=8):
    """
    Initialize a Session object, and File objects for each given filename.
    """
    self.filenames = filenames
    self.hashes = hashes
    self.blocksize = blocksize
    self.threads = threads
    self.separator = separator
    self.fo = {}
  
  def hash(self, p=False):
    """
    Perform the hashes of the files via each File object's .hash method,
      using a Queue and N worker threads to do N files at once.
    Set p to force immediate printing of report lines.
    """
    for f in self.filenames:
      if not f in self.fo:
        self.fo[f] = File(f, self.hashes, self.blocksize, self.separator)
    def worker():
      while 1:
        f = q.get()
        if not self.fo[f].result:
          self.fo[f].hash(p)
        q.task_done()
    q = Queue()
    files = len(self.filenames)
    if files < self.threads:
      self.threads = files
    log.info('Using %d threads' % self.threads)
    for i in range(self.threads):
      t = Thread(target=worker)
      t.daemon = True
      t.start()
    for f in self.filenames:
      q.put(f)
    q.join()
  
  def report(self):
    """
    Generate the report and the report lines for each File object.
    """
    header = 'Filename%sSize' % self.separator
    for h in self.hashes:
      header += self.separator + h.upper()
    #header += self.separator + 'Histogram'
    header += self.separator + 'Entropy'
    print header
    self.hash(1);

if __name__ == "__main__":

  import argparse
  import sys

  sys.stdout.flush()

  epilog = """
Copyright © 2013 by Nick Jensen

This module is free software; you may redistribute it and/or modify it
under the terms of the GNU GPLv3.
"""

  def positive_int(string):
    """
    Test if value is a positive integer.
    """
    value = int(string)
    if value < 1:
      msg = '%r is not a positive integer' % string
      raise argparse.ArgumentTypeError(msg)
    return value

  argparser = argparse.ArgumentParser(epilog=epilog,
    formatter_class=argparse.RawTextHelpFormatter)
  argparser.add_argument('-t', '--threads', metavar='N', default=8,
    help='maximum number of threads (default: 8)', type=positive_int)
  argparser.add_argument('--tab', action='store_true',
    help='tab separated')
  argparser.add_argument('filenames', nargs='+', metavar='FILENAME',
    help='one or more files to hash')
  args = argparser.parse_args()

  files = len(args.filenames)
  threads = files if files < args.threads else args.threads
  separator = '\t' if args.tab else ','

  Session(args.filenames, separator=separator, threads=threads).report()

