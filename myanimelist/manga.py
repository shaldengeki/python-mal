#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedMangaPageError(Error):
  def __init__(self, manga_id):
    super(MalformedMangaPageError, self).__init__()
    self.manga_id = manga_id
  def __str__(self):
    return "\n".join([
      super(MalformedMangaPageError, self).__str__(),
      "Manga ID: " + unicode(self.manga_id)
    ])

class InvalidMangaError(Error):
  def __init__(self, manga_id):
    super(InvalidMangaError, self).__init__()
    self.manga_id = manga_id
  def __str__(self):
    return "\n".join([
      super(InvalidMangaError, self).__str__(),
      "Manga ID: " + unicode(self.manga_id)
    ])

class Manga(Base):
  def __repr__(self):
    return u"<Manga ID: " + unicode(self.id) + u">"
  def __hash__(self):
    return hash(self.id)
  def __eq__(self, manga):
    return isinstance(manga, Manga) and self.id == manga.id
  def __ne__(self, manga):
    return not self.__eq__(manga)
  def __init__(self, session, manga_id):
    super(Manga, self).__init__(session)
    self.id = manga_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidMangaError(self.id)
    self._title = None