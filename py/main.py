"""
sungrow all right reserved

@File : main.py

@Author : zhangzhengguang

@Date : 2020/6/4 10:26

@Desc : 起始文件

"""
from os import getpid
from sys import stdout
from json import dumps
from socket import socket, AF_INET, SOCK_STREAM
from flask import Flask, Response
from sungrow.utils.logutil import LogUtil
from sungrow.utils.jsonutil import JsonUtil
from sungrow.common.businesserror import BusinessError
from sungrow.common.responsemessage import ResponseMessage
from sungrow.common.errorcode import ERROR, SUCCESS
from sungrow.common.constants import SERVICE_HOST, SECRET_KEY
from sungrow.modules.ota import view

# 设置http名称
app = Flask(__name__)
# 配置密钥
app.config['SECRET_KEY'] = SECRET_KEY
app.register_blueprint(view.bp)

log = LogUtil.getLogger(__name__)


@app.errorhandler(Exception)
def handle_exception(e):
    """
    通用异常处理
    :param e: 异常
    :return:
    """
    # pass through HTTP errors
    if isinstance(e, BusinessError):
        # 自定义异常处理
        return Response(JsonUtil.dumps(ResponseMessage(e)), mimetype='application/json')
    else:
        log.error(e.args)
        # 系统异常
        return Response(JsonUtil.dumps(ResponseMessage(ERROR)), mimetype='application/json')


@app.after_request
def response_handle(response):
    """
    结果封装
    :param response: 返回对象
    :return:
    """
    # 如果返回的是json,且是字典不包含result_code
    if response.is_json:
        res_data = response.get_json()
        if isinstance(res_data, dict) and res_data.get("result_code") is not None:
            return response
        else:
            return Response(JsonUtil.dumps(ResponseMessage(SUCCESS, data=res_data)), mimetype='application/json')
    return response


def send_port():
    """获取为被使用的端口号，8081为起始探测值,并返回给前端"""
    # 创建socket对象并进行连接
    # 端口范围
    for port in range(8081, 65535):
        try:
            web_server_socket = socket(AF_INET, SOCK_STREAM)
            web_server_socket.bind((SERVICE_HOST, port))
        except Exception as exception:
            log.debug(exception.args)
        else:
            web_server_socket.close()
            stdout.write(dumps({"name": "set-info", "port": port, "pid": getpid()}))
            stdout.flush()
            return port


if __name__ == '__main__':
    # 获取为被使用的端口号，8081为起始探测值,并返回给前端
    app_port = send_port()

    # 服务启动
    app.run(host=SERVICE_HOST, port=app_port, debug=False)
