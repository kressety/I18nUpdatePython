#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import zipfile
from pathlib import Path

from .utils import Logger, FileUtil


class ResourcePackConverter:
    """
    资源包转换器，用于合并和转换资源包
    对应Java版项目中的ResourcePackConverter.java
    """
    
    def __init__(self, resource_packs, output_filename):
        """
        初始化资源包转换器
        
        Args:
            resource_packs: ResourcePack对象列表
            output_filename: 输出文件名
        """
        self.resource_packs = resource_packs
        self.source_paths = [rp.get_tmp_file_path() for rp in resource_packs]
        self.output_file_path = FileUtil.get_resource_pack_path(output_filename)
        self.tmp_output_file_path = FileUtil.get_temporary_path(output_filename)
    
    def convert(self, pack_format, description):
        """
        转换资源包
        
        Args:
            pack_format: 目标资源包格式
            description: 资源包描述信息
        """
        Logger.info(f"开始转换资源包: {', '.join(str(p) for p in self.source_paths)} -> {self.tmp_output_file_path}")
        
        processed_files = set()
        
        try:
            # 创建输出目录
            os.makedirs(os.path.dirname(self.tmp_output_file_path), exist_ok=True)
            
            # 创建新的zip文件
            with zipfile.ZipFile(self.tmp_output_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                # 处理每个源资源包
                for source_path in self.source_paths:
                    Logger.info(f"处理资源包: {source_path}")
                    
                    # 检查源文件是否存在
                    if not os.path.exists(source_path):
                        Logger.warning(f"源资源包不存在: {source_path}")
                        continue
                        
                    with zipfile.ZipFile(source_path, 'r') as zip_in:
                        # 获取所有条目
                        for entry in zip_in.infolist():
                            name = entry.filename
                            
                            # 跳过pack.mcmeta（稍后会创建新的）
                            if name.lower() == "pack.mcmeta":
                                continue
                            
                            # 避免重复文件
                            if name in processed_files:
                                continue
                            
                            processed_files.add(name)
                            
                            # 复制文件内容到新zip
                            zip_out.writestr(name, zip_in.read(name))
                
                # 创建新的pack.mcmeta
                pack_meta = {
                    "pack": {
                        "pack_format": pack_format,
                        "description": description
                    }
                }
                zip_out.writestr("pack.mcmeta", json.dumps(pack_meta, indent=2, ensure_ascii=False))
            
            Logger.info(f"资源包转换完成: {self.tmp_output_file_path}")
            
            # 同步到游戏目录 - 修复参数顺序
            FileUtil.sync_tmp_file(self.output_file_path, self.tmp_output_file_path, True)
            
        except Exception as e:
            Logger.error(f"转换资源包失败: {e}")
            raise