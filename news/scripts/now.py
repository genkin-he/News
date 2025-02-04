# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import traceback
from urllib.parse import quote
import urllib.request  # 发送请求
import json
import re
from util.spider_util import SpiderUtil

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "_ga=GA1.1.1337123095.1733714167; _ga_PSJPX029ZD=GS1.1.1733714174.1.1.1733714184.50.0.0; __utma=262549139.1337123095.1733714167.1733714284.1733714284.1; __utmb=262549139.0.10.1733714284; __utmc=262549139; __utmz=262549139.1733714284.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=262549139.|1=deviceType=desktop=1; _ga_DGFECMB23C=GS1.1.1733714166.1.1.1733715785.60.0.1304140467; __utmt=1; __utma=262549139.1337123095.1733714167.1733714284.1733714284.1; __utmb=262549139.1.10.1733714284; __utmc=262549139; __utmz=262549139.1733714284.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=262549139.|1=deviceType=desktop=1",
    "Referer": "https://news.now.com/home/finance",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

base_url = "https://news.now.com"
filename = "./news/data/now/list.json"
current_links = []
util = SpiderUtil()


def run(link):
    data = util.history_posts(filename)
    _articles = data["articles"]
    _links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(link, None, headers)
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request, timeout=8)
    if response.status == 200:
        body = response.read().decode("utf-8", errors="ignore")
        items = json.loads(body)
        for index in range(len(items)):
            if index > 4:
                break
            id = items[index]["newsId"]
            title = items[index]["title"]
            description = items[index]["summary"].replace("瀏覽MOBILE網頁", "")
            image = items[index]["imageUrl"]
            link = "https://news.now.com/home/technology/player?newsId={}".format(id)
            category = items[index]["categoryName"]
            if link in ",".join(_links):
                print("now exists link: ", link)
                break
            if description != "":
                insert = True
                _articles.insert(
                    index,
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "image": image,
                        "category": category,
                        "pub_date": util.current_time_string(),
                        "source": "now",
                        "kind": 1,
                        "language": "zh-HK",
                    },
                )

        if len(_articles) > 0 and insert:
            if len(_articles) > 10:
                _articles = _articles[:10]
            util.write_json_to_file(_articles, filename)
    else:
        util.log_action_error("now request error: {}".format(response))


util.execute_with_timeout(
    run, "https://news.now.com/api/getNewsList?category=121&pageSize=200&pageNo=1"
)

util.execute_with_timeout(
    run, "https://news.now.com/api/getNewsList?category=502&pageSize=200&pageNo=1"
)
