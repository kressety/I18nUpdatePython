#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import importlib.resources
from pathlib import Path
import requests
import time
import logging

from .version import Version, VersionRange


class I18nConfig:
    """配置管理类，负责解析元数据和处理版本匹配"""
    
    # CFPA资源包下载根路径
    CFPA_ASSET_ROOT = "http://downloader1.meitangdehulu.com:22943/"
    
    # 元数据在线源
    METADATA_SOURCE = "https://raw.githubusercontent.com/CFPAOrg/I18nUpdateMod3/refs/heads/main/src/main/resources/i18nMetaData.json"
    METADATA_MIRROR = "https://github-proxy.mealuet.com/https://raw.githubusercontent.com/CFPAOrg/I18nUpdateMod3/refs/heads/main/src/main/resources/i18nMetaData.json"
    
    # 元数据缓存
    _i18n_metadata = None
    _metadata_cache_time = 0
    _metadata_cache_duration = 3600  # 缓存有效期1小时
    
    @classmethod
    def _load_metadata(cls):
        """加载元数据文件"""
        # 如果已有缓存且未过期，直接使用
        current_time = time.time()
        if cls._i18n_metadata is not None and (current_time - cls._metadata_cache_time) < cls._metadata_cache_duration:
            return
        
        # 尝试从在线源获取
        metadata = cls._fetch_online_metadata()
        if metadata:
            cls._i18n_metadata = metadata
            cls._metadata_cache_time = current_time
            logging.info("成功从在线源获取元数据")
            return
            
        # 如果在线源都获取失败，抛出异常
        raise ConnectionError("无法从在线源获取元数据，请检查网络连接或稍后再试")
    
    @classmethod
    def _fetch_online_metadata(cls):
        """从在线源获取元数据"""
        sources = [cls.METADATA_SOURCE, cls.METADATA_MIRROR]
        
        for source in sources:
            try:
                logging.info(f"尝试从 {source} 获取元数据")
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    return json.loads(response.text)
            except Exception as e:
                logging.warning(f"从 {source} 获取元数据失败: {str(e)}")
                continue
        
        return None
    
    @classmethod
    def _get_game_metadata(cls, minecraft_version):
        """获取指定Minecraft版本的游戏元数据"""
        cls._load_metadata()
        version_obj = Version(minecraft_version)
        
        for game_meta in cls._i18n_metadata["games"]:
            version_range = VersionRange(game_meta["gameVersions"])
            if version_range.contains(version_obj):
                return game_meta
        
        raise ValueError(f"找不到版本 {minecraft_version} 对应的元数据信息")
    
    @classmethod
    def _get_asset_metadata(cls, minecraft_version, loader):
        """获取特定版本和加载器的资源包元数据"""
        cls._load_metadata()
        
        # 筛选出匹配目标版本的资产
        matching_assets = [
            asset for asset in cls._i18n_metadata["assets"] 
            if asset["targetVersion"] == minecraft_version
        ]
        
        if not matching_assets:
            return None
        
        # 优先返回匹配加载器的资产，否则返回第一个匹配的资产
        for asset in matching_assets:
            if asset["loader"].lower() == loader.lower():
                return asset
        
        return matching_assets[0]
    
    @classmethod
    def get_asset_detail(cls, minecraft_version, loader):
        """
        根据Minecraft版本和加载器类型获取资源包详情
        
        Args:
            minecraft_version: Minecraft版本号（如1.16.5）
            loader: 加载器类型（Forge/Fabric/Quilt）
            
        Returns:
            包含下载信息和转换信息的字典
        """
        game_meta = cls._get_game_metadata(minecraft_version)
        
        result = {
            "downloads": [],
            "convertPackFormat": game_meta["packFormat"],
            "convertFileName": f"Minecraft-Mod-Language-Modpack-Converted-{minecraft_version}.zip"
        }
        
        # 获取每个源版本的资源包下载信息
        for source_version in game_meta["convertFrom"]:
            asset_meta = cls._get_asset_metadata(source_version, loader)
            if asset_meta:
                result["downloads"].append({
                    "fileName": asset_meta["filename"],
                    "fileUrl": cls.CFPA_ASSET_ROOT + asset_meta["filename"],
                    "md5Url": cls.CFPA_ASSET_ROOT + asset_meta["md5Filename"],
                    "targetVersion": asset_meta["targetVersion"]
                })
        
        if not result["downloads"]:
            raise ValueError(f"无法找到版本 {minecraft_version} ({loader}) 对应的资源包")
        
        return result