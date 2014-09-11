#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedMangaPageError(Error):
  def __init__(self, manga_id, html, message=None):
    super(MalformedMangaPageError, self).__init__(message=message)
    self.manga_id = int(manga_id)
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode('utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedMangaPageError, self).__str__(),
      "ID: " + unicode(self.manga_id),
      "HTML: " + self.html
    ]).encode('utf-8')

class InvalidMangaError(Error):
  def __init__(self, manga_id, message=None):
    super(InvalidMangaError, self).__init__(message=message)
    self.manga_id = manga_id
  def __str__(self):
    return "\n".join([
      super(InvalidMangaError, self).__str__(),
      "ID: " + unicode(self.manga_id)
    ])

class Manga(Base):
  def __init__(self, session, manga_id):
    super(Manga, self).__init__(session)
    self.id = manga_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidMangaError(self.id)
    self._title = None

  def load(self):
    # TODO
    pass

  @property
  @loadable('load')
  def title(self):
    return self._title