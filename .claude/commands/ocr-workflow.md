---
description: 基于 PaddleOCR 的 CSAPP 章节 PDF 提取工作流
argument-hint: <命令> [章节编号...]
---

# CSAPP OCR 工作流命令

## 概述

此命令用于执行基于 PaddleOCR-VL-1.5 的 PDF 提取工作流，将 CSAPP PDF 书籍转换为可翻译的 Markdown 文档。

## 可用操作

根据 `$ARGUMENTS` 执行相应操作：

### 1. 查看状态 (`status`)

显示所有章节的工作流状态。

```bash
python Books/CSAPP/ocr_workflow.py status
```

### 2. 提取章节 (`extract <章节编号>`)

运行完整提取流水线：PDF → 图片 → OCR → 拼接

```bash
# 单章节
python Books/CSAPP/ocr_workflow.py pipeline --chapters 01

# 多章节
python Books/CSAPP/ocr_workflow.py pipeline --chapters 01 02 03
```

### 3. 仅转换 PDF (`pdf2img`)

将 PDF 转换为图片（不执行 OCR）。

```bash
python Books/CSAPP/ocr_workflow.py pdf2img --dpi 300
```

### 4. 仅整理图片 (`organize <章节编号>`)

按章节整理已转换的图片。

```bash
python Books/CSAPP/ocr_workflow.py organize --chapters 01 02
```

### 5. 仅 OCR 提取 (`ocr <章节编号>`)

对已整理的图片运行 OCR。

```bash
python Books/CSAPP/ocr_workflow.py ocr --chapter 01 --device gpu:0
```

### 6. 仅拼接文档 (`concat <章节编号>`)

将 OCR 结果拼接为章节文档。

```bash
python Books/CSAPP/ocr_workflow.py concat --chapter 01
```

### 7. 翻译章节 (`translate <章节编号>`)

翻译提取的原始文档。使用 `/translate-csapp` 命令的翻译规范。

## 工作流程

```
PDF 文件 (CSAPP_2016.pdf)
    │
    ▼ [pdf2img: 300 DPI]
extract_images/all/
    │  (0001.png, 0002.png, ...)
    │
    ▼ [organize: 按章节页码范围]
extract_images/{chapter}/
    │  (符号链接到 all/)
    │
    ▼ [ocr: PaddleOCR-VL-1.5]
paddleocr_texts/{chapter}/
    │  (每页一个 .md 文件)
    │
    ▼ [concat: 拼接]
raw_texts/{chapter}-{english_title}.md
    │
    ▼ [translate: 使用术语表]
chapters/{chapter}-{chinese_title}.md
```

## 章节信息

来自 `chapter_mapping.py`：

| 编号 | 中文标题 | 页码范围 |
|------|----------|----------|
| 00 | 前言 | 15-30 |
| 01 | 计算机系统漫游 | 31-58 |
| 02 | 信息的表示和处理 | 60-190 |
| 03 | 程序的机器级表示 | 191-378 |
| 04 | 处理器体系结构 | 379-522 |
| 05 | 优化程序性能 | 523-606 |
| 06 | 存储器层次结构 | 607-694 |
| 07 | 链接 | 696-746 |
| 08 | 异常控制流 | 747-825 |
| 09 | 虚拟内存 | 826-910 |
| 10 | 系统级I/O | 912-939 |
| 11 | 网络编程 | 940-992 |
| 12 | 并发编程 | 993-1062 |
| appendix | 错误处理 | 1063-1067 |

## 执行步骤

根据 `$ARGUMENTS` 解析命令并执行：

### 如果参数是 "status"：

1. 执行 `python Books/CSAPP/ocr_workflow.py status`
2. 展示结果给用户

### 如果参数以 "extract" 开头：

1. 解析章节编号
2. 执行完整流水线：
   ```bash
   python Books/CSAPP/ocr_workflow.py pipeline --chapters <章节> --device gpu:0
   ```
3. 报告处理结果

### 如果参数以 "translate" 开头：

1. 解析章节编号
2. 读取 `raw_texts/{chapter}-{english_title}.md`
3. 使用 `/translate-csapp` 的术语表和规范进行翻译
4. 保存到 `chapters/{chapter}-{chinese_title}.md`

## 依赖检查

执行前检查依赖是否已安装：

```python
# 检查 PaddleOCR
python -c "from paddleocr import PaddleOCRVL; print('PaddleOCR OK')"

# 检查 pdf2image
python -c "from pdf2image import convert_from_path; print('pdf2image OK')"
```

如果依赖缺失，提示安装：

```bash
# 安装 PaddlePaddle (GPU)
pip install paddlepaddle-gpu

# 安装 PaddleOCR
pip install "paddleocr[doc-parser]"

# 安装 pdf2image
pip install pdf2image

# 安装系统依赖 (Ubuntu)
sudo apt-get install poppler-utils
```

## 错误处理

- **GPU 不可用**：自动回退到 CPU 模式
- **poppler 缺失**：使用 PyMuPDF 作为备选
- **OCR 失败**：记录日志，跳过失败页面继续处理
- **文件不存在**：提示用户先运行前置步骤

## 输出目录结构

```
Books/CSAPP/
├── extract_images/
│   ├── all/           # 所有页面的 PNG 图片
│   ├── 01/            # 第01章图片（符号链接）
│   ├── 02/
│   └── ...
├── paddleocr_texts/
│   ├── 01/            # 第01章每页的 OCR 结果
│   ├── 02/
│   └── ...
├── raw_texts/
│   └── 01-A_Tour_of_Computer_Systems.md
└── chapters/
    └── 01-计算机系统漫游.md
```
