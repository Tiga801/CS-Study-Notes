# CSAPP - 深入理解计算机系统

> Computer Systems: A Programmer's Perspective (3rd Edition)
>
> 作者: Randal E. Bryant, David R. O'Hallaron

## 书籍简介

《深入理解计算机系统》(CSAPP) 是计算机科学领域的经典教材，从程序员的视角全面介绍计算机系统的核心概念。本书涵盖数据表示、机器级程序、处理器架构、内存层次结构、链接、异常控制流、虚拟内存、系统级 I/O、网络编程和并发编程等主题。

## 目录

| 章节 | 中文标题 | 英文标题 | 状态 |
|------|----------|----------|------|
| 00 | [前言](chapters/00-前言.md) | Preface | 已翻译 |
| 01 | [计算机系统漫游](chapters/01-计算机系统漫游.md) | A Tour of Computer Systems | 已翻译 |
| 02 | [信息的表示和处理](chapters/02-信息的表示和处理.md) | Representing and Manipulating Information | 待翻译 |
| 03 | [程序的机器级表示](chapters/03-程序的机器级表示.md) | Machine-Level Representation of Programs | 待翻译 |
| 04 | [处理器体系结构](chapters/04-处理器体系结构.md) | Processor Architecture | 待翻译 |
| 05 | [优化程序性能](chapters/05-优化程序性能.md) | Optimizing Program Performance | 待翻译 |
| 06 | [存储器层次结构](chapters/06-存储器层次结构.md) | The Memory Hierarchy | 待翻译 |
| 07 | [链接](chapters/07-链接.md) | Linking | 待翻译 |
| 08 | [异常控制流](chapters/08-异常控制流.md) | Exceptional Control Flow | 待翻译 |
| 09 | [虚拟内存](chapters/09-虚拟内存.md) | Virtual Memory | 待翻译 |
| 10 | [系统级I/O](chapters/10-系统级IO.md) | System-Level I/O | 待翻译 |
| 11 | [网络编程](chapters/11-网络编程.md) | Network Programming | 待翻译 |
| 12 | [并发编程](chapters/12-并发编程.md) | Concurrent Programming | 待翻译 |
| 附录 | [错误处理](chapters/appendix-错误处理.md) | Error Handling | 待翻译 |

## 目录结构

```
CSAPP/
├── README.md           # 本文件
├── INSTALL.md          # 环境安装说明
├── CSAPP_2016.pdf      # 原版 PDF
├── chapters/           # Markdown 章节文件
│   ├── 01-计算机系统漫游.md
│   ├── 02-信息的表示和处理.md
│   └── ...
├── code/               # 代码示例
│   ├── ch01/          # 第1章代码
│   ├── ch02/          # 第2章代码
│   └── ...
├── figures/            # 图片资源
├── chapter_mapping.py  # 章节映射配置
├── extract_chapters.py # PDF 提取脚本
├── text_to_markdown.py # Markdown 转换脚本
└── convert_csapp.py    # 主转换脚本
```

## 使用方法

### 环境准备

```bash
# 激活 conda 环境
conda activate book

# 或者按照 INSTALL.md 安装依赖
```

### 转换章节

```bash
# 查看所有章节
python convert_csapp.py --list

# 转换单个章节
python convert_csapp.py -c 01

# 转换多个章节
python convert_csapp.py -c 01 02 03

# 转换所有章节
python convert_csapp.py --all

# 生成章节模板（不提取内容）
python convert_csapp.py -c 01 --template
```

### 翻译工作流程

1. 运行脚本提取章节原文
2. 在 Claude 对话中逐节翻译为中文
3. 将翻译结果更新到对应的 Markdown 文件
4. 提取代码示例到 `code/` 目录

## 学习资源

- [CMU 官方课程页面](http://csapp.cs.cmu.edu/)
- [CMU 15-213 课程视频](https://www.youtube.com/playlist?list=PLbY-cFJNzq7z_tQGq-rxtq_n2QQDf5vnM)
- [书籍配套实验 (Labs)](http://csapp.cs.cmu.edu/3e/labs.html)

## 术语表

| 英文 | 中文 |
|------|------|
| byte | 字节 |
| word | 字 |
| cache | 高速缓存 |
| register | 寄存器 |
| stack | 栈 |
| heap | 堆 |
| pointer | 指针 |
| process | 进程 |
| thread | 线程 |
| virtual memory | 虚拟内存 |
| linker | 链接器 |
| compiler | 编译器 |

## 贡献指南

欢迎提交 Issue 或 Pull Request 来改进翻译质量或修复错误。
