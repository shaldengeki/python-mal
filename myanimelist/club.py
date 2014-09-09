#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedClubPageError(Error):
  def __init__(self, club_id):
    super(MalformedClubPageError, self).__init__()
    self.club_id = club_id
  def __str__(self):
    return "\n".join([
      super(MalformedClubPageError, self).__str__(),
      "Club ID: " + unicode(self.club_id)
    ])

class InvalidClubError(Error):
  def __init__(self, club_id):
    super(InvalidClubError, self).__init__()
    self.club_id = club_id
  def __str__(self):
    return "\n".join([
      super(InvalidClubError, self).__str__(),
      "Club ID: " + unicode(self.club_id)
    ])

class Club(Base):
  def __repr__(self):
    return u"<Club ID: " + unicode(self.id) + u">"
  def __hash__(self):
    return hash(self.id)
  def __eq__(self, club):
    return isinstance(club, Club) and self.id == club.id
  def __ne__(self, club):
    return not self.__eq__(club)
  def __init__(self, session, club_id):
    super(Club, self).__init__(session)
    self.id = club_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidClubError(self.id)
    self._name = None
    self._num_members = None

  @property
  @loadable('load')
  def name(self):
    return self._name

  @property
  @loadable('load')
  def num_members(self):
    return self._num_members
