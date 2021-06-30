"""
sungrow all right reserved

@File : sqlutil.py

@Author : zhangzhengguang@sungrowpower.com

@Date : 2020/06/11:10:00

@Desc : sql 工具类

"""
from sungrow.utils.logutil import LogUtil
from re import compile
from os import listdir
from os.path import splitext, join
from sungrow.common import constants
from xml.etree.ElementTree import parse
from enum import Enum


class SqlFragmentType(Enum):
    """ sql片段类型"""
    # 字符串
    TEXT = 'text'
    IF = 'if'
    ELSE = 'else'
    TRIM = 'trim'
    FOREACH = 'foreach'


class SqlUtil(object):
    """sqlite 工具类"""
    _log = LogUtil.getLogger(__name__)

    KEY_MATCH = compile(r'#{([][\'\"\w]+)}|:(\w+)')

    KEY_DOLLAR_MATCH = compile(r'\${([][\'"\w]+)}')

    SPACE_MATCH = compile('\s+')
    # sql文件所在路径
    _SQL_PATH = getattr(constants, 'SQL_PATH', '') or join(constants.ROOT_PATH, 'static', 'sql', 'sqlite')

    _slq_map = {}

    @classmethod
    def get_sql(cls, _id, data):
        """
        根据入参动态拼接sql语句"
        :param _id: sql文件名 + . + id
        :param data: 定义sql时所有的变量字典，如果缺失将报错
        :return: 
        """""
        if isinstance(data, dict):
            pass
        elif isinstance(data, list) and isinstance(data[0], dict):
            data = data[0]
        else:
            data = {}

        def dollar_replace(m):
            """
            匹配${aa}并处理
            :param m: 匹配到的组
            :return:
            """
            name = m.group(1)
            return str(eval(name, data))

        sql_cfg = cls._slq_map.get(_id)
        if sql_cfg:
            sql_list = cls.__get_sql_fragment(sql_cfg, data)
            return cls.KEY_DOLLAR_MATCH.sub(dollar_replace, cls.SPACE_MATCH.sub(' ', ' '.join(sql_list)))
        else:
            return ''

    @classmethod
    def __get_sql_fragment(cls, sql_cfg, data):
        """解析元素对象"""

        sql_list = []
        for i in range(len(sql_cfg)):
            cfg = sql_cfg[i]
            if cfg.get("type") == SqlFragmentType.TEXT:
                sql_list.append(cfg.get("data"))
            # if标签解析
            elif cfg.get("type") == SqlFragmentType.IF:
                try:
                    result = eval(cfg.get('test'), data)
                except:
                    result = False
                if result:
                    sql_list.append(cfg.get('data'))
                    if cfg.get('children'):
                        sql_children = cls.__get_sql_fragment(cfg.get('children'), data)
                        sql_list.extend(sql_children)
                # else标签解析
                else:
                    if i < len(sql_cfg) - 1 and sql_cfg[i + 1].get('type') == SqlFragmentType.ELSE:
                        sql_list.append(sql_cfg[i + 1].get('data'))
                        if sql_cfg[i + 1].get('children'):
                            sql_children = cls.__get_sql_fragment(sql_cfg[i + 1].get('children'), data)
                            sql_list.extend(sql_children)
            # 处理foreach
            elif cfg.get("type") == SqlFragmentType.FOREACH:
                if cfg.get('open'):
                    sql_list.append(cfg.get('open'))
                collection = cfg.get('collection')
                item_list = data.get(cfg.get('collection'))
                if not isinstance(item_list, list):
                    data[cfg.get('collection')] = [x for x in item_list]
                if item_list:
                    for n in range(len(item_list)):
                        def repl_foreach(m):
                            """处理foreach表达式"""
                            match_str = m.group(0)
                            if cfg.get('item'):
                                match_str = match_str.replace(cfg.get('item'), collection + '[' + str(n) + ']')
                            if cfg.get('index'):
                                match_str = match_str.replace(cfg.get('index'), str(n))
                            return match_str

                        sql_list.append(cls.KEY_DOLLAR_MATCH.sub(
                            repl_foreach, cls.KEY_MATCH.sub(repl_foreach, cfg.get('data'))))
                        if cfg.get('separator'):
                            sql_list.append(cfg.get('separator'))
                    if cfg.get('separator'):
                        sql_list.pop()
                if cfg.get('close'):
                    sql_list.append(cfg.get('close'))
            # 处理trim标签
            elif cfg.get("type") == SqlFragmentType.TRIM:
                if cfg.get('children'):
                    sql_children = cls.__get_sql_fragment(cfg.get('children'), data)
                    sql_children = list(filter(lambda a: a and not a.isspace(), sql_children))
                    if sql_children:
                        sql_str = ' '.join(sql_children)
                        # 处理前后缀
                        prefix_overrides = cfg.get('prefixOverrides')
                        if prefix_overrides:
                            prefix_overrides = prefix_overrides.split('|')
                            sql_str = sql_str.strip()
                            for prefix_override in prefix_overrides:
                                sql_str = sql_str.lstrip(prefix_override)
                        suffix_overrides = cfg.get('suffixOverrides')
                        if suffix_overrides:
                            suffix_overrides = suffix_overrides.split('|')
                            sql_str = sql_str.strip()
                            for suffix_override in suffix_overrides:
                                sql_str = sql_str.rstrip(suffix_override)
                        if cfg.get('prefix'):
                            sql_list.append(cfg.get('prefix'))
                        sql_list.append(sql_str)
                        if cfg.get('suffix'):
                            sql_list.append(cfg.get('suffix'))

        return sql_list

    @classmethod
    def parse_sql_xml(cls):
        """解析sql文件夹下所有xml文件，并加载到内存中"""
        for a in listdir(cls._SQL_PATH):
            s = splitext(a)
            if s[1] == '.xml':
                with open(join(cls._SQL_PATH, a), encoding='utf-8') as cfg:
                    cls.__load_sql_xml(cfg, s[0])

    @classmethod
    def __load_sql_xml(cls, f, name):
        """ 解析xml数据"""
        root = parse(f).getroot()
        # 遍历各sql
        sql_list = list(root)
        for sql in sql_list:
            # sql包含的元素
            sql_children = []
            # 统一保存到缓存中
            cls._slq_map[name + '.' + sql.get('id')] = sql_children
            # 元素开头的sql
            if sql.text and not sql.text.isspace():
                sql_children.append({"type": SqlFragmentType.TEXT, "data": sql.text.strip()})
            for sql_fragment in list(sql):
                sql_children.append(cls.__parse_sql_fragment(sql_fragment))
                # 元素开头的sql
                if sql_fragment.tail and not sql_fragment.tail.isspace():
                    sql_children.append({"type": SqlFragmentType.TEXT, "data": sql_fragment.tail.strip()})

    @classmethod
    def __parse_sql_fragment(cls, sql):
        """解析sql中的标签"""
        data = {"type": SqlFragmentType(sql.tag), "data": sql.text.strip()}
        data.update(sql.attrib)
        sql_children = list(sql)
        if sql_children:
            children = []
            for sql_fragment in sql_children:
                children.append(cls.__parse_sql_fragment(sql_fragment))
                # 元素开头的sql
                if sql_fragment.tail and not sql_fragment.tail.isspace():
                    children.append({"type": SqlFragmentType.TEXT, "data": sql_fragment.tail.strip()})
            data['children'] = children
        return data


# 加载模块时加载sql模板信息
SqlUtil.parse_sql_xml()

if __name__ == '__main__':
    SqlUtil.parse_sql_xml()
