#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib

# causes httplib to return the partial response from a server in case the read fails to be complete.
def patch_http_response_read(func):
  def inner(*args):
    try:
      return func(*args)
    except httplib.IncompleteRead, e:
      return e.partial
  return inner
httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)