#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedPersonPageError(Error):
  def __init__(self, person_id):
    super(MalformedPersonPageError, self).__init__()
    self.person_id = person_id
  def __str__(self):
    return "\n".join([
      super(MalformedPersonPageError, self).__str__(),
      "Person ID: " + unicode(self.person_id)
    ])

class InvalidPersonError(Error):
  def __init__(self, person_id):
    super(InvalidPersonError, self).__init__()
    self.person_id = person_id
  def __str__(self):
    return "\n".join([
      super(InvalidPersonError, self).__str__(),
      "Person ID: " + unicode(self.person_id)
    ])

class Person(Base):
  def __repr__(self):
    return u"<Person ID: " + unicode(self.id) + u">"
  def __hash__(self):
    return hash(self.id)
  def __eq__(self, person):
    return isinstance(person, Person) and self.id == person.id
  def __ne__(self, person):
    return not self.__eq__(person)
  def __init__(self, session, person_id):
    super(Person, self).__init__(session)
    self.id = person_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidPersonError(self.id)
    self._name = None

  @property
  @loadable('load')
  def name(self):
    return self._name