#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re
import urllib

def fix_bad_html(html):
  """
    Fixes for various DOM errors that MAL commits.
  """
  # on anime list pages, sometimes tds won't be properly opened.
  html = re.sub(r'[\s]td class=', "<td class=", html)
  # on anime list pages, if the user doesn't specify progress, MAL will try to close a span it didn't open.
  def anime_list_closing_span(match):
    return match.group(u'count') + '/' + match.group(u'total') + '</td>'
  html = re.sub(r'(?P<count>[0-9\-]+)</span>/(?P<total>[0-9\-]+)</a></span></td>', anime_list_closing_span, html)
  return html

def urlencode(url):
  """
    Given a string, return a string that can be used safely in a MAL url.
  """
  return urllib.urlencode({'': url.encode(u'utf-8').replace(' ', '_')})[1:].replace('%2F', '/')

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
  if text == u"Now":
    return datetime.datetime.now()

  seconds_match = re.match(r'(?P<seconds>[0-9]+) second(s)? ago', text)
  if seconds_match:
    return datetime.datetime.now() - datetime.timedelta(seconds=int(seconds_match.group(u'seconds')))

  minutes_match = re.match(r'(?P<minutes>[0-9]+) minute(s)? ago', text)
  if minutes_match:
    return datetime.datetime.now() - datetime.timedelta(minutes=int(minutes_match.group(u'minutes')))

  hours_match = re.match(r'(?P<hours>[0-9]+) hour(s)? ago', text)
  if hours_match:
    return datetime.datetime.now() - datetime.timedelta(hours=int(hours_match.group(u'hours')))

  today_match = re.match(r'Today, (?P<hour>[0-9]+):(?P<minute>[0-9]+) (?P<am>[APM]+)', text)
  if today_match:
    hour = int(today_match.group(u'hour'))
    minute = int(today_match.group(u'minute'))
    am = today_match.group(u'am')
    if am == u'PM' and hour < 12:
      hour += 12
    today = datetime.date.today()
    return datetime.datetime(year=today.year, month=today.month, day=today.day, hour=hour, minute=minute, second=0)

  yesterday_match = re.match(r'Yesterday, (?P<hour>[0-9]+):(?P<minute>[0-9]+) (?P<am>[APM]+)', text)
  if yesterday_match:
    hour = int(yesterday_match.group(u'hour'))
    minute = int(yesterday_match.group(u'minute'))
    am = yesterday_match.group(u'am')
    if am == u'PM' and hour < 12:
      hour += 12
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    return datetime.datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=hour, minute=minute, second=0)

  try:
    return datetime.datetime.strptime(text, '%m-%d-%y, %I:%M %p')
  except ValueError:
    pass
  # see if it's a date.
  try:
    return datetime.datetime.strptime(text, '%m-%d-%y').date()
  except ValueError:
    pass
  try:
    return datetime.datetime.strptime(text, '%Y-%m-%d').date()
  except ValueError:
    pass
  try:
    return datetime.datetime.strptime(text, '%Y-%m-00').date()
  except ValueError:
    pass
  try:
    return datetime.datetime.strptime(text, '%Y-00-00').date()
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
  try:
    return datetime.datetime.strptime(text, '%b %d, %Y').date()
  except ValueError:
    pass
  # see if it's a month/year pairing.
  return datetime.datetime.strptime(text, '%b %Y').date()