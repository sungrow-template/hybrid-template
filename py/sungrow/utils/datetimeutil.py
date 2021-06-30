"""
sungrow all right reserved

@File : datetimeutil.py

@Author : zhangzhengguang@sungrowpower.com

@Date : 2020/09/14 11:00

@Desc : 日期时间工具类

"""
from datetime import datetime


class DateTimeUtil(object):
    """日期时间工具类"""

    # 日期时间格式化
    DATE_TIME_FORMAT_NONE = '%Y%m%d%H%M%S'

    @classmethod
    def get_date_time_str(cls, _format, tz=None):
        """
        把当前日期按 format格式输出为字符串
        :param _format: 字符串输出格式
        :param tz: 时区
        :return: 如'2020-09-01 00:00:00'
        """
        return datetime.now(tz).strftime(_format)


if __name__ == '__main__':
    print(DateTimeUtil.get_date_time_str(DateTimeUtil.DATE_TIME_FORMAT_NONE))
