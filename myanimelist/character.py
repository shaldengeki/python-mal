#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re
import urllib

import utilities
from base import Base, Error, loadable

class MalformedCharacterPageError(Error):
  def __init__(self, character_id, html, message=None):
    super(MalformedCharacterPageError, self).__init__(message=message)
    self.character_id = int(character_id)
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode('utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedCharacterPageError, self).__str__(),
      "Character ID: " + unicode(self.character_id),
      "HTML: " + self.html
    ]).encode('utf-8')

class InvalidCharacterError(Error):
  def __init__(self, character_id, message=None):
    super(InvalidCharacterError, self).__init__(message=message)
    self.character_id = character_id
  def __str__(self):
    return "\n".join([
      super(InvalidCharacterError, self).__str__(),
      "Character ID: " + unicode(self.character_id)
    ])

class Character(Base):
  def __repr__(self):
    return u"<Character ID: " + unicode(self.id) + u">"
  def __hash__(self):
    return hash(self.id)
  def __eq__(self, character):
    return isinstance(character, Character) and self.id == character.id
  def __ne__(self, character):
    return not self.__eq__(character)
  def __init__(self, session, character_id):
    super(Character, self).__init__(session)
    self.id = character_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidCharacterError(self.id)
    self._name = None
    self._full_name = None
    self._name_jpn = None
    self._description = None
    self._voice_actors = None
    self._animeography = None
    self._mangaography = None
    self._num_favorites = None
    self._favorites = None
    self._picture = None
    self._pictures = None
    self._clubs = None

  def parse_sidebar(self, html):
    """
      Given a MAL character page's HTML, returns a dict with this character's attributes found on the sidebar.
    """
    character_info = {}
    character_page = bs4.BeautifulSoup(html)
    error_tag = character_page.find('div', {'class': 'badresult'})
    if error_tag:
      # MAL says the character does not exist.
      raise InvalidCharacterError(self.id)
    full_name_tag = character_page.find('div', {'id': 'contentWrapper'}).find('h1')
    if not full_name_tag:
      # Page is malformed.
      raise MalformedCharacterPageError(self.id, html, message="Could not find title div")
    character_info['full_name'] = full_name_tag.text.strip()

    info_panel_first = character_page.find('div', {'id': 'content'}).find('table').find('td')

    picture_tag = info_panel_first.find('img')
    character_info['picture'] = picture_tag.get('src')

    # assemble animeography for this character.
    character_info['animeography'] = {}
    animeography_header = info_panel_first.find('div', text=u'Animeography')
    if animeography_header:
      animeography_table = animeography_header.find_next_sibling('table')
      for row in animeography_table.find_all('tr'):
        # second column has anime info.
        info_col = row.find_all('td')[1]
        anime_link = info_col.find('a')
        link_parts = anime_link.get('href').split('/')
        # of the form: /anime/1/Cowboy_Bebop
        anime = self.session.anime(int(link_parts[2])).set({'title': anime_link.text})
        role = info_col.find('small').text
        character_info['animeography'][anime] = role

    # assemble mangaography for this character.
    character_info['mangaography'] = {}
    mangaography_header = info_panel_first.find('div', text=u'Mangaography')
    if mangaography_header:
      mangaography_table = mangaography_header.find_next_sibling('table')
      for row in mangaography_table.find_all('tr'):
        # second column has manga info.
        info_col = row.find_all('td')[1]
        manga_link = info_col.find('a')
        link_parts = manga_link.get('href').split('/')
        # of the form: /manga/1/Cowboy_Bebop
        manga = self.session.manga(int(link_parts[2])).set({'title': manga_link.text})
        role = info_col.find('small').text
        character_info['mangaography'][manga] = role

    num_favorites_node = info_panel_first.find(text=re.compile(u'Member Favorites: '))
    character_info['num_favorites'] = int(num_favorites_node.strip().split(': ')[1])

    return character_info

  def parse(self, html):
    """
      Given a MAL character page's HTML, returns a dict with this character's attributes.
    """
    character_info = self.parse_sidebar(html)
    character_page = bs4.BeautifulSoup(html)

    second_col = character_page.find('div', {'id': 'content'}).find('table').find('tr').find_all('td', recursive=False)[1]
    name_elt = second_col.find('div', {'class': 'normal_header'})

    name_jpn_node = name_elt.find('small')
    if name_jpn_node:
      character_info['name_jpn'] = name_jpn_node.text[1:-1]
    else:
      character_info['name_jpn'] = None
    name_elt.find('span').extract()
    character_info['name'] = name_elt.text.rstrip()

    description_elts = []
    curr_elt = name_elt.nextSibling
    while True:
      if curr_elt.name not in [None, u'br']:
        break
      description_elts.append(unicode(curr_elt))
      curr_elt = curr_elt.nextSibling
    character_info['description'] = ''.join(description_elts)

    character_info['voice_actors'] = {}
    voice_actors_header = second_col.find('div', text=u'Voice Actors')
    if voice_actors_header:
      voice_actors_table = voice_actors_header.find_next_sibling('table')
      for row in voice_actors_table.find_all('tr'):
        # second column has va info.
        info_col = row.find_all('td')[1]
        voice_actor_link = info_col.find('a')
        name = ' '.join(reversed(voice_actor_link.text.split(', ')))
        link_parts = voice_actor_link.get('href').split('/')
        # of the form: /people/82/Romi_Park
        person = self.session.person(int(link_parts[2])).set({'name': name})
        language = info_col.find('small').text
        character_info['voice_actors'][person] = language
    return character_info

    self._name = None
    self._full_name = None
    self._name_jpn = None
    self._description = None
    self._voice_actors = None
    self._animeography = None
    self._mangaography = None
    self._num_favorites = None
    self._favorites = None
    self._picture = None
    self._pictures = None
    self._clubs = None

  def parse_favorites(self, html):
    character_info = self.parse_sidebar(html)
    favorites_page = bs4.BeautifulSoup(html)
    second_col = favorites_page.find('div', {'id': 'content'}).find('table').find('tr').find_all('td', recursive=False)[1]
    character_info['favorites'] = []
    curr_elt = second_col.find('div', text=u'Users with Favorites').nextSibling
    while curr_elt is not None:
      if curr_elt.name == u'a':
        link_parts = curr_elt.get('href').split('/')
        # of the form /profile/shaldengeki
        character_info['favorites'].append(self.session.user(username=link_parts[2]))
      curr_elt = curr_elt.nextSibling

    return character_info

  def parse_pictures(self, html):
    character_info = self.parse_sidebar(html)
    picture_page = bs4.BeautifulSoup(html)
    second_col = picture_page.find('div', {'id': 'content'}).find('table').find('tr').find_all('td', recursive=False)[1]

    picture_table = second_col.find('table', recursive=False)
    character_info['pictures'] = []
    if picture_table:
      character_info['pictures'] = map(lambda img: img.get('src'), picture_table.find_all('img'))
    return character_info

  def parse_clubs(self, html):
    character_info = self.parse_sidebar(html)
    clubs_page = bs4.BeautifulSoup(html)
    second_col = clubs_page.find('div', {'id': 'content'}).find('table').find('tr').find_all('td', recursive=False)[1]

    clubs_header = second_col.find('div', text=u'Related Clubs')
    character_info['clubs'] = []
    if clubs_header:
      curr_elt = clubs_header.nextSibling
      while curr_elt is not None:
        if curr_elt.name == u'div':
          link = curr_elt.find('a')
          club_id = int(re.match(r'/clubs\.php\?cid=(?P<id>[0-9]+)', link.get('href')).group('id'))
          num_members = int(re.match(r'(?P<num>[0-9]+) members', curr_elt.find('small').text).group('num'))
          character_info['clubs'].append(self.session.club(club_id).set({'name': link.text, 'num_members': num_members}))
        curr_elt = curr_elt.nextSibling
    return character_info

  def load(self):
    """
      Fetches the MAL character page and sets the current character's attributes.
    """
    character = self.session.session.get('http://myanimelist.net/character/' + str(self.id)).text
    self.set(self.parse(character))
    return self

  def load_favorites(self):
    """
      Fetches the MAL character favorites page and sets the current character's attributes.
    """
    print 'http://myanimelist.net/character/' + str(self.id) + '/favorites'
    urlencoded_name = urllib.urlencode({'': self.name.encode('utf-8').replace(' ', '_')})[1:].replace('%2F', '/')
    character = self.session.session.get('http://myanimelist.net/character/' + str(self.id) + '/' + urlencoded_name + '/favorites').text
    self.set(self.parse_favorites(character))
    return self

  def load_pictures(self):
    """
      Fetches the MAL character pictures page and sets the current character's attributes.
    """
    urlencoded_name = urllib.urlencode({'': self.name.encode('utf-8').replace(' ', '_')})[1:].replace('%2F', '/')
    character = self.session.session.get('http://myanimelist.net/character/' + str(self.id) + '/' + urlencoded_name + '/pictures').text
    self.set(self.parse_pictures(character))
    return self

  def load_clubs(self):
    """
      Fetches the MAL character clubs page and sets the current character's attributes.
    """
    urlencoded_name = urllib.urlencode({'': self.name.encode('utf-8').replace(' ', '_')})[1:].replace('%2F', '/')
    character = self.session.session.get('http://myanimelist.net/character/' + str(self.id) + '/' + urlencoded_name + '/clubs').text
    self.set(self.parse_clubs(character))
    return self

  @property
  @loadable('load')
  def name(self):
    return self._name

  @property
  @loadable('load')
  def full_name(self):
    return self._full_name

  @property
  @loadable('load')
  def name_jpn(self):
    return self._name_jpn

  @property
  @loadable('load')
  def description(self):
    return self._description

  @property
  @loadable('load')
  def voice_actors(self):
    return self._voice_actors

  @property
  @loadable('load')
  def animeography(self):
    return self._animeography

  @property
  @loadable('load')
  def mangaography(self):
    return self._mangaography

  @property
  @loadable('load')
  def num_favorites(self):
    return self._num_favorites

  @property
  @loadable('load_favorites')
  def favorites(self):
    return self._favorites

  @property
  @loadable('load')
  def picture(self):
    return self._picture

  @property
  @loadable('load_pictures')
  def pictures(self):
    return self._pictures

  @property
  @loadable('load_clubs')
  def clubs(self):
    return self._clubs

