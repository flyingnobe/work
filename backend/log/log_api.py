from elasticsearch import Elasticsearch
from typing import Union
from datetime import datetime, timedelta
from datetime import date, datetime
from elasticsearch.exceptions import ConnectionTimeout
import re

   # start_time与end_time因mode而不同
    # 在absolute模式下，start_time, end_time需为datetime格式
    # 在relative模式下，start_time为任意数字的s,m,h,d,etc...，end_time不需要赋值, e.g start_time=1d, 表示查找一天前的日志
    # 在speed模式下，start_time, end_time都不需要赋值，只需要指定label的取值, e.g label=yesterday, 表示查找昨天零时至二十四时的日志
    # :param mode: 指定查看模式，有absolute，relative，speed三种
    # :param node: 指定集群节点
    # :param pod: 指定pod名称
    # :param size: 指定日志数量
    # :param start_time: 开始时间
    # :param end_time: 截止时间
    # :param label: 用于speed模式，有today，yesterday，last_week三种
    # :return: 日志list

class logAPI:
    def __init__(self, url: str, username: str, password: str, index_name: str):
        self.elastic = Elasticsearch(
            [url],
            basic_auth=(username, password),
            verify_certs=False,
            timeout=60
        )
        self.index_name = index_name
        # 保证search的数据一致性
        self.start_time = None
        self.end_time = None
        self.size = None
        self.node = None
        self.pod = None

    # log查找功能
    def query(self, mode: str, node: str, pod: str, size: Union[int, str], start_time:Union[int,datetime,str,None] , end_time:Union[int,datetime,str,None], label=None):
         # 检查查询模式并设置起始和结束时间，以便将其用于查询
        if mode.lower() == 'absolute':

            # 处理 start_time
            if isinstance(start_time, int):
                start_time = datetime.fromtimestamp(start_time)
            if isinstance(start_time, str):
                start_time = int(start_time)
                start_time = datetime.fromtimestamp(start_time)

            # 处理 end_time
            if isinstance(end_time, int):
                end_time = datetime.fromtimestamp(end_time)
            if isinstance(end_time, str):
                end_time = int(end_time)
                end_time = datetime.fromtimestamp(end_time)

        if mode.lower() == 'relative':
            # 格式化 start_time
            regex_pattern = r"(\d+d)?(\d+h)?(\d+m)?(\d+s)?"
            result = re.findall(regex_pattern, start_time)
            output_list = [group for group in result[0] if group]  # 移除空字符串
            # 调整时区
            basetime = 'now+8h'
            start_time_str='-'.join(output_list)
            start_time=f'{basetime}-{start_time_str}'
            end_time = 'now'

        if mode.lower() == 'speed':

            if label.lower() == 'today':
                start_time = datetime.combine(date.today(), datetime.min.time())
                end_time = 'now'

            if label.lower() == 'yesterday':
                start_time = datetime.combine(date.today() - timedelta(days=1), datetime.min.time())
                end_time = datetime.combine(date.today(), datetime.min.time())
            
            if label.lower() == 'last_week':
                today = date.today()
                last_monday = date.today() - timedelta(days=today.isoweekday()) - timedelta(days=6)
                start_time = datetime.combine(last_monday, datetime.min.time())
                end_time = start_time + timedelta(weeks=1)
        
        # 处理 size
        if isinstance(size, str):
            size = int(size)

        # 给self.size赋值
        self.size = size

        # 给self.node赋值
        self.node = node

        # 给self.pod赋值
        self.pod = pod

        # 给self.start_time赋值
        self.start_time = start_time

        # 给self.start_time赋值
        self.end_time = end_time
        
        # 定义Elasticsearch查询
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": start_time,
                                    "lte": end_time
                                }
                            }
                        },
                        {
                            "match": {
                                "kubernetes.node.name": node
                            }
                        },
                        {
                            "match": {
                                "kubernetes.pod.name": pod
                            }
                        }
                    ]
                }
            },
            "sort": {
                "@timestamp": {
                    "order": "asc"
                }
            },
            "size": size
        }
        # 使用Elasticsearch搜索查询并返回结果
        try:
            response = self.elastic.search(index=self.index_name, body=query)
            data_query = response['hits']['hits']
        except ConnectionTimeout as e:
            print('Connection Timeout:', e)       
        # print(query)
        return data_query

    # log数据search功能 key value
    def data_search(self, key: str, value: str):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": self.start_time,
                                    "lte": self.end_time
                                }
                            }
                        },
                        {
                            "match": {
                                "kubernetes.node.name": self.node
                            }
                        },
                        {
                            "match": {
                                "kubernetes.pod.name": self.pod
                            }
                        },
                        {
                            "wildcard": {
                                key: {
                                    "value": "*" + value + "*"
                                }
                            }
                        }
                    ]
                }
            },
            "sort": {
                "@timestamp": {
                    "order": "asc"
                }
            },
            "size": self.size
        }
        try:
            response = self.elastic.search(index=self.index_name, body=query)
            data = response['hits']['hits']
        except ConnectionTimeout as e:
            print('Connection Timeout:', e)
        # print(query)
        return data
       
    # log数据search功能 value
    # 目前可以在"message", "kubernetes.*", "event.*", "agent.*"里进行模
    def full_text_search(self, value: str):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": self.start_time,
                                    "lte": self.end_time
                                }
                            }
                        },
                        {
                            "match": {
                                "kubernetes.node.name": self.node
                            }
                        },
                        {
                            "match": {
                                "kubernetes.pod.name": self.pod
                            }
                        },
                        {
                            "multi_match": {
                                "query": value,
                                "fields": ["message", "kubernetes.*", "event.*", "agent.*"],
                                "fuzziness": "AUTO"
                            }
                        }
                    ]
                }
            },
            "sort": {
                "@timestamp": {
                    "order": "asc"
                }
            },
            "size": self.size
        }
        try:
            response = self.elastic.search(index=self.index_name, body=query)
            data = response['hits']['hits']
        except ConnectionTimeout as e:
            print('Connection Timeout:', e)
        return data