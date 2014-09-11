#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re
import urllib
import collections

import utilities
from base import Base, Error, loadable
import media_list

class MalformedAnimeListPageError(media_list.MalformedMediaListPageError):
  pass

class InvalidAnimeListError(media_list.InvalidMediaListError):
  pass

class AnimeList(media_list.MediaList):
  __id_attribute = "username"
  def __init__(self, session, user_name):
    super(AnimeList, self).__init__(session, user_name)

  @property
  def type(self):
    return "anime"

  def load_large_list(self):
    """
      Loads each section of the anime list separately.
      This is necessary for users who have large anime lists,
      as MAL refuses to display the whole list at once.
    """
    statuses = [1, 2, 3, 4, 6]
    section_results = []
    for status in statuses:
      media_list = self.session.session.get(u'http://myanimelist.net/' + self.type + u'list/' + utilities.urlencode(self.username) + u'&' + urllib.urlencode({'status': status, 'order': 0})).text
      section_results.append(self.parse(media_list, is_section=True))
    # we have to do some finagling to get the correct combined stats.
    stats_sum = sum((collections.Counter(d['stats']) for d in section_results), collections.Counter())
    # weigh mean score, score dev by total number of entries in each section.
    stats_sum['Mean Score'] = sum(d['stats']['Mean Score'] * len(d['list']) for d in section_results) / sum(len(d['list']) for d in section_results)
    stats_sum['Score Dev.'] = sum(d['stats']['Score Dev.'] * len(d['list']) for d in section_results) / sum(len(d['list']) for d in section_results)
    return {
      'list': {k: v for d in section_results for k,v in d['list'].iteritems()},
      'stats': stats_sum
    }

  def parse(self, html, is_section=False):
    list_info = {}
    html = utilities.fix_bad_html(html)
    list_page = bs4.BeautifulSoup(html)

    bad_username_elt = list_page.find('div', {'class': 'badresult'})
    if bad_username_elt:
      raise InvalidAnimeListError(self.username, message=u"Invalid username when fetching anime list")

    if is_section:
      stats_elt = list_page.find('td', {'class': 'category_totals'})
      print "Section only"
    else:
      stats_elt = list_page.find('div', {'id': 'grand_totals'})
      print "All sections"

    if not stats_elt:
      if u'disabled for lists' in list_page.text:
        return self.load_large_list()
      else:
        raise MalformedAnimeListPageError(self.username, html, message="Could not find section headers in anime list")

    list_info[u'stats'] = {}
    stats_rows = stats_elt.text.strip().split('\n')
    for row in stats_rows:
      row = re.match(r'(?P<category>[A-Za-z\ \.]+): ?(?P<value>[0-9\,\-\.]*)?', row.lstrip()).groupdict()
      row['value'] = row['value'].replace(',', '')
      if row['category'] in ['TV', 'OVA', 'Movies', 'Spcl.', 'Eps', 'DL Eps']:
        try:
          row['value'] = int(row['value'])
        except ValueError:
          row['value'] = 0
      elif row['category'] in ['Days', 'Score Dev.']:
        try:
          row['value'] = round(float(row['value']), 2)
        except ValueError:
          row['value'] = 0.00
      elif row['category'] in ['Mean Score']:
        try:
          row['value'] = round(float(row['value']), 1)
        except ValueError:
          row['value'] = 0.0
      list_info[u'stats'][row['category']] = row['value']

    list_info[u'list'] = {}
    headers = list_page.find_all(u'div', {'class': 'header_title'})
    headers = map(lambda x: x.parent.parent.parent, headers)
    for header in headers:
      table_header = header.findNext(u'table')
      table_header_cols = table_header.find_all(u'td', {'class': 'table_header'})
      offset_col = 0
      started_col = False
      finished_col = False
      if any(map(lambda x: u'#' == x.text, table_header_cols)):
        offset_col += 1

      if any(map(lambda x: u'Started' in x.text, table_header_cols)):
        started_col = True

      if any(map(lambda x: u'Finished' in x.text, table_header_cols)):
        finished_col = True

      curr_row = table_header.findNext(u'table')
      while not curr_row.find(u'td', {'class': 'category_totals'}):
        cols = curr_row.find_all(u'td')
        anime_link = cols[offset_col].find(u'a', recursive=False)
        link_parts = anime_link.get(u'href').split(u'/')
        # of the form: /anime/15061/Aikatsu!
        anime = self.session.anime(int(link_parts[2])).set({'title': anime_link.text})
        entry_info = {u'status': header.text.strip()}
        try:
          entry_info[u'score'] = int(cols[offset_col + 1].text)
        except ValueError:
          entry_info[u'score'] = None
        progress_parts = cols[offset_col + 3].text.split(u'/')
        try:
          entry_info[u'episodes_watched'] = int(progress_parts[0])
        except ValueError:
          entry_info[u'episodes_watched'] = 0
        entry_info[u'tags'] = map(lambda x: x.text, cols[offset_col + 4].find_all(u'a'))
        entry_info[u'started'] = None
        if started_col and cols[offset_col + 5].text.strip() != u'':
          entry_info[u'started'] = utilities.parse_profile_date(cols[offset_col + 5].text)
        entry_info[u'finished'] = None
        if finished_col and cols[offset_col + 6].text.strip() != u'':
          entry_info[u'finished'] = utilities.parse_profile_date(cols[offset_col + 6].text)
        list_info[u'list'][anime] = entry_info
        curr_row = curr_row.findNext(u'table')
    return list_info