"""
数据访问层（Repository/DAO）
封装CSV文件读取操作，提供统一的数据访问接口
"""
import os
import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path

class DataRepository:
    """数据仓库类，封装所有数据访问操作"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化数据仓库
        
        参数:
        - data_dir: 数据文件目录路径
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise ValueError(f"数据目录不存在: {data_dir}")
    
    def read_csv(self, filename: str) -> pd.DataFrame:
        """
        读取CSV文件
        
        参数:
        - filename: CSV文件名（如 "DimProducts.csv"）
        
        返回:
        - DataFrame对象
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            return df
        except Exception as e:
            raise ValueError(f"读取CSV文件失败 {file_path}: {str(e)}")
    
    def read_all_csvs(self) -> Dict[str, pd.DataFrame]:
        """
        读取data目录下的所有CSV文件
        
        返回:
        - 字典，key为文件名，value为DataFrame
        """
        csv_files = list(self.data_dir.glob("*.csv"))
        result = {}
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8')
                result[csv_file.name] = df
            except Exception as e:
                print(f"警告：读取文件 {csv_file.name} 失败: {str(e)}")
        
        return result
    
    def get_csv_info(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        获取CSV文件信息
        
        参数:
        - filename: 文件名，如果为None则返回所有文件信息
        
        返回:
        - 文件信息字典
        """
        if filename:
            file_path = self.data_dir / filename
            if not file_path.exists():
                return {"error": f"文件不存在: {filename}"}
            
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
                return {
                    "filename": filename,
                    "rows": len(df),
                    "columns": df.columns.tolist(),
                    "column_count": len(df.columns),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "sample_data": df.head(5).to_dict('records')
                }
            except Exception as e:
                return {"error": f"读取文件失败: {str(e)}"}
        else:
            # 返回所有CSV文件信息
            csv_files = list(self.data_dir.glob("*.csv"))
            result = {}
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file, encoding='utf-8')
                    result[csv_file.name] = {
                        "rows": len(df),
                        "columns": df.columns.tolist(),
                        "column_count": len(df.columns)
                    }
                except Exception as e:
                    result[csv_file.name] = {"error": str(e)}
            return result
    
    def query_csv(
        self, 
        filename: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        查询CSV数据（支持过滤和限制）
        
        参数:
        - filename: CSV文件名
        - filters: 过滤条件字典，如 {"StoreId": "S-PAR-01", "ProductId": "P-ICE-001"}
        - limit: 返回记录数限制
        
        返回:
        - 过滤后的DataFrame
        """
        df = self.read_csv(filename)
        
        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if key in df.columns:
                    df = df[df[key] == value]
        
        # 应用限制
        if limit and limit > 0:
            df = df.head(limit)
        
        return df
