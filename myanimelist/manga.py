#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import pytz
import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedMangaPageError(Error):
  def __init__(self, manga):
    super(MalformedMangaPageError, self).__init__()
    self.manga = manga
  def __str__(self):
    return "\n".join([
      super(MalformedMangaPageError, self).__str__(),
      "Manga ID: " + unicode(self.manga.id)
    ])

class InvalidMangaError(Error):
  def __init__(self, manga):
    super(InvalidMangaError, self).__init__()
    self.manga = manga
  def __str__(self):
    return "\n".join([
      super(InvalidMangaError, self).__str__(),
      "Manga ID: " + unicode(self.manga.id)
    ])

def parse_date(text):
  """
    Parses a MAL date on an manga page.
    May raise ValueError if a malformed date is found.
    If text is "Unknown" or "?" then returns None.
    Otherwise, returns a datetime.date object.
  """
  if text == "Unknown" or text == "?":
    return None
  try:
    aired_date = datetime.datetime.strptime(text, '%Y').date()
  except ValueError:
    # see if it's a date.
    aired_date = datetime.datetime.strptime(text, '%b %d, %Y').date()
  return aired_date

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
      raise InvalidMangaError(self)
    self._title = None