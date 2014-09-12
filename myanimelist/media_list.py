#!/usr/bin/python
# -*- coding: utf-8 -*-

import abc
import bs4
import collections
import decimal
import re
import urllib

import utilities
from base import Base, Error, loadable

class MalformedMediaListPageError(Error):
  def __init__(self, username, html, message=None):
    super(MalformedMediaListPageError, self).__init__(message=message)
    if isinstance(username, unicode):
      self.username = username
    else:
      self.username = str(username).decode(u'utf-8')
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedMediaListPageError, self).__str__(),
      "Username: " + unicode(self.username),
      "HTML: " + self.html
    ]).encode(u'utf-8')

class InvalidMediaListError(Error):
  def __init__(self, username, message=None):
    super(InvalidMediaListError, self).__init__(message=message)
    if isinstance(username, unicode):
      self.username = username
    else:
      self.username = str(username).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(InvalidMediaListError, self).__str__(),
      "Username: " + unicode(self.username)
    ])

class MediaList(Base):
  __metaclass__ = abc.ABCMeta

  __id_attribute = "username"
  def __init__(self, session, user_name):
    super(MediaList, self).__init__(session)
    self.username = user_name
    if not isinstance(self.username, unicode) or len(self.username) < 4:
      raise InvalidMediaListError(self.username)
    self._list = None
    self._stats = None

  # subclasses must define a list type, a list verb ala "watch", "read", etc, and a parser for the media list DOM.
  @abc.abstractproperty
  def type(self):
    pass

  @abc.abstractproperty
  def verb(self):
    pass

  def load_large_list(self):
    """
      Loads each section of the media list separately.
      This is necessary for users who have large media lists,
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

  def parse_section_row(self, soup, status, column_names):
    """
      Given:
        soup: a bs4 element containing the current media list's row
        status: the section that this row belongs under
      Return a dict of this row's parseable attributes.
    """
    cols = soup.find_all(u'td')
    entry_info = {u'status': status}
    try:
      entry_info[u'score'] = int(cols[column_names['score']].text)
    except ValueError:
      entry_info[u'score'] = None
    return entry_info

  def parse_section_columns(self, columns):
    """
      Given:
        columns: a list of bs4 elements containing a media list section's header columns
      Return a dict of table column names to column indices, for use in parse_section_row.
    """
    column_names = {}
    for i,column in enumerate(columns):
      if column.text == u'#':
        column_names['#'] = i
      elif u'Title' in column.text:
        column_names['title'] = i
      elif u'Score' in column.text:
        column_names['score'] = i
    return column_names    

  def parse(self, html, is_section=False):
    list_info = {}
    html = utilities.fix_bad_html(html)
    list_page = bs4.BeautifulSoup(html)

    bad_username_elt = list_page.find('div', {'class': 'badresult'})
    if bad_username_elt:
      raise InvalidMediaListError(self.username, message=u"Invalid username when fetching " + self.type + " list")

    if is_section:
      stats_elt = list_page.find('td', {'class': 'category_totals'})
    else:
      stats_elt = list_page.find('div', {'id': 'grand_totals'})

    if not stats_elt:
      if u'disabled for lists' in list_page.text:
        return self.load_large_list()
      else:
        raise MalformedMediaListPageError(self.username, html, message="Could not find section headers in " + self.type + " list")

    list_info[u'stats'] = {}
    stats_rows = stats_elt.text.strip().split('\n')
    for row in stats_rows:
      row = re.match(r'(?P<category>[A-Za-z\ \.]+): ?(?P<value>[0-9\,\-\.]*)?', row.lstrip()).groupdict()
      row['value'] = row['value'].replace(',', '')
      if '.' not in row['value']:
        try:
          row['value'] = int(row['value'])
        except ValueError:
          row['value'] = 0
      else:
        try:
          row['value'] = decimal.Decimal(row['value'])
        except ValueError:
          row['value'] = 0.0
      list_info[u'stats'][row['category']] = row['value']

    list_info[u'list'] = {}
    headers = list_page.find_all(u'div', {'class': 'header_title'})
    headers = map(lambda x: x.parent.parent.parent, headers)
    for header in headers:
      table_header = header.findNext(u'table')
      table_header_cols = table_header.find_all(u'td', {'class': 'table_header'})
      column_names = self.parse_section_columns(table_header_cols)

      curr_row = table_header.findNext(u'table')
      while not curr_row.find(u'td', {'class': 'category_totals'}):
        cols = curr_row.find_all(u'td')
        media_link = cols[column_names['title']].find(u'a', recursive=False)
        link_parts = media_link.get(u'href').split(u'/')
        # of the form: /anime|manga/15061/Aikatsu!
        media = getattr(self.session, self.type)(int(link_parts[2])).set({'title': media_link.text})
        list_info[u'list'][media] = self.parse_section_row(curr_row, header.text.strip(), column_names)
        curr_row = curr_row.findNext(u'table')
    return list_info
  def load(self):
    media_list = self.session.session.get(u'http://myanimelist.net/' + self.type + u'list/' + utilities.urlencode(self.username)).text
    self.set(self.parse(media_list))
    return self

  @property
  @loadable(u'load')
  def list(self):
    return self._list

  @property
  @loadable(u'load')
  def stats(self):
    return self._stats

  def section(self, status):
    return {k: self.list[k] for k in self.list if self.list[k][u'status'] == status}