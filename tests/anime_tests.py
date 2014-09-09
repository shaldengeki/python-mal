#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import datetime
import pytz
import myanimelist.session
import myanimelist.anime

class testAnimeClass(object):
  @classmethod
  def setUpClass(self):
    self.session = myanimelist.session.Session()
    self.bebop = self.session.anime(1)
    self.hex = self.session.character(94717)
    self.hex_va = self.session.person(5766)
    self.bebop_side_story = self.session.anime(5)
    self.spicy_wolf = self.session.anime(2966)
    self.holo = self.session.character(7373)
    self.holo_va = self.session.person(70)
    self.spicy_wolf_sequel = self.session.anime(6007)
    self.space_dandy = self.session.anime(20057)
    self.toaster = self.session.character(110427)
    self.toaster_va = self.session.person(611)
    self.totoro = self.session.anime(523)
    self.satsuki = self.session.character(267)
    self.satsuki_va = self.session.person(1104)
    self.invalid_anime = self.session.anime(457384754)
    self.latest_anime = myanimelist.anime.Anime.newest(self.session)

  @raises(TypeError)
  def testNoIDInvalidAnime(self):
    self.session.anime()

  @raises(TypeError)
  def testNoSessionInvalidLatestAnime(self):
    myanimelist.anime.Anime.newest()

  @raises(myanimelist.anime.InvalidAnimeError)
  def testNegativeInvalidAnime(self):
    self.session.anime(-1)

  @raises(myanimelist.anime.InvalidAnimeError)
  def testFloatInvalidAnime(self):
    self.session.anime(1.5)

  @raises(myanimelist.anime.InvalidAnimeError)
  def testNonExistentAnime(self):
    self.invalid_anime.load()

  def testLatestAnime(self):
    assert isinstance(self.latest_anime, myanimelist.anime.Anime)
    assert self.latest_anime.id > 20000

  def testAnimeValid(self):
    assert isinstance(self.bebop, myanimelist.anime.Anime)

  def testTitle(self):
    assert self.bebop.title == u'Cowboy Bebop'
    assert self.spicy_wolf.title == u'Ookami to Koushinryou'
    assert self.space_dandy.title == u'Space☆Dandy'

  def testPicture(self):
    assert isinstance(self.spicy_wolf.picture, unicode)
    assert isinstance(self.space_dandy.picture, unicode)
    assert isinstance(self.bebop.picture, unicode)
    assert isinstance(self.totoro.picture, unicode)

  def testAlternativeTitles(self):
    assert u'Japanese' in self.bebop.alternative_titles and isinstance(self.bebop.alternative_titles['Japanese'], list) and u'カウボーイビバップ' in self.bebop.alternative_titles['Japanese']
    assert u'English' in self.spicy_wolf.alternative_titles and isinstance(self.spicy_wolf.alternative_titles['English'], list) and u'Spice and Wolf' in self.spicy_wolf.alternative_titles['English']
    assert u'Japanese' in self.space_dandy.alternative_titles and isinstance(self.space_dandy.alternative_titles['Japanese'], list) and u'スペース☆ダンディ' in self.space_dandy.alternative_titles['Japanese']

  def testTypes(self):
    assert self.bebop.type == u'TV'
    assert self.totoro.type == u'Movie'

  def testEpisodes(self):
    assert self.spicy_wolf.episodes == 13
    assert self.bebop.episodes == 26
    assert self.totoro.episodes == 1
    assert self.space_dandy.episodes == 13

  def testStatus(self):
    assert self.spicy_wolf.status == u'Finished Airing'
    assert self.totoro.status == u'Finished Airing'
    assert self.bebop.status == u'Finished Airing'
    assert self.space_dandy.status == u'Finished Airing'

  def testAired(self):
    assert self.spicy_wolf.aired == (datetime.date(month=1, day=8, year=2008), datetime.date(month=5, day=30, year=2008))
    assert self.bebop.aired == (datetime.date(month=4, day=3, year=1998), datetime.date(month=4, day=24, year=1999))
    assert self.space_dandy.aired == (datetime.date(month=1, day=5, year=2014),datetime.date(month=3,day=27,year=2014))
    assert self.totoro.aired == (datetime.date(month=4, day=16, year=1988),)

  def testDuration(self):
    assert self.spicy_wolf.duration == 24
    print self.totoro.duration
    assert self.totoro.duration == 86
    assert self.space_dandy.duration == 24
    assert self.bebop.duration == 24

  def testWeightedScore(self):
    assert isinstance(self.spicy_wolf.weighted_score, tuple)
    assert isinstance(self.spicy_wolf.weighted_score[0], float) and self.spicy_wolf.weighted_score[0] > 0 and self.spicy_wolf.weighted_score[0] < 10
    assert isinstance(self.spicy_wolf.weighted_score[1], int) and self.spicy_wolf.weighted_score[1] >= 0
    assert isinstance(self.bebop.weighted_score, tuple)
    assert isinstance(self.bebop.weighted_score[0], float) and self.bebop.weighted_score[0] > 0 and self.bebop.weighted_score[0] < 10
    assert isinstance(self.bebop.weighted_score[1], int) and self.bebop.weighted_score[1] >= 0
    assert isinstance(self.space_dandy.weighted_score, tuple)
    assert isinstance(self.space_dandy.weighted_score[0], float) and self.space_dandy.weighted_score[0] > 0 and self.space_dandy.weighted_score[0] < 10
    assert isinstance(self.space_dandy.weighted_score[1], int) and self.space_dandy.weighted_score[1] >= 0
    assert isinstance(self.totoro.weighted_score, tuple)
    assert isinstance(self.totoro.weighted_score[0], float) and self.totoro.weighted_score[0] > 0 and self.totoro.weighted_score[0] < 10
    assert isinstance(self.totoro.weighted_score[1], int) and self.totoro.weighted_score[1] >= 0

  def testRank(self):
    assert isinstance(self.spicy_wolf.rank, int) and self.spicy_wolf.rank > 0
    assert isinstance(self.bebop.rank, int) and self.bebop.rank > 0
    assert isinstance(self.space_dandy.rank, int) and self.space_dandy.rank > 0
    assert isinstance(self.totoro.rank, int) and self.totoro.rank > 0
    
  def testPopularity(self):
    assert isinstance(self.spicy_wolf.popularity, int) and self.spicy_wolf.popularity > 0
    assert isinstance(self.bebop.popularity, int) and self.bebop.popularity > 0
    assert isinstance(self.space_dandy.popularity, int) and self.space_dandy.popularity > 0
    assert isinstance(self.totoro.popularity, int) and self.totoro.popularity > 0
    
  def testMembers(self):
    assert isinstance(self.spicy_wolf.members, int) and self.spicy_wolf.members > 0
    assert isinstance(self.bebop.members, int) and self.bebop.members > 0
    assert isinstance(self.space_dandy.members, int) and self.space_dandy.members > 0
    assert isinstance(self.totoro.members, int) and self.totoro.members > 0
    
  def testFavorites(self):
    assert isinstance(self.spicy_wolf.favorites, int) and self.spicy_wolf.favorites > 0
    assert isinstance(self.bebop.favorites, int) and self.bebop.favorites > 0
    assert isinstance(self.space_dandy.favorites, int) and self.space_dandy.favorites > 0
    assert isinstance(self.totoro.favorites, int) and self.totoro.favorites > 0

  def testSynopsis(self):
    assert isinstance(self.spicy_wolf.synopsis, unicode) and len(self.spicy_wolf.synopsis) > 0 and u'Holo' in self.spicy_wolf.synopsis
    assert isinstance(self.bebop.synopsis, unicode) and len(self.bebop.synopsis) > 0 and u'Spike' in self.bebop.synopsis
    assert isinstance(self.space_dandy.synopsis, unicode) and len(self.space_dandy.synopsis) > 0 and u'dandy' in self.space_dandy.synopsis
    assert isinstance(self.totoro.synopsis, unicode) and len(self.totoro.synopsis) > 0 and u'Satsuki' in self.totoro.synopsis

  def testRelated(self):
    assert isinstance(self.spicy_wolf.related, dict) and 'Sequel' in self.spicy_wolf.related and self.spicy_wolf_sequel in self.spicy_wolf.related['Sequel']
    assert isinstance(self.bebop.related, dict) and 'Side story' in self.bebop.related and self.bebop_side_story in self.bebop.related['Side story']

  def testCharacters(self):
    assert isinstance(self.spicy_wolf.characters, dict) and len(self.spicy_wolf.characters) > 0
    assert self.holo in self.spicy_wolf.characters and self.spicy_wolf.characters[self.holo]['role'] == 'Main' and self.holo_va in self.spicy_wolf.characters[self.holo]['voice_actors']
    assert isinstance(self.bebop.characters, dict) and len(self.bebop.characters) > 0
    assert self.hex in self.bebop.characters and self.bebop.characters[self.hex]['role'] == 'Supporting' and self.hex_va in self.bebop.characters[self.hex]['voice_actors']
    assert isinstance(self.space_dandy.characters, dict) and len(self.space_dandy.characters) > 0
    assert self.toaster in self.space_dandy.characters and self.space_dandy.characters[self.toaster]['role'] == 'Supporting' and self.toaster_va in self.space_dandy.characters[self.toaster]['voice_actors']
    assert isinstance(self.totoro.characters, dict) and len(self.totoro.characters) > 0
    assert self.satsuki in self.totoro.characters and self.totoro.characters[self.satsuki]['role'] == 'Main' and self.satsuki_va in self.totoro.characters[self.satsuki]['voice_actors']

  def testVoiceActors(self):
    assert isinstance(self.spicy_wolf.voice_actors, dict) and len(self.spicy_wolf.voice_actors) > 0
    assert self.holo_va in self.spicy_wolf.voice_actors and self.spicy_wolf.voice_actors[self.holo_va]['role'] == 'Main' and self.spicy_wolf.voice_actors[self.holo_va]['character'] == self.holo
    assert isinstance(self.bebop.voice_actors, dict) and len(self.bebop.voice_actors) > 0
    assert self.hex_va in self.bebop.voice_actors and self.bebop.voice_actors[self.hex_va]['role'] == 'Supporting' and self.bebop.voice_actors[self.hex_va]['character'] == self.hex
    assert isinstance(self.space_dandy.voice_actors, dict) and len(self.space_dandy.voice_actors) > 0
    assert self.toaster_va in self.space_dandy.voice_actors and self.space_dandy.voice_actors[self.toaster_va]['role'] == 'Supporting' and self.space_dandy.voice_actors[self.toaster_va]['character'] == self.toaster
    assert isinstance(self.totoro.voice_actors, dict) and len(self.totoro.voice_actors) > 0
    assert self.satsuki_va in self.totoro.voice_actors and self.totoro.voice_actors[self.satsuki_va]['role'] == 'Main' and self.totoro.voice_actors[self.satsuki_va]['character'] == self.satsuki

  def testStaff(self):
    assert isinstance(self.spicy_wolf.staff, dict) and len(self.spicy_wolf.staff) > 0
    assert self.session.person(472) in self.spicy_wolf.staff and u'Producer' in self.spicy_wolf.staff[self.session.person(472)]
    assert isinstance(self.bebop.staff, dict) and len(self.bebop.staff) > 0
    assert self.session.person(12221) in self.bebop.staff and u'Inserted Song Performance' in self.bebop.staff[self.session.person(12221)]
    assert isinstance(self.space_dandy.staff, dict) and len(self.space_dandy.staff) > 0
    assert self.session.person(10127) in self.space_dandy.staff and all(x in self.space_dandy.staff[self.session.person(10127)] for x in [u'Theme Song Composition', u'Theme Song Lyrics', u'Theme Song Performance'])
    assert isinstance(self.totoro.staff, dict) and len(self.totoro.staff) > 0
    assert self.session.person(1870) in self.totoro.staff and all(x in self.totoro.staff[self.session.person(1870)] for x in [u'Director', u'Script', u'Storyboard'])