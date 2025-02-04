from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import threading
import time
import traceback


class SpiderUtil:
    def __init__(self):
        self.path = "./news/scripts/util/urls.json"

    def exists(self, link):
        """
        检查给定链接是否存在于urls.json文件中。
        如果存在，返回True；如果不存在，将链接添加到文件中并返回None。
        
        参数:
        link (str): 要检查的链接。
        
        返回:
        bool: 如果链接存在于文件中，返回True；否则返回None。
        """
        with open(self.path) as user_file:
            urls = json.load(user_file)
            if urls.has_key(link):
                return True
            else:
                urls[link] = 1
                with open(self.path, 'w') as f:
                    f.write(json.dumps(urls))

    def history_posts(self, filepath):
        """
        从指定文件中读取历史文章数据，并返回文章列表和链接列表。
        
        参数:
        filepath (str): 包含历史文章数据的文件路径。
        
        返回:
        dict: 包含文章列表和链接列表的字典。
        """
        try:
            with open(filepath) as user_file:
                articles = json.load(user_file)["data"]
                links = []
                for article in articles:
                    links.append(article["link"])
                return {'articles': articles, 'links': links}
        except:
            return {'articles': [], 'links': []}

    def parse_time(self, time_str, format):
        """
        将给定的时间字符串解析为本地时间，并返回格式化后的时间字符串。
        
        参数:
        time_str (str): 要解析的时间字符串。
        format (str): 时间字符串的格式。
        
        返回:
        str: 格式化后的本地时间字符串。
        """
        timeObj = datetime.strptime(time_str, format)
        local_time = timeObj + timedelta(hours=8)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def has_chinese(self, string):
        """
        检查字符串中是否包含中文字符。
        
        参数:
        string (str): 要检查的字符串。
        
        返回:
        bool: 如果字符串中包含中文字符，返回True；否则返回False。
        """
        for ch in string:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    def current_time(self):
        """
        获取当前的本地时间，时区为UTC+8。
        
        返回:
        datetime: 当前的本地时间。
        """
        return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

    def md5(self, string):
        """
        计算给定字符串的MD5哈希值。
        
        参数:
        string (str): 要计算哈希值的字符串。
        
        返回:
        str: 字符串的MD5哈希值。
        """
        return hashlib.md5(string.encode()).hexdigest()

    def current_time_string(self):
        """
        获取当前的本地时间字符串，格式为"YYYY-MM-DD HH:MM:SS"。
        
        返回:
        str: 当前的本地时间字符串。
        """
        return self.current_time().strftime("%Y-%m-%d %H:%M:%S")
    
    def convert_utc_to_local(self, timestamp):
        """
        将传入的时间戳转换为本地时间（UTC+8），并返回格式化后的时间字符串。

        参数:
        timestamp (int/str): 要转换的时间戳，可以是整数或字符串。

        返回:
        str: 格式化后的本地时间字符串，格式为"YYYY-MM-DD HH:MM:SS"。
        """
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
        local_time = utc_time.astimezone(timezone(timedelta(hours=8)))
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def append_to_temp_file(self, file_path, data):
        try:
            # 检查文件是否存在，如果不存在则创建一个空文件
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    pass
            # 以追加模式打开文件并写入数据
            with open(file_path, 'a') as file:
                file.write(data)
        except Exception as e:
            # 捕获异常并打印错误信息
            print(f"写入临时文件过程中发生错误: {str(e)}")

    def log_action_error(self, error_message, notify=True):
        # 打印错误信息
        print(error_message)
        # 将错误信息追加到临时文件中
        if notify:
            # 定义临时文件路径
            temp_file_path = "./tmp/action_errors.log"
            # 如果错误信息长度超过100，截取前100个字符并换行
            if len(error_message) > 100:
                error_message = error_message[:100] + "\n"
            self.append_to_temp_file(temp_file_path, error_message + "\n")
        return

    def get_env_variable(self, key, fallback):
        """
        获取环境变量的值，如果不存在则返回默认值

        参数:
        key (str): 环境变量的键
        fallback (str): 如果环境变量不存在时返回的默认值

        返回:
        str: 环境变量的值或默认值
        """
        return os.getenv(key, fallback)
    
    def execute_with_timeout(self, func, *args, timeout=10, notify=True, **kwargs):
        """
        接受一个函数，执行这个函数并设置超时时间，同时统计函数的执行时间

        参数:
        func (callable): 要执行的函数
        *args: 传递给函数的位置参数
        timeout (int): 超时时间，单位为秒
        **kwargs: 传递给函数的关键字参数

        返回:
        tuple: (执行结果, 执行时间) 如果在超时时间内完成
        None: 如果函数执行超时
        """

        # 打印调用栈信息
        stack = traceback.extract_stack()
        # 获取倒数第二个调用（即调用execute_with_timeout的地方）
        filename = os.path.basename(stack[-2].filename)
        lineno = stack[-2].lineno
        class FuncThread(threading.Thread):
            def __init__(self, func, *args, **kwargs):
                threading.Thread.__init__(self)
                self.func = func
                self.args = args
                self.kwargs = kwargs
                self.result = None
                self.execution_time = None

            def run(self):
                start_time = time.time()
                try:
                    self.func(*self.args, **self.kwargs)
                except Exception as e:
                    traceback.print_exc()
                    # 使用外部的log_action_error方法
                    self._log_action_error(f"{filename}#{lineno} error: {repr(e)}\n", notify)
                finally:
                    end_time = time.time()
                    self.execution_time = end_time - start_time   

            def _log_action_error(self, error_message, notify=True):
                # 调用外部类的log_action_error方法
                self._outer.log_action_error(error_message, notify)

        # 将外部类的实例传递给线程类
        thread = FuncThread(func, *args, **kwargs)
        thread._outer = self
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            return None
        if thread.execution_time > 2:
            print(f"Function #{filename}#{lineno} executed in {thread.execution_time:.3f} seconds.")
        return None

    def write_json_to_file(self, data, filename):
        """
        将 JSON 数据以格式化的形式写入传入的文件

        参数:
        data (dict): 要写入文件的 JSON 数据
        filename (str): 文件名

        返回:
        None
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"data": data}, f, ensure_ascii=False, indent=4)
            print(f"JSON data has been written to {filename} successfully.")
        except Exception as e:
            print(f"Error writing JSON data to {filename}: {e}")