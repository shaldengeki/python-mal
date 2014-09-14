#!/usr/bin/python
# -*- coding: utf-8 -*-
import abc
import bs4
import functools

import utilities

class Error(Exception):
  def __init__(self, message=None):
    super(Error, self).__init__()
    self.message = message
  def __str__(self):
    return unicode(self.message) if self.message is not None else u""

def loadable(func_name):
  '''
    Decorator for getters that require a load() upon first access.
  '''
  def inner(func):
    cached_name = '_' + func.__name__
    @functools.wraps(func)
    def _decorator(self, *args, **kwargs):
      if getattr(self, cached_name) is None:
        getattr(self, func_name)()
      return func(self, *args, **kwargs)
    return _decorator
  return inner

class Base(object):
  '''
    Abstract base class for MAL resources.
    Provides autoloading, auto-setting functionality for other MAL objects.
  '''
  __metaclass__ = abc.ABCMeta

  # attribute name for primary reference key to this object.
  # when an attribute by the name given by _id_attribute is passed into set(),
  # set() doesn't prepend an underscore for load()ing.
  _id_attribute = "id"

  def __repr__(self):
    return u"".join([
      "<",
      self.__class__.__name__,
      " ",
      self._id_attribute,
      ": ",
      unicode(getattr(self, self._id_attribute)),
      ">"
    ])
  def __hash__(self):
    return hash(getattr(self, self._id_attribute))
  def __eq__(self, other):
    return isinstance(other, self.__class__) and getattr(self, self._id_attribute) == getattr(other, other._id_attribute)
  def __ne__(self, other):
    return not self.__eq__(other)

  def __init__(self, session):
    self.session = session
    self.suppress_exceptions = False

  @abc.abstractmethod
  def load(self):
    pass

  def set(self, attr_dict):
    """
    Sets attributes of this user object with keys found in dict.
    """
    for key in attr_dict:
      if key == self._id_attribute:
        try:
          setattr(self, self._id_attribute, attr_dict[key])
        except:
          print u"Dict:"
          print attr_dict
          print u"Key: " + key
          raise
      else:
        setattr(self, u"_" + key, attr_dict[key])
    return self