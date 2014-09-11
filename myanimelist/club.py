#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedClubPageError(Error):
  def __init__(self, club_id, html, message=None):
    super(MalformedClubPageError, self).__init__(message=message)
    self.club_id = int(club_id)
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedClubPageError, self).__str__(),
      "ID: " + unicode(self.club_id),
      "HTML: " + self.html
    ]).encode(u'utf-8')

class InvalidClubError(Error):
  def __init__(self, club_id, message=None):
    super(InvalidClubError, self).__init__(message=message)
    self.club_id = club_id
  def __str__(self):
    return "\n".join([
      super(InvalidClubError, self).__str__(),
      "ID: " + unicode(self.club_id)
    ])

class Club(Base):
  def __init__(self, session, club_id):
    super(Club, self).__init__(session)
    self.id = club_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidClubError(self.id)
    self._name = None
    self._num_members = None

  def load(self):
    # TODO
    pass

  @property
  @loadable(u'load')
  def name(self):
    return self._name

  @property
  @loadable(u'load')
  def num_members(self):
    return self._num_members
