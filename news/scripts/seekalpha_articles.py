# -*- coding: UTF-8 -*-
import logging
import traceback
import urllib.request  # 发送请求
import json
from util.spider_util import SpiderUtil

util = SpiderUtil()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "machine_cookie=3663331148119; _sasource=; _gcl_au=1.1.1402177077.1735639585; _ga=GA1.1.976084898.1735639585; session_id=95a10743-da86-4d90-aa05-7883ebc2ccaa; _clck=1m3981t%7C2%7Cfs8%7C0%7C1828; pxcts=b8e95052-c8df-11ef-93ad-a0cb717eaabf; _pxvid=b8e940b4-c8df-11ef-93ac-7e1c64da6706; __hstc=234155329.2d747576f5f9961532a1b28ff069eb2f.1735804895357.1735804895357.1735804895357.1; hubspotutk=2d747576f5f9961532a1b28ff069eb2f; __hssrc=1; _ga_KGRFF2R2C5=GS1.1.1735804866.2.1.1735805100.58.0.0; _uetsid=b8456ab0c8df11ef86f1c374541dffdb; _uetvid=e4fb9e10c75e11efb77ccf83bac62251; sailthru_content=45e035fd7c11ad399f50bf6ed4c749a0bf78837017058c6ec77d3a7b51e0cbcd8403d90a5ca6647022cb099df0aea278; sailthru_visitor=a72ef253-3746-4974-adf6-867a95440d95; _clsk=hsjwto%7C1735805103009%7C3%7C1%7Cn.clarity.ms%2Fcollect; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Farticle%2F4747222-brenntag-an-update-and-a-new-buy-rating%22%2C%22fromMpArticle%22%3Atrue%2C%22isMpArticle%22%3Atrue%2C%22pageKey%22%3A%229f572e49-d9ca-405f-b28f-bc826e51972a%22%7D; _px3=c1dfee0e055bb3d75933650bfc11f6b6cf5514e9c9d506dc23ae115a6a90628c:XORShWwjgnknSwB6IS1BrBey1Q6fLDi82mM2teu44YGId+BGJEoOVxo5GSghpdqRAnwcgjaTlr0KdKD9z5n83w==:1000:ZYt1YMb6M+N8zOodkA7Gf2JRW741NZ0SHwHRj2hRIWyBD/Voj3mG8E9ZlBlpojw4GXLEQYcN2wdwbZn18kvl6GQfyaws+50+YK4K/4GambPbSc3LdgWHshFMm2ZuA8QOhg+YmSB6M0fEFaU6/OKR8tTT2g4wE9woxsiiXZVec7EmebYIlXhSPzkYVirw7ItPZ34vZZ7CLx4d4mEcT+OgDCYHxywzyFPrRjdMug0jTiU=",
}

base_url = "https://seekingalpha.com"
filename = "./news/data/seekalpha/articles.json"


def get_detail(id):
    link = "https://seekingalpha.com/api/v3/articles/{}?include=author%2CprimaryTickers%2CsecondaryTickers%2CotherTags%2Cpresentations%2Cpresentations.slides%2Cauthor.authorResearch%2Cauthor.userBioTags%2Cco_authors%2CpromotedService%2Csentiments".format(
        id
    )
    request = urllib.request.Request(
        link,
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        content = json.loads(body)["data"]["attributes"]["content"]
        return content


def run():
    data = util.history_posts(filename)
    articles = data["articles"]
    links = data["links"]
    insert = False

    # request中放入参数，请求头信息
    request = urllib.request.Request(
        "https://seekingalpha.com/api/v3/articles?filter[category]=latest-articles&filter[since]=0&filter[until]=0&include=author%2CprimaryTickers%2CsecondaryTickers&isMounting=true&page[size]=5&page[number]=1",
        None,
        headers,
    )
    # urlopen打开链接（发送请求获取响应）
    response = urllib.request.urlopen(request)
    if response.status == 200:
        body = response.read().decode("utf-8")
        posts = json.loads(body)["data"]
        for index in range(len(posts)):
            if index < 1:
                post = posts[index]
                id = post["id"]
                title = post["attributes"]["title"]
                image = post["attributes"]["gettyImageUrl"]
                link = base_url + post["links"]["self"]
                publish_on = post["attributes"]["publishOn"]
                pub_date = util.current_time_string()
                if "-05:00" in publish_on:
                    pub_date = util.parse_time(publish_on, "%Y-%m-%dT%H:%M:%S-05:00")
                elif "-04:00" in publish_on:
                    pub_date = util.parse_time(publish_on, "%Y-%m-%dT%H:%M:%S-04:00")
                if link in ",".join(links):
                    print("seekalpha_articles exists link: ", link)
                    break
                description = get_detail(id)
                if description != "":
                    insert = True
                    articles.insert(
                        0,
                        {
                            "id": id,
                            "title": title,
                            "description": description,
                            "image": image,
                            "link": link,
                            "pub_date": pub_date,
                            "source": "seekalpha_articles",
                            "kind": 1,
                            "language": "en",
                        },
                    )
        if len(articles) > 0 and insert:
            if len(articles) > 10:
                articles = articles[:10]
            util.write_json_to_file(articles, filename)
    else:
        util.log_action_error("seekalpha_articles request error: {}".format(response))


util.execute_with_timeout(run)
