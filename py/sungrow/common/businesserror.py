"""
sungrow all right reserved

@File : businesserror.py

@Author : zhangzhengguang

@Date : 2020/06/17:10:33

@Desc : 自定义异常

"""


class BusinessError(Exception):
    """自定义异常"""

    def __init__(self, code, message=None, data=None):
        # 如果第一个参数为字典则特殊处理
        if isinstance(code, dict):
            self.error_code = code.get('code')
            self.error_msg = code.get('message')
            self.error_data = data
        else:
            self.error_code = code
            self.error_msg = message
            self.error_data = data
