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
      self.username = str(username).decode(u'utf-8')
    if isinstance(html, unicode):
      self.html = html
    else:
      self.html = str(html).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(MalformedUserPageError, self).__str__(),
      "Username: " + unicode(self.username),
      "HTML: " + self.html
    ]).encode(u'utf-8')

class InvalidUserError(Error):
  def __init__(self, username, message=None):
    super(InvalidUserError, self).__init__(message=message)
    if isinstance(username, unicode):
      self.username = username
    else:
      self.username = str(username).decode(u'utf-8')
  def __str__(self):
    return "\n".join([
      super(InvalidUserError, self).__str__(),
      "Username: " + unicode(self.username)
    ])

class User(Base):
  _id_attribute = "username"

  @staticmethod
  def find_username_from_user_id(session, user_id):
    """
      Given a user_id, return the corresponding MAL user's username.
    """
    comments_page = session.session.get(u'http://myanimelist.net/comments.php?' + urllib.urlencode({'id': int(user_id)})).text
    comments_page = bs4.BeautifulSoup(comments_page)
    username_elt = comments_page.find('h1')
    if "'s Comments" not in username_elt.text:
      raise InvalidUserError(user_id, message="Invalid user ID given when looking up username")
    return username_elt.text.replace("'s Comments", "")

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
    error_tag = user_page.find(u'div', {u'class': u'badresult'})
    if error_tag:
        raise InvalidUserError(self.username)

    username_tag = user_page.find(u'div', {u'id': u'contentWrapper'}).find(u'h1')
    if not username_tag.find(u'div'):
      # otherwise, raise a MalformedUserPageError.
      raise MalformedUserPageError(self.username, html, message=u"Could not find title div")
    info_panel_first = user_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'td')

    picture_tag = info_panel_first.find(u'img')
    user_info[u'picture'] = picture_tag.get(u'src')

    # the user ID is always present in the blogfeed link.
    all_comments_link = info_panel_first.find(u'a', text=u'Blog Feed')
    user_info[u'id'] = int(all_comments_link.get(u'href').split(u'&id=')[1])

    infobar_headers = info_panel_first.find_all(u'div', {u'class': u'normal_header'})
    if infobar_headers:
      favorite_anime_header = infobar_headers[0]
      if u'Favorite Anime' in favorite_anime_header.text:
        user_info[u'favorite_anime'] = []
        favorite_anime_table = favorite_anime_header.nextSibling.nextSibling
        if favorite_anime_table.name == u'table':
          for row in favorite_anime_table.find_all(u'tr'):
            cols = row.find_all(u'td')
            anime_link = cols[1].find(u'a')
            link_parts = anime_link.get(u'href').split(u'/')
            # of the form /anime/467/Ghost_in_the_Shell:_Stand_Alone_Complex
            user_info[u'favorite_anime'].append(self.session.anime(int(link_parts[2])).set({u'title': anime_link.text}))
      favorite_manga_header = infobar_headers[1]
      if u'Favorite Manga' in favorite_manga_header.text:
        user_info[u'favorite_manga'] = []
        favorite_manga_table = favorite_manga_header.nextSibling.nextSibling
        if favorite_manga_table.name == u'table':
          for row in favorite_manga_table.find_all(u'tr'):
            cols = row.find_all(u'td')
            manga_link = cols[1].find(u'a')
            link_parts = manga_link.get(u'href').split(u'/')
            # of the form /manga/467/Ghost_in_the_Shell:_Stand_Alone_Complex
            user_info[u'favorite_manga'].append(self.session.manga(int(link_parts[2])).set({u'title': manga_link.text}))
      favorite_character_header = infobar_headers[2]
      if u'Favorite Characters' in favorite_character_header.text:
        user_info[u'favorite_characters'] = {}
        favorite_character_table = favorite_character_header.nextSibling.nextSibling
        if favorite_character_table.name == u'table':
          for row in favorite_character_table.find_all(u'tr'):
            cols = row.find_all(u'td')
            character_link = cols[1].find(u'a')
            link_parts = character_link.get(u'href').split(u'/')
            # of the form /character/467/Ghost_in_the_Shell:_Stand_Alone_Complex
            character = self.session.character(int(link_parts[2])).set({u'title': character_link.text})

            anime_link = cols[1].find(u'div').find(u'a')
            link_parts = anime_link.get(u'href').split(u'/')
            # of the form /anime/467
            anime = self.session.anime(int(link_parts[2])).set({u'title': anime_link.text})

            user_info[u'favorite_characters'][character] = anime
      favorite_people_header = infobar_headers[3]
      if u'Favorite People' in favorite_people_header.text:
        user_info[u'favorite_people'] = []
        favorite_person_table = favorite_people_header.nextSibling.nextSibling
        if favorite_person_table.name == u'table':
          for row in favorite_person_table.find_all(u'tr'):
            cols = row.find_all(u'td')
            person_link = cols[1].find(u'a')
            link_parts = person_link.get(u'href').split(u'/')
            # of the form /person/467/Ghost_in_the_Shell:_Stand_Alone_Complex
            user_info[u'favorite_people'].append(self.session.person(int(link_parts[2])).set({u'title': person_link.text}))
    return user_info

  def parse(self, html):
    user_info = self.parse_sidebar(html)
    user_page = bs4.BeautifulSoup(html)

    section_headings = user_page.find_all(u'div', {u'class': u'normal_header'})

    # parse general details.
    # we have to work from the bottom up, since there's broken HTML after every header.
    last_online_elt = user_page.find(u'td', text=u'Last Online')
    if last_online_elt:
      general_table = last_online_elt.parent.parent
      if general_table and general_table.name == u'table':
        last_online_elt = general_table.find(u'td', text=u'Last Online')
        if last_online_elt:
          user_info[u'last_online'] = utilities.parse_profile_date(last_online_elt.findNext(u'td').text)
        gender = general_table.find(u'td', text=u'Gender')
        if gender:
          user_info[u'gender'] = gender.findNext(u'td').text
        birthday = general_table.find(u'td', text=u'Birthday')
        if birthday:
          user_info[u'birthday'] = utilities.parse_profile_date(birthday.findNext(u'td').text)
        location = general_table.find(u'td', text=u'Location')
        if location:
          user_info[u'location'] = location.findNext(u'td').text
        website = general_table.find(u'td', text=u'Website')
        if website:
          user_info[u'website'] = website.findNext(u'td').text
        join_date = general_table.find(u'td', text=u'Join Date')
        if join_date:
          user_info[u'join_date'] = utilities.parse_profile_date(join_date.findNext(u'td').text)
        access_rank = general_table.find(u'td', text=u'Access Rank')
        if access_rank:
          user_info[u'access_rank'] = access_rank.findNext(u'td').text
        anime_list_views = general_table.find(u'td', text=u'Anime List Views')
        if anime_list_views:
          user_info[u'anime_list_views'] = int(anime_list_views.findNext(u'td').text.replace(',', ''))
        manga_list_views = general_table.find(u'td', text=u'Manga List Views')
        if manga_list_views:
          user_info[u'manga_list_views'] = int(manga_list_views.findNext(u'td').text.replace(',', ''))
        num_comments = general_table.find(u'td', text=u'Comments')
        if num_comments:
          user_info[u'num_comments'] = int(num_comments.findNext(u'td').text.replace(',', ''))
        num_forum_posts = general_table.find(u'td', text=u'Forum Posts')
        if num_forum_posts:
          user_info[u'num_forum_posts'] = int(num_forum_posts.findNext(u'td').text.replace(" (Find All)", "").replace(',', ''))

    # last list updates.
    list_updates_header = filter(lambda x: u'Last List Updates' in x.text, section_headings)
    if list_updates_header:
      list_updates_header = list_updates_header[0]
      list_updates_table = list_updates_header.findNext(u'table')
      if list_updates_table:
        user_info[u'last_list_updates'] = {}
        for row in list_updates_table.find_all(u'tr'):
          cols = row.find_all(u'td')
          info_col = cols[1]
          media_link = info_col.find(u'a')
          link_parts = media_link.get(u'href').split(u'/')
          # of the form /(anime|manga)/10087/Fate/Zero
          if link_parts[1] == u'anime':
            media = self.session.anime(int(link_parts[2])).set({u'title': media_link.text})
          else:
            media = self.session.manga(int(link_parts[2])).set({u'title': media_link.text})
          list_update = {}
          progress_div = info_col.find(u'div', {u'class': u'spaceit_pad'})
          if progress_div:
            progress_match = re.match(r'(?P<status>[A-Za-z]+)(  at (?P<episodes>[0-9]+) of (?P<total_episodes>[0-9]+))?', progress_div.text).groupdict()
            list_update[u'status'] = progress_match[u'status']
            if progress_match[u'episodes'] is None:
              list_update[u'episodes'] = None
            else:
              list_update[u'episodes'] = int(progress_match[u'episodes'])
            if progress_match[u'total_episodes'] is None:
              list_update[u'total_episodes'] = None
            else:
              list_update[u'total_episodes'] = int(progress_match[u'total_episodes'])
          time_div = info_col.find(u'div', {u'class': u'lightLink'})
          if time_div:
            list_update[u'time'] = utilities.parse_profile_date(time_div.text)
          user_info[u'last_list_updates'][media] = list_update

    lower_section_headings = user_page.find_all(u'h2')
    # anime stats.
    anime_stats_header = filter(lambda x: u'Anime Stats' in x.text, lower_section_headings)
    if anime_stats_header:
      anime_stats_header = anime_stats_header[0]
      anime_stats_table = anime_stats_header.findNext(u'table')
      if anime_stats_table:
        user_info[u'anime_stats'] = {}
        for row in anime_stats_table.find_all(u'tr'):
          cols = row.find_all(u'td')
          value = cols[1].text
          if cols[1].find(u'span', {u'title': u'Days'}):
            value = round(float(value), 1)
          else:
            value = int(value)
          user_info[u'anime_stats'][cols[0].text] = value

    # manga stats.
    manga_stats_header = filter(lambda x: u'Manga Stats' in x.text, lower_section_headings)
    if manga_stats_header:
      manga_stats_header = manga_stats_header[0]
      manga_stats_table = manga_stats_header.findNext(u'table')
      if manga_stats_table:
        user_info[u'manga_stats'] = {}
        for row in manga_stats_table.find_all(u'tr'):
          cols = row.find_all(u'td')
          value = cols[1].text
          if cols[1].find(u'span', {u'title': u'Days'}):
            value = round(float(value), 1)
          else:
            value = int(value)
          user_info[u'manga_stats'][cols[0].text] = value

    about_header = filter(lambda x: u'About' in x.text, section_headings)
    if about_header:
      about_header = about_header[0]
      user_info[u'about'] = about_header.findNext(u'div').text.strip()
    return user_info

  def parse_reviews(self, html):
    user_info = self.parse_sidebar(html)
    reviews_page = bs4.BeautifulSoup(html)

    second_col = reviews_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'tr').find_all(u'td', recursive=False)[1]
    user_info[u'reviews'] = {}
    reviews = second_col.find_all(u'div', {u'class': u'borderDark'})
    if reviews:
      for row in reviews:
        review_info = {}
        (meta_elt, review_elt, _) = row.find_all(u'div', recursive=False)
        meta_rows = meta_elt.find_all(u'div', recursive=False)
        review_info[u'date'] = utilities.parse_profile_date(meta_rows[0].find(u'div').text)
        media_link = meta_rows[0].find(u'a')
        link_parts = media_link.get(u'href').split(u'/')
        # of the form /(anime|manga)/9760/Hoshi_wo_Ou_Kodomo
        if link_parts[1] == u'anime':
          media = self.session.anime(int(link_parts[2])).set({u'title': media_link.text})
        else:
          media = self.session.manga(int(link_parts[2])).set({u'title': media_link.text})

        helpfuls = meta_rows[1].find(u'span', recursive=False)
        helpful_match = re.match(r'(?P<people_helped>[0-9]+) of (?P<people_total>[0-9]+)', helpfuls.text).groupdict()
        review_info[u'people_helped'] = int(helpful_match[u'people_helped'])
        review_info[u'people_total'] = int(helpful_match[u'people_total'])

        consumption_match = re.match(r'(?P<media_consumed>[0-9]+) of (?P<media_total>[0-9?]+)', meta_rows[2].text).groupdict()
        review_info[u'media_consumed'] = int(consumption_match[u'media_consumed'])
        if consumption_match[u'media_total'] == u'?':
          review_info[u'media_total'] = None
        else:
          review_info[u'media_total'] = int(consumption_match[u'media_total'])

        review_info[u'rating'] = int(meta_rows[3].find(u'div').text.replace(u'Overall Rating: ', ''))

        for x in review_elt.find_all([u'div', 'a']):
          x.extract()
        review_info[u'text'] = review_elt.text.strip()
        user_info[u'reviews'][media] = review_info
    return user_info

  def parse_recommendations(self, html):
    user_info = self.parse_sidebar(html)
    recommendations_page = bs4.BeautifulSoup(html)
    second_col = recommendations_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'tr').find_all(u'td', recursive=False)[1]
    recommendations = second_col.find_all(u"div", {u"class": u"spaceit borderClass"})
    if recommendations:
      user_info[u'recommendations'] = {}
      for row in recommendations[1:]:
        anime_table = row.find(u'table')
        animes = anime_table.find_all(u'td')
        liked_anime_link = animes[0].find(u'a', recursive=False)
        link_parts = liked_anime_link.get(u'href').split(u'/')
        # of the form /anime/64/Rozen_Maiden
        liked_anime = self.session.anime(int(link_parts[2])).set({u'title': liked_anime_link.text})

        recommended_anime_link = animes[1].find(u'a', recursive=False)
        link_parts = recommended_anime_link.get(u'href').split(u'/')
        # of the form /anime/64/Rozen_Maiden
        recommended_anime = self.session.anime(int(link_parts[2])).set({u'title': recommended_anime_link.text})

        recommendation_text = row.find(u'p').text

        recommendation_menu = row.find(u'div', recursive=False)
        utilities.extract_tags(recommendation_menu)
        recommendation_date = utilities.parse_profile_date(recommendation_menu.text.split(u' - ')[1])

        user_info[u'recommendations'][liked_anime] = {u'anime': recommended_anime, 'text': recommendation_text, 'date': recommendation_date}
    return user_info

  def parse_clubs(self, html):
    user_info = self.parse_sidebar(html)
    clubs_page = bs4.BeautifulSoup(html)
    second_col = clubs_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'tr').find_all(u'td', recursive=False)[1]
    user_info[u'clubs'] = []

    club_list = second_col.find(u'ol')
    if club_list:
      clubs = club_list.find_all(u'li')
      for row in clubs:
        club_link = row.find(u'a')
        link_parts = club_link.get(u'href').split(u'?cid=')
        # of the form /clubs.php?cid=10178
        user_info[u'clubs'].append(self.session.club(int(link_parts[1])).set({u'name': club_link.text}))
    return user_info

  def parse_friends(self, html):
    user_info = self.parse_sidebar(html)
    friends_page = bs4.BeautifulSoup(html)
    second_col = friends_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'tr').find_all(u'td', recursive=False)[1]
    user_info[u'friends'] = {}

    friends = second_col.find_all(u'div', {u'class': u'friendHolder'})
    if friends:
      for row in friends:
        block = row.find(u'div', {u'class': u'friendBlock'})
        cols = block.find_all(u'div')

        friend_link = cols[1].find(u'a')
        friend = self.session.user(friend_link.text)

        friend_info = {}
        if len(cols) > 2 and cols[2].text != u'':
          friend_info[u'last_active'] = utilities.parse_profile_date(cols[2].text.strip())

        if len(cols) > 3 and cols[3].text != u'':
          friend_info[u'since'] = utilities.parse_profile_date(cols[3].text.replace(u'Friends since', '').strip())
        user_info[u'friends'][friend] = friend_info
    return user_info

  def load(self):
    """
      Fetches the MAL user profile and sets the current user's attributes.
    """
    user_profile = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username)).text
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
      user_reviews = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username) + u'/reviews&' + urllib.urlencode({u'p': page})).text
      parse_result = self.parse_reviews(user_reviews)
      if page == 0:
        # only set attributes once the first time around.
        self.set(parse_result)
      if len(parse_result[u'reviews']) == 0:
        break
      review_collection.append(parse_result[u'reviews'])
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
    user_recommendations = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username) + u'/recommendations').text
    self.set(self.parse_recommendations(user_recommendations))
    return self

  def load_clubs(self):
    """
      Fetches the MAL user's clubs and sets the current user's attributes.
    """
    user_clubs = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username) + u'/clubs').text
    self.set(self.parse_clubs(user_clubs))
    return self

  def load_friends(self):
    """
      Fetches the MAL user's friends and sets the current user's attributes.
    """
    user_friends = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username) + u'/friends').text
    self.set(self.parse_friends(user_friends))
    return self

  @property
  @loadable(u'load')
  def id(self):
    return self._id

  @property
  @loadable(u'load')
  def picture(self):
    return self._picture

  @property
  @loadable(u'load')
  def favorite_anime(self):
    return self._favorite_anime

  @property
  @loadable(u'load')
  def favorite_manga(self):
    return self._favorite_manga

  @property
  @loadable(u'load')
  def favorite_characters(self):
    return self._favorite_characters

  @property
  @loadable(u'load')
  def favorite_people(self):
    return self._favorite_people

  @property
  @loadable(u'load')
  def last_online(self):
    return self._last_online

  @property
  @loadable(u'load')
  def gender(self):
    return self._gender

  @property
  @loadable(u'load')
  def birthday(self):
    return self._birthday

  @property
  @loadable(u'load')
  def location(self):
    return self._location

  @property
  @loadable(u'load')
  def website(self):
    return self._website

  @property
  @loadable(u'load')
  def join_date(self):
    return self._join_date

  @property
  @loadable(u'load')
  def access_rank(self):
    return self._access_rank

  @property
  @loadable(u'load')
  def anime_list_views(self):
    return self._anime_list_views

  @property
  @loadable(u'load')
  def manga_list_views(self):
    return self._manga_list_views

  @property
  @loadable(u'load')
  def num_comments(self):
    return self._num_comments

  @property
  @loadable(u'load')
  def num_forum_posts(self):
    return self._num_forum_posts

  @property
  @loadable(u'load')
  def last_list_updates(self):
    return self._last_list_updates

  @property
  @loadable(u'load')
  def about(self):
    return self._about

  @property
  @loadable(u'load')
  def anime_stats(self):
    return self._anime_stats

  @property
  @loadable(u'load')
  def manga_stats(self):
    return self._manga_stats

  @property
  @loadable(u'load_reviews')
  def reviews(self):
    return self._reviews

  @property
  @loadable(u'load_recommendations')
  def recommendations(self):
    return self._recommendations

  @property
  @loadable(u'load_clubs')
  def clubs(self):
    return self._clubs

  @property
  @loadable(u'load_friends')
  def friends(self):
    return self._friends

  def anime_list(self):
    return self.session.anime_list(self.username)

  def manga_list(self):
    return self.session.manga_list(self.username)
    