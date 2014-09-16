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

  def parse_entry_media_attributes(self, soup):
    attributes = super(MangaList, self).parse_entry_media_attributes(soup)

    try:
      attributes['chapters'] = int(soup.find('series_chapters').text)
    except ValueError:
      attributes['chapters'] = None
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      attributes['volumes'] = int(soup.find('series_volumes').text)
    except ValueError:
      attributes['volumes'] = None
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    return attributes

  def parse_entry(self, soup):
    manga,entry_info = super(MangaList, self).parse_entry(soup)

    try:
      entry_info[u'chapters_read'] = int(soup.find('my_read_chapters').text)
    except ValueError:
      entry_info[u'chapters_read'] = 0
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      entry_info[u'volumes_read'] = int(soup.find('my_read_volumes').text)
    except ValueError:
      entry_info[u'volumes_read'] = 0
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      entry_info[u'rereading'] = bool(soup.find('my_rereadingg').text)
    except ValueError:
      entry_info[u'rereading'] = False
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      entry_info[u'chapters_reread'] = int(soup.find('my_rereading_chap').text)
    except ValueError:
      entry_info[u'chapters_reread'] = 0
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    return manga,entry_info
