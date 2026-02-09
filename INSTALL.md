# 环境安装说明

本文档介绍如何配置 PDF 转 Markdown 工具的运行环境。

## 前置条件

- Linux 操作系统 (Ubuntu 20.04+)
- Anaconda 或 Miniconda 已安装

## 安装步骤

### 1. 创建 Conda 环境

```bash
# 创建名为 'book' 的 conda 环境，使用 Python 3.10
conda create -n book python=3.10 -y

# 激活环境
conda activate book
```

### 2. 安装 Python 依赖

```bash
# 安装 PDF 处理库
pip install pymupdf pdfplumber

# 可选：安装数据处理库
pip install pandas
```

### 3. 验证安装

```bash
# 激活环境
conda activate book

# 验证 PyMuPDF 安装
python -c "import fitz; print(f'PyMuPDF version: {fitz.version}')"

# 验证 pdfplumber 安装
python -c "import pdfplumber; print('pdfplumber installed successfully')"
```

## 依赖包说明

| 包名 | 版本 | 用途 |
|------|------|------|
| pymupdf | 1.26.7+ | PDF 文本提取和处理 |
| pdfplumber | 0.11.9+ | PDF 表格和布局提取 |
| Pillow | 12.1.0+ | 图像处理（pdfplumber 依赖）|

## 使用方法

```bash
# 1. 激活环境
conda activate book

# 2. 进入项目目录
cd /path/to/CS-Study-Notes/Books/CSAPP

# 3. 运行转换脚本
python convert_csapp.py
```

## 常见问题

### Q: conda 命令找不到？

确保已正确初始化 conda：

```bash
source ~/anaconda3/etc/profile.d/conda.sh
# 或者
source ~/miniconda3/etc/profile.d/conda.sh
```

### Q: 如何查看已安装的包？

```bash
conda activate book
pip list
```

### Q: 如何删除环境重新安装？

```bash
conda deactivate
conda env remove -n book
# 然后重新按照上述步骤安装
```

## 目录结构

安装完成后，项目目录结构如下：

```
Books/CSAPP/
├── CSAPP_2016.pdf          # 原始 PDF 文件
├── INSTALL.md              # 本安装文档
├── README.md               # 书籍说明
├── chapters/               # 生成的 Markdown 章节
├── code/                   # 提取的代码示例
│   ├── ch01/
│   ├── ch02/
│   └── ...
├── figures/                # 图片资源
├── chapter_mapping.py      # 章节页码映射
├── extract_chapters.py     # PDF 提取脚本
├── text_to_markdown.py     # Markdown 转换脚本
└── convert_csapp.py        # 主转换脚本
```
