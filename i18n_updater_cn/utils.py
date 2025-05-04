#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具类模块，提供日志和文件操作等功能
"""

import os
import sys
import enum
import shutil
import datetime
from pathlib import Path


class Logger:
    """
    日志记录工具
    对应Java版项目中的Log.java
    """
    
    class Level(enum.Enum):
        DEBUG = 0
        INFO = 1
        WARNING = 2
        ERROR = 3
    
    # 当前日志级别
    _level = Level.INFO
    
    # 日志文件
    _log_file = None
    
    @classmethod
    def set_level(cls, level):
        """设置日志级别"""
        cls._level = level
    
    @classmethod
    def set_log_file(cls, path):
        """设置日志文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(path), exist_ok=True)
            cls._log_file = open(path, "a", encoding="utf-8")
        except Exception as e:
            print(f"打开日志文件失败: {e}", file=sys.stderr)
    
    @classmethod
    def _log(cls, level, message):
        """记录日志"""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{now}] [{level.name}]: {message}\n"
        
        # 写入日志文件
        if cls._log_file:
            try:
                cls._log_file.write(log_line)
                cls._log_file.flush()
            except Exception as e:
                print(f"写入日志文件失败: {e}", file=sys.stderr)
        
        # 根据日志级别输出到控制台
        if level.value >= cls._level.value:
            if level == cls.Level.ERROR or level == cls.Level.WARNING:
                print(log_line, end='', file=sys.stderr)
            else:
                print(log_line, end='')
    
    @classmethod
    def debug(cls, message, *args):
        """记录调试日志"""
        if args:
            message = message % args
        cls._log(cls.Level.DEBUG, message)
    
    @classmethod
    def info(cls, message, *args):
        """记录信息日志"""
        if args:
            message = message % args
        cls._log(cls.Level.INFO, message)
    
    @classmethod
    def warning(cls, message, *args):
        """记录警告日志"""
        if args:
            message = message % args
        cls._log(cls.Level.WARNING, message)
    
    @classmethod
    def error(cls, message, *args):
        """记录错误日志"""
        if args:
            message = message % args
        cls._log(cls.Level.ERROR, message)


class FileUtil:
    """
    文件操作工具
    对应Java版项目中的FileUtil.java
    """
    
    # 资源包目录
    _resource_pack_dir = None
    
    # 临时目录
    _temporary_dir = None
    
    @classmethod
    def set_resource_pack_dir(cls, path):
        """设置资源包目录"""
        cls._safe_create_dir(path)
        cls._resource_pack_dir = path
    
    @classmethod
    def set_temporary_dir(cls, path):
        """设置临时目录"""
        cls._safe_create_dir(path)
        cls._temporary_dir = path
    
    @staticmethod
    def _safe_create_dir(path):
        """安全地创建目录"""
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            Logger.warning(f"创建目录失败: {path}, 错误: {e}")
    
    @classmethod
    def get_resource_pack_path(cls, filename):
        """获取资源包路径"""
        if cls._resource_pack_dir is None:
            raise ValueError("资源包目录未设置")
        return Path(cls._resource_pack_dir) / filename
    
    @classmethod
    def get_temporary_path(cls, filename):
        """获取临时文件路径"""
        if cls._temporary_dir is None:
            raise ValueError("临时目录未设置")
        return Path(cls._temporary_dir) / filename
    
    @classmethod
    def sync_tmp_file(cls, file_path, tmp_file_path, save_to_game=True):
        """
        同步临时文件和目标文件
        
        Args:
            file_path: 目标文件路径
            tmp_file_path: 临时文件路径
            save_to_game: 是否保存到游戏目录
        """
        # 两个文件都不存在
        if not os.path.exists(file_path) and not os.path.exists(tmp_file_path):
            Logger.debug("两个文件都不存在，无需同步")
            return
        
        # 比较两个文件的修改时间
        if os.path.exists(file_path) and os.path.exists(tmp_file_path):
            file_mtime = os.path.getmtime(file_path)
            tmp_file_mtime = os.path.getmtime(tmp_file_path)
            
            # 文件时间相同，已经同步
            if abs(file_mtime - tmp_file_mtime) < 1:  # 允许1秒误差
                Logger.debug("文件已经同步")
                return
                
            # 确定哪个文件更新
            if file_mtime > tmp_file_mtime:
                source = file_path
                target = tmp_file_path
            else:
                source = tmp_file_path
                target = file_path
        elif os.path.exists(file_path):
            source = file_path
            target = tmp_file_path
        else:
            source = tmp_file_path
            target = file_path
        
        # 如果不需要保存到游戏且目标是游戏文件，则跳过
        if not save_to_game and target == file_path:
            return
        
        # 复制文件
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target), exist_ok=True)
            
            shutil.copy2(source, target)
            Logger.info(f"同步文件: {source} -> {target}")
        except Exception as e:
            Logger.warning(f"同步文件失败: {e}")
            raise