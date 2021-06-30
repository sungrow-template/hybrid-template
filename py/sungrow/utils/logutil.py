"""
sungrow all right reserved

@File : logutil.py

@Author : zhangzhengguang@sungrowpower.com

@Date : 2020/01/04:10:00

@Desc : log 工具类

"""
import logging
from os import makedirs
from shutil import rmtree
from pathlib import Path
from os.path import exists, join
from sungrow.common import constants
from sungrow.utils.datetimeutil import DateTimeUtil

LOG_PATH = getattr(constants, 'LOG_PATH', '') or join(constants.ROOT_PATH, 'userdata', 'logs')
# 保留指定的文件夹个数，多余的删除
if exists(LOG_PATH):
    log_max = (getattr(constants, 'LOG_MAX_COUNT', '') or 500) - 1
    p = Path(LOG_PATH)
    ps = sorted((x for x in p.iterdir() if x.is_dir()), reverse=True)
    while len(ps) > log_max:
        rmtree(ps.pop())

LOG_PATH = join(LOG_PATH, DateTimeUtil.get_date_time_str(DateTimeUtil.DATE_TIME_FORMAT_NONE), '')
LOG_LEVEL = getattr(constants, 'LOG_LEVEL', '')

LEVEL_MAP = {"debug": logging.DEBUG, "info": logging.INFO, "warn": logging.WARN, "error": logging.ERROR,
             "fatal": logging.FATAL}

if not exists(LOG_PATH):
    makedirs(LOG_PATH)
logname = LOG_PATH + 'out.log'  # 指定输出的日志文件名
# 创建一个handler，用于写入日志文件
fh = logging.FileHandler(logname, encoding='utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码

# 创建一个handler，用于将日志输出到控制台
ch = logging.StreamHandler()
# 定义handler的输出格式
formatter = logging.Formatter(
    '%(asctime)s-%(process)d-%(thread)d-%(threadName)s-%(levelname)s-%(name)s:%(lineno)d:%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
root = logging.getLogger()
root.addHandler(fh)
root.addHandler(ch)

if LOG_LEVEL:
    for name, _level in LOG_LEVEL.items():
        logging.getLogger(name).setLevel(LEVEL_MAP.get(_level.lower()))


class LogUtil(object):
    """log 工具类"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def getLogger(cls, loggername, level=None):
        """定义一个函数，回调logger实例"""
        # 创建一个logger
        logger = logging.getLogger(loggername)
        if level:
            logger.setLevel(level)
        return logger
