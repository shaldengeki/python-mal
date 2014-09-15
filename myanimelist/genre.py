#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, MalformedPageError, InvalidBaseError, loadable

class MalformedGenrePageError(MalformedPageError):
  pass

class InvalidGenreError(InvalidBaseError):
  pass

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
