"""
sungrow all right reserved

@File : num_uitls.py

@Author : zhangzhengguang@sungrowpower.com

@Date : 2020/01/04:10:00

@Desc : 数字 工具类

"""
from struct import unpack, pack
from sungrow.common.businesserror import BusinessError
from sungrow.common.errorcode import PARAMETER_ERR0R
from array import array


class NumberUtil(object):
    """数字工具类"""

    TYPE_MAPPING = {'S32': {'len': 4, 'format': 'i'}, 'U32': {'len': 4, 'format': 'I'},
                    'S16': {'len': 2, 'format': 'h'}, 'U16': {'len': 2, 'format': 'H'},
                    'U64': {'len': 8, 'format': 'Q'}, 'S64': {'len': 8, 'format': 'q'}}

    @classmethod
    def to_hex_str(cls, num, _len):
        """
        把十进制数字转成16进制字符串，长度_len
        :param num: 待转换数据
        :param _len: 输出字符串长度
        :return: 如02
        """
        if num > -1:
            temp = hex(num)[2:]
            return ('0' * (_len - len(temp)) + temp).upper()
        else:
            return (hex(num & int('f' * _len, 16))[2:]).upper()

    @classmethod
    def str_to_hex(cls, data_str, len_):
        """
        把字符串转成16进制字符串，长度_len
        :param data_str: 待转换数据
        :param len_: 输出字符串长度
        :return: 如02000000
        """
        temp = str(data_str).encode('utf8')
        if len_ <= 2 * len(temp):
            return temp.hex()[:len_]
        else:
            pos = len_ - 2 * len(temp)
            return temp.hex() + '0' * pos

    @classmethod
    def str_to_int(cls, data_str, data_type=None):
        """
        把字符串转成10进制数字
        :param data_str: 待转换数据
        :param data_type: 待转换数据类型
        :return: 如16
        """

        if data_str.startswith('0x') or data_str.startswith('0X'):
            if data_type in cls.TYPE_MAPPING:
                num, = unpack('>' + cls.TYPE_MAPPING[data_type]['format'], bytes.fromhex(data_str[2:]))
            else:
                num = int(data_str, 16)
            return num
        else:
            return int(data_str, 10)

    @classmethod
    def str_to_hex(cls, data_str, len_):
        """
        把字符串转成16进制字符串，长度_len
        :param data_str: 待转换数据
        :param len_: 输出字符串长度
        :return: 如02000000
        """
        temp = str(data_str).encode('utf8')
        if len_ <= 2 * len(temp):
            return temp.hex()[:len_]
        else:
            pos = len_ - 2 * len(temp)
            return temp.hex() + '0' * pos

    @classmethod
    def to_hex_str_by_type(cls, data, data_type: str, data_len: int = None):
        """
        把十进制数字或字符串转成16进制字符串，按data_type类型转换
        :param data: 待转换数据
        :param data_type: 数据类型 支持'S32', 'U32', 'S16', 'U16', 'U64', 'S64', 'UTF8'
        :param data_len: 生成的字节长度
        :return: 如02
        """
        # 入参不能为空
        if data is None or not data_type or data_len is None:
            raise BusinessError(PARAMETER_ERR0R)
        # 字符串转换
        if data_type in {'UTF8'}:
            res = data.encode().hex()
            if not data_len:
                return res
            offset = data_len * 2 - len(res)
            if offset > 0:
                return res + offset * '0'
            elif offset == 0:
                return res
            else:
                return res[:offset]
        # 数字类转换
        if data_type in cls.TYPE_MAPPING:
            type_temp = cls.TYPE_MAPPING[data_type]
            if isinstance(data, str):
                data = cls.str_to_int(data, data_type)
            byte_arr = pack('>{}'.format(type_temp['format']), data)
        else:
            raise BusinessError(PARAMETER_ERR0R)
        res = bytearray()
        for i in range(len(byte_arr) >> 1, 0, -1):
            res.extend(byte_arr[(i - 1) * 2:i * 2])
        return res.hex()

    @classmethod
    def parse_hex(cls, data, data_type=None):
        """
        将16进制字符串根据类型转为正确的内容
        :param data: 待转换数据
        :param data_type: 数据类型
        """
        if data_type == 'UTF8':
            return bytes.fromhex(data).rstrip(b'\00').decode()
        if data_type in cls.TYPE_MAPPING:
            type_temp = cls.TYPE_MAPPING[data_type]
            try:
                num, = unpack('>{}'.format(type_temp['format']), cls.reverse_words(bytes.fromhex(data)))
            except:
                # 数据中存在很多数据类型和长度不匹配得情况，此时为空
                return ''
            return num
        else:
            return int(data, 16)

    @classmethod
    def to_words(cls, data, data_type):
        """
        把十进制数字或字符串转成0-65535的数字数组，按data_type类型转换
        :param data: 待转换数据
        :param data_type: 数据类型 支持'S32', 'U32', 'S16', 'U16', 'U64', 'S64', 'UTF8'
        :return: 如02
        """
        if data_type == 'UTF8':
            byte_arr = bytearray(data, 'utf8')
            if len(byte_arr) % 2 != 0:
                byte_arr.append(0)
            return [unpack('>H', byte_arr[i * 2:(i + 1) * 2])[0] for i in range(len(byte_arr) // 2)]
        if data_type in cls.TYPE_MAPPING:
            byte_arr = pack('>{}'.format(cls.TYPE_MAPPING[data_type]['format']), data)
        else:
            raise BusinessError(PARAMETER_ERR0R)
        return [unpack('>H', byte_arr[(i - 1) * 2:i * 2])[0] for i in range(len(byte_arr) // 2, 0, -1)]

    @classmethod
    def parse_words(cls, words, data_type):
        """
        把0-65535的数字数组转成十进制数字或字符串，按data_type类型转换
        :param words: 待转换数据
        :param data_type: 数据类型 支持'S32', 'U32', 'S16', 'U16', 'U64', 'S64'，'UTF8'
        :return: 如02
        """
        words = list(words)
        if data_type == 'UTF8':
            res = pack('>{}H'.format(len(words)), *words)
            return res.rstrip(b'\00').decode()
        if data_type in cls.TYPE_MAPPING:
            words.reverse()
            byte_arr = pack('>{}H'.format(len(words)), *words)
            res, = unpack('>{}'.format(cls.TYPE_MAPPING[data_type]['format']), byte_arr)
            return res
        else:
            raise BusinessError(PARAMETER_ERR0R)

    @classmethod
    def reverse_words(cls, data):
        """
        把字节数组按两个字节翻转
        :param data: 字节数组
        :return: 翻转过的字节数组
        """
        arr = array('H', data)
        arr.reverse()
        return arr.tobytes()
