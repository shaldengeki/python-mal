#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import datetime

import myanimelist.session
import myanimelist.media_list
import myanimelist.anime_list

class testAnimeListClass(object):
  @classmethod
  def setUpClass(self):
    self.session = myanimelist.session.Session()

    self.shal = self.session.anime_list(u'shaldengeki')
    self.fz = self.session.anime(10087)
    self.trigun = self.session.anime(6)
    self.clannad = self.session.anime(2167)

    self.pl = self.session.anime_list(u'PaperLuigi')
    self.baccano = self.session.anime(2251)
    self.pokemon = self.session.anime(20159)
    self.dmc = self.session.anime(3702)

    self.mona = self.session.anime_list(u'monausicaa')
    self.zombie = self.session.anime(3354)
    self.lollipop = self.session.anime(1509)
    self.musume = self.session.anime(5246)

    self.threger = self.session.anime_list(u'threger')

  @raises(TypeError)
  def testNoUsernameInvalidAnimeList(self):
    self.session.anime_list()

  @raises(myanimelist.media_list.InvalidMediaListError)
  def testNonexistentUsernameInvalidAnimeList(self):
    self.session.anime_list(u'aspdoifpjsadoifjapodsijfp').load()

  def testUserValid(self):
    assert isinstance(self.shal, myanimelist.anime_list.AnimeList)

  def testUsername(self):
    assert self.shal.username == u'shaldengeki'
    assert self.mona.username == u'monausicaa'

  def testType(self):
    assert self.shal.type == u'anime'

  def testList(self):
    assert isinstance(self.shal.list, dict) and len(self.shal.list) == 146
    assert self.fz in self.shal.list and self.clannad in self.shal.list and self.trigun in self.shal.list
    assert self.shal.list[self.fz][u'status'] == u'Watching' and self.shal.list[self.clannad][u'status'] == u'Completed' and self.shal.list[self.trigun][u'status'] == u'Plan to Watch'
    assert self.shal.list[self.fz][u'score'] == None and self.shal.list[self.clannad][u'score'] == 9 and self.shal.list[self.trigun][u'score'] == None
    assert self.shal.list[self.fz][u'episodes_watched'] == 6 and self.shal.list[self.clannad][u'episodes_watched'] == 23 and self.shal.list[self.trigun][u'episodes_watched'] == 6
    assert self.shal.list[self.fz][u'tags'] == [] and self.shal.list[self.clannad][u'tags'] == [] and self.shal.list[self.trigun][u'tags'] == []
    assert self.shal.list[self.fz][u'started'] == None and self.shal.list[self.clannad][u'started'] == None and self.shal.list[self.trigun][u'started'] == None
    assert self.shal.list[self.fz][u'finished'] == None and self.shal.list[self.clannad][u'finished'] == None and self.shal.list[self.trigun][u'finished'] == None

    assert isinstance(self.pl.list, dict) and len(self.pl.list) >= 795
    assert self.baccano in self.pl.list and self.pokemon in self.pl.list and self.dmc in self.pl.list
    assert self.pl.list[self.baccano][u'status'] == u'Completed' and self.pl.list[self.pokemon][u'status'] == u'On-Hold' and self.pl.list[self.dmc][u'status'] == u'Dropped'
    assert self.pl.list[self.baccano][u'score'] == 10 and self.pl.list[self.pokemon][u'score'] == None and self.pl.list[self.dmc][u'score'] == 2
    assert self.pl.list[self.baccano][u'episodes_watched'] == 13 and self.pl.list[self.pokemon][u'episodes_watched'] == 2 and self.pl.list[self.dmc][u'episodes_watched'] == 1
    assert self.pl.list[self.baccano][u'tags'] == [] and self.pl.list[self.pokemon][u'tags'] == [] and self.pl.list[self.dmc][u'tags'] == [u'too fuck', u'too wet']
    assert self.pl.list[self.baccano][u'started'] == datetime.date(year=2009, month=7, day=27) and self.pl.list[self.pokemon][u'started'] == datetime.date(year=2013, month=10, day=5) and self.pl.list[self.dmc][u'started'] == datetime.date(year=2010, month=9, day=27)
    assert self.pl.list[self.baccano][u'finished'] == datetime.date(year=2009, month=7, day=28) and self.pl.list[self.pokemon][u'finished'] == None and self.pl.list[self.dmc][u'finished'] == None

    assert isinstance(self.mona.list, dict) and len(self.mona.list) >= 1822
    assert self.zombie in self.mona.list and self.lollipop in self.mona.list and self.musume in self.mona.list
    assert self.mona.list[self.zombie][u'status'] == u'Completed' and self.mona.list[self.lollipop][u'status'] == u'On-Hold' and self.mona.list[self.musume][u'status'] == u'Plan to Watch'
    assert self.mona.list[self.zombie][u'score'] == 7 and self.mona.list[self.lollipop][u'score'] == None and self.mona.list[self.musume][u'score'] == None
    assert self.mona.list[self.zombie][u'episodes_watched'] == 2 and self.mona.list[self.lollipop][u'episodes_watched'] == 12 and self.mona.list[self.musume][u'episodes_watched'] == 0
    assert self.mona.list[self.zombie][u'tags'] == [] and self.mona.list[self.lollipop][u'tags'] == [u'GW with AKJ and Shal'] and self.mona.list[self.musume][u'tags'] == []
    assert self.mona.list[self.zombie][u'started'] == None and self.mona.list[self.lollipop][u'started'] == None and self.mona.list[self.musume][u'started'] == None
    assert self.mona.list[self.zombie][u'finished'] == None and self.mona.list[self.lollipop][u'finished'] == None and self.mona.list[self.musume][u'finished'] == None

    assert isinstance(self.threger.list, dict) and len(self.threger.list) == 0

  def testStats(self):
    assert isinstance(self.shal.stats, dict) and len(self.shal.stats) > 0
    print self.shal.stats
    assert self.shal.stats[u'TV'] == 98 and self.shal.stats[u'OVA'] == 11 and self.shal.stats[u'Movies'] == 27 and self.shal.stats[u'Spcl.'] == 10 and self.shal.stats[u'Eps'] == 2239 and self.shal.stats[u'DL Eps'] == 266 and float(self.shal.stats[u'Days']) == 38.11 and float(self.shal.stats[u'Mean Score']) == 14.1 and float(self.shal.stats[u'Score Dev.']) == -9.1

    assert isinstance(self.pl.stats, dict) and len(self.pl.stats) > 0
    assert self.pl.stats[u'TV'] >= 649 and self.pl.stats[u'OVA'] >= 47 and self.pl.stats[u'Movies'] >= 53 and self.pl.stats[u'Spcl.'] >= 35 and self.pl.stats[u'Eps'] >= 7522 and self.pl.stats[u'DL Eps'] >= 1010 and self.pl.stats[u'Days'] >= 125.91 and self.pl.stats[u'Mean Score'] > 0

    assert isinstance(self.mona.stats, dict) and len(self.mona.stats) > 0
    assert self.mona.stats[u'TV'] >= 849 and self.mona.stats[u'OVA'] >= 315 and self.mona.stats[u'Movies'] >= 265 and self.mona.stats[u'Spcl.'] >= 242 and self.mona.stats[u'Eps'] >= 26742 and self.mona.stats[u'DL Eps'] >= 98 and self.mona.stats[u'Days'] >= 443.21 and self.mona.stats[u'Mean Score'] > 0

    assert isinstance(self.threger.stats, dict) and len(self.threger.stats) > 0
    assert self.threger.stats[u'TV'] == 0 and self.threger.stats[u'OVA'] == 0 and self.threger.stats[u'Movies'] == 0 and self.threger.stats[u'Spcl.'] == 0 and self.threger.stats[u'Eps'] == 0 and self.threger.stats[u'DL Eps'] == 0 and float(self.threger.stats[u'Days']) == 0 and float(self.threger.stats[u'Mean Score']) == 0.0 and float(self.threger.stats[u'Score Dev.']) == 0.0

  def testSection(self):
    assert isinstance(self.shal.section(u'Watching'), dict) and self.fz in self.shal.section(u'Watching')
    assert isinstance(self.pl.section(u'Completed'), dict) and self.baccano in self.pl.section(u'Completed')
    assert isinstance(self.mona.section(u'Plan to Watch'), dict) and self.musume in self.mona.section(u'Plan to Watch')
    assert isinstance(self.threger.section(u'Watching'), dict) and len(self.threger.section(u'Watching')) == 0
