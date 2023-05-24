from yaml import full_load
from trace_get.trace_api import traceAPI

# 这段代码在 `trace_app` 应用程序加载时运行,仅被调用一次

# 读取配置文件
config = full_load(open("trace_config.yaml", "r"))
# 实例化traceAPI类对象并查询数据
trace1 = traceAPI(config['api'], config['username'], config['password'], config['index'])