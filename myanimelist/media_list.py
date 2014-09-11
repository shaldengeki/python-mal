#!/usr/bin/python
# -*- coding: utf-8 -*-

import abc
import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedMediaListPageError(Error):
  def __init__(self, user_name):
    super(MalformedMediaListPageError, self).__init__()
    self.user_name = user_name
  def __str__(self):
    return "\n".join([
      super(MalformedMediaListPageError, self).__str__(),
      "MediaList username: " + unicode(self.user_name)
    ])

class InvalidMediaListError(Error):
  def __init__(self, user_name):
    super(InvalidMediaListError, self).__init__()
    self.user_name = user_name
  def __str__(self):
    return "\n".join([
      super(InvalidMediaListError, self).__str__(),
      "MediaList username: " + unicode(self.user_name)
    ])

class MediaList(Base):
  __metaclass__ = abc.ABCMeta

  __id_attribute = "username"
  def __init__(self, session, user_name):
    super(MediaList, self).__init__(session)
    self.username = user_name
    if not isinstance(self.username, unicode) or len(self.username) < 4:
      raise InvalidMediaListError(self.username)

  # subclasses must define a list type.
  @abc.abstractmethod
  def type(self):
    pass

  @property
  @loadable('load')
  def name(self):
    return self._name