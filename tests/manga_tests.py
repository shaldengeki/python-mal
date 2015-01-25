#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import datetime
import myanimelist.session
import myanimelist.manga

class testMangaClass(object):
  @classmethod
  def setUpClass(self):
    self.session = myanimelist.session.Session()

    self.monster = self.session.manga(1)
    self.mystery = self.session.genre(7)
    self.mystery_tag = self.session.tag(u'mystery')
    self.urasawa = self.session.person(1867)
    self.original = self.session.publication(1)
    self.heinemann = self.session.character(6123)
    self.monster_side_story = self.session.manga(10968)

    self.holic = self.session.manga(10)
    self.supernatural = self.session.genre(37)
    self.supernatural_tag = self.session.tag(u'supernatural')
    self.clamp = self.session.person(1877)
    self.bessatsu = self.session.publication(450)
    self.doumeki = self.session.character(567)
    self.holic_sequel = self.session.manga(46010)

    self.naruto = self.session.manga(11)
    self.shounen = self.session.genre(27)
    self.action_tag = self.session.tag(u'action')
    self.kishimoto = self.session.person(1879)
    self.shonen_jump_weekly = self.session.publication(83)
    self.ebizou = self.session.character(31825)

    self.tomoyo_after = self.session.manga(3941)
    self.drama = self.session.genre(8)
    self.romance_tag = self.session.tag(u'romance')
    self.sumiyoshi = self.session.person(3830)
    self.dragon_age = self.session.publication(98)
    self.kanako = self.session.character(21227)

    self.judos = self.session.manga(79819)
    self.action = self.session.genre(1)
    self.kondou = self.session.person(18765)

    self.invalid_anime = self.session.manga(457384754)
    self.latest_manga = myanimelist.manga.Manga.newest(self.session)

  @raises(TypeError)
  def testNoIDInvalidManga(self):
    self.session.manga()

  @raises(TypeError)
  def testNoSessionInvalidLatestManga(self):
    myanimelist.manga.Manga.newest()

  @raises(myanimelist.manga.InvalidMangaError)
  def testNegativeInvalidManga(self):
    self.session.manga(-1)

  @raises(myanimelist.manga.InvalidMangaError)
  def testFloatInvalidManga(self):
    self.session.manga(1.5)

  @raises(myanimelist.manga.InvalidMangaError)
  def testNonExistentManga(self):
    self.invalid_anime.load()

  def testLatestManga(self):
    assert isinstance(self.latest_manga, myanimelist.manga.Manga)
    assert self.latest_manga.id > 79818

  def testMangaValid(self):
    assert isinstance(self.monster, myanimelist.manga.Manga)

  def testTitle(self):
    assert self.monster.title == u'Monster'
    assert self.holic.title == u'xxxHOLiC'
    assert self.naruto.title == u'Naruto'
    assert self.tomoyo_after.title == u'Clannad: Tomoyo After'
    assert self.judos.title == u'Judos'

  def testPicture(self):
    assert isinstance(self.holic.picture, unicode)
    assert isinstance(self.naruto.picture, unicode)
    assert isinstance(self.monster.picture, unicode)
    assert isinstance(self.tomoyo_after.picture, unicode)
    assert isinstance(self.judos.picture, unicode)

  def testAlternativeTitles(self):
    assert u'Japanese' in self.monster.alternative_titles and isinstance(self.monster.alternative_titles[u'Japanese'], list) and u'MONSTER モンスター' in self.monster.alternative_titles[u'Japanese']
    assert u'Synonyms' in self.holic.alternative_titles and isinstance(self.holic.alternative_titles[u'Synonyms'], list) and u'xxxHolic Cage' in self.holic.alternative_titles[u'Synonyms']
    assert u'Japanese' in self.naruto.alternative_titles and isinstance(self.naruto.alternative_titles[u'Japanese'], list) and u'NARUTO -ナルト-' in self.naruto.alternative_titles[u'Japanese']
    assert u'English' in self.tomoyo_after.alternative_titles and isinstance(self.tomoyo_after.alternative_titles[u'English'], list) and u'Tomoyo After ~Dear Shining Memories~' in self.tomoyo_after.alternative_titles[u'English']
    assert u'Synonyms' in self.judos.alternative_titles and isinstance(self.judos.alternative_titles[u'Synonyms'], list) and u'Juudouzu' in self.judos.alternative_titles[u'Synonyms']

  def testTypes(self):
    assert self.monster.type == u'Manga'
    assert self.tomoyo_after.type == u'Manga'
    assert self.judos.type == u'Manga'

  def testVolumes(self):
    assert self.holic.volumes == 19
    assert self.monster.volumes == 18
    assert self.tomoyo_after.volumes == 1
    assert self.naruto.volumes == 72
    assert self.judos.volumes == 3

  def testChapters(self):
    assert self.holic.chapters == 213
    assert self.monster.chapters == 162
    assert self.tomoyo_after.chapters == 4
    assert self.naruto.chapters == 700
    assert self.judos.chapters == None

  def testStatus(self):
    assert self.holic.status == u'Finished'
    assert self.tomoyo_after.status == u'Finished'
    assert self.monster.status == u'Finished'
    assert self.naruto.status == u'Finished'

  def testPublished(self):
    assert self.holic.published == (datetime.date(month=2, day=24, year=2003), datetime.date(month=2, day=9, year=2011))
    assert self.monster.published == (datetime.date(month=12, day=5, year=1994), datetime.date(month=12, day=20, year=2001))
    assert self.naruto.published == (datetime.date(month=9, day=21, year=1999),datetime.date(month=11, day=10, year=2014))
    assert self.tomoyo_after.published == (datetime.date(month=4, day=20, year=2007), datetime.date(month=10, day=20, year=2007))

  def testGenres(self):
    assert isinstance(self.holic.genres, list) and len(self.holic.genres) > 0 and self.mystery in self.holic.genres and self.supernatural in self.holic.genres
    assert isinstance(self.tomoyo_after.genres, list) and len(self.tomoyo_after.genres) > 0 and self.drama in self.tomoyo_after.genres
    assert isinstance(self.naruto.genres, list) and len(self.naruto.genres) > 0 and self.shounen in self.naruto.genres
    assert isinstance(self.monster.genres, list) and len(self.monster.genres) > 0 and self.mystery in self.monster.genres
    assert isinstance(self.judos.genres, list) and len(self.judos.genres) > 0 and self.shounen in self.judos.genres and self.action in self.judos.genres

  def testAuthors(self):
    assert isinstance(self.holic.authors, dict) and len(self.holic.authors) > 0 and self.clamp in self.holic.authors and self.holic.authors[self.clamp] == u'Story & Art'
    assert isinstance(self.tomoyo_after.authors, dict) and len(self.tomoyo_after.authors) > 0 and self.sumiyoshi in self.tomoyo_after.authors and self.tomoyo_after.authors[self.sumiyoshi] == u'Art'
    assert isinstance(self.naruto.authors, dict) and len(self.naruto.authors) > 0 and self.kishimoto in self.naruto.authors and self.naruto.authors[self.kishimoto] == u'Story & Art'
    assert isinstance(self.monster.authors, dict) and len(self.monster.authors) > 0 and self.urasawa in self.monster.authors and self.monster.authors[self.urasawa] == u'Story & Art'
    assert isinstance(self.judos.authors, dict) and len(self.judos.authors) > 0 and self.kondou in self.judos.authors and self.judos.authors[self.kondou] == u'Story & Art'

  def testSerialization(self):
    assert isinstance(self.holic.serialization, myanimelist.publication.Publication) and self.bessatsu == self.holic.serialization
    assert isinstance(self.tomoyo_after.serialization, myanimelist.publication.Publication) and self.dragon_age == self.tomoyo_after.serialization
    assert isinstance(self.naruto.serialization, myanimelist.publication.Publication) and self.shonen_jump_weekly == self.naruto.serialization
    assert isinstance(self.monster.serialization, myanimelist.publication.Publication) and self.original == self.monster.serialization
    assert isinstance(self.judos.serialization, myanimelist.publication.Publication) and self.shonen_jump_weekly == self.judos.serialization

  def testScore(self):
    assert isinstance(self.holic.score, tuple)
    assert self.holic.score[0] > 0 and self.holic.score[0] < 10
    assert isinstance(self.holic.score[1], int) and self.holic.score[1] >= 0
    assert isinstance(self.monster.score, tuple)
    assert self.monster.score[0] > 0 and self.monster.score[0] < 10
    assert isinstance(self.monster.score[1], int) and self.monster.score[1] >= 0
    assert isinstance(self.naruto.score, tuple)
    assert self.naruto.score[0] > 0 and self.naruto.score[0] < 10
    assert isinstance(self.naruto.score[1], int) and self.naruto.score[1] >= 0
    assert isinstance(self.tomoyo_after.score, tuple)
    assert self.tomoyo_after.score[0] > 0 and self.tomoyo_after.score[0] < 10
    assert isinstance(self.tomoyo_after.score[1], int) and self.tomoyo_after.score[1] >= 0
    assert self.judos.score[0] >= 0 and self.judos.score[0] <= 10
    assert isinstance(self.judos.score[1], int) and self.judos.score[1] >= 0

  def testRank(self):
    assert isinstance(self.holic.rank, int) and self.holic.rank > 0
    assert isinstance(self.monster.rank, int) and self.monster.rank > 0
    assert isinstance(self.naruto.rank, int) and self.naruto.rank > 0
    assert isinstance(self.tomoyo_after.rank, int) and self.tomoyo_after.rank > 0
    assert isinstance(self.judos.rank, int) and self.judos.rank > 0
    
  def testPopularity(self):
    assert isinstance(self.holic.popularity, int) and self.holic.popularity > 0
    assert isinstance(self.monster.popularity, int) and self.monster.popularity > 0
    assert isinstance(self.naruto.popularity, int) and self.naruto.popularity > 0
    assert isinstance(self.tomoyo_after.popularity, int) and self.tomoyo_after.popularity > 0
    assert isinstance(self.judos.popularity, int) and self.judos.popularity > 0
    
  def testMembers(self):
    assert isinstance(self.holic.members, int) and self.holic.members > 0
    assert isinstance(self.monster.members, int) and self.monster.members > 0
    assert isinstance(self.naruto.members, int) and self.naruto.members > 0
    assert isinstance(self.tomoyo_after.members, int) and self.tomoyo_after.members > 0
    assert isinstance(self.judos.members, int) and self.judos.members > 0
    
  def testFavorites(self):
    assert isinstance(self.holic.favorites, int) and self.holic.favorites > 0
    assert isinstance(self.monster.favorites, int) and self.monster.favorites > 0
    assert isinstance(self.naruto.favorites, int) and self.naruto.favorites > 0
    assert isinstance(self.tomoyo_after.favorites, int) and self.tomoyo_after.favorites > 0
    assert isinstance(self.judos.favorites, int) and self.judos.favorites >= 0

  def testPopularTags(self):
    assert isinstance(self.holic.popular_tags, dict) and len(self.holic.popular_tags) > 0 and self.supernatural_tag in self.holic.popular_tags and self.holic.popular_tags[self.supernatural_tag] >= 269
    assert isinstance(self.tomoyo_after.popular_tags, dict) and len(self.tomoyo_after.popular_tags) > 0 and self.romance_tag in self.tomoyo_after.popular_tags and self.tomoyo_after.popular_tags[self.romance_tag] >= 57
    assert isinstance(self.naruto.popular_tags, dict) and len(self.naruto.popular_tags) > 0 and self.action_tag in self.naruto.popular_tags and self.naruto.popular_tags[self.action_tag] >= 561
    assert isinstance(self.monster.popular_tags, dict) and len(self.monster.popular_tags) > 0 and self.mystery_tag in self.monster.popular_tags and self.monster.popular_tags[self.mystery_tag] >= 105
    assert isinstance(self.judos.popular_tags, dict) and len(self.judos.popular_tags) == 0

  def testSynopsis(self):
    assert isinstance(self.holic.synopsis, unicode) and len(self.holic.synopsis) > 0 and u'Watanuki' in self.holic.synopsis
    assert isinstance(self.monster.synopsis, unicode) and len(self.monster.synopsis) > 0 and u'Tenma' in self.monster.synopsis
    assert isinstance(self.naruto.synopsis, unicode) and len(self.naruto.synopsis) > 0 and u'Hokage' in self.naruto.synopsis
    assert isinstance(self.tomoyo_after.synopsis, unicode) and len(self.tomoyo_after.synopsis) > 0 and u'Clannad' in self.tomoyo_after.synopsis
    assert isinstance(self.judos.synopsis, unicode) and len(self.judos.synopsis) > 0 and u'hardcore' in self.judos.synopsis

  def testRelated(self):
    assert isinstance(self.holic.related, dict) and 'Sequel' in self.holic.related and self.holic_sequel in self.holic.related[u'Sequel']
    assert isinstance(self.monster.related, dict) and 'Side story' in self.monster.related and self.monster_side_story in self.monster.related[u'Side story']

  def testCharacters(self):
    assert isinstance(self.holic.characters, dict) and len(self.holic.characters) > 0
    assert self.doumeki in self.holic.characters and self.holic.characters[self.doumeki]['role'] == 'Main'

    assert isinstance(self.monster.characters, dict) and len(self.monster.characters) > 0
    assert self.heinemann in self.monster.characters and self.monster.characters[self.heinemann]['role'] == 'Main'

    assert isinstance(self.naruto.characters, dict) and len(self.naruto.characters) > 0
    assert self.ebizou in self.naruto.characters and self.naruto.characters[self.ebizou]['role'] == 'Supporting'

    assert isinstance(self.tomoyo_after.characters, dict) and len(self.tomoyo_after.characters) > 0
    assert self.kanako in self.tomoyo_after.characters and self.tomoyo_after.characters[self.kanako]['role'] == 'Supporting'