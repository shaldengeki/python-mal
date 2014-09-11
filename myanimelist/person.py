#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedPersonPageError(Error):
  def __init__(self, person_id, html, message=None):
    super(MalformedPersonPageError, self).__init__(message=message)
    self.person_id = int(person_id)
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedPersonPageError, self).__str__(),
      "ID: " + unicode(self.person_id),
      "HTML: " + self.html
    ]).encode(u'utf-8')

class InvalidPersonError(Error):
  def __init__(self, person_id, message=None):
    super(InvalidPersonError, self).__init__(message=message)
    self.person_id = person_id
  def __str__(self):
    return "\n".join([
      super(InvalidPersonError, self).__str__(),
      "ID: " + unicode(self.person_id)
    ])

class Person(Base):
  def __init__(self, session, person_id):
    super(Person, self).__init__(session)
    self.id = person_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidPersonError(self.id)
    self._name = None

  def load(self):
    # TODO
    pass

  @property
  @loadable(u'load')
  def name(self):
    return self._name