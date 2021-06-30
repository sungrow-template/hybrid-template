"""
sungrow all right reserved

@File : constants.py

@Author : Peng Jie

@Date : 2020/3/3 11:04

@Desc : 配置常量

"""
from sys import argv
from os.path import join, dirname

# main 所在路径，即根目录,如 D:/git/baseframework/base-electron/py/
ROOT_PATH = join(dirname(argv[0]), '')

# 获取最新版本地址
OTA_GET_VERSION_URL = 'https://api.isolarcloud.com:8770/otaService/version/getVersion'
# OTA提供的产品代码
OTA_PRODUCT_CODE = 'FFFFA71FD7084ACD88678B335F04046A'
# OTA提供的产品秘钥
OTA_SECRET = '14D0442E787B4F2AD4C90CA2A8FC6A47'
# 固定的sys_code，必传
OTA_SYS_CODE = '920'
#  固定的秘钥appkey， 必传
OTA_APPKEY = 'D021A0CB31EE7136C0A6A627C62C868E'

# flask密钥
SECRET_KEY = b'z\xbc\xba\x87\x06\xfb\xf9\xec\x08\xf5\xc9]\x01\n\xaa\xe1'

# 服务地址
SERVICE_HOST = "127.0.0.1"

# 各路径日志级别
LOG_LEVEL = {"werkzeug": "error", "": "debug"}
# 日志保留最大个数
LOG_MAX_COUNT = 10


