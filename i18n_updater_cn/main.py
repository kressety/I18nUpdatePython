#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minecraft 汉化包更新器
根据用户指定的版本，下载或转换相应的汉化包

基于Java版项目 I18nUpdateMod3 重写
"""

import os
import sys
import json
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from .config import I18nConfig
from .resource_pack import ResourcePack
from .resource_converter import ResourcePackConverter
from .utils import Logger, FileUtil


def get_default_storage_path():
    """获取默认的本地存储路径"""
    user_home = Path.home()
    app_data_path = None

    # 检查特定的应用数据路径是否存在
    if os.name == 'nt':  # Windows
        app_data_path = os.getenv('LocalAppData')
    elif sys.platform == 'darwin':  # macOS
        app_data_path = user_home / 'Library' / 'Application Support'
    
    # 使用XDG标准（Linux等）
    xdg_data_home = os.getenv('XDG_DATA_HOME')
    if not xdg_data_home:
        xdg_data_home = user_home / '.local' / 'share'
    
    # 返回第一个存在的路径，或默认使用XDG路径
    if app_data_path and os.path.exists(app_data_path):
        return Path(app_data_path) / ".i18n_updater_cn"
    return Path(xdg_data_home) / ".i18n_updater_cn"


def download_or_convert_language_pack(minecraft_version, loader="Forge", output_dir=None, temp_dir=None, debug=False):
    """
    下载或转换指定版本的汉化包
    
    Args:
        minecraft_version: Minecraft版本号（如1.16.5）
        loader: Mod加载器类型（Forge/Fabric/Quilt）
        output_dir: 汉化包输出目录路径，如果为None则使用当前目录
        temp_dir: 临时文件目录路径，如果为None则使用系统临时目录
        debug: 是否启用调试模式
        
    Returns:
        dict: 包含操作结果的字典，包括输出文件路径等信息
    """
    if debug:
        Logger.set_level(Logger.Level.DEBUG)
        
    Logger.info(f"I18n汉化包更新器启动，Minecraft版本: {minecraft_version}, Mod加载器: {loader}")
    
    # 设置输出目录
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
        
    Logger.debug(f"输出目录: {output_dir}")
    FileUtil.set_resource_pack_dir(output_dir)
    
    # 设置临时目录
    if temp_dir is None:
        temp_dir = get_default_storage_path() 
    else:
        temp_dir = Path(temp_dir)
        
    Logger.debug(f"临时目录: {temp_dir}")
    
    result = {
        "success": False,
        "version": minecraft_version,
        "loader": loader,
        "output_dir": str(output_dir),
        "output_file": None,
        "error": None
    }
    
    try:
        # 获取该版本对应的资源包详情
        assets = I18nConfig.get_asset_detail(minecraft_version, loader)
        
        # 更新资源包
        language_packs = []
        convert_not_need = len(assets['downloads']) == 1 and assets['downloads'][0]['targetVersion'] == minecraft_version
        final_filename = assets['downloads'][0]['fileName']
        
        for download_detail in assets['downloads']:
            target_version = download_detail['targetVersion']
            version_temp_dir = temp_dir / target_version
            FileUtil.set_temporary_dir(version_temp_dir)
            
            # 下载或更新资源包
            language_pack = ResourcePack(download_detail['fileName'], convert_not_need)
            language_pack.check_update(download_detail['fileUrl'], download_detail['md5Url'])
            language_packs.append(language_pack)
        
        # 如果需要转换资源包
        if not convert_not_need:
            FileUtil.set_temporary_dir(temp_dir / minecraft_version)
            final_filename = assets['convertFileName']
            converter = ResourcePackConverter(language_packs, final_filename)
            
            # 构建资源包描述
            if len(assets['downloads']) > 1:
                target_versions = [d['targetVersion'] for d in assets['downloads']]
                description = f"该包由{' 和 '.join(target_versions)}版本合并\n作者：CFPA团队及汉化项目贡献者"
            else:
                description = f"该包对应的官方支持版本为{assets['downloads'][0]['targetVersion']}\n作者：CFPA团队及汉化项目贡献者"
            
            converter.convert(assets['convertPackFormat'], description)
        
        # 操作完成
        output_file = output_dir / final_filename
        Logger.info(f"汉化包已保存到: {output_file}")
        
        result["success"] = True
        result["output_file"] = str(output_file)
        
    except Exception as e:
        Logger.error(f"更新资源包失败: {e}")
        result["error"] = str(e)
        
    return result


def select_directory(title="选择目录"):
    """打开目录选择对话框"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes("-topmost", True)  # 置顶对话框
    directory = filedialog.askdirectory(title=title)
    root.destroy()
    return directory if directory else None


def show_message(title, message):
    """显示消息对话框"""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo(title, message)
    root.destroy()


def cli_main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description='Minecraft汉化包更新工具')
    parser.add_argument('version', help='Minecraft版本，例如1.16.5')
    parser.add_argument('--loader', '-l', default='Forge', choices=['Forge', 'Fabric', 'Quilt'], 
                        help='Mod加载器类型 (默认: Forge)')
    parser.add_argument('--output', '-o', help='汉化包输出目录路径 (默认: 弹出选择对话框)')
    parser.add_argument('--temp', '-t', help='临时文件目录路径 (默认: 系统默认位置)')
    parser.add_argument('--gui', '-g', action='store_true', help='使用图形界面选择输出目录')
    parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    output_dir = args.output
    
    # 如果没有指定输出目录或使用了GUI模式，则弹出选择对话框
    if output_dir is None or args.gui:
        selected_dir = select_directory("选择汉化包保存位置")
        if selected_dir:
            output_dir = selected_dir
        else:
            print("未选择目录，操作取消")
            sys.exit(0)
    
    try:
        result = download_or_convert_language_pack(
            args.version, 
            args.loader, 
            output_dir, 
            args.temp, 
            args.debug
        )
        
        if result["success"]:
            success_msg = f"汉化包已成功下载到:\n{result['output_file']}"
            print(success_msg)
            if args.gui:
                show_message("下载成功", success_msg)
        else:
            print(f"错误: {result['error']}")
            if args.gui:
                show_message("下载失败", f"下载汉化包失败:\n{result['error']}")
    except Exception as e:
        print(f"错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli_main()