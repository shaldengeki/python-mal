#!/usr/bin/python
# -*- coding: utf-8 -*-

import abc
import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedMediaListPageError(Error):
  def __init__(self, username, html, message=None):
    super(MalformedMediaListPageError, self).__init__(message=message)
    if isinstance(username, unicode):
      self.username = username
    else:
      self.username = str(username).decode('utf-8')
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode('utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedMediaListPageError, self).__str__(),
      "Username: " + unicode(self.username),
      "HTML: " + self.html
    ]).encode('utf-8')

class InvalidMediaListError(Error):
  def __init__(self, username, message=None):
    super(InvalidMediaListError, self).__init__(message=message)
    if isinstance(username, unicode):
      self.username = username
    else:
      self.username = str(username).decode('utf-8')
  def __str__(self):
    return "\n".join([
      super(InvalidMediaListError, self).__str__(),
      "Username: " + unicode(self.username)
    ])

class MediaList(Base):
  __metaclass__ = abc.ABCMeta

  __id_attribute = "username"
  def __init__(self, session, user_name):
    super(MediaList, self).__init__(session)
    self.username = user_name
    if not isinstance(self.username, unicode) or len(self.username) < 4:
      raise InvalidMediaListError(self.username)
    self._list = None
    self._stats = None

  # subclasses must define a list type, a list dict (what an unfortunate name), and a stats dict.
  @abc.abstractproperty
  def type(self):
    pass

  @property
  @loadable('load')
  def list(self):
    return self._list

  @property
  @loadable('load')
  def stats(self):
    return self._stats