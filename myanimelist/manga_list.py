#!/usr/bin/python
# -*- coding: utf-8 -*-

import utilities
from base import Base, Error, loadable
import media_list

class MangaList(media_list.MediaList):
  __id_attribute = "username"
  def __init__(self, session, user_name):
    super(MangaList, self).__init__(session, user_name)

  @property
  def type(self):
    return "manga"

  @property
  def verb(self):
    return "read"

  def parse_section_row(self, soup, status, column_names):
    entry_info = super(MangaList, self).parse_section_row(soup, status, column_names)
    cols = soup.find_all(u'td')

    chapter_parts = cols[column_names[u'chapters']].text.split(u'/')
    try:
      entry_info[u'chapters'] = int(chapter_parts[0])
    except ValueError:
      entry_info[u'chapters'] = 0

    volume_parts = cols[column_names[u'volumes']].text.split(u'/')
    try:
      entry_info[u'volumes'] = int(volume_parts[0])
    except ValueError:
      entry_info[u'volumes'] = 0

    entry_info[u'tags'] = []
    if 'tags' in column_names:
      entry_info[u'tags'] = map(lambda x: x.text, cols[column_names[u'tags']].find_all(u'a'))

    entry_info[u'priority'] = None
    if 'priority' in column_names:
      entry_info[u'priority'] = cols[column_names[u'priority']].text

    entry_info[u'started'] = None
    if 'started' in column_names and cols[column_names[u'started']].text.strip() != u'':
      entry_info[u'started'] = utilities.parse_profile_date(cols[column_names[u'started']].text)
    entry_info[u'finished'] = None
    if 'finished' in column_names and cols[column_names[u'finished']].text.strip() != u'':
      entry_info[u'finished'] = utilities.parse_profile_date(cols[column_names[u'finished']].text)
    return entry_info

  def parse_section_columns(self, columns):
    column_names = super(MangaList, self).parse_section_columns(columns)
    for i,column in enumerate(columns):
      if u'Chapters' in column.text:
        column_names[u'chapters'] = i
      elif u'Volumes' in column.text:
        column_names[u'volumes'] = i
      elif u'Tags' in column.text:
        column_names[u'tags'] = i
      elif u'Priority' in column.text:
        column_names[u'priority'] = i
      elif u'Started' in column.text:
        column_names[u'started'] = i
      elif u'Finished' in column.text:
        column_names[u'finished'] = i
    return column_names