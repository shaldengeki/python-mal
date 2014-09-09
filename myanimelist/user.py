#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedUserPageError(Error):
  def __init__(self, user_id=None, username=None):
    super(MalformedUserPageError, self).__init__()
    self.user_id = user_id
    self.username = username
  def __str__(self):
    return "\n".join([
      super(MalformedUserPageError, self).__str__(),
      "User ID: " + unicode(self.user_id),
      "Username: " + unicode(self.username)
    ])

class InvalidUserError(Error):
  def __init__(self, user_id=None, username=None):
    super(InvalidUserError, self).__init__()
    self.user_id = user_id
    self.username = username
  def __str__(self):
    return "\n".join([
      super(InvalidUserError, self).__str__(),
      "User ID: " + unicode(self.user_id),
      "Username: " + unicode(self.username)
    ])

class User(Base):
  def __repr__(self):
    return u"<User ID: " + unicode(self.id) + u">"
  def __hash__(self):
    return hash(self.id)
  def __eq__(self, user):
    return isinstance(user, User) and self.id == user.id
  def __ne__(self, user):
    return not self.__eq__(user)
  def __init__(self, session, id=None, username=None):
    super(User, self).__init__(session)
    self.id = id
    self.username = username
    if (not isinstance(self.id, int) or int(self.id) < 1) and (not isinstance(self.username, basestring) or len(self.username) < 1):
      raise InvalidUserError(self.id, self.username)