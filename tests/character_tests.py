#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import myanimelist.session
import myanimelist.character
import myanimelist.user

class testCharacterClass(object):
  @classmethod
  def setUpClass(self):
    self.session = myanimelist.session.Session()
    self.spike = self.session.character(1)
    self.ed = self.session.character(11)
    self.maria = self.session.character(112693)
    self.invalid_character = self.session.character(457384754)

  @raises(TypeError)
  def testNoIDInvalidCharacter(self):
    self.session.character()

  @raises(myanimelist.character.InvalidCharacterError)
  def testNegativeInvalidCharacter(self):
    self.session.character(-1)

  @raises(myanimelist.character.InvalidCharacterError)
  def testFloatInvalidCharacter(self):
    self.session.character(1.5)

  @raises(myanimelist.character.InvalidCharacterError)
  def testNonExistentCharacter(self):
    self.invalid_character.load()

  def testCharacterValid(self):
    assert isinstance(self.spike, myanimelist.character.Character)
    assert isinstance(self.maria, myanimelist.character.Character)

  def testName(self):
    assert self.spike.name == u'Spike Spiegel'
    assert self.ed.name == u'Edward Elric'
    assert self.maria.name == u'Maria'

  def testFullName(self):
    assert self.spike.full_name == u'Spike  Spiegel'
    assert self.ed.full_name == u'Edward "Ed, Fullmetal Alchemist, Hagane no shounen, Chibi, Pipsqueak" Elric'
    assert self.maria.full_name == u'Maria'

  def testJapaneseName(self):
    assert self.spike.name_jpn == u'スパイク・スピーゲル'
    assert self.ed.name_jpn == u'エドワード・エルリック'
    assert self.maria.name_jpn == u'マリア'

  def testDescription(self):
    assert isinstance(self.spike.description, unicode) and len(self.spike.description) > 0
    assert isinstance(self.ed.description, unicode) and len(self.ed.description) > 0
    assert isinstance(self.maria.description, unicode) and len(self.maria.description) > 0    

  def testPicture(self):
    assert isinstance(self.spike.picture, unicode) and len(self.spike.picture) > 0
    assert isinstance(self.ed.picture, unicode) and len(self.ed.picture) > 0
    assert isinstance(self.maria.picture, unicode) and len(self.maria.picture) > 0

  def testPictures(self):
    assert isinstance(self.spike.pictures, list) and len(self.spike.pictures) > 0 and all(map(lambda p: isinstance(p, unicode) and p.startswith(u'http://'), self.spike.pictures))
    assert isinstance(self.ed.pictures, list) and len(self.ed.pictures) > 0 and all(map(lambda p: isinstance(p, unicode) and p.startswith(u'http://'), self.ed.pictures))
    assert isinstance(self.maria.pictures, list)

  def testAnimeography(self):
    assert isinstance(self.spike.animeography, dict) and len(self.spike.animeography) > 0 and self.session.anime(1) in self.spike.animeography
    assert isinstance(self.ed.animeography, dict) and len(self.ed.animeography) > 0 and self.session.anime(5114) in self.ed.animeography
    assert isinstance(self.maria.animeography, dict) and len(self.maria.animeography) > 0 and self.session.anime(26441) in self.maria.animeography

  def testMangaography(self):
    assert isinstance(self.spike.mangaography, dict) and len(self.spike.mangaography) > 0 and self.session.manga(173) in self.spike.mangaography
    assert isinstance(self.ed.mangaography, dict) and len(self.ed.mangaography) > 0 and self.session.manga(4658) in self.ed.mangaography
    assert isinstance(self.maria.mangaography, dict) and len(self.maria.mangaography) > 0 and self.session.manga(12336) in self.maria.mangaography

  def testNumFavorites(self):
    assert isinstance(self.spike.num_favorites, int) and self.spike.num_favorites > 12000
    assert isinstance(self.ed.num_favorites, int) and self.ed.num_favorites > 19000
    assert isinstance(self.maria.num_favorites, int)

  def testFavorites(self):
    assert isinstance(self.spike.favorites, list) and len(self.spike.favorites) > 12000 and all(map(lambda u: isinstance(u, myanimelist.user.User), self.spike.favorites))
    assert isinstance(self.ed.favorites, list) and len(self.ed.favorites) > 19000 and all(map(lambda u: isinstance(u, myanimelist.user.User), self.ed.favorites))
    assert isinstance(self.maria.favorites, list)

  def testClubs(self):
    assert isinstance(self.spike.clubs, list) and len(self.spike.clubs) > 50 and all(map(lambda u: isinstance(u, myanimelist.club.Club), self.spike.clubs))
    assert isinstance(self.ed.clubs, list) and len(self.ed.clubs) > 200 and all(map(lambda u: isinstance(u, myanimelist.club.Club), self.ed.clubs))
    assert isinstance(self.maria.clubs, list)