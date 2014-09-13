#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedGenrePageError(Error):
  def __init__(self, genre_id, html, message=None):
    super(MalformedGenrePageError, self).__init__(message=message)
    self.genre_id = int(genre_id)
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedGenrePageError, self).__str__(),
      "ID: " + unicode(self.genre_id),
      "HTML: " + self.html
    ]).encode(u'utf-8')

class InvalidGenreError(Error):
  def __init__(self, genre_id, message=None):
    super(InvalidGenreError, self).__init__(message=message)
    self.genre_id = genre_id
  def __str__(self):
    return "\n".join([
      super(InvalidGenreError, self).__str__(),
      "ID: " + unicode(self.genre_id)
    ])

class Genre(Base):
  def __init__(self, session, genre_id):
    super(Genre, self).__init__(session)
    self.id = genre_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidGenreError(self.id)
    self._name = None

  def load(self):
    # TODO
    pass

  @property
  @loadable(u'load')
  def name(self):
    return self._name
