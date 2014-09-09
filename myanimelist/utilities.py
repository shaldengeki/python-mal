#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

def extract_tags(tags):
  map(lambda x: x.extract(), tags)

def parse_profile_date(text):
  """
    Parses a MAL date on a profile page.
    May raise ValueError if a malformed date is found.
    If text is "Unknown" or "?" or "Not available" then returns None.
    Otherwise, returns a datetime.date object.
  """
  if text == u"Unknown" or text == u"?" or text == u"Not available":
    return None
  try:
    aired_date = datetime.datetime.strptime(text, '%Y').date()
  except ValueError:
    # see if it's a date.
    try:
      aired_date = datetime.datetime.strptime(text, '%b %d, %Y').date()
    except ValueError:
      # see if it's a month/year pairing.
      aired_date = datetime.datetime.strptime(text, '%b %Y').date()
  return aired_date