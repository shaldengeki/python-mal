#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import pytz
import bs4
import re

import utilities
from base import Base, Error, loadable

class MalformedAnimePageError(Error):
  def __init__(self, anime, html, message=None):
    super(MalformedAnimePageError, self).__init__(message=message)
    self.anime = anime
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode('utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedAnimePageError, self).__str__(),
      "Anime ID: " + unicode(self.anime.id),
      "HTML: " + self.html
    ]).encode('utf-8')

class InvalidAnimeError(Error):
  def __init__(self, anime, message=None):
    super(InvalidAnimeError, self).__init__(message=message)
    self.anime = anime
  def __str__(self):
    return "\n".join([
      super(InvalidAnimeError, self).__str__(),
      "Anime ID: " + unicode(self.anime.id)
    ])

def parse_date(text):
  """
    Parses a MAL date on an anime page.
    May raise ValueError if a malformed date is found.
    If text is "Unknown" or "?" or "Not available" then returns None.
    Otherwise, returns a datetime.date object.
  """
  if text == u"Unknown" or text == u"?" or text == u"Not available":
    return None
  try:
    aired_date = datetime.datetime.strptime(text, '%Y').date()
  except ValueError:
    # see if it's a date.
    try:
      aired_date = datetime.datetime.strptime(text, '%b %d, %Y').date()
    except ValueError:
      # see if it's a month/year pairing.
      aired_date = datetime.datetime.strptime(text, '%b %Y').date()
  return aired_date

class Anime(Base):
  def __repr__(self):
    return u"<Anime ID: " + unicode(self.id) + u">"
  def __hash__(self):
    return hash(self.id)
  def __eq__(self, anime):
    return isinstance(anime, Anime) and self.id == anime.id
  def __ne__(self, anime):
    return not self.__eq__(anime)
  def __init__(self, session, anime_id):
    super(Anime, self).__init__(session)
    self.id = anime_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidAnimeError(self)
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

  def parse_sidebar(self, html):
    """
      Given a MAL anime page's HTML, returns a dict with this anime's attributes found on the sidebar.
    """
    anime_info = {}
    anime_page = bs4.BeautifulSoup(html)
    title_tag = anime_page.find('div', {'id': 'contentWrapper'}).find('h1')
    if not title_tag.find('div'):
      # if MAL says the series doesn't exist, raise an InvalidAnimeError.
      error_tag = anime_page.find('h1', text=u'Invalid Request')
      if error_tag:
        raise InvalidAnimeError(self)
      # otherwise, raise a MalformedAnimePageError.
      raise MalformedAnimePageError(self, html, message="Could not find title div")

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
        aired_date = parse_date(aired_parts[0])
      except ValueError:
        raise MalformedAnimePageError(self, aired_parts[0], message="Could not parse single air date")
      anime_info['aired'] = (aired_date,)
    else:
      # two airing dates.
      try:
        air_start = parse_date(aired_parts[0])
      except ValueError:
        raise MalformedAnimePageError(self, aired_parts[0], message="Could not parse first of two air dates")
      try:
        air_end = parse_date(aired_parts[1])
      except ValueError:
        raise MalformedAnimePageError(self, aired_parts[1], message="Could not parse second of two air dates")
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
        curr_elt = link.previous_sibling
        if curr_elt is None:
          # we've reached the end of the list.
          break
        related_type = None
        while True:
          if not curr_elt:
            raise MalformedAnimePageError(self, related_elt, message="Prematurely reached end of related anime listing")
          if isinstance(curr_elt, bs4.NavigableString):
            type_match = re.match('(?P<type>[a-zA-Z\ \-]+):', curr_elt)
            if type_match:
              related_type = type_match.group('type')
              break
          curr_elt = curr_elt.previous_sibling
        # parse link: may be manga or anime.
        href_parts = link.get('href').split('/')
        title = link.text
        obj_id = int(href_parts[4])
        non_title_parts = href_parts[:5]
        if 'manga' in non_title_parts:
          new_obj = self.session.manga(obj_id).set({'title': title})
        elif 'anime' in non_title_parts:
          new_obj = self.session.anime(obj_id).set({'title': title})
        else:
          raise MalformedAnimePageError(self, link, message="Related thing is of unknown type")
        if related_type not in related:
          related[related_type] = [new_obj]
        else:
          related[related_type].append(new_obj)
      anime_info['related'] = related
    else:
      anime_info['related'] = None
    return anime_info

  def parse_stats(self, html):
    """
      Given a MAL anime stats page's HTML, returns a dict with this anime's attributes.
    """
    anime_info = self.parse_sidebar(html)

    status_stats = {}

    watching_elt = soup.find('span', {'class': 'dark_text'}, text="Watching:").nextSibling
    status_stats['watching'] = int(watching_elt.strip().replace(',', ''))

    completed_elt = soup.find('span', {'class': 'dark_text'}, text="Completed:").nextSibling
    status_stats['completed'] = int(completed_elt.strip().replace(',', ''))

    on_hold_elt = soup.find('span', {'class': 'dark_text'}, text="On-Hold:").nextSibling
    status_stats['on_hold'] = int(on_hold_elt.strip().replace(',', ''))

    dropped_elt = soup.find('span', {'class': 'dark_text'}, text="Dropped:").nextSibling
    status_stats['dropped'] = int(dropped_elt.strip().replace(',', ''))

    plan_to_watch_elt = soup.find('span', {'class': 'dark_text'}, text="Plan to Watch:").nextSibling
    status_stats['plan_to_watch'] = int(plan_to_watch_elt.strip().replace(',', ''))

    anime_info['status_stats'] = status_stats

    score_stats_header = soup.find('h2', text='Score Stats')
    score_stats_table = score_stats_header.find_next_sibling('table')
    if score_stats_table:
      score_stats = {}
      score_rows = score_stats_table.find_all('div', {'class': 'spaceit_pad'})
      for i in xrange(10):
        score_stats[10-i] = int(score_rows[i].find('small').text.replace('(', '').replace(' votes)', ''))
      anime_info['score_stats'] = score_stats
    return anime_info

  def load(self):
    """
      Fetches the MAL anime page and sets the current anime's attributes.
    """
    anime_page = self.session.session.get('http://myanimelist.net/anime/' + str(self.id)).content
    self.set(self.parse(anime_page))
    return self

  def load_stats(self):
        """
      Fetches the MAL anime page and sets the current anime's attributes.
    """
    anime_page = self.session.session.get('http://myanimelist.net/anime/' + str(self.id) + '/stats').content
    self.set(self.parse_stats(anime_page))
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
  @loadable('load_stats')
  def status_stats(self):
    return self._status_stats

  @property
  @loadable('load_stats')
  def score_stats(self):
    return self._score_stats
