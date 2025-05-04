#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import importlib.resources
from pathlib import Path

from .version import Version, VersionRange


class I18nConfig:
    """配置管理类，负责解析元数据和处理版本匹配"""
    
    # CFPA资源包下载根路径
    CFPA_ASSET_ROOT = "http://downloader1.meitangdehulu.com:22943/"
    
    # 元数据缓存
    _i18n_metadata = None
    
    @classmethod
    def _load_metadata(cls):
        """加载元数据文件"""
        if cls._i18n_metadata is not None:
            return
        
        # 首先尝试从包资源中加载
        try:
            metadata_text = importlib.resources.read_text('i18n_updater_cn', 'i18nMetaData.json', encoding='utf-8')
            cls._i18n_metadata = json.loads(metadata_text)
            return
        except (ImportError, FileNotFoundError):
            pass

        # 尝试从当前目录加载
        metadata_path = Path(__file__).parent / "i18nMetaData.json"
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                cls._i18n_metadata = json.load(f)
            return
        
        # 如果找不到文件，使用内置的默认元数据
        cls._i18n_metadata = cls._get_default_metadata()
    
    @staticmethod
    def _get_default_metadata():
        """获取内置的默认元数据，这样即使没有外部文件也能工作"""
        return {
            "version": "3.6.2",
            "games": [
                {"gameVersions": "[1.6.1,1.8.9]", "packFormat": 1, "convertFrom": ["1.10.2", "1.12.2"]},
                {"gameVersions": "[1.9,1.10.2]", "packFormat": 2, "convertFrom": ["1.10.2", "1.12.2"]},
                {"gameVersions": "[1.11,1.12.2]", "packFormat": 3, "convertFrom": ["1.12.2"]},
                {"gameVersions": "[1.13,1.14.4]", "packFormat": 4, "convertFrom": ["1.16"]},
                {"gameVersions": "[1.15,1.16.1]", "packFormat": 5, "convertFrom": ["1.16"]},
                {"gameVersions": "[1.16.2,1.16.5]", "packFormat": 6, "convertFrom": ["1.16"]},
                {"gameVersions": "[1.17,1.17.1]", "packFormat": 7, "convertFrom": ["1.18", "1.16"]},
                {"gameVersions": "[1.18,1.18.2]", "packFormat": 8, "convertFrom": ["1.18"]},
                {"gameVersions": "[1.19,1.19.2]", "packFormat": 9, "convertFrom": ["1.19", "1.18"]},
                {"gameVersions": "[1.19.3,1.19.3]", "packFormat": 12, "convertFrom": ["1.19", "1.18"]},
                {"gameVersions": "[1.19.4,1.19.4]", "packFormat": 13, "convertFrom": ["1.19", "1.18"]},
                {"gameVersions": "[1.20,1.20.1]", "packFormat": 15, "convertFrom": ["1.20", "1.19", "1.18"]},
                {"gameVersions": "[1.20.2,1.20.2]", "packFormat": 18, "convertFrom": ["1.20", "1.19", "1.18"]},
                {"gameVersions": "[1.20.3,1.20.4]", "packFormat": 22, "convertFrom": ["1.20", "1.19", "1.18"]},
                {"gameVersions": "[1.20.5,1.20.6]", "packFormat": 32, "convertFrom": ["1.20", "1.19", "1.18"]},
                {"gameVersions": "[1.21,1.21.1]", "packFormat": 34, "convertFrom": ["1.21", "1.20", "1.19"]},
                {"gameVersions": "[1.21.2,1.21.3]", "packFormat": 42, "convertFrom": ["1.21", "1.20", "1.19"]},
                {"gameVersions": "[1.21.4,1.21.4]", "packFormat": 46, "convertFrom": ["1.21", "1.20", "1.19"]},
                {"gameVersions": "[1.21.5,1.21.5]", "packFormat": 55, "convertFrom": ["1.21", "1.20", "1.19"]}
            ],
            "assets": [
                {"targetVersion": "1.10.2", "loader": "Forge", "filename": "Minecraft-Mod-Language-Modpack-1-10-2.zip", "md5Filename": "1.10.2.md5"},
                {"targetVersion": "1.12.2", "loader": "Forge", "filename": "Minecraft-Mod-Language-Modpack.zip", "md5Filename": "1.12.2.md5"},
                {"targetVersion": "1.16", "loader": "Forge", "filename": "Minecraft-Mod-Language-Modpack-1-16.zip", "md5Filename": "1.16.md5"},
                {"targetVersion": "1.16", "loader": "Fabric", "filename": "Minecraft-Mod-Language-Modpack-1-16-Fabric.zip", "md5Filename": "1.16-fabric.md5"},
                {"targetVersion": "1.18", "loader": "Forge", "filename": "Minecraft-Mod-Language-Modpack-1-18.zip", "md5Filename": "1.18.md5"},
                {"targetVersion": "1.18", "loader": "Fabric", "filename": "Minecraft-Mod-Language-Modpack-1-18-Fabric.zip", "md5Filename": "1.18-fabric.md5"},
                {"targetVersion": "1.19", "loader": "Forge", "filename": "Minecraft-Mod-Language-Modpack-1-19.zip", "md5Filename": "1.19.md5"},
                {"targetVersion": "1.20", "loader": "Forge", "filename": "Minecraft-Mod-Language-Modpack-1-20.zip", "md5Filename": "1.20.md5"},
                {"targetVersion": "1.20", "loader": "Fabric", "filename": "Minecraft-Mod-Language-Modpack-1-20-Fabric.zip", "md5Filename": "1.20-fabric.md5"},
                {"targetVersion": "1.21", "loader": "Forge", "filename": "Minecraft-Mod-Language-Modpack-1-21.zip", "md5Filename": "1.21.md5"},
                {"targetVersion": "1.21", "loader": "Fabric", "filename": "Minecraft-Mod-Language-Modpack-1-21-Fabric.zip", "md5Filename": "1.21-fabric.md5"}
            ]
        }
    
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