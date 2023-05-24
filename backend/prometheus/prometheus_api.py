from typing import Union
from datetime import datetime
from prometheus_api_client import PrometheusConnect

invalid_metrics = [
    "container_scrape_error",
    "container_ulimits_soft",
    "container_network_receive_packets_dropped_total",
    "container_fs_io_time_seconds_total",
    "container_fs_io_time_weighted_seconds_total",
    "container_fs_limit_bytes",
    "container_fs_read_seconds_total",
    "container_fs_reads_merged_total",
    "container_blkio_device_usage_total"
]

class PrometheusAPI:
     #disable_ssl –（bool）如果设置为 True，将禁用对向 prometheus 主机发出的 http 请求的 SSL 证书验证
    def __init__(self, url: str):
        self.client = PrometheusConnect(url, disable_ssl=True)
    #start_time: Union[int, datetime]表示变量既可以是int型也可以是datetime型
    def query_range(self, metric_name: str, pod: str, start_time: Union[int, datetime,str], end_time: Union[int, datetime,str], step: int = 800):
        # 将int型time数据转换成date型
        if isinstance(start_time, int):
            start_time = datetime.fromtimestamp(start_time)
        if isinstance(end_time, int):
            end_time = datetime.fromtimestamp(end_time)
        # postman测试用例需要，发的是str型
        if isinstance(start_time,str):
            start_time = int(start_time)
            start_time = datetime.fromtimestamp(start_time)
        if isinstance(end_time,str):
            end_time = int(end_time)  # end_time now is end_time = datetime.now() 或 datetime.ut
            end_time = datetime.fromtimestamp(end_time)  # end_time now is end_time = datetime.utc
        
        if metric_name.endswith("_total") or metric_name in ['container_last_seen', 'container_memory_cache', 'container_memory_max_usage_bytes']:
            #拼接prometheus 查询语句
            query = f"rate({metric_name}{{pod=~'{pod}.+'}}[5m])"
        else:
            query = f"{metric_name}{{pod=~'{pod}.+'}}"
        data_raw = self.client.custom_query_range(query, start_time, end_time, step=step)
        
        if len(data_raw) == 0:
            return {"error": f"No data found for metric {metric_name} and pod {pod}"}
        else:
            data = []
            for item in data_raw[0]['values']:
                date_time = datetime.fromtimestamp(int(item[0]))
                float_value = float(item[1])  # float value is needed to be able to add it to the list as a whole.
                data.append({'time': date_time, 'value': float_value})
            return {"data": data}
 # returns data in a dict format
    
    def all_metrics(self):
        '''获取所有的metrics'''
        # 调用prometheus的all_metrics方法获取所有的名称列表
        all_metrics = self.prom.all_metrics()
        all_metrics = list(filter(lambda x: True if x.startswith("container") and not x.startswith("container_fs") and not x.startswith("container_network") and x not in invalid_metrics else False, all_metrics))
        return all_metrics