"""
sungrow all right reserved

@File : httputil.py

@Author : zhangzhengguang@sungrowpower.com

@Date : 2020/06/19:10:00

@Desc : http 工具类

"""
from requests import post as lib_post, get as lib_get, codes
from sungrow.common.errorcode import HTTP_RESULT_ERROR, HTTP_ERROR
from sungrow.common.businesserror import BusinessError


class HttpUtil(object):
    """http 工具类"""

    @classmethod
    def post(cls, url, data=None, json=None, headers=None, timeout=None, get_all=False, **kwargs):
        """
        http post请求
        :param url: 请求地址
        :param data: 字典或元组列表
        :param json:json数据
        :param headers:表头，默认{'Content-Type': 'application/json'}
        :param timeout:超时时间 ，默认20秒
        :param get_all:
        :param kwargs:
        :return:
        """
        # 设置默认消息头 默认json数据
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        if headers['Content-Type'] is None:
            headers['Content-Type'] = 'application/json'
        res = lib_post(url, data=data, json=json, headers=headers, timeout=timeout or 20, **kwargs)

        # 处理相应
        if res.status_code == codes.ok:
            # 如果是json数据则返回json
            if str(res.headers['Content-Type']).startswith('application/json'):
                res_json = res.json()
                # 判断结果正确性 1为成功 其他为失败
                if get_all:
                    return res_json
                elif res_json['result_code'] != '1':
                    raise BusinessError(code=HTTP_RESULT_ERROR, data=res_json)
                else:
                    return res_json['result_data']
            else:
                return res
        else:
            raise BusinessError(HTTP_ERROR)

    @classmethod
    def get(cls, url, params=None, timeout=None, **kwargs):
        return lib_get(url, params=params, timeout=timeout or 10, **kwargs)
