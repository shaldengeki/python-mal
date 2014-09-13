#!/usr/bin/python
# -*- coding: utf-8 -*-

import abc
from base import Base

class Media(Base):
  """
    Base class for all media resources on MAL.
  """
  __metaclass__ = abc.ABCMeta

  # a container of status terms for this media.
  # keys are status ints, values are statuses e.g. "Airing"
  @abc.abstractproperty
  def status_terms(self):
    pass