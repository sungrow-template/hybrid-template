"""
sungrow all right reserved

@File : responsemessage.py

@Author : zhangzhengguang

@Date : 2020/06/17:10:33

@Desc : 返回结果

"""
from json import dumps
from flask import Response
from sungrow.common.businesserror import BusinessError
from sungrow.common.errorcode import FAILURE, SUCCESS, ERROR
from sungrow.utils.logutil import LogUtil
from functools import wraps


class ResponseMessage:
    """json返回结果类"""

    def __init__(self, code, message=None, data=None):
        # 如果为字典则分别设置code,message
        if isinstance(code, dict):
            self.result_code = SUCCESS.get("code") if code.get('code') == SUCCESS.get("code") else ERROR.get("code")
            self.result_msg = code.get('message')
            self.result_data = {"code": code.get('code'), "data": data or code.get('data')}
        # 如果为BusinessError，则需各字段转换
        elif isinstance(code, BusinessError):
            self.result_code = FAILURE.get("code")
            self.result_msg = code.error_msg
            self.result_data = {"data": data or code.error_data, "code": code.error_code}
        # 否则 正常设置
        else:
            self.result_code = SUCCESS.get("code") if str(code) == SUCCESS.get("code") else ERROR.get("code")
            self.result_msg = message
            self.result_data = {"data": data, "code": code}


def response_message_json(f):
    """json返回值装饰器"""

    log = LogUtil.getLogger(__name__)

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
        except BaseException as e:
            log.error(e.args)
            raise
        else:
            if not isinstance(result, dict):
                return Response(dumps(result), content_type='application/json')
            else:
                return result

    return decorated_function
