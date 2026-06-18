"""
数据访问层（Repository/DAO）
封装SQL Server数据库访问操作，提供统一的数据访问接口
使用ODBC Driver 17 for SQL Server
连接参数通过环境变量配置，参见 .env.example
"""
import os
import pyodbc
from typing import Dict, List, Optional, Any, Tuple


class MssqlRepository:
    """SQL Server数据仓库类，封装所有数据库访问操作"""

    def __init__(
        self,
        server: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: Optional[str] = None,
    ):
        """
        初始化SQL Server数据仓库。
        参数优先使用传入值，未传入时从环境变量读取：
        MSSQL_SERVER, MSSQL_DATABASE, MSSQL_USERNAME, MSSQL_PASSWORD, MSSQL_DRIVER

        参数:
        - server: 服务器地址
        - database: 数据库名称
        - username: 用户名
        - password: 密码
        - driver: ODBC驱动名称
        """
        self.connection_string = self._build_connection_string(
            server=server,
            database=database,
            username=username,
            password=password,
            driver=driver,
        )

    def _build_connection_string(
        self,
        server: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: Optional[str] = None,
    ) -> str:
        driver = driver or os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")
        server = server or os.getenv("MSSQL_SERVER", "")
        database = database or os.getenv("MSSQL_DATABASE", "master")
        username = username or os.getenv("MSSQL_USERNAME", "")
        password = password or os.getenv("MSSQL_PASSWORD", "")
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )

    def _get_connection(self) -> pyodbc.Connection:
        """获取数据库连接"""
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except pyodbc.Error as e:
            raise ConnectionError(f"数据库连接失败: {str(e)}")

    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        执行查询SQL，返回字典列表

        参数:
        - sql: SQL查询语句
        - params: SQL参数（用于参数化查询）

        返回:
        - 查询结果列表，每行为一个字典
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # 处理日期类型转为字符串
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[col] = value
                result.append(row_dict)
            return result
        finally:
            conn.close()

    def execute_scalar(self, sql: str, params: Optional[tuple] = None) -> Any:
        """
        执行查询SQL，返回单个值

        参数:
        - sql: SQL查询语句
        - params: SQL参数

        返回:
        - 单个查询结果值
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def execute_non_query(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        执行非查询SQL（INSERT/UPDATE/DELETE），返回影响行数

        参数:
        - sql: SQL语句
        - params: SQL参数

        返回:
        - 受影响的行数
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            affected = cursor.rowcount
            conn.commit()
            return affected
        finally:
            conn.close()
