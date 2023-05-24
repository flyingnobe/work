from yaml import full_load
from log.log_api import logAPI

# 这段代码在 `log_app` 应用程序加载时运行,仅被调用一次

# 读取配置文件
config = full_load(open("log_config.yaml", "r"))
# 实例化logAPI类对象并查询数据
log = logAPI(config['api'], config['username'], config['password'], config['index'])