#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedTagPageError(Error):
  def __init__(self, tag_name, html, message=None):
    super(MalformedTagPageError, self).__init__(message=message)
    if isinstance(tag_name, unicode):
      self.tag_name = tag_name
    else:
      self.tag_name = str(tag_name).decode(u'utf-8')
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedTagPageError, self).__str__(),
      "Name: " + unicode(self.tag_name),
      "HTML: " + self.html
    ]).encode(u'utf-8')

class InvalidTagError(Error):
  def __init__(self, tag_name, message=None):
    super(InvalidTagError, self).__init__(message=message)
    if isinstance(tag_name, unicode):
      self.tag_name = tag_name
    else:
      self.tag_name = str(tag_name).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(InvalidTagError, self).__str__(),
      "Name: " + unicode(self.tag_name)
    ])

class Tag(Base):
  _id_attribute = "name"
  def __init__(self, session, name):
    super(Tag, self).__init__(session)
    self.name = name
    if not isinstance(self.name, unicode) or len(self.name) < 1:
      raise InvalidTagError(self.name)

  def load(self):
    # TODO
    pass