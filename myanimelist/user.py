#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedUserPageError(Error):
  def __init__(self, username):
    super(MalformedUserPageError, self).__init__()
    self.username = username
  def __str__(self):
    return "\n".join([
      super(MalformedUserPageError, self).__str__(),
      "Username: " + unicode(self.username)
    ])

class InvalidUserError(Error):
  def __init__(self, username):
    super(InvalidUserError, self).__init__()
    self.username = username
  def __str__(self):
    return "\n".join([
      super(InvalidUserError, self).__str__(),
      "Username: " + unicode(self.username)
    ])

class User(Base):
  def __repr__(self):
    return u"<User name: " + unicode(self.name) + ">"
  def __hash__(self):
    return hash(self.name)
  def __eq__(self, user):
    return isinstance(user, User) and self.name == user.name
  def __ne__(self, user):
    return not self.__eq__(user)
  def __init__(self, session, username):
    super(User, self).__init__(session)
    self.username = username
    if not isinstance(self.username, basestring) or len(self.username) < 1:
      raise InvalidUserError(self.username)
    self._id = None

  @property
  @loadable('load')
  def id(self):
    return self._id
