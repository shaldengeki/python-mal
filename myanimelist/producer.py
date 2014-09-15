#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class InvalidProducerError(Error):
  def __init__(self, producer_id, message=None):
    super(InvalidProducerError, self).__init__(message=message)
    self.producer_id = producer_id
  def __str__(self):
    return "\n".join([
      super(InvalidProducerError, self).__str__(),
      "ID: " + unicode(self.producer_id)
    ])

class Producer(Base):
  def __init__(self, session, producer_id):
    super(Producer, self).__init__(session)
    self.id = producer_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidProducerError(self.id)
    self._name = None

  def load(self):
    # TODO
    pass

  @property
  @loadable(u'load')
  def name(self):
    return self._name