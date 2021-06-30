"""
sungrow all right reserved

@File : jsonutil.py

@Author : zhangzhengguang@sungrowpower.com

@Date : 2020/06/18:10:00

@Desc : json 工具类

"""
from json import dumps

from sungrow.common.responsemessage import ResponseMessage


class JsonUtil(object):
    """JSON相关工具类"""

    @classmethod
    def object_convert(cls, obj):
        return obj.__dict__

    @classmethod
    def dumps(cls, obj, **kwargs):
        # 如果为自定义返回值，则使用自定义转换方法
        if isinstance(obj, ResponseMessage):
            # 设置默认转换方法为自定义的
            if 'default' not in kwargs or not kwargs['default']:
                kwargs['default'] = JsonUtil.object_convert
        return dumps(obj, **kwargs)
