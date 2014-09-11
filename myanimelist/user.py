#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re
import urllib

import utilities
from base import Base, Error, loadable

class MalformedUserPageError(Error):
  def __init__(self, username, html, message=None):
    super(MalformedUserPageError, self).__init__(message=message)
    if isinstance(username, unicode):
      self.username = username
    else:
      self.username = str(username).decode('utf-8')
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode('utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedUserPageError, self).__str__(),
      "Username: " + unicode(self.username),
      "HTML: " + self.html
    ]).encode('utf-8')

class InvalidUserError(Error):
  def __init__(self, username, message=None):
    super(InvalidUserError, self).__init__(message=message)
    if isinstance(username, unicode):
      self.username = username
    else:
      self.username = str(username).decode('utf-8')
  def __str__(self):
    return "\n".join([
      super(InvalidUserError, self).__str__(),
      "Username: " + unicode(self.username)
    ])

class User(Base):
  _id_attribute = "username"
  def __init__(self, session, username):
    super(User, self).__init__(session)
    self.username = username
    if not isinstance(self.username, basestring) or len(self.username) < 1:
      raise InvalidUserError(self.username)
    self._picture = None
    self._favorite_anime = None
    self._favorite_manga = None
    self._favorite_characters = None
    self._favorite_people = None
    self._last_online = None
    self._gender = None
    self._birthday = None
    self._location = None
    self._website = None
    self._join_date = None
    self._access_rank = None
    self._anime_list_views = None
    self._manga_list_views = None
    self._num_comments = None
    self._num_forum_posts = None
    self._last_list_updates = None
    self._about = None
    self._anime_stats = None
    self._manga_stats = None
    self._reviews = None
    self._recommendations = None
    self._clubs = None
    self._friends = None

  def parse_sidebar(self, html):
    user_info = {}
    user_page = bs4.BeautifulSoup(html)
    # if MAL says the series doesn't exist, raise an InvalidUserError.
    error_tag = user_page.find('div', {'class': 'badresult'})
    if error_tag:
        raise InvalidUserError(self.username)

    username_tag = user_page.find('div', {'id': 'contentWrapper'}).find('h1')
    if not username_tag.find('div'):
      # otherwise, raise a MalformedUserPageError.
      raise MalformedUserPageError(self.username, html, message="Could not find title div")
    info_panel_first = user_page.find('div', {'id': 'content'}).find('table').find('td')

    picture_tag = info_panel_first.find('img')
    user_info['picture'] = picture_tag.get('src')

    # the user ID is always present in the blogfeed link.
    all_comments_link = info_panel_first.find('a', text=u'Blog Feed')
    user_info['id'] = int(all_comments_link.get('href').split('&id=')[1])

    infobar_headers = info_panel_first.find_all('div', {'class': 'normal_header'})
    if infobar_headers:
      favorite_anime_header = infobar_headers[0]
      if u'Favorite Anime' in favorite_anime_header.text:
        user_info['favorite_anime'] = []
        favorite_anime_table = favorite_anime_header.nextSibling.nextSibling
        if favorite_anime_table.name == u'table':
          for row in favorite_anime_table.find_all('tr'):
            cols = row.find_all('td')
            anime_link = cols[1].find('a')
            link_parts = anime_link.get('href').split('/')
            # of the form /anime/467/Ghost_in_the_Shell:_Stand_Alone_Complex
            user_info['favorite_anime'].append(self.session.anime(int(link_parts[2])).set({'title': anime_link.text}))
      favorite_manga_header = infobar_headers[1]
      if u'Favorite Manga' in favorite_manga_header.text:
        user_info['favorite_manga'] = []
        favorite_manga_table = favorite_manga_header.nextSibling.nextSibling
        if favorite_manga_table.name == u'table':
          for row in favorite_manga_table.find_all('tr'):
            cols = row.find_all('td')
            manga_link = cols[1].find('a')
            link_parts = manga_link.get('href').split('/')
            # of the form /manga/467/Ghost_in_the_Shell:_Stand_Alone_Complex
            user_info['favorite_manga'].append(self.session.manga(int(link_parts[2])).set({'title': manga_link.text}))
      favorite_character_header = infobar_headers[2]
      if u'Favorite Characters' in favorite_character_header.text:
        user_info['favorite_characters'] = {}
        favorite_character_table = favorite_character_header.nextSibling.nextSibling
        if favorite_character_table.name == u'table':
          for row in favorite_character_table.find_all('tr'):
            cols = row.find_all('td')
            character_link = cols[1].find('a')
            link_parts = character_link.get('href').split('/')
            # of the form /character/467/Ghost_in_the_Shell:_Stand_Alone_Complex
            character = self.session.character(int(link_parts[2])).set({'title': character_link.text})

            anime_link = cols[1].find('div').find('a')
            link_parts = anime_link.get('href').split('/')
            # of the form /anime/467
            anime = self.session.anime(int(link_parts[2])).set({'title': anime_link.text})

            user_info['favorite_characters'][character] = anime
      favorite_people_header = infobar_headers[3]
      if u'Favorite People' in favorite_people_header.text:
        user_info['favorite_people'] = []
        favorite_person_table = favorite_people_header.nextSibling.nextSibling
        if favorite_person_table.name == u'table':
          for row in favorite_person_table.find_all('tr'):
            cols = row.find_all('td')
            person_link = cols[1].find('a')
            link_parts = person_link.get('href').split('/')
            # of the form /person/467/Ghost_in_the_Shell:_Stand_Alone_Complex
            user_info['favorite_people'].append(self.session.person(int(link_parts[2])).set({'title': person_link.text}))
    return user_info

  def parse(self, html):
    user_info = self.parse_sidebar(html)
    user_page = bs4.BeautifulSoup(html)

    section_headings = user_page.find_all('div', {'class': 'normal_header'})

    # parse general details.
    # we have to work from the bottom up, since there's broken HTML after every header.
    last_online_elt = user_page.find('td', text=u'Last Online')
    if last_online_elt:
      general_table = last_online_elt.parent.parent
      if general_table and general_table.name == u'table':
        last_online_elt = general_table.find('td', text=u'Last Online')
        if last_online_elt:
          user_info['last_online'] = utilities.parse_profile_date(last_online_elt.findNext('td').text)
        gender = general_table.find('td', text=u'Gender')
        if gender:
          user_info['gender'] = gender.findNext('td').text
        birthday = general_table.find('td', text=u'Birthday')
        if birthday:
          user_info['birthday'] = utilities.parse_profile_date(birthday.findNext('td').text)
        location = general_table.find('td', text=u'Location')
        if location:
          user_info['location'] = location.findNext('td').text
        website = general_table.find('td', text=u'Website')
        if website:
          user_info['website'] = website.findNext('td').text
        join_date = general_table.find('td', text=u'Join Date')
        if join_date:
          user_info['join_date'] = utilities.parse_profile_date(join_date.findNext('td').text)
        access_rank = general_table.find('td', text=u'Access Rank')
        if access_rank:
          user_info['access_rank'] = access_rank.findNext('td').text
        anime_list_views = general_table.find('td', text=u'Anime List Views')
        if anime_list_views:
          user_info['anime_list_views'] = utilities.decommaify_int(anime_list_views.findNext('td').text)
        manga_list_views = general_table.find('td', text=u'Manga List Views')
        if manga_list_views:
          user_info['manga_list_views'] = utilities.decommaify_int(manga_list_views.findNext('td').text)
        num_comments = general_table.find('td', text=u'Comments')
        if num_comments:
          user_info['num_comments'] = utilities.decommaify_int(num_comments.findNext('td').text)
        num_forum_posts = general_table.find('td', text=u'Forum Posts')
        if num_forum_posts:
          user_info['num_forum_posts'] = utilities.decommaify_int(num_forum_posts.findNext('td').text.replace(" (Find All)", ""))

    # last list updates.
    list_updates_header = filter(lambda x: u'Last List Updates' in x.text, section_headings)
    if list_updates_header:
      list_updates_header = list_updates_header[0]
      list_updates_table = list_updates_header.findNext('table')
      if list_updates_table:
        user_info['last_list_updates'] = {}
        for row in list_updates_table.find_all('tr'):
          cols = row.find_all('td')
          info_col = cols[1]
          media_link = info_col.find('a')
          link_parts = media_link.get('href').split('/')
          # of the form /(anime|manga)/10087/Fate/Zero
          if link_parts[1] == u'anime':
            media = self.session.anime(int(link_parts[2])).set({'title': media_link.text})
          else:
            media = self.session.manga(int(link_parts[2])).set({'title': media_link.text})
          list_update = {}
          progress_div = info_col.find('div', {'class': 'spaceit_pad'})
          if progress_div:
            progress_match = re.match(r'(?P<status>[A-Za-z]+)(  at (?P<episodes>[0-9]+) of (?P<total_episodes>[0-9]+))?', progress_div.text).groupdict()
            list_update['status'] = progress_match['status']
            if progress_match['episodes'] is None:
              list_update['episodes'] = None
            else:
              list_update['episodes'] = int(progress_match['episodes'])
            if progress_match['total_episodes'] is None:
              list_update['total_episodes'] = None
            else:
              list_update['total_episodes'] = int(progress_match['total_episodes'])
          time_div = info_col.find('div', {'class': 'lightLink'})
          if time_div:
            list_update['time'] = utilities.parse_profile_date(time_div.text)
          user_info['last_list_updates'][media] = list_update

    lower_section_headings = user_page.find_all('h2')
    # anime stats.
    anime_stats_header = filter(lambda x: u'Anime Stats' in x.text, lower_section_headings)
    if anime_stats_header:
      anime_stats_header = anime_stats_header[0]
      anime_stats_table = anime_stats_header.findNext('table')
      if anime_stats_table:
        user_info['anime_stats'] = {}
        for row in anime_stats_table.find_all('tr'):
          cols = row.find_all('td')
          value = cols[1].text
          if cols[1].find('span', {'title': 'Days'}):
            value = round(float(value), 1)
          else:
            value = int(value)
          user_info['anime_stats'][cols[0].text] = value

    # manga stats.
    manga_stats_header = filter(lambda x: u'Manga Stats' in x.text, lower_section_headings)
    if manga_stats_header:
      manga_stats_header = manga_stats_header[0]
      manga_stats_table = manga_stats_header.findNext('table')
      if manga_stats_table:
        user_info['manga_stats'] = {}
        for row in manga_stats_table.find_all('tr'):
          cols = row.find_all('td')
          value = cols[1].text
          if cols[1].find('span', {'title': 'Days'}):
            value = round(float(value), 1)
          else:
            value = int(value)
          user_info['manga_stats'][cols[0].text] = value

    about_header = filter(lambda x: u'About' in x.text, section_headings)
    if about_header:
      about_header = about_header[0]
      user_info['about'] = about_header.findNext('div').text.strip()
    return user_info

  def parse_reviews(self, html):
    user_info = self.parse_sidebar(html)
    reviews_page = bs4.BeautifulSoup(html)

    second_col = reviews_page.find('div', {'id': 'content'}).find('table').find('tr').find_all('td', recursive=False)[1]
    user_info['reviews'] = {}
    reviews = second_col.find_all('div', {'class': 'borderDark'})
    if reviews:
      for row in reviews:
        review_info = {}
        (meta_elt, review_elt, _) = row.find_all('div', recursive=False)
        meta_rows = meta_elt.find_all('div', recursive=False)
        review_info['date'] = utilities.parse_profile_date(meta_rows[0].find('div').text)
        media_link = meta_rows[0].find('a')
        link_parts = media_link.get('href').split('/')
        # of the form /(anime|manga)/9760/Hoshi_wo_Ou_Kodomo
        if link_parts[1] == u'anime':
          media = self.session.anime(int(link_parts[2])).set({'title': media_link.text})
        else:
          media = self.session.manga(int(link_parts[2])).set({'title': media_link.text})

        helpfuls = meta_rows[1].find('span', recursive=False)
        helpful_match = re.match(r'(?P<people_helped>[0-9]+) of (?P<people_total>[0-9]+)', helpfuls.text).groupdict()
        review_info['people_helped'] = int(helpful_match['people_helped'])
        review_info['people_total'] = int(helpful_match['people_total'])

        consumption_match = re.match(r'(?P<media_consumed>[0-9]+) of (?P<media_total>[0-9?]+)', meta_rows[2].text).groupdict()
        review_info['media_consumed'] = int(consumption_match['media_consumed'])
        if consumption_match['media_total'] == u'?':
          review_info['media_total'] = None
        else:
          review_info['media_total'] = int(consumption_match['media_total'])

        review_info['rating'] = int(meta_rows[3].find('div').text.replace('Overall Rating: ', ''))

        for x in review_elt.find_all(['div', 'a']):
          x.extract()
        review_info['text'] = review_elt.text.strip()
        user_info['reviews'][media] = review_info
    return user_info

  def parse_recommendations(self, html):
    user_info = self.parse_sidebar(html)
    recommendations_page = bs4.BeautifulSoup(html)
    second_col = recommendations_page.find('div', {'id': 'content'}).find('table').find('tr').find_all('td', recursive=False)[1]
    recommendations = second_col.find_all("div", {"class": "spaceit borderClass"})
    if recommendations:
      user_info['recommendations'] = {}
      for row in recommendations[1:]:
        anime_table = row.find('table')
        animes = anime_table.find_all('td')
        liked_anime_link = animes[0].find('a', recursive=False)
        link_parts = liked_anime_link.get('href').split('/')
        # of the form /anime/64/Rozen_Maiden
        liked_anime = self.session.anime(int(link_parts[2])).set({'title': liked_anime_link.text})

        recommended_anime_link = animes[1].find('a', recursive=False)
        link_parts = recommended_anime_link.get('href').split('/')
        # of the form /anime/64/Rozen_Maiden
        recommended_anime = self.session.anime(int(link_parts[2])).set({'title': recommended_anime_link.text})

        recommendation_text = row.find('p').text

        recommendation_menu = row.find('div', recursive=False)
        utilities.extract_tags(recommendation_menu)
        recommendation_date = utilities.parse_profile_date(recommendation_menu.text.split(' - ')[1])

        user_info['recommendations'][liked_anime] = {'anime': recommended_anime, 'text': recommendation_text, 'date': recommendation_date}
    return user_info

  def parse_clubs(self, html):
    user_info = self.parse_sidebar(html)
    clubs_page = bs4.BeautifulSoup(html)
    second_col = clubs_page.find('div', {'id': 'content'}).find('table').find('tr').find_all('td', recursive=False)[1]
    user_info['clubs'] = []

    club_list = second_col.find('ol')
    if club_list:
      clubs = club_list.find_all('li')
      for row in clubs:
        club_link = row.find('a')
        link_parts = club_link.get('href').split('?cid=')
        # of the form /clubs.php?cid=10178
        user_info['clubs'].append(self.session.club(int(link_parts[1])).set({'name': club_link.text}))
    return user_info

  def parse_friends(self, html):
    user_info = self.parse_sidebar(html)
    friends_page = bs4.BeautifulSoup(html)
    second_col = friends_page.find('div', {'id': 'content'}).find('table').find('tr').find_all('td', recursive=False)[1]
    user_info['friends'] = {}

    friends = second_col.find_all('div', {'class': 'friendHolder'})
    if friends:
      for row in friends:
        block = row.find('div', {'class': 'friendBlock'})
        cols = block.find_all('div')

        friend_link = cols[1].find('a')
        friend = self.session.user(friend_link.text)

        friend_info = {}
        if len(cols) > 2 and cols[2].text != u'':
          friend_info['last_active'] = utilities.parse_profile_date(cols[2].text.strip())

        if len(cols) > 3 and cols[3].text != u'':
          friend_info['since'] = utilities.parse_profile_date(cols[3].text.replace('Friends since', '').strip())
        user_info['friends'][friend] = friend_info
    return user_info

  def load(self):
    """
      Fetches the MAL user profile and sets the current user's attributes.
    """
    user_profile = self.session.session.get('http://myanimelist.net/profile/' + utilities.urlencode(self.username)).text
    self.set(self.parse(user_profile))
    return self

  def load_reviews(self):
    """
      Fetches the MAL user's reviews and sets the current user's attributes.
    """
    page = 0
    # collect all reviews over all pages.
    review_collection = []
    while True:
      user_reviews = self.session.session.get('http://myanimelist.net/profile/' + utilities.urlencode(self.username) + '/reviews&' + urllib.urlencode({'p': page})).text
      parse_result = self.parse_reviews(user_reviews)
      if page == 0:
        # only set attributes once the first time around.
        self.set(parse_result)
      if len(parse_result['reviews']) == 0:
        break
      review_collection.append(parse_result['reviews'])
      page += 1

    # merge the review collections into one review dict, and set it.
    self.set({
      'reviews': {k: v for d in review_collection for k,v in d.iteritems()}
    })
    return self

  def load_recommendations(self):
    """
      Fetches the MAL user's recommendations and sets the current user's attributes.
    """
    user_recommendations = self.session.session.get('http://myanimelist.net/profile/' + utilities.urlencode(self.username) + '/recommendations').text
    self.set(self.parse_recommendations(user_recommendations))
    return self

  def load_clubs(self):
    """
      Fetches the MAL user's clubs and sets the current user's attributes.
    """
    user_clubs = self.session.session.get('http://myanimelist.net/profile/' + utilities.urlencode(self.username) + '/clubs').text
    self.set(self.parse_clubs(user_clubs))
    return self

  def load_friends(self):
    """
      Fetches the MAL user's friends and sets the current user's attributes.
    """
    user_friends = self.session.session.get('http://myanimelist.net/profile/' + utilities.urlencode(self.username) + '/friends').text
    self.set(self.parse_friends(user_friends))
    return self

  @property
  @loadable('load')
  def id(self):
    return self._id

  @property
  @loadable('load')
  def picture(self):
    return self._picture

  @property
  @loadable('load')
  def favorite_anime(self):
    return self._favorite_anime

  @property
  @loadable('load')
  def favorite_manga(self):
    return self._favorite_manga

  @property
  @loadable('load')
  def favorite_characters(self):
    return self._favorite_characters

  @property
  @loadable('load')
  def favorite_people(self):
    return self._favorite_people

  @property
  @loadable('load')
  def last_online(self):
    return self._last_online

  @property
  @loadable('load')
  def gender(self):
    return self._gender

  @property
  @loadable('load')
  def birthday(self):
    return self._birthday

  @property
  @loadable('load')
  def location(self):
    return self._location

  @property
  @loadable('load')
  def website(self):
    return self._website

  @property
  @loadable('load')
  def join_date(self):
    return self._join_date

  @property
  @loadable('load')
  def access_rank(self):
    return self._access_rank

  @property
  @loadable('load')
  def anime_list_views(self):
    return self._anime_list_views

  @property
  @loadable('load')
  def manga_list_views(self):
    return self._manga_list_views

  @property
  @loadable('load')
  def num_comments(self):
    return self._num_comments

  @property
  @loadable('load')
  def num_forum_posts(self):
    return self._num_forum_posts

  @property
  @loadable('load')
  def last_list_updates(self):
    return self._last_list_updates

  @property
  @loadable('load')
  def about(self):
    return self._about

  @property
  @loadable('load')
  def anime_stats(self):
    return self._anime_stats

  @property
  @loadable('load')
  def manga_stats(self):
    return self._manga_stats

  @property
  @loadable('load_reviews')
  def reviews(self):
    return self._reviews

  @property
  @loadable('load_recommendations')
  def recommendations(self):
    return self._recommendations

  @property
  @loadable('load_clubs')
  def clubs(self):
    return self._clubs

  @property
  @loadable('load_friends')
  def friends(self):
    return self._friends