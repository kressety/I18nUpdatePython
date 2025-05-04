#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
版本号解析和比较
对应Java版项目中的Version.java和VersionRange.java
"""

import re


class Version:
    """版本号类，用于解析和比较版本号"""
    
    def __init__(self, version_str):
        """
        初始化版本号
        
        Args:
            version_str: 版本字符串，如"1.16.5"
        """
        self.version_str = version_str
        self.versions = []
        self._parse_version(version_str)
    
    def _parse_version(self, version_str):
        """
        解析版本字符串，提取版本号
        
        例如 "1.16.5" 会被解析为 [1, 16, 5]
        """
        # 使用正则表达式提取版本号中的数字部分
        numbers = re.findall(r'\d+', version_str)
        self.versions = [int(num) for num in numbers]
    
    def __eq__(self, other):
        """判断两个版本是否相等"""
        if not isinstance(other, Version):
            return False
        return self.versions == other.versions
    
    def __lt__(self, other):
        """比较两个版本的大小"""
        min_len = min(len(self.versions), len(other.versions))
        
        # 逐位比较版本号
        for i in range(min_len):
            if self.versions[i] != other.versions[i]:
                return self.versions[i] < other.versions[i]
        
        # 如果前面位数都相同，则版本号位数少的小于位数多的
        return len(self.versions) < len(other.versions)
    
    def __le__(self, other):
        """小于等于比较"""
        return self < other or self == other
    
    def __gt__(self, other):
        """大于比较"""
        return not self <= other
    
    def __ge__(self, other):
        """大于等于比较"""
        return not self < other
    
    def __str__(self):
        """版本号的字符串表示"""
        return self.version_str
    
    def __repr__(self):
        """版本号的调试表示"""
        return f"Version({self.version_str})"


class VersionRange:
    """版本范围类，用于判断版本是否在指定范围内"""
    
    def __init__(self, range_str):
        """
        初始化版本范围
        
        Args:
            range_str: 范围字符串，格式如"[1.16,1.16.5]"
        """
        self.range_str = range_str
        self.from_version = None
        self.to_version = None
        self.contains_left = False
        self.contains_right = False
        self._parse_version_range(range_str)
    
    def _parse_version_range(self, range_str):
        """
        解析版本范围字符串
        
        格式：
        - "[1.16,1.16.5]" 表示 1.16 <= version <= 1.16.5
        - "(1.16,1.16.5)" 表示 1.16 < version < 1.16.5
        - "[1.16,1.16.5)" 表示 1.16 <= version < 1.16.5
        """
        # 检查左右边界符号
        if range_str.startswith('['):
            self.contains_left = True
        elif range_str.startswith('('):
            self.contains_left = False
        else:
            raise ValueError(f"无效的版本范围：{range_str}")
        
        if range_str.endswith(']'):
            self.contains_right = True
        elif range_str.endswith(')'):
            self.contains_right = False
        else:
            raise ValueError(f"无效的版本范围：{range_str}")
        
        # 提取版本部分，去掉左右边界符号
        versions_part = range_str[1:-1]
        
        # 分割两个版本
        if ',' not in versions_part:
            raise ValueError(f"无效的版本范围（缺少逗号分隔符）：{range_str}")
            
        from_str, to_str = versions_part.split(',', 1)
        
        # 创建版本对象
        if from_str:
            self.from_version = Version(from_str)
        
        if to_str:
            self.to_version = Version(to_str)
    
    def contains(self, version):
        """
        判断给定版本是否在范围内
        
        Args:
            version: Version对象或版本字符串
            
        Returns:
            布尔值，表示是否在范围内
        """
        if isinstance(version, str):
            version = Version(version)
        
        # 检查下界
        if self.from_version:
            if self.contains_left:
                if version < self.from_version:
                    return False
            else:
                if version <= self.from_version:
                    return False
        
        # 检查上界
        if self.to_version:
            if self.contains_right:
                if version > self.to_version:
                    return False
            else:
                if version >= self.to_version:
                    return False
        
        return True
    
    def __str__(self):
        """版本范围的字符串表示"""
        return self.range_str
    
    def __repr__(self):
        """版本范围的调试表示"""
        return f"VersionRange({self.range_str})"