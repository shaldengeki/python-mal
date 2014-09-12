#!/usr/bin/python
# -*- coding: utf-8 -*-

import utilities
from base import Base, Error, loadable
import media_list

class AnimeList(media_list.MediaList):
  __id_attribute = "username"
  def __init__(self, session, user_name):
    super(AnimeList, self).__init__(session, user_name)

  @property
  def type(self):
    return "anime"

  @property
  def verb(self):
    return "watch"

  def parse_section_row(self, soup, status, column_names):
    entry_info = super(AnimeList, self).parse_section_row(soup, status, column_names)

    cols = soup.find_all(u'td')
    progress_parts = cols[column_names.index('progress')].text.split(u'/')
    try:
      entry_info[u'episodes_watched'] = int(progress_parts[0])
    except ValueError:
      entry_info[u'episodes_watched'] = 0
    entry_info[u'tags'] = map(lambda x: x.text, cols[column_names.index('tags')].find_all(u'a'))
    entry_info[u'started'] = None
    if 'started' in column_names and cols[column_names.index('started')].text.strip() != u'':
      entry_info[u'started'] = utilities.parse_profile_date(cols[column_names.index('started')].text)
    entry_info[u'finished'] = None
    if 'finished' in column_names and cols[column_names.index('finished')].text.strip() != u'':
      entry_info[u'finished'] = utilities.parse_profile_date(cols[column_names.index('finished')].text)
    return entry_info

  def parse_section_columns(self, columns):
    column_names = super(AnimeList, self).parse_section_columns(columns)
    for column in columns:
      if u'Type' in column.text:
        column_names.append('type')
      elif u'Progress' in column.text:
        column_names.append('progress')
      elif u'Tags' in column.text:
        column_names.append('tags')
      elif u'Started' in column.text:
        column_names.append('started')
      elif u'Finished' in column.text:
        column_names.append('finished')
    return column_names