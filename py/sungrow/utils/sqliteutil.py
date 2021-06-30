"""
sungrow all right reserved

@File : sqliteutil.py

@Author : zhangzhengguang@sungrowpower.com

@Date : 2020/06/04:10:00

@Desc : sqlite 工具类

"""
from sqlite3 import connect
from threading import RLock
from os.path import join, exists
from os import makedirs, remove, rename
from shutil import copy
from functools import wraps
from sungrow.common import constants
from sungrow.utils.logutil import LogUtil
from sungrow.utils.sqlutil import SqlUtil

_log = LogUtil.getLogger(__name__)


class SqliteUtil(object):
    """sqlite 工具类"""

    # 默认数据库连接
    _conn = None
    # 串行数据库锁
    _lock = RLock()

    DB_PATH = getattr(constants, 'DB_PATH', '') or join(constants.ROOT_PATH, 'userdata', 'userdb', '')

    _DB_NAME = getattr(constants, 'DB_NAME', '') or 'sqlite.db'

    DB_TEMPLATE_PATH = getattr(constants, 'DB_TEMPLATE_PATH', '') or join(constants.ROOT_PATH, 'static', 'db', '')

    @classmethod
    def get_cursor(cls):
        """
        获取数据库连接
        :return:
        """
        if not cls._conn:
            cls._conn = connect(join(cls.DB_PATH, cls._DB_NAME), check_same_thread=False)
        return cls._conn.cursor()

    @classmethod
    def upgrade_db(cls):
        """
        升级数据库文件
        :return:
        """
        # 初始化判断数据库是否存在，否则复制同级目录数据库到用户目录
        user_db_name = join(cls.DB_PATH, cls._DB_NAME)
        root_db_name = join(cls.DB_TEMPLATE_PATH, cls._DB_NAME)
        if not exists(cls.DB_PATH):
            makedirs(cls.DB_PATH)
        if not exists(user_db_name):
            copy(root_db_name, user_db_name)
        else:
            # 比较数据库版本是否一致
            root_connect = connect(root_db_name)
            root_version = cls.select_one(sql_id="sqliteutil.select_db_version", con=root_connect)
            root_connect.close()

            user_version = cls.select_one(sql_id="sqliteutil.select_db_version")
            # 如果两个版本不一致，则需要升级数据库
            if root_version.get("value") != user_version.get("value"):
                temp_db_name = user_db_name + '.temp'
                copy(root_db_name, temp_db_name)
                dist_connect = connect(temp_db_name)
                cls.copy_db(cls._conn, dist_connect)
                dist_connect.close()
                cls._conn.close()
                cls._conn = None
                # 删除原文件，并把目标文件改成数据源名
                remove(user_db_name)
                rename(temp_db_name, user_db_name)

        return True

    @classmethod
    def copy_db(cls, source, dist):
        """
        复制数据库数据
        :param source:
        :param dist:
        :return:
        """
        # 比较两数据源表
        source_tables = cls.select_list(sql_id='sqliteutil.select_db_table', con=source)
        dist_tables = cls.select_list(sql_id='sqliteutil.select_db_table', con=dist)
        source_tables_set = set(x.get('name') for x in source_tables)
        dist_tables_set = set(x.get('name') for x in dist_tables)
        # 计算共有表数据
        same_tables = dist_tables_set.intersection(source_tables_set)
        # 复制每一个相同表的数据
        if same_tables:
            for same_table in same_tables:
                source_columns = cls.select_list(sql_id='sqliteutil.select_table_column',
                                                 para={"same_table": same_table}, con=source)
                dist_columns = cls.select_list(sql_id='sqliteutil.select_table_column',
                                               para={"same_table": same_table}, con=dist)
                source_columns_set = set(x.get('name') for x in source_columns)
                dist_columns_set = set(x.get('name') for x in dist_columns)
                # 计算共有的列
                same_colmns = source_columns_set.intersection(dist_columns_set)
                # 如果没有id则跳过不处理
                if "id" not in same_colmns:
                    continue
                source_data = cls.select_list(sql_id='sqliteutil.select_table_data',
                                              para={"columns": same_colmns, "table_name": same_table}, con=source)
                # 把查询的每一行插入到新数据库
                if source_data:
                    for row_data in source_data:
                        # 不存在则插入
                        if not cls.select_one(sql_id='sqliteutil.select_source_data',
                                              para={"id": row_data.get("id"), "table_name": same_table}, con=dist):
                            cls.insert(sql_id='sqliteutil.insert_dist_data',
                                       para={"columns": same_colmns, "table_name": same_table,
                                             "data": row_data}, con=dist)
            # 提交事务
            dist.commit()

    @classmethod
    def parse_sql(cls, sql, _para):
        """
        根据带占位符的sql和入参返回符合sqlite3的api入参参数
        :param sql: 字符串，如 insert into test(col) values(#{value})
        :param _para: 字典或列表两种，只有多条插入时才是列表。{'value':1}或[{'value':1},{'value':2}]
        :return: tuple,如 (insert into test(col) values(?),(1,))或(insert into test(col) values(?),[(1,),(2,)])
        """
        key_list = []

        def repl(m):
            key = m.group(1) or m.group(2)
            key_list.append(key)
            return '?'

        sql = SqlUtil.KEY_MATCH.sub(repl, sql)
        if isinstance(_para, dict):
            result = []
            for temp in key_list:
                result.append(eval(temp, _para))
            return sql, tuple(result)
        elif isinstance(_para, list):
            result = []
            for dict_para in _para:
                temp_list = []
                for temp in key_list:
                    temp_list.append(eval(temp, dict_para))
                result.append(tuple(temp_list))
            return sql, result
        else:
            return sql, None

    @classmethod
    def select_one(cls, sql_str=None, sql_id=None, para=None, con=None):
        """
        查询单条数据，返回数据字典
        :param sql_str: 字符串sql支持?,:name,#{name}三种形式入参
        :param sql_id: sql文件中定义的文件名+.+id
        :param para: 如果是？入参则para为列表或元组，如果入参为关键字入参：name,#{name}则para为字典
        :param con: 数据库连接，如果传入con 则使用传入的为数据源
        :return: dict
        """
        with cls._lock:
            sql = sql_str or SqlUtil.get_sql(sql_id, para)
            if isinstance(para, dict):
                sql, para = cls.parse_sql(sql, para)
            cls._log.debug("sql:" + sql)
            cls._log.debug("参数：%s", para)
            # 获取游标
            cu = con.cursor() if con else cls.get_cursor()
            try:
                if para:
                    cu.execute(sql, para)
                else:
                    cu.execute(sql)
                column_array = [d[0] for d in cu.description]
                r = cu.fetchone()
            finally:
                cu.close()
            # 把元祖转换成字典
            if r:
                r = dict(zip(column_array, r))
            return r

    @classmethod
    def select_list(cls, sql_str=None, sql_id=None, para=None, con=None):
        """
         查询数据，返回列表
        :param sql_str: 字符串sql支持?,:name,#{name}三种形式入参
        :param sql_id: sql文件中定义的文件名+.+id
        :param para: 如果是？入参则para为列表或元组，如果入参为关键字入参：name,#{name}则para为字典
        :param con: 数据库连接，如果传入con 则使用传入的为数据源
        :return: list
        """
        with cls._lock:
            sql = sql_str or SqlUtil.get_sql(sql_id, para)
            if isinstance(para, dict):
                sql, para = cls.parse_sql(sql, para)
            cls._log.debug("sql:" + sql)
            cls._log.debug("参数：%s", para)
            # 获取游标
            cu = con.cursor() if con else cls.get_cursor()
            try:
                if para:
                    cu.execute(sql, para)
                else:
                    cu.execute(sql)
                column_array = [d[0] for d in cu.description]
                result_list = cu.fetchall()
            finally:
                cu.close()
            # 把元祖转换成字典
            if result_list:
                result_list = [dict(zip(column_array, r)) for r in result_list]
            return result_list

    @classmethod
    def delete(cls, sql_str=None, sql_id=None, para=None, con=None):
        """
        执行表数据删除
        :param sql_str: 字符串sql支持?,:name,#{name}三种形式入参
        :param sql_id: sql文件中定义的文件名+.+id
        :param para: 如果是？入参则para为列表或元组，如果入参为关键字入参：name,#{name}则para为字典
        :param con: 数据库连接，如果传入con 则使用传入的为数据源
        :return: int 语句影响行数
        """
        sql = sql_str or SqlUtil.get_sql(sql_id, para)
        if isinstance(para, dict):
            sql, para = cls.parse_sql(sql, para)
        cls._log.debug("sql:" + sql)
        cls._log.debug("参数：%s", para)
        # 获取游标
        cu = con.cursor() if con else cls.get_cursor()
        try:
            if para:
                cu.execute(sql, para)
            else:
                cu.execute(sql)
            res = cu.rowcount
        finally:
            cu.close()
        return res

    @classmethod
    def insert(cls, sql_str=None, sql_id=None, para=None, con=None):
        """
        插入数据
        :param sql_str: 字符串sql支持?,:name,#{name}三种形式入参
        :param sql_id: sql文件中定义的文件名+.+id
        :param para: 如果是？入参则para为列表或元组，如果入参为关键字入参：name,#{name}则para为字典
        :param con: 数据库连接，如果传入con 则使用传入的为数据源
        :return int 新增的主键id
        """
        sql = sql_str or SqlUtil.get_sql(sql_id, para)
        if isinstance(para, dict):
            sql, para = cls.parse_sql(sql, para)
        cls._log.debug("sql:" + sql)
        cls._log.debug("参数：%s", para)
        # 获取游标
        cu = con.cursor() if con else cls.get_cursor()
        try:
            if para:
                cu.execute(sql, para)
            else:
                cu.execute(sql)
            return cu.lastrowid
        finally:
            cu.close()

    @classmethod
    def insert_list(cls, sql_str=None, sql_id=None, para=None, con=None):
        """
        插入数据
        :param sql_str: 字符串sql支持?,:name,#{name}三种形式入参
        :param sql_id: sql文件中定义的文件名+.+id
        :param para: 入参为列表，如果是？入参则列表元素为列表或元组，如果入参为关键字入参：name,#{name}则列表元素为字典
        :param con: 数据库连接，如果传入con 则使用传入的为数据源
        :return int 新增的主键id
        """
        sql = sql_str or SqlUtil.get_sql(sql_id, para)
        if isinstance(para, list) and isinstance(para[0], dict):
            sql, para = cls.parse_sql(sql, para)
        cls._log.debug("sql:" + sql)
        cls._log.debug("参数：%s", para)
        # 获取游标
        cu = con.cursor() if con else cls.get_cursor()
        try:
            if para:
                cu.executemany(sql, para)
            else:
                cu.execute(sql)
            return cu.lastrowid
        finally:
            cu.close()

    @classmethod
    def update(cls, sql_str=None, sql_id=None, para=None, con=None):
        """
        更新表数据
        :param sql_str: 字符串sql支持?,:name,#{name}三种形式入参
        :param sql_id: sql文件中定义的文件名+.+id
        :param para: 如果是？入参则para为列表或元组，如果入参为关键字入参：name,#{name}则para为字典
        :param con: 数据库连接，如果传入con 则使用传入的为数据源
        :return:int 语句影响行数
        """
        sql = sql_str or SqlUtil.get_sql(sql_id, para)
        if isinstance(para, dict):
            sql, para = cls.parse_sql(sql, para)
        cls._log.debug("sql:" + sql)
        cls._log.debug("参数：%s", para)
        # 获取游标
        cu = con.cursor() if con else cls.get_cursor()
        try:
            if para:
                cu.execute(sql, para)
            else:
                cu.execute(sql)
            res = cu.rowcount
        finally:
            cu.close()
        return res

    @classmethod
    def rollback(cls, con=None):
        return con.rollback() if con else cls._conn.rollback()

    @classmethod
    def commit(cls, con=None):
        return con.commit() if con else cls._conn.commit()

    @classmethod
    def acquire_lock(cls):
        cls._lock.acquire()

    @classmethod
    def release_lock(cls):
        cls._lock.release()


def transactional(f):
    """事务装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            SqliteUtil.acquire_lock()
            data = f(*args, **kwargs)
        except Exception as e:
            SqliteUtil.rollback()
            _log.debug('{}:{}'.format(f.__name__, str(e.args)))
            raise
        else:
            SqliteUtil.commit()
            return data
        finally:
            SqliteUtil.release_lock()

    return decorated_function
