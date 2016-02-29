#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-02-28 17:41:37
# @Author  : Raymond Wong (549425036@qq.com)
# @Link    : github/Raymond-Wong

import os
import sys
import threading
import copy

# 设置5秒超时
import socket
socket.setdefaulttimeout(5.0)

from Downloader import YoutubeDownloader

class BatchDownloader(threading.Thread):
  urls = []
  name = ""

  def __init__(self, name, urls):
    super(BatchDownloader, self).__init__()
    self.urls = copy.deepcopy(urls)
    self.name = name

  def run(self):
    for url in self.urls:
      downloader = YoutubeDownloader(self.name, url)
      downloader.run()


if __name__ == '__main__':
  try:
    f = open(sys.argv[1])
  except Exception as e:
    print u'''
使用方法:
  python BatchDownload.py ./urls/train.txt 
或者：
  python BatchDownload.py ./urls/test.txt
下载得到的视频将储存在./videos路径下
出错导致无法下载的视频连接将储存在./log.txt文件中
    '''
  urls = map(lambda x:x.split(" ")[0], f.readlines())
  urls = list(set(urls))
  print u'[INFO][main]\t共读取到 %d 个链接待下载' % len(urls)
  pool = []
  threadAmount = 10
  start = 0
  end = 0
  for i in xrange(0, threadAmount):
    start = end
    end = start + len(urls) / threadAmount
    if end > len(urls):
      end = len(urls)
    print u'[INFO][main]\t%d 到 %d 分配给 downloader%d' % (start, end, i)
    pool.append(BatchDownloader("BatchDownloader_" + str(i), urls[start : end]))
    pool[-1].start()
  for downloader in pool:
    downloader.join()

