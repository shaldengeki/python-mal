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

  def parse_entry_media_attributes(self, soup):
    attributes = super(AnimeList, self).parse_entry_media_attributes(soup)

    try:
      attributes['episodes'] = int(soup.find('series_episodes').text)
    except ValueError:
      attributes['episodes'] = None
    except:
      if not self.session.suppress_parse_exceptions:
        raise
    
    return attributes

  def parse_entry(self, soup):
    anime,entry_info = super(AnimeList, self).parse_entry(soup)

    try:
      entry_info[u'episodes_watched'] = int(soup.find('my_watched_episodes').text)
    except ValueError:
      entry_info[u'episodes_watched'] = 0
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      entry_info[u'rewatching'] = bool(soup.find('my_rewatching').text)
    except ValueError:
      entry_info[u'rewatching'] = False
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      entry_info[u'episodes_rewatched'] = int(soup.find('my_rewatching_ep').text)
    except ValueError:
      entry_info[u'episodes_rewatched'] = 0
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    return anime,entry_info

  def parse_section_columns(self, columns):
    column_names = super(AnimeList, self).parse_section_columns(columns)
    for i,column in enumerate(columns):
      if u'Type' in column.text:
        column_names[u'type'] = i
      elif u'Progress' in column.text:
        column_names[u'progress'] = i
      elif u'Tags' in column.text:
        column_names[u'tags'] = i
      elif u'Started' in column.text:
        column_names[u'started'] = i
      elif u'Finished' in column.text:
        column_names[u'finished'] = i
    return column_names