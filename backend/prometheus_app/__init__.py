from prometheus.prometheus_api import PrometheusAPI
from yaml import full_load

# 这段代码在 `prometheus_app` 应用程序加载时运行,仅被调用一次

# 读取配置文件
config = full_load(open("prometheus_config.yaml", "r"))
# 实例化PrometheusAPI类对象并查询数据
prom = PrometheusAPI(config["api"])