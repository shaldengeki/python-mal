#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4

def extract_tags(tags):
  map(lambda x: x.extract(), tags)