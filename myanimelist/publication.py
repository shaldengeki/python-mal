#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedPublicationPageError(Error):
  def __init__(self, publication_id, html, message=None):
    super(MalformedPublicationPageError, self).__init__(message=message)
    self.publication_id = int(publication_id)
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedPublicationPageError, self).__str__(),
      "ID: " + unicode(self.publication_id),
      "HTML: " + self.html
    ]).encode(u'utf-8')

class InvalidPublicationError(Error):
  def __init__(self, publication_id, message=None):
    super(InvalidPublicationError, self).__init__(message=message)
    self.publication_id = publication_id
  def __str__(self):
    return "\n".join([
      super(InvalidPublicationError, self).__str__(),
      "ID: " + unicode(self.publication_id)
    ])

class Publication(Base):
  def __init__(self, session, publication_id):
    super(Publication, self).__init__(session)
    self.id = publication_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidPublicationError(self.id)
    self._name = None

  def load(self):
    # TODO
    pass

  @property
  @loadable(u'load')
  def name(self):
    return self._name
