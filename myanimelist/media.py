#!/usr/bin/python
# -*- coding: utf-8 -*-

import abc
import bs4
import decimal
import re

import utilities
from base import Base, Error

class MalformedMediaPageError(Error):
  def __init__(self, media_id, html, message=None):
    super(MalformedMediaPageError, self).__init__(message=message)
    self.media_id = int(media_id)
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedMediaPageError, self).__str__(),
      "ID: " + unicode(self.media_id),
      "HTML: " + self.html
    ]).encode(u'utf-8')

class InvalidMediaError(Error):
  def __init__(self, media_id, message=None):
    super(InvalidMediaError, self).__init__(message=message)
    self.media_id = media_id
  def __str__(self):
    return "\n".join([
      super(InvalidMediaError, self).__str__(),
      "ID: " + unicode(self.media_id)
    ])

class Media(Base):
  """
    Base class for all media resources on MAL.
  """
  __metaclass__ = abc.ABCMeta

  # a container of status terms for this media.
  # keys are status ints, values are statuses e.g. "Airing"
  @abc.abstractproperty
  def status_terms(self):
    pass

  def parse_sidebar(self, html):
    """
      Given a MAL media page's HTML, returns a dict with this media's attributes found on the sidebar.
    """
    media_info = {}
    media_page = bs4.BeautifulSoup(utilities.fix_bad_html(html))

    # if MAL says the series doesn't exist, raise an InvalidMediaError.
    error_tag = media_page.find(u'div', {'class': 'badresult'})
    if error_tag:
        raise InvalidMediaError(self.id)

    title_tag = media_page.find(u'div', {'id': 'contentWrapper'}).find(u'h1')
    if not title_tag.find(u'div'):
      # otherwise, raise a MalformedMediaPageError.
      raise MalformedMediaPageError(self.id, html, message="Could not find title div")

    utilities.extract_tags(title_tag.find_all())
    media_info[u'title'] = title_tag.text.strip()

    info_panel_first = media_page.find(u'div', {'id': 'content'}).find(u'table').find(u'td')

    picture_tag = info_panel_first.find(u'img')
    media_info[u'picture'] = picture_tag.get(u'src').decode('utf-8')

    # assemble alternative titles for this series.
    media_info[u'alternative_titles'] = {}
    alt_titles_header = info_panel_first.find(u'h2', text=u'Alternative Titles')
    if alt_titles_header:
      next_tag = alt_titles_header.find_next_sibling(u'div', {'class': 'spaceit_pad'})
      while True:
        if next_tag is None or not next_tag.find(u'span', {'class': 'dark_text'}):
          # not a language node, break.
          break
        # get language and remove the node.
        language = next_tag.find(u'span').text[:-1]
        utilities.extract_tags(next_tag.find_all(u'span', {'class': 'dark_text'}))
        names = next_tag.text.strip().split(u', ')
        media_info[u'alternative_titles'][language] = names
        next_tag = next_tag.find_next_sibling(u'div', {'class': 'spaceit_pad'})

    type_tag = info_panel_first.find(text=u'Type:').parent.parent
    utilities.extract_tags(type_tag.find_all(u'span', {'class': 'dark_text'}))
    media_info[u'type'] = type_tag.text.strip()

    status_tag = info_panel_first.find(text=u'Status:').parent.parent
    utilities.extract_tags(status_tag.find_all(u'span', {'class': 'dark_text'}))
    media_info[u'status'] = status_tag.text.strip()

    genres_tag = info_panel_first.find(text=u'Genres:').parent.parent
    utilities.extract_tags(genres_tag.find_all(u'span', {'class': 'dark_text'}))
    media_info[u'genres'] = []
    for genre_link in genres_tag.find_all('a'):
      link_parts = genre_link.get('href').split('[]=')
      # of the form /anime|manga.php?genre[]=1
      genre = self.session.genre(int(link_parts[1])).set({'name': genre_link.text})
      media_info[u'genres'].append(genre)

    # grab statistics for this media.
    score_tag = info_panel_first.find(text=u'Score:').parent.parent
    # get score and number of users.
    users_node = [x for x in score_tag.find_all(u'small') if u'scored by' in x.text][0]
    num_users = int(users_node.text.split(u'scored by ')[-1].split(u' users')[0])
    utilities.extract_tags(score_tag.find_all())
    media_info[u'score'] = (decimal.Decimal(score_tag.text.strip()), num_users)

    rank_tag = info_panel_first.find(text=u'Ranked:').parent.parent
    utilities.extract_tags(rank_tag.find_all())
    media_info[u'rank'] = int(rank_tag.text.strip()[1:].replace(u',', ''))

    popularity_tag = info_panel_first.find(text=u'Popularity:').parent.parent
    utilities.extract_tags(popularity_tag.find_all())
    media_info[u'popularity'] = int(popularity_tag.text.strip()[1:].replace(u',', ''))

    members_tag = info_panel_first.find(text=u'Members:').parent.parent
    utilities.extract_tags(members_tag.find_all())
    media_info[u'members'] = int(members_tag.text.strip().replace(u',', ''))

    favorites_tag = info_panel_first.find(text=u'Favorites:').parent.parent
    utilities.extract_tags(favorites_tag.find_all())
    media_info[u'favorites'] = int(favorites_tag.text.strip().replace(u',', ''))

    # get popular tags.
    tags_header = media_page.find(u'h2', text=u'Popular Tags')
    tags_tag = tags_header.find_next_sibling(u'span')
    media_info[u'popular_tags'] = {}
    for tag_link in tags_tag.find_all('a'):
      tag = self.session.tag(tag_link.text)
      num_people = int(re.match(r'(?P<people>[0-9]+) people', tag_link.get('title')).group('people'))
      media_info[u'popular_tags'][tag] = num_people

    return media_info

