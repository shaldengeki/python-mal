#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import decimal
import re

import utilities
from base import Base, Error, loadable
import media

class MalformedMangaPageError(media.MalformedMediaPageError):
  pass

class InvalidMangaError(media.InvalidMediaError):
  pass

class Manga(media.Media):
  status_terms = [
    u'Unknown',
    u'Publishing',
    u'Finished',
    u'Not yet published'
  ]

  @staticmethod
  def newest(session):
    '''
      Returns the newest manga on MAL.
    '''
    p = session.session.get(u'http://myanimelist.net/manga.php?o=9&c[]=a&c[]=d&cv=2&w=1').text
    soup = bs4.BeautifulSoup(p)
    latest_entry = soup.find(u"div", {u"class": u"hoverinfo"})
    if not latest_entry:
      raise MalformedMangaPageError(0, p, u"No manga entries found on recently-added page")
    latest_id = int(latest_entry[u'rel'][1:])
    return Manga(session, latest_id)

  def __init__(self, session, manga_id):
    super(Manga, self).__init__(session)
    self.id = manga_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidMangaError(self.id)
    self._title = None

  def __init__(self, session, manga_id):
    super(Manga, self).__init__(session)
    self.id = manga_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidMangaError(self.id)
    self._title = None
    self._picture = None
    self._alternative_titles = None
    self._type = None
    self._volumes = None
    self._chapters = None
    self._status = None
    self._published = None
    self._genres = None
    self._authors = None
    self._serialization = None
    self._score = None
    self._rank = None
    self._popularity = None
    self._members = None
    self._favorites = None
    self._popular_tags = None
    self._synopsis = None
    self._related = None
    self._score_stats = None
    self._status_stats = None
    self._characters = None

  def parse_sidebar(self, html):
    """
      Given a MAL manga page's HTML, returns a dict with this manga's attributes found on the sidebar.
    """
    manga_page = bs4.BeautifulSoup(html)

    # if MAL says the series doesn't exist, raise an InvalidMangaError.
    error_tag = manga_page.find(u'div', {'class': 'badresult'})
    if error_tag:
        raise InvalidMangaError(self.id)

    title_tag = manga_page.find(u'div', {'id': 'contentWrapper'}).find(u'h1')
    if not title_tag.find(u'div'):
      # otherwise, raise a MalformedMangaPageError.
      raise MalformedMangaPageError(self.id, html, message="Could not find title div")

    # otherwise, begin parsing.
    manga_info = super(Manga, self).parse_sidebar(html)

    info_panel_first = manga_page.find(u'div', {'id': 'content'}).find(u'table').find(u'td')

    volumes_tag = info_panel_first.find(text=u'Volumes:').parent.parent
    utilities.extract_tags(volumes_tag.find_all(u'span', {'class': 'dark_text'}))
    manga_info[u'volumes'] = int(volumes_tag.text.strip()) if volumes_tag.text.strip() != 'Unknown' else None

    chapters_tag = info_panel_first.find(text=u'Chapters:').parent.parent
    utilities.extract_tags(chapters_tag.find_all(u'span', {'class': 'dark_text'}))
    manga_info[u'chapters'] = int(chapters_tag.text.strip()) if chapters_tag.text.strip() != 'Unknown' else None

    published_tag = info_panel_first.find(text=u'Published:').parent.parent
    utilities.extract_tags(published_tag.find_all(u'span', {'class': 'dark_text'}))
    published_parts = published_tag.text.strip().split(u' to ')
    if len(published_parts) == 1:
      # this published once.
      try:
        published_date = utilities.parse_profile_date(published_parts[0])
      except ValueError:
        raise MalformedMangaPageError(self.id, published_parts[0], message="Could not parse single publish date")
      manga_info[u'published'] = (published_date,)
    else:
      # two publishing dates.
      try:
        publish_start = utilities.parse_profile_date(published_parts[0])
      except ValueError:
        raise MalformedMangaPageError(self.id, published_parts[0], message="Could not parse first of two publish dates")
      if published_parts == u'?':
        # this is still publishing.
        publish_end = None
      else:
        try:
          publish_end = utilities.parse_profile_date(published_parts[1])
        except ValueError:
          raise MalformedMangaPageError(self.id, published_parts[1], message="Could not parse second of two publish dates")
      manga_info[u'published'] = (publish_start, publish_end)

    authors_tag = info_panel_first.find(text=u'Authors:').parent.parent
    utilities.extract_tags(authors_tag.find_all(u'span', {'class': 'dark_text'}))
    manga_info[u'authors'] = {}
    for author_link in authors_tag.find_all('a'):
      link_parts = author_link.get('href').split('/')
      # of the form /people/1867/Naoki_Urasawa
      person = self.session.person(int(link_parts[2])).set({'name': author_link.text})
      role = author_link.nextSibling.replace(' (', '').replace(')', '')
      manga_info[u'authors'][person] = role

    serialization_tag = info_panel_first.find(text=u'Serialization:').parent.parent
    publication_link = serialization_tag.find('a')
    manga_info[u'serialization'] = None
    if publication_link:
      link_parts = publication_link.get('href').split('mid=')
      # of the form /manga.php?mid=1
      manga_info[u'serialization'] = self.session.publication(int(link_parts[1])).set({'name': publication_link.text})

    return manga_info
  def parse(self, html):
    """
      Given a MAL anime page's HTML, returns a dict with this anime's attributes.
    """
    manga_info = self.parse_sidebar(html)
    manga_page = bs4.BeautifulSoup(html)

    synopsis_elt = manga_page.find(u'h2', text=u'Synopsis').parent
    utilities.extract_tags(synopsis_elt.find_all(u'h2'))
    manga_info[u'synopsis'] = synopsis_elt.text.strip()

    related_title = manga_page.find(u'h2', text=u'Related Manga')
    if related_title:
      related_elt = related_title.parent
      utilities.extract_tags(related_elt.find_all(u'h2'))
      related = {}
      for link in related_elt.find_all(u'a'):
        href = link.get(u'href').replace(u'http://myanimelist.net', '')
        if not re.match(r'/(anime|manga)', href):
          break
        curr_elt = link.previous_sibling
        if curr_elt is None:
          # we've reached the end of the list.
          break
        related_type = None
        while True:
          if not curr_elt:
            raise MalformedMangaPageError(self.id, related_elt, message="Prematurely reached end of related manga listing")
          if isinstance(curr_elt, bs4.NavigableString):
            type_match = re.match(u'(?P<type>[a-zA-Z\ \-]+):', curr_elt)
            if type_match:
              related_type = type_match.group(u'type')
              break
          curr_elt = curr_elt.previous_sibling
        # parse link: may be manga or anime.
        href_parts = href.split(u'/')
        title = link.text

        # sometimes links on MAL are broken, of the form /manga//
        if href_parts[2] == '':
          continue
        obj_id = int(href_parts[2])
        non_title_parts = href_parts[:3]
        if 'manga' in non_title_parts:
          new_obj = self.session.manga(obj_id).set({'title': title})
        elif 'anime' in non_title_parts:
          new_obj = self.session.anime(obj_id).set({'title': title})
        else:
          raise MalformedMangaPageError(self.id, link, message="Related thing is of unknown type")
        if related_type not in related:
          related[related_type] = [new_obj]
        else:
          related[related_type].append(new_obj)
      manga_info[u'related'] = related
    else:
      manga_info[u'related'] = None
    return manga_info

  def parse_characters(self, html):
    """
      Given a MAL manga's character page HTML, return a dict with this manga's character attributes.
    """
    html = utilities.fix_bad_html(html)
    manga_info = self.parse_sidebar(html)
    character_page = bs4.BeautifulSoup(html)
    character_title = filter(lambda x: 'Characters' in x.text, character_page.find_all(u'h2'))
    manga_info[u'characters'] = {}
    if character_title:
      character_title = character_title[0]
      curr_elt = character_title.find_next_sibling(u'table')
      while curr_elt:
        curr_row = curr_elt.find(u'tr')
        # character in second col.
        (_, character_col) = curr_row.find_all(u'td', recursive=False)
        character_link = character_col.find(u'a')
        character_name = ' '.join(reversed(character_link.text.split(u', ')))
        link_parts = character_link.get(u'href').split(u'/')
        # of the form /character/7373/Holo
        character = self.session.character(int(link_parts[2])).set({'name': character_name})
        role = character_col.find(u'small').text
        manga_info[u'characters'][character] = role
        curr_elt = curr_elt.find_next_sibling(u'table')
    return manga_info

  def parse_stats(self, html):
    """
      Given a MAL manga stats page's HTML, returns a dict with this manga's attributes.
    """
    manga_info = self.parse_sidebar(html)
    manga_page = bs4.BeautifulSoup(html)

    status_stats = {
      'watching': 0,
      'completed': 0,
      'on_hold': 0,
      'dropped': 0,
      'plan_to_watch': 0
    }
    watching_elt = manga_page.find(u'span', {'class': 'dark_text'}, text="Watching:")
    if watching_elt:
      status_stats[u'watching'] = int(watching_elt.nextSibling.strip().replace(u',', ''))

    completed_elt = manga_page.find(u'span', {'class': 'dark_text'}, text="Completed:")
    if completed_elt:
      status_stats[u'completed'] = int(completed_elt.nextSibling.strip().replace(u',', ''))

    on_hold_elt = manga_page.find(u'span', {'class': 'dark_text'}, text="On-Hold:")
    if on_hold_elt:
      status_stats[u'on_hold'] = int(on_hold_elt.nextSibling.strip().replace(u',', ''))

    dropped_elt = manga_page.find(u'span', {'class': 'dark_text'}, text="Dropped:")
    if dropped_elt:
      status_stats[u'dropped'] = int(dropped_elt.nextSibling.strip().replace(u',', ''))

    plan_to_watch_elt = manga_page.find(u'span', {'class': 'dark_text'}, text="Plan to Watch:")
    if plan_to_watch_elt:
      status_stats[u'plan_to_watch'] = int(plan_to_watch_elt.nextSibling.strip().replace(u',', ''))
    manga_info[u'status_stats'] = status_stats

    score_stats_header = manga_page.find(u'h2', text='Score Stats')
    score_stats = {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
      5: 0,
      6: 0,
      7: 0,
      8: 0,
      9: 0,
      10: 0
    }
    if score_stats_header:
      score_stats_table = score_stats_header.find_next_sibling(u'table')
      if score_stats_table:
        score_stats = {}
        score_rows = score_stats_table.find_all(u'tr')
        for i in xrange(len(score_rows)):
          score_value = int(score_rows[i].find(u'td').text)
          score_stats[score_value] = int(score_rows[i].find(u'small').text.replace(u'(u', '').replace(u' votes)', ''))
    manga_info[u'score_stats'] = score_stats

    return manga_info

  def load(self):
    """
      Fetches the MAL manga page and sets the current manga's attributes.
    """
    manga_page = self.session.session.get(u'http://myanimelist.net/manga/' + str(self.id)).text
    self.set(self.parse(manga_page))
    return self

  def load_characters(self):
    """
      Fetches the MAL manga's characters page and sets the current manga's attributes.
    """
    characters_page = self.session.session.get(u'http://myanimelist.net/manga/' + str(self.id) + u'/' + utilities.urlencode(self.title) + u'/characters').text
    self.set(self.parse_characters(characters_page))
    return self
    
  def load_stats(self):
    """
      Fetches the MAL manga stats page and sets the current manga's attributes.
    """
    stats_page = self.session.session.get(u'http://myanimelist.net/manga/' + str(self.id) + u'/' + utilities.urlencode(self.title) + u'/stats').text
    self.set(self.parse_stats(stats_page))
    return self

  @property
  @loadable(u'load')
  def title(self):
    return self._title

  @property
  @loadable(u'load')
  def picture(self):
    return self._picture

  @property
  @loadable(u'load')
  def alternative_titles(self):
    return self._alternative_titles

  @property
  @loadable(u'load')
  def type(self):
    return self._type

  @property
  @loadable(u'load')
  def volumes(self):
    return self._volumes

  @property
  @loadable(u'load')
  def chapters(self):
    return self._chapters

  @property
  @loadable(u'load')
  def status(self):
    return self._status

  @property
  @loadable(u'load')
  def published(self):
    return self._published

  @property
  @loadable(u'load')
  def authors(self):
    return self._authors

  @property
  @loadable(u'load')
  def genres(self):
    return self._genres

  @property
  @loadable(u'load')
  def serialization(self):
    return self._serialization

  @property
  @loadable(u'load')
  def score(self):
    return self._score

  @property
  @loadable(u'load')
  def rank(self):
    return self._rank

  @property
  @loadable(u'load')
  def popularity(self):
    return self._popularity

  @property
  @loadable(u'load')
  def members(self):
    return self._members

  @property
  @loadable(u'load')
  def favorites(self):
    return self._favorites

  @property
  @loadable(u'load')
  def popular_tags(self):
    return self._popular_tags
  
  @property
  @loadable(u'load')
  def synopsis(self):
    return self._synopsis

  @property
  @loadable(u'load')
  def related(self):
    return self._related

  @property
  @loadable(u'load_characters')
  def characters(self):
    return self._characters

  @property
  @loadable(u'load_stats')
  def status_stats(self):
    return self._status_stats

  @property
  @loadable(u'load_stats')
  def score_stats(self):
    return self._score_stats