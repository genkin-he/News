# -*- coding: UTF-8 -*-
import json
from datetime import datetime, timezone, timedelta
import hashlib
import os

path = "./news/scripts/util/urls.json"

def exists(link):
    with open(path) as user_file:
        urls = json.load(user_file)
        if urls.has_key(link):
            return True
        else:
            urls[link] = 1
            with open(path,'w') as f:
                f.write(json.dumps(urls))
                
                
def history_posts(filepath):
    try:
        with open(filepath) as user_file:
            articles = json.load(user_file)["data"]
            links = []
            for article in articles:
                links.append(article["link"])
            return {'articles': articles, 'links': links}
    except:
        return {'articles': [], 'links': []}
    
def parse_time(time_str, format):
    # utc = "2021-03-08T08:28:47.776Z"
    # UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    timeObj = datetime.strptime(time_str, format)
    local_time = timeObj + timedelta(hours=8)
    return local_time.strftime("%Y-%m-%d %H:%M:%S")

def has_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
 
    return False

def current_time():
    # 获取当前时间(北京时间)
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

def md5(string):
    return hashlib.md5(string.encode()).hexdigest()

def current_time_string():
    return current_time().strftime("%Y-%m-%d %H:%M:%S")

def append_to_temp_file(file_path, data):
    """
    往指定临时文件追加数据
    :param file_path: 临时文件路径
    :param data: 需要追加的数据
    """
    try:
        # 如果文件不存在，先创建一个空文件
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                pass
        with open(file_path, 'a') as file:
            file.write(data)
    except Exception as e:
        print(f"写入临时文件过程中发生错误: {str(e)}")

def log_action_error(error_message):
    """
    记录操作错误信息到临时文件
    :param error_message: 错误信息
    """
    print(error_message)
    temp_file_path = "./tmp/action_errors.log"
    if len(error_message) > 100:
        error_message = error_message[:100] + "\n"
    append_to_temp_file(temp_file_path, error_message + "\n")
    return
