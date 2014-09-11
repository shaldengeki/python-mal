#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedAnimePageError(Error):
  def __init__(self, anime_id, html, message=None):
    super(MalformedAnimePageError, self).__init__(message=message)
    self.anime_id = int(anime_id)
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode('utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedAnimePageError, self).__str__(),
      "Anime ID: " + unicode(self.anime_id),
      "HTML: " + self.html
    ]).encode('utf-8')

class InvalidAnimeError(Error):
  def __init__(self, anime_id, message=None):
    super(InvalidAnimeError, self).__init__(message=message)
    self.anime_id = anime_id
  def __str__(self):
    return "\n".join([
      super(InvalidAnimeError, self).__str__(),
      "Anime ID: " + unicode(self.anime_id)
    ])

class Anime(Base):
  @staticmethod
  def newest(session):
    '''
      Returns the newest anime on MAL.
    '''
    p = session.session.get('http://myanimelist.net/anime.php?o=9&c[]=a&c[]=d&cv=2&w=1').text
    soup = bs4.BeautifulSoup(p)
    latest_entry = soup.find("div", {"class": "hoverinfo"})
    if not latest_entry:
      raise MalformedAnimePageError(0, p, "No anime entries found on recently-added page")
    latest_id = int(latest_entry['rel'][1:])
    return Anime(session, latest_id)

  def __init__(self, session, anime_id):
    super(Anime, self).__init__(session)
    self.id = anime_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidAnimeError(self.id)
    self._title = None
    self._picture = None
    self._alternative_titles = None
    self._type = None
    self._episodes = None
    self._status = None
    self._aired = None
    self._producers = None
    self._genres = None
    self._duration = None
    self._rating = None
    self._weighted_score = None
    self._rank = None
    self._popularity = None
    self._members = None
    self._favorites = None
    self._tags = None
    self._synopsis = None
    self._related = None
    self._score_stats = None
    self._status_stats = None
    self._characters = None
    self._voice_actors = None
    self._staff = None

  def parse_sidebar(self, html):
    """
      Given a MAL anime page's HTML, returns a dict with this anime's attributes found on the sidebar.
    """
    anime_info = {}
    anime_page = bs4.BeautifulSoup(html)

    # if MAL says the series doesn't exist, raise an InvalidAnimeError.
    error_tag = anime_page.find('div', {'class': 'badresult'})
    if error_tag:
        raise InvalidAnimeError(self.id)

    title_tag = anime_page.find('div', {'id': 'contentWrapper'}).find('h1')
    if not title_tag.find('div'):
      # otherwise, raise a MalformedAnimePageError.
      raise MalformedAnimePageError(self.id, html, message="Could not find title div")

    utilities.extract_tags(title_tag.find_all())
    anime_info['title'] = title_tag.text.strip()

    info_panel_first = anime_page.find('div', {'id': 'content'}).find('table').find('td')

    picture_tag = info_panel_first.find('img')
    anime_info['picture'] = picture_tag.get('src')

    # assemble alternative titles for this series.
    anime_info['alternative_titles'] = {}
    alt_titles_header = info_panel_first.find('h2', text=u'Alternative Titles')
    if alt_titles_header:
      next_tag = alt_titles_header.find_next_sibling('div', {'class': 'spaceit_pad'})
      while True:
        if next_tag is None or not next_tag.find('span', {'class': 'dark_text'}):
          # not a language node, break.
          break
        # get language and remove the node.
        language = next_tag.find('span').text[:-1]
        utilities.extract_tags(next_tag.find_all('span', {'class': 'dark_text'}))
        names = next_tag.text.strip().split(', ')
        anime_info['alternative_titles'][language] = names
        next_tag = next_tag.find_next_sibling('div', {'class': 'spaceit_pad'})

    info_header = info_panel_first.find('h2', text=u'Information')

    type_tag = info_header.find_next_sibling('div')
    utilities.extract_tags(type_tag.find_all('span', {'class': 'dark_text'}))
    anime_info['type'] = type_tag.text.strip()

    episode_tag = type_tag.find_next_sibling('div')
    utilities.extract_tags(episode_tag.find_all('span', {'class': 'dark_text'}))
    anime_info['episodes'] = int(episode_tag.text.strip()) if episode_tag.text.strip() != 'Unknown' else 0

    status_tag = episode_tag.find_next_sibling('div')
    utilities.extract_tags(status_tag.find_all('span', {'class': 'dark_text'}))
    anime_info['status'] = status_tag.text.strip()

    aired_tag = status_tag.find_next_sibling('div')
    utilities.extract_tags(aired_tag.find_all('span', {'class': 'dark_text'}))
    aired_parts = aired_tag.text.strip().split(' to ')
    if len(aired_parts) == 1:
      # this aired once.
      try:
        aired_date = utilities.parse_profile_date(aired_parts[0])
      except ValueError:
        raise MalformedAnimePageError(self.id, aired_parts[0], message="Could not parse single air date")
      anime_info['aired'] = (aired_date,)
    else:
      # two airing dates.
      try:
        air_start = utilities.parse_profile_date(aired_parts[0])
      except ValueError:
        raise MalformedAnimePageError(self.id, aired_parts[0], message="Could not parse first of two air dates")
      try:
        air_end = utilities.parse_profile_date(aired_parts[1])
      except ValueError:
        raise MalformedAnimePageError(self.id, aired_parts[1], message="Could not parse second of two air dates")
      anime_info['aired'] = (air_start, air_end)

    producers_tag = aired_tag.find_next_sibling('div')
    utilities.extract_tags(producers_tag.find_all('span', {'class': 'dark_text'}))
    utilities.extract_tags(producers_tag.find_all('sup'))
    anime_info['producers'] = producers_tag.text.strip().split(', ')

    genres_tag = producers_tag.find_next_sibling('div')
    utilities.extract_tags(genres_tag.find_all('span', {'class': 'dark_text'}))
    anime_info['genres'] = genres_tag.text.strip().split(', ')

    duration_tag = genres_tag.find_next_sibling('div')
    utilities.extract_tags(duration_tag.find_all('span', {'class': 'dark_text'}))
    anime_info['duration'] = duration_tag.text.strip()
    duration_parts = [part.strip() for part in anime_info['duration'].split('.')]
    duration_mins = 0
    for part in duration_parts:
      part_match = re.match('(?P<num>[0-9]+)', part)
      if not part_match:
        continue
      part_volume = int(part_match.group('num'))
      if part.endswith('hr'):
        duration_mins += part_volume * 60
      elif part.endswith('min'):
        duration_mins += part_volume
    anime_info['duration'] = duration_mins

    rating_tag = duration_tag.find_next_sibling('div')
    utilities.extract_tags(rating_tag.find_all('span', {'class': 'dark_text'}))
    anime_info['rating'] = rating_tag.text.strip()

    # grab statistics for this anime.
    stats_header = anime_page.find('h2', text=u'Statistics')

    weighted_score_tag = stats_header.find_next_sibling('div')
    # get weighted score and number of users.
    users_node = [x for x in weighted_score_tag.find_all('small') if u'scored by' in x.text][0]
    weighted_users = int(users_node.text.split(u'scored by ')[-1].split(u' users')[0])
    utilities.extract_tags(weighted_score_tag.find_all())
    anime_info['weighted_score'] = (float(weighted_score_tag.text.strip()), weighted_users)

    rank_tag = weighted_score_tag.find_next_sibling('div')
    utilities.extract_tags(rank_tag.find_all())
    anime_info['rank'] = int(rank_tag.text.strip()[1:].replace(',', '')) if rank_tag.text.strip()[1:].replace(',', '') != 'Unknown' else 0

    popularity_tag = rank_tag.find_next_sibling('div')
    utilities.extract_tags(popularity_tag.find_all())
    anime_info['popularity'] = int(popularity_tag.text.strip()[1:].replace(',', '')) if popularity_tag.text.strip()[1:].replace(',', '') != 'Unknown' else 0

    members_tag = popularity_tag.find_next_sibling('div')
    utilities.extract_tags(members_tag.find_all())
    anime_info['members'] = int(members_tag.text.strip().replace(',', '')) if members_tag.text.strip().replace(',', '') != 'Unknown' else 0

    favorites_tag = members_tag.find_next_sibling('div')
    utilities.extract_tags(favorites_tag.find_all())
    anime_info['favorites'] = int(favorites_tag.text.strip().replace(',', '')) if favorites_tag.text.strip().replace(',', '') != 'Unknown' else 0

    # get popular tags.
    tags_header = anime_page.find('h2', text=u'Popular Tags')
    tags_tag = tags_header.find_next_sibling('span')
    anime_info['tags'] = tags_tag.text.strip().split(' ')
    return anime_info    

  def parse(self, html):
    """
      Given a MAL anime page's HTML, returns a dict with this anime's attributes.
    """
    anime_info = self.parse_sidebar(html)
    anime_page = bs4.BeautifulSoup(html)

    synopsis_elt = anime_page.find('h2', text=u'Synopsis').parent
    utilities.extract_tags(synopsis_elt.find_all('h2'))
    anime_info['synopsis'] = synopsis_elt.text.strip()

    related_title = anime_page.find('h2', text=u'Related Anime')
    if related_title:
      related_elt = related_title.parent
      utilities.extract_tags(related_elt.find_all('h2'))
      related = {}
      for link in related_elt.find_all('a'):
        href = link.get('href').replace('http://myanimelist.net', '')
        if not re.match(r'/(anime|manga)', href):
          break
        curr_elt = link.previous_sibling
        if curr_elt is None:
          # we've reached the end of the list.
          break
        related_type = None
        while True:
          if not curr_elt:
            raise MalformedAnimePageError(self.id, related_elt, message="Prematurely reached end of related anime listing")
          if isinstance(curr_elt, bs4.NavigableString):
            type_match = re.match('(?P<type>[a-zA-Z\ \-]+):', curr_elt)
            if type_match:
              related_type = type_match.group('type')
              break
          curr_elt = curr_elt.previous_sibling
        # parse link: may be manga or anime.
        href_parts = href.split('/')
        title = link.text

        # sometimes links on MAL are broken, of the form /anime//
        if href_parts[2] == '':
          continue
        obj_id = int(href_parts[2])
        non_title_parts = href_parts[:3]
        if 'manga' in non_title_parts:
          new_obj = self.session.manga(obj_id).set({'title': title})
        elif 'anime' in non_title_parts:
          new_obj = self.session.anime(obj_id).set({'title': title})
        else:
          raise MalformedAnimePageError(self.id, link, message="Related thing is of unknown type")
        if related_type not in related:
          related[related_type] = [new_obj]
        else:
          related[related_type].append(new_obj)
      anime_info['related'] = related
    else:
      anime_info['related'] = None
    return anime_info

  def parse_characters(self, html):
    """
      Given a MAL anime's character page HTML, return a dict with this anime's character/staff/va attributes.
    """
    anime_info = self.parse_sidebar(html)
    character_page = bs4.BeautifulSoup(html)
    character_title = filter(lambda x: 'Characters & Voice Actors' in x.text, character_page.find_all('h2'))
    anime_info['characters'] = {}
    anime_info['voice_actors'] = {}
    if character_title:
      character_title = character_title[0]
      curr_elt = character_title.nextSibling
      while True:
        if curr_elt.name != u'table':
          break
        curr_row = curr_elt.find('tr')
        # character in second col, VAs in third.
        (_, character_col, va_col) = curr_row.find_all('td', recursive=False)

        character_link = character_col.find('a')
        character_name = ' '.join(reversed(character_link.text.split(', ')))
        link_parts = character_link.get('href').split('/')
        # of the form /character/7373/Holo
        character = self.session.character(int(link_parts[2])).set({'name': character_name})
        role = character_col.find('small').text
        character_entry = {'role': role, 'voice_actors': {}}

        va_table = va_col.find('table')
        if va_table:
          for row in va_table.find_all('tr'):
            va_info_cols = row.find_all('td')
            if not va_info_cols:
              # don't ask me why MAL has an extra blank table row i don't know!!!
              continue
            va_info_col = va_info_cols[0]
            va_link = va_info_col.find('a')
            if va_link:
              va_name = ' '.join(reversed(va_link.text.split(', ')))
              link_parts = va_link.get('href').split('/')
              # of the form /people/70/Ami_Koshimizu
              person = self.session.person(int(link_parts[2])).set({'name': va_name})
              language = va_info_col.find('small').text
              anime_info['voice_actors'][person] = {'role': role, 'character': character, 'language': language}
              character_entry['voice_actors'][person] = language
        anime_info['characters'][character] = character_entry
        curr_elt = curr_elt.nextSibling

    staff_title = filter(lambda x: 'Staff' in x.text, character_page.find_all('h2'))
    anime_info['staff'] = {}
    if staff_title:
      staff_title = staff_title[0]
      staff_table = staff_title.nextSibling.nextSibling
      for row in staff_table.find_all('tr'):
        # staff info in second col.
        info = row.find_all('td')[1]
        staff_link = info.find('a')
        staff_name = ' '.join(reversed(staff_link.text.split(', ')))
        link_parts = staff_link.get('href').split('/')
        # of the form /people/1870/Miyazaki_Hayao
        person = self.session.person(int(link_parts[2])).set({'name': staff_name})
        # staff role(s).
        anime_info['staff'][person] = set(info.find('small').text.split(', '))
    return anime_info

  def parse_stats(self, html):
    """
      Given a MAL anime stats page's HTML, returns a dict with this anime's attributes.
    """
    anime_info = self.parse_sidebar(html)
    anime_page = bs4.BeautifulSoup(html)

    status_stats = {
      'watching': 0,
      'completed': 0,
      'on_hold': 0,
      'dropped': 0,
      'plan_to_watch': 0
    }
    watching_elt = anime_page.find('span', {'class': 'dark_text'}, text="Watching:")
    if watching_elt:
      status_stats['watching'] = int(watching_elt.nextSibling.strip().replace(',', ''))

    completed_elt = anime_page.find('span', {'class': 'dark_text'}, text="Completed:")
    if completed_elt:
      status_stats['completed'] = int(completed_elt.nextSibling.strip().replace(',', ''))

    on_hold_elt = anime_page.find('span', {'class': 'dark_text'}, text="On-Hold:")
    if on_hold_elt:
      status_stats['on_hold'] = int(on_hold_elt.nextSibling.strip().replace(',', ''))

    dropped_elt = anime_page.find('span', {'class': 'dark_text'}, text="Dropped:")
    if dropped_elt:
      status_stats['dropped'] = int(dropped_elt.nextSibling.strip().replace(',', ''))

    plan_to_watch_elt = anime_page.find('span', {'class': 'dark_text'}, text="Plan to Watch:")
    if plan_to_watch_elt:
      status_stats['plan_to_watch'] = int(plan_to_watch_elt.nextSibling.strip().replace(',', ''))
    anime_info['status_stats'] = status_stats

    score_stats_header = anime_page.find('h2', text='Score Stats')
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
      score_stats_table = score_stats_header.find_next_sibling('table')
      if score_stats_table:
        score_stats = {}
        score_rows = score_stats_table.find_all('tr')
        for i in xrange(len(score_rows)):
          score_value = int(score_rows[i].find('td').text)
          score_stats[score_value] = int(score_rows[i].find('small').text.replace('(', '').replace(' votes)', ''))
    anime_info['score_stats'] = score_stats

    return anime_info

  def load(self):
    """
      Fetches the MAL anime page and sets the current anime's attributes.
    """
    anime_page = self.session.session.get('http://myanimelist.net/anime/' + str(self.id)).text
    self.set(self.parse(anime_page))
    return self

  def load_characters(self):
    """
      Fetches the MAL anime's characters page and sets the current anime's attributes.
    """
    characters_page = self.session.session.get('http://myanimelist.net/anime/' + str(self.id) + '/' + utilities.urlencode(self.title) + '/characters').text
    self.set(self.parse_characters(characters_page))
    return self
    
  def load_stats(self):
    """
      Fetches the MAL anime stats page and sets the current anime's attributes.
    """
    stats_page = self.session.session.get('http://myanimelist.net/anime/' + str(self.id) + '/' + utilities.urlencode(self.title) + '/stats').text
    self.set(self.parse_stats(stats_page))
    return self

  @property
  @loadable('load')
  def title(self):
    return self._title

  @property
  @loadable('load')
  def picture(self):
    return self._picture

  @property
  @loadable('load')
  def alternative_titles(self):
    return self._alternative_titles

  @property
  @loadable('load')
  def type(self):
    return self._type

  @property
  @loadable('load')
  def episodes(self):
    return self._episodes

  @property
  @loadable('load')
  def status(self):
    return self._status

  @property
  @loadable('load')
  def aired(self):
    return self._aired

  @property
  @loadable('load')
  def producers(self):
    return self._producers

  @property
  @loadable('load')
  def genres(self):
    return self._genres

  @property
  @loadable('load')
  def duration(self):
    return self._duration

  @property
  @loadable('load')
  def rating(self):
    return self._rating

  @property
  @loadable('load')
  def weighted_score(self):
    return self._weighted_score

  @property
  @loadable('load')
  def rank(self):
    return self._rank

  @property
  @loadable('load')
  def popularity(self):
    return self._popularity

  @property
  @loadable('load')
  def members(self):
    return self._members

  @property
  @loadable('load')
  def favorites(self):
    return self._favorites

  @property
  @loadable('load')
  def tags(self):
    return self._tags
  
  @property
  @loadable('load')
  def synopsis(self):
    return self._synopsis

  @property
  @loadable('load')
  def related(self):
    return self._related

  @property
  @loadable('load_characters')
  def characters(self):
    return self._characters

  @property
  @loadable('load_characters')
  def voice_actors(self):
    return self._voice_actors

  @property
  @loadable('load_characters')
  def staff(self):
    return self._staff  

  @property
  @loadable('load_stats')
  def status_stats(self):
    return self._status_stats

  @property
  @loadable('load_stats')
  def score_stats(self):
    return self._score_stats
