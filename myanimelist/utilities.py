#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re
import urllib

def urlencode(url):
  """
    Given a string, return a string that can be used safely in a MAL url.
  """
  return urllib.urlencode({'': url.encode('utf-8').replace(' ', '_')})[1:].replace('%2F', '/')


def extract_tags(tags):
  map(lambda x: x.extract(), tags)

def decommaify_int(number):
  """
    Return an int represented by number, with commas removed.
  """
  return int(number.replace(',', ''))

def parse_profile_date(text):
  """
    Parses a MAL date on a profile page.
    May raise ValueError if a malformed date is found.
    If text is "Unknown" or "?" or "Not available" then returns None.
    Otherwise, returns a datetime.date object.
  """
  if text == u"Unknown" or text == u"?" or text == u"Not available":
    return None
  if text == u"Now":
    return datetime.datetime.now()

  seconds_match = re.match(r'(?P<seconds>[0-9]+) second(s)? ago', text)
  if seconds_match:
    return datetime.datetime.now() - datetime.timedelta(seconds=int(seconds_match.group('seconds')))

  minutes_match = re.match(r'(?P<minutes>[0-9]+) minute(s)? ago', text)
  if minutes_match:
    return datetime.datetime.now() - datetime.timedelta(minutes=int(minutes_match.group('minutes')))

  hours_match = re.match(r'(?P<hours>[0-9]+) hour(s)? ago', text)
  if hours_match:
    return datetime.datetime.now() - datetime.timedelta(hours=int(hours_match.group('hours')))

  today_match = re.match(r'Today, (?P<hour>[0-9]+):(?P<minute>[0-9]+) (?P<am>[APM]+)', text)
  if today_match:
    hour = int(today_match.group('hour'))
    minute = int(today_match.group('minute'))
    am = today_match.group('am')
    if am == u'PM':
      hour += 12
    today = datetime.date.today()
    return datetime.datetime(year=today.year, month=today.month, day=today.day, hour=hour, minute=minute, second=0)

  yesterday_match = re.match(r'Yesterday, (?P<hour>[0-9]+):(?P<minute>[0-9]+) (?P<am>[APM]+)', text)
  if yesterday_match:
    hour = int(yesterday_match.group('hour'))
    minute = int(yesterday_match.group('minute'))
    am = yesterday_match.group('am')
    if am == u'PM':
      hour += 12
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    return datetime.datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=hour, minute=minute, second=0)

  try:
    return datetime.datetime.strptime(text, '%m-%d-%y, %I:%M %p')
  except ValueError:
    pass
  try:
    return datetime.datetime.strptime(text, '%B %d, %Y').date()
  except ValueError:
    pass
  try:
    return datetime.datetime.strptime(text, '%b %d, %Y').date()
  except ValueError:
    pass
  try:
    return datetime.datetime.strptime(text, '%Y').date()
  except ValueError:
    pass
  # see if it's a date.
  try:
    return datetime.datetime.strptime(text, '%b %d, %Y').date()
  except ValueError:
    pass
  # see if it's a month/year pairing.
  return datetime.datetime.strptime(text, '%b %Y').date()