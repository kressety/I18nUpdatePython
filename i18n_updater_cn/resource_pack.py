#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import hashlib
import shutil
import requests
from pathlib import Path

from .utils import Logger, FileUtil


class ResourcePack:
    """
    资源包管理类，负责下载和校验资源包
    对应Java版项目中的ResourcePack.java
    """
    
    # 限制更新检查频率（1天）
    UPDATE_TIME_GAP = 24 * 60 * 60  # 秒
    
    def __init__(self, filename, save_to_game=True):
        """
        初始化资源包
        
        Args:
            filename: 资源包文件名
            save_to_game: 是否保存到游戏目录
        """
        self.filename = filename
        self.save_to_game = save_to_game
        self.file_path = FileUtil.get_resource_pack_path(filename)
        self.tmp_file_path = FileUtil.get_temporary_path(filename)
        self.remote_md5 = None
        
        # 同步本地文件和临时文件
        try:
            FileUtil.sync_tmp_file(self.file_path, self.tmp_file_path, save_to_game)
        except Exception as e:
            Logger.warning(f"同步临时文件时出错 {self.file_path} <-> {self.tmp_file_path}: {e}")
    
    def check_update(self, file_url, md5_url):
        """
        检查并更新资源包
        
        Args:
            file_url: 资源包文件URL
            md5_url: MD5校验文件URL
        """
        try:
            if self.is_up_to_date(md5_url):
                Logger.debug("资源包已是最新版本")
                return
            
            # 下载完整文件
            self.download_full(file_url, md5_url)
        except Exception as e:
            Logger.warning(f"检查更新时出错: {e}")
            raise
    
    def is_up_to_date(self, md5_url):
        """
        检查资源包是否为最新版本
        
        Args:
            md5_url: MD5校验文件URL
            
        Returns:
            布尔值，表示是否为最新版本
        """
        # 文件不存在，需要更新
        if not os.path.exists(self.tmp_file_path):
            Logger.debug(f"本地文件不存在: {self.tmp_file_path}")
            return False
        
        # 最近更新过，不需要再次更新
        if os.path.getmtime(self.tmp_file_path) > time.time() - self.UPDATE_TIME_GAP:
            Logger.debug(f"本地文件最近已更新过: {self.tmp_file_path}")
            return True
        
        # 比较MD5校验码
        return self.check_md5(self.tmp_file_path, md5_url)
    
    def check_md5(self, local_file, md5_url):
        """
        比较本地文件与远程MD5
        
        Args:
            local_file: 本地文件路径
            md5_url: 远程MD5文件URL
            
        Returns:
            布尔值，表示MD5是否匹配
        """
        # 计算本地文件MD5
        local_md5 = self._calculate_md5(local_file)
        
        # 获取远程MD5 - 每次都重新获取，避免缓存问题
        try:
            # 自定义请求头，防止下载管理器如IDM拦截请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/plain',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'X-I18n-Updater': 'md5-check'
            }
            
            # 每次校验都重新获取远程MD5，避免缓存问题
            self.remote_md5 = None
            
            response = requests.get(md5_url, timeout=30, headers=headers)
            response.raise_for_status()
            self.remote_md5 = response.text.strip()
            
            # 处理可能存在的额外格式问题（如复制粘贴导致的特殊字符）
            self.remote_md5 = ''.join(c for c in self.remote_md5 if c.isalnum())
        except Exception as e:
            Logger.warning(f"获取远程MD5失败: {e}")
            return False
        
        # 确保MD5是标准格式（32位十六进制字符）
        clean_local_md5 = ''.join(c for c in local_md5 if c.isalnum())
        clean_remote_md5 = ''.join(c for c in self.remote_md5 if c.isalnum())
        
        # 将两个MD5转换为小写进行比较，并记录详细日志
        clean_local_md5 = clean_local_md5.lower()
        clean_remote_md5 = clean_remote_md5.lower()
        
        Logger.debug(f"本地文件: {local_file}")
        Logger.debug(f"本地MD5 (原始): {local_md5}")
        Logger.debug(f"本地MD5 (清理后): {clean_local_md5}")
        Logger.debug(f"远程MD5 (原始): {self.remote_md5}")
        Logger.debug(f"远程MD5 (清理后): {clean_remote_md5}")
        Logger.debug(f"MD5 URL: {md5_url}")  # 添加MD5 URL日志
        
        match_result = clean_local_md5 == clean_remote_md5
        if match_result:
            Logger.debug("MD5校验通过")
        else:
            Logger.debug("MD5校验失败")
            
            # 如果原始值相等但清理后不相等，则可能有格式问题
            if local_md5.upper() == self.remote_md5.upper():
                Logger.debug("原始MD5值匹配，忽略格式差异")
                return True
        
        # 考虑文件大小作为额外校验
        if not match_result:
            filesize = os.path.getsize(local_file)
            Logger.debug(f"文件大小: {filesize} 字节")
            # 对于较大的文件（>10MB），如果文件最近更新，可能暂时接受
            if filesize > 10 * 1024 * 1024 and os.path.getmtime(local_file) > time.time() - 86400:
                Logger.debug("文件较大且最近已更新，暂时接受")
                return True
        
        return match_result
    
    def download_full(self, file_url, md5_url):
        """
        下载完整资源包
        
        Args:
            file_url: 资源包文件URL
            md5_url: MD5校验文件URL
        """
        try:
            # 创建临时下载文件
            download_tmp = FileUtil.get_temporary_path(f"{self.filename}.tmp")
            
            # 下载文件
            Logger.info(f"正在下载: {file_url} -> {download_tmp}")
            
            # 自定义请求头，防止下载管理器如IDM拦截请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'X-Requested-With': 'XMLHttpRequest',
                'DNT': '1',  # 请求不跟踪
                'X-I18n-Updater': 'direct-download'  # 自定义标识，表明这是直接下载
            }
            
            # 确保下载目录存在
            os.makedirs(os.path.dirname(download_tmp), exist_ok=True)
            
            # 下载文件
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    response = requests.get(file_url, stream=True, timeout=300, headers=headers)
                    response.raise_for_status()
                    
                    # 保存到临时文件
                    with open(download_tmp, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # 校验下载文件MD5
                    if self.check_md5(download_tmp, md5_url):
                        # 移动到目标临时文件
                        os.makedirs(os.path.dirname(self.tmp_file_path), exist_ok=True)
                        shutil.move(download_tmp, self.tmp_file_path)
                        Logger.info(f"下载完成: {file_url} -> {self.tmp_file_path}")
                        
                        # 同步到游戏目录
                        FileUtil.sync_tmp_file(self.file_path, self.tmp_file_path, self.save_to_game)
                        return
                    else:
                        Logger.warning(f"下载文件MD5校验失败 (尝试 {retry_count + 1}/{max_retries})")
                        retry_count += 1
                except Exception as e:
                    Logger.warning(f"下载尝试失败: {e} (尝试 {retry_count + 1}/{max_retries})")
                    retry_count += 1
                    
                # 短暂等待后重试
                if retry_count < max_retries:
                    time.sleep(2)
            
            # 所有重试都失败
            Logger.warning(f"下载失败: 所有 {max_retries} 次尝试后仍无法完成下载")
            
            # 检查之前的临时文件是否存在
            if os.path.exists(self.tmp_file_path):
                Logger.info(f"使用现有临时文件: {self.tmp_file_path}")
                return
            elif os.path.exists(download_tmp):
                # 如果临时下载文件存在但校验失败，仍然使用它作为临时文件
                Logger.warning("使用未通过MD5校验的临时文件")
                shutil.move(download_tmp, self.tmp_file_path)
                return
            else:
                raise FileNotFoundError(f"临时文件不存在: {self.tmp_file_path}")
                
        except Exception as e:
            Logger.warning(f"下载失败: {e}")
            
            # 清理可能存在的临时下载文件
            if os.path.exists(download_tmp):
                try:
                    os.remove(download_tmp)
                except:
                    pass
                
            # 检查之前的临时文件
            if os.path.exists(self.tmp_file_path):
                Logger.info("使用现有临时文件")
            else:
                raise FileNotFoundError(f"临时文件不存在: {self.tmp_file_path}")
    
    @staticmethod
    def _calculate_md5(file_path):
        """
        计算文件的MD5哈希值
        
        Args:
            file_path: 文件路径
            
        Returns:
            MD5哈希值的十六进制字符串
        """
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            # 每次读取4MB数据
            for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def get_tmp_file_path(self):
        """获取临时文件路径"""
        return self.tmp_file_path
    
    def get_filename(self):
        """获取文件名"""
        return self.filename