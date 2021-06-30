"""
sungrow all right reserved

@File : encrypt_utils.py

@Author : zhangzhengguang@sungrowpower.com

@Date : 2020/01/04:10:00

@Desc : 加密工具类

"""
from hashlib import md5 as lib_md5


class EncryptUtil(object):
    """加密工具类"""

    # 每次处理文件大小 默认1兆
    _FILE_PART_SIZE = 1048576

    @classmethod
    def md5(cls, origin):
        """字符串md5加密"""
        # 创建md5对象
        md5_ = lib_md5()
        # 因为python3里默认的str是unicode,所以此处必须encode
        md5_.update(origin.encode(encoding='utf-8'))
        return md5_.hexdigest()

    @classmethod
    def file_md5(cls, file):
        """文件md5加密"""
        # 创建md5对象
        md5_ = lib_md5()
        while True:
            # 读取文件一次1兆
            tmp_data = file.read(cls._FILE_PART_SIZE)
            if not tmp_data:
                break
            md5_.update(tmp_data)
        return str(md5_.hexdigest()).upper()


if __name__ == '__main__':
    print(EncryptUtil.md5('DE5B8AE14832431DB737B8006E7B21C3159255657032879A65DA71F4D8CAC2023FAE4C39B4589'))
