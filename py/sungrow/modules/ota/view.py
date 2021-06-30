"""
sungrow all right reserved

@File : view.py

@Author : 张争光

@Date : 2020/06/20:10:33

@Desc :OTA在线升级

"""
from os.path import basename, dirname, join
from os import rename, mkdir
import sys
import json
from time import time
from sungrow.common import constants
from flask import request, Blueprint
from sungrow.utils.httputil import HttpUtil
from sungrow.utils.encryptutil import EncryptUtil
from sungrow.common.businesserror import BusinessError
from sungrow.common.errorcode import UPDATE_PACK_ERROR, HTTP_RESULT_ERROR, PARAMETER_ERR0R, HTTP_ERROR
from sungrow.common.responsemessage import response_message_json
from sungrow.utils.logutil import LogUtil
from shutil import rmtree


# 每次处理文件大小 默认1兆
_FILE_PART_SIZE = 1048576

_DOWNLOADING_SUFFIX = '.downloading'

bp = Blueprint('ota', __name__, url_prefix='/ota')

_log = LogUtil.getLogger(__name__)

# 获取的最新版本信息
_version_info = {}


@bp.route('/get_version', methods=['POST'])
@response_message_json
def get_version():
    """
    获取最新版本升级包信息
    :return: dict
    """
    data = request.json
    product_code = data.get('product_code')
    if not product_code or not product_code.startswith('v'):
        raise BusinessError(code=PARAMETER_ERR0R)
    time_str = str(round(time() * 1000))
    # MD5值
    md5 = EncryptUtil.md5(constants.OTA_PRODUCT_CODE + time_str + constants.OTA_SECRET)
    # 获取当前版本升级包信息
    try:
        version_info = HttpUtil.post(constants.OTA_GET_VERSION_URL, get_all=True, json={
            'product_code': constants.OTA_PRODUCT_CODE,
            'send_time': time_str,
            'sign': md5,
            'sys_code': constants.OTA_SYS_CODE,
            'appkey': constants.OTA_APPKEY
        })
    except Exception as e:
        _log.warning('ota get version error: {}'.format(e))
        raise BusinessError(code=HTTP_ERROR)
    else:
        # 有数据且与原版本不一致则更新
        if version_info and version_info.get('result_code') == '1':
            _version_info.clear()
            res_data = version_info.get('result_data')
            if res_data and res_data.get("version_number") != product_code:
                _version_info.update(version_info.get('result_data'))
            return _version_info
        else:
            # 如果没有信息则说明为第一个版本，即最新版本
            if version_info['result_code'] == 'OTA_15':
                _version_info.clear()
                return
            else:
                _version_info.clear()
                raise BusinessError(code=HTTP_RESULT_ERROR, data=_version_info)


@bp.route('/new_version_download', methods=['POST'])
@response_message_json
def new_version_download():
    """
    下载最新升级包
    :return:
    """
    json_data = request.json
    # 获取下载路径
    file_path = json_data.get('file_path')
    # 如果没有下载完成会是一个加downloading的文件
    file_name = basename(file_path)
    file_path = dirname(file_path)
    # 先清空下载路径下所有文件
    rmtree(file_path)
    mkdir(file_path)
    file_full_name = join(file_path, file_name + _DOWNLOADING_SUFFIX)
    temp_size = 0
    file_data = HttpUtil.get(_version_info['resource_url'], stream=True, verify=False)
    # 下载升级包
    with open(file_full_name, "wb") as f:
        file_length = _version_info['size']
        for chunk in file_data.iter_content(chunk_size=_FILE_PART_SIZE):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
                ###这是下载实现进度显示####
                flag = '1' if temp_size == file_length else '0'
                sys.stdout.write(json.dumps({'name': 'ota', 'code': '1', 'flag': flag,
                                             'procss': "%d" % (100 * temp_size / file_length)}))
                sys.stdout.flush()

    # 检查下载文件
    _check_file(file_path, file_name, temp_size)


def _check_file(file_path, file_name, temp_size):
    """
    检查文件的完整性
    :param file_path: 文件路径
    :param file_name: 文件名
    :param temp_size: 已下载文件大小
    :return:
    """
    file_full_name = join(file_path, file_name + _DOWNLOADING_SUFFIX)
    """做MD5处理，与OTA传来的MD5进行校验，若为一样，则下载完毕，自动打开，若不一样则提示：下载错误是否重新下载"""
    length = _version_info.get('size')
    resource_hash = _version_info.get('resource_hash')
    # 文件大小校验
    if temp_size < length:
        raise BusinessError(UPDATE_PACK_ERROR)
    with open(file_full_name, "rb") as f:
        file_md5 = EncryptUtil.file_md5(f)

    # file md5值校验
    if file_md5 != resource_hash:
        raise BusinessError(UPDATE_PACK_ERROR)

    new_name = join(file_path, file_name)
    # 修改文件后缀
    rename(file_full_name, new_name)
