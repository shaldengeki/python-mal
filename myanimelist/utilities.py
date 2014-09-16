#!/usr/bin/python
# -*- coding: utf-8 -*-
import bs4
import datetime
import re
import urllib

def fix_bad_html(html):
  """
    Fixes for various DOM errors that MAL commits.
    Yes, I know this is a cardinal sin, but there's really no elegant way to fix this.
  """
  # on anime list pages, sometimes tds won't be properly opened.
  html = re.sub(r'[\s]td class=', "<td class=", html)
  # on anime list pages, if the user doesn't specify progress, MAL will try to close a span it didn't open.
  def anime_list_closing_span(match):
    return match.group(u'count') + '/' + match.group(u'total') + '</td>'
  html = re.sub(r'(?P<count>[0-9\-]+)</span>/(?P<total>[0-9\-]+)</a></span></td>', anime_list_closing_span, html)

  # on anime info pages, under rating, there's an extra </div> by the "licensing company" note.
  html = html.replace('<small>L</small></sup><small> represents licensing company</small></div>', '<small>L</small></sup><small> represents licensing company</small>')

  # on manga character pages, sometimes the character info column will have an extra </div>.
  def manga_character_double_closed_div_picture(match):
    return "<td " + match.group(u'td_tag') + ">\n\t\t\t<div " + match.group(u'div_tag') + "><a " + match.group(u'a_tag') + "><img " + match.group(u'img_tag') + "></a></div>\n\t\t\t</td>"
  html = re.sub(r"""<td (?P<td_tag>[^>]+)>\n\t\t\t<div (?P<div_tag>[^>]+)><a (?P<a_tag>[^>]+)><img (?P<img_tag>[^>]+)></a></div>\n\t\t\t</div>\n\t\t\t</td>""", manga_character_double_closed_div_picture, html)

  def manga_character_double_closed_div_character(match):
    return """<a href="/character/""" + match.group(u'char_link') + """">""" + match.group(u'char_name') + """</a>\n\t\t\t<div class="spaceit_pad"><small>""" + match.group(u'role') + """</small></div>"""
  html = re.sub(r"""<a href="/character/(?P<char_link>[^"]+)">(?P<char_name>[^<]+)</a>\n\t\t\t<div class="spaceit_pad"><small>(?P<role>[A-Za-z ]+)</small></div>\n\t\t\t</div>""", manga_character_double_closed_div_character, html)
  return html

def get_clean_dom(html):
  """
    Given raw HTML from a MAL page, return a BeautifulSoup object with cleaned HTML.
  """
  return bs4.BeautifulSoup(fix_bad_html(html), "html.parser")

def urlencode(url):
  """
    Given a string, return a string that can be used safely in a MAL url.
  """
  return urllib.urlencode({'': url.encode(u'utf-8').replace(' ', '_')})[1:].replace('%2F', '/')

def extract_tags(tags):
  map(lambda x: x.extract(), tags)

def parse_profile_date(text, suppress=False):
  """
    Parses a MAL date on a profile page.
    May raise ValueError if a malformed date is found.
    If text is "Unknown" or "?" or "Not available" then returns None.
    Otherwise, returns a datetime.date object.
  """
  try:
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
  except:
    if suppress:
      return None
    raise