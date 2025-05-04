# Minecraft模组汉化包更新器 (i18n-updater-cn)

[![PyPI version](https://img.shields.io/pypi/v/i18n-updater-cn.svg)](https://pypi.org/project/i18n-updater-cn/)
[![Python Version](https://img.shields.io/pypi/pyversions/i18n-updater-cn.svg)](https://pypi.org/project/i18n-updater-cn/)
[![License](https://img.shields.io/github/license/kressety/I18nUpdatePython)](LICENSE)

这个Python软件包是[I18nUpdateMod](https://github.com/CFPAOrg/I18nUpdateMod3)的Python实现版本，用于自动下载、合并和转换由[CFPAOrg团队](http://cfpa.team/)维护的Minecraft模组汉化包。

汉化资源包使用[Minecraft Mod Language Package](https://github.com/CFPAOrg/Minecraft-Mod-Language-Package)项目中的文件，适用于各种Minecraft版本。

## 安装

使用pip安装:

```bash
pip install i18n-updater-cn
```

## 使用方法

### 命令行使用

基本用法（将弹出对话框让您选择保存位置）:

```bash
i18n-updater-cn 1.20.4
```

指定Mod加载器:

```bash
i18n-updater-cn 1.18.2 --loader Fabric
```

直接指定输出目录:

```bash
i18n-updater-cn 1.16.5 --output D:/Downloads
```

查看完整帮助:

```bash
i18n-updater-cn --help
```

### 作为Python库使用

您也可以在自己的Python项目中导入并使用这个库：

```python
from i18n_updater_cn import download_or_convert_language_pack

# 下载并转换汉化包
result = download_or_convert_language_pack(
    minecraft_version="1.20.4",
    loader="Forge",
    output_dir="D:/Downloads",
    debug=True
)

# 检查结果
if result["success"]:
    print(f"汉化包已保存到: {result['output_file']}")
else:
    print(f"下载失败: {result['error']}")
```

## 支持的版本

- **Minecraft**: 1.6.1 ~ 1.21.5 所有版本
- **Mod加载器**: Forge、NeoForge、Fabric、Quilt
- **Python**: 3.6 及以上版本

## 相关项目

- [I18nUpdateMod3](https://github.com/CFPAOrg/I18nUpdateMod3) - 本项目的Java版本原型
- [Minecraft-Mod-Language-Package](https://github.com/CFPAOrg/Minecraft-Mod-Language-Package) - 中文汉化资源包项目