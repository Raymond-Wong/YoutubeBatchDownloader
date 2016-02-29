#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-02-28 20:17:55
# @Author  : Raymond Wong (549425036@qq.com)
# @Link    : github/Raymond-Wong

import os
import sys
import urllib
import time
import threading

from bs4 import BeautifulSoup

BASE_DIR = './videos'
TOOL_URL = 'http://keepvid.com/?url='
LOG_FILE = './log.txt'
LOCK = threading.Lock()
FILE_LOCK = threading.Lock()

class YoutubeDownloader:
  name = ''
  url = None
  target = None

  def __init__(self, name, target):
    self.name = name
    self.url = target

  def downloadSpeed(self, costTime):
    unit = 'B/s'
    size = int(urllib.urlopen(self.target).info().getheaders("Content-Length")[0])
    speed = size / costTime
    if speed < 1024:
      return str(speed) + " " + unit
    speed /= 1024
    unit = "KB/s"
    if speed < 1024:
      return str(speed) + " " + unit
    speed /= 1024
    unit = "MB/s"
    return str(speed) + " " + unit

  # 获取url指向页面的document
  def getHtml(self, url):
    self.logger('INFO', (u'尝试获取 %s 指向页面的内容' % url))
    page = urllib.urlopen(url)
    html = page.read()
    return html


  def download(self, info):
    vid = self.url.split('v=')[-1]
    self.logger('INFO', (u'尝试下载 %s，下载链接为 %s，vid为 %s' % (self.url, '---', vid)))
    startTime = time.clock()
    localDir = os.path.join(BASE_DIR, vid + '.mp4')
    urllib.urlretrieve(info[1], localDir, process)
    costTime = time.clock() - startTime
    self.logger('INFO', (u'成功下载 %s，储存在 %s 路径下，耗时 %s，平均下载速度为 %s' % (self.url, localDir, prettyTime(costTime), self.downloadSpeed(costTime))))

  def logger(self, tp, msg):
    if LOCK.acquire():
      print u'[%s][%s]\t%s' % (tp, self.name, msg)
      LOCK.release()

  def run(self):
    try:
      vid = self.url.split('v=')[-1]
      if (vid + '.mp4') in os.listdir(BASE_DIR):
        self.logger('WARN', (u'%s 视频已下载' % self.url))
        return
      html = self.getHtml(TOOL_URL + self.url)
      downloadList = getDownloadList(html)
      info = getNameAndUrl(downloadList)
      self.target = info[1]
      self.download(info)
    except Exception as e:
      print e
      self.logger('WARN', (u'%s 指向的视频已失效' % self.url))
      if FILE_LOCK.acquire():
        f = open(LOG_FILE, 'a')
        f.write(self.url + "\n")
        f.close()
        FILE_LOCK.release()

# 获取页面中可下载的链接
def getDownloadList(html):
  doc = BeautifulSoup(html, 'lxml')
  dl = doc.find(id='dl')
  return dl.find_all('a')

# 根据工具网站返回的内容获取视频的名称以及下载链接
def getNameAndUrl(downloadList):
  name = downloadList[1].get_text().encode('utf-8')
  url = downloadList[2].attrs['href']
  return (name, url)

# 显示下载进度
def process(a, b, c):
  # per = 100 * a * b / c
  # if per > 100:
  #   per = 100
  # print '%.1f%%' % per
  pass

def prettyTime(second):
  hour = 0
  minute = 0
  if second < 60:
    return str(second) + u"秒"
  minute = int(second / 60)
  second = second % 60
  if minute < 60:
    return str(minute) + u"分钟" + str(second) + u"秒"
  hour = int(minute / 60)
  minute = minute % 60
  return str(hour) + u"小时" + str(minute) + u"分钟" + str(second) + u"秒"
