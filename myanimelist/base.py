#!/usr/bin/python
# -*- coding: utf-8 -*-

class Error(Exception):
  def __init__(self, message=None):
    super(Error, self).__init__()
    self.message = message
  def __str__(self):
    return unicode(self.message) if self.message is not None else u""

def loadable(func):
  '''
    Decorator for getters that require a load() upon first access.
  '''
  cached_name = '_' + func.__name__
  def _decorator(self, *args, **kwargs):
    if getattr(self, cached_name) is None:
      self.load()
    return func(self, *args, **kwargs)
  return _decorator

class Base(object):
  '''
    Provides autoloading, auto-setting functionality for other MAL objects.
  '''
  def __init__(self, session):
    self.session = session

  def load(self):
    raise NotImplementedError("Subclasses must implement load()")

  def set(self, attr_dict):
    """
    Sets attributes of this user object with keys found in dict.
    """
    for key in attr_dict:
      if key == 'id':
        self.id = attr_dict[key]
      else:
        setattr(self, "_" + key, attr_dict[key])
    return self