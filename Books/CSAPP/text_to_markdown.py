#!/usr/bin/env python3
"""
文本转 Markdown 脚本

将从 PDF 提取的原始文本转换为格式化的 Markdown 文档。
"""

import re
from pathlib import Path
from typing import List, Tuple

from chapter_mapping import ChapterInfo, GLOSSARY


def detect_section_headers(text: str, chapter_num: str) -> List[Tuple[str, int, str]]:
    """
    检测章节标题和小节标题

    Args:
        text: 原始文本
        chapter_num: 章节编号

    Returns:
        [(标题文本, 层级, 原始行), ...]
    """
    headers = []
    lines = text.split('\n')

    # 匹配模式
    # 章节标题: "1 A Tour of Computer Systems"
    chapter_pattern = rf'^{chapter_num}\s+[A-Z][A-Za-z\s]+$'
    # 一级小节: "1.1 Information Is Bits + Context"
    section_pattern = rf'^{chapter_num}\.(\d+)\s+[A-Z]'
    # 二级小节: "1.1.1 Some Title"
    subsection_pattern = rf'^{chapter_num}\.(\d+)\.(\d+)\s+[A-Z]'

    for line in lines:
        line = line.strip()
        if re.match(chapter_pattern, line):
            headers.append((line, 1, line))
        elif re.match(subsection_pattern, line):
            headers.append((line, 3, line))
        elif re.match(section_pattern, line):
            headers.append((line, 2, line))

    return headers


def detect_code_blocks(text: str) -> List[Tuple[str, str, int, int]]:
    """
    检测代码块

    Args:
        text: 原始文本

    Returns:
        [(代码内容, 语言类型, 起始行, 结束行), ...]
    """
    code_blocks = []
    lines = text.split('\n')
    in_code = False
    code_lines = []
    code_start = 0
    code_lang = "c"

    for i, line in enumerate(lines):
        # Shell 命令检测
        if line.strip().startswith('linux>') or line.strip().startswith('unix>'):
            if not in_code:
                in_code = True
                code_start = i
                code_lang = "bash"
            code_lines.append(line)
        # C 代码检测
        elif re.match(r'^(#include|int\s+main|void\s+|long\s+|char\s+|unsigned\s+)', line.strip()):
            if not in_code:
                in_code = True
                code_start = i
                code_lang = "c"
            code_lines.append(line)
        # 汇编代码检测
        elif re.match(r'^\s*(pushq|popq|movq|movl|addq|subq|ret|call)\s+', line):
            if not in_code:
                in_code = True
                code_start = i
                code_lang = "asm"
            code_lines.append(line)
        # 代码块结束
        elif in_code and line.strip() == "":
            if code_lines:
                code_blocks.append((
                    '\n'.join(code_lines),
                    code_lang,
                    code_start,
                    i - 1
                ))
            in_code = False
            code_lines = []
        elif in_code:
            code_lines.append(line)

    # 处理最后一个代码块
    if code_lines:
        code_blocks.append((
            '\n'.join(code_lines),
            code_lang,
            code_start,
            len(lines) - 1
        ))

    return code_blocks


def clean_text(text: str) -> str:
    """
    清理文本，移除页码标记等

    Args:
        text: 原始文本

    Returns:
        清理后的文本
    """
    # 移除页码标记
    text = re.sub(r'--- Page \d+ ---\n', '', text)

    # 移除多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 移除行首行尾空白（保留缩进）
    lines = text.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]

    return '\n'.join(cleaned_lines)


def text_to_markdown(
    text: str,
    chapter_info: ChapterInfo,
    include_page_markers: bool = False
) -> str:
    """
    将原始文本转换为 Markdown 格式

    Args:
        text: 原始文本
        chapter_info: 章节信息
        include_page_markers: 是否保留页码标记

    Returns:
        Markdown 格式的文本
    """
    if not include_page_markers:
        text = clean_text(text)

    lines = text.split('\n')
    md_lines = []
    chapter_num = chapter_info.chapter_num

    # 添加章节头部
    md_lines.append(f"# 第{chapter_num}章 {chapter_info.chinese_title}")
    md_lines.append("")
    md_lines.append(f"> 原书: Chapter {chapter_num} - {chapter_info.english_title}")
    md_lines.append("")
    md_lines.append("## 本章概述")
    md_lines.append("")
    md_lines.append("<!-- TODO: 添加本章概述 -->")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    in_code_block = False
    code_lang = "c"

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 跳过空行（但保留段落间的空行）
        if not stripped:
            if not in_code_block:
                md_lines.append("")
            continue

        # 检测章节标题
        chapter_match = re.match(rf'^{chapter_num}\s+([A-Z][A-Za-z\s]+)$', stripped)
        if chapter_match:
            md_lines.append(f"\n## {stripped}\n")
            continue

        # 检测二级小节标题 (如 1.4.1)
        subsection_match = re.match(
            rf'^{chapter_num}\.(\d+)\.(\d+)\s+(.+)$', stripped
        )
        if subsection_match:
            md_lines.append(f"\n### {stripped}\n")
            continue

        # 检测一级小节标题 (如 1.4)
        section_match = re.match(rf'^{chapter_num}\.(\d+)\s+(.+)$', stripped)
        if section_match:
            md_lines.append(f"\n## {stripped}\n")
            continue

        # 检测 Shell 命令
        if stripped.startswith('linux>') or stripped.startswith('unix>'):
            if not in_code_block:
                md_lines.append("\n```bash")
                in_code_block = True
                code_lang = "bash"
            md_lines.append(line)
            continue

        # 检测 C 代码开始
        if re.match(r'^(#include|int\s+main|void\s+\w+|long\s+\w+|char\s+\w+)', stripped):
            if not in_code_block:
                md_lines.append("\n```c")
                in_code_block = True
                code_lang = "c"
            md_lines.append(line)
            continue

        # 检测汇编代码
        if re.match(r'^\s*(pushq|popq|movq|movl|addq|subq|ret\s|call\s)', stripped):
            if not in_code_block:
                md_lines.append("\n```asm")
                in_code_block = True
                code_lang = "asm"
            md_lines.append(line)
            continue

        # 代码块内的行
        if in_code_block:
            # 检测代码块结束（遇到普通文本行）
            if not stripped.startswith((' ', '\t')) and not re.match(r'^[{}();]', stripped):
                md_lines.append("```\n")
                in_code_block = False
                md_lines.append(line)
            else:
                md_lines.append(line)
            continue

        # 普通文本行
        md_lines.append(line)

    # 关闭未关闭的代码块
    if in_code_block:
        md_lines.append("```")

    # 添加章节小结
    md_lines.append("\n---\n")
    md_lines.append("## 本章小结")
    md_lines.append("")
    md_lines.append("<!-- TODO: 添加本章要点总结 -->")
    md_lines.append("")
    md_lines.append("- 要点 1")
    md_lines.append("- 要点 2")
    md_lines.append("- 要点 3")

    return '\n'.join(md_lines)


def create_chapter_template(chapter_info: ChapterInfo) -> str:
    """
    创建章节 Markdown 模板

    Args:
        chapter_info: 章节信息

    Returns:
        Markdown 模板
    """
    template = f"""# 第{chapter_info.chapter_num}章 {chapter_info.chinese_title}

> 原书: Chapter {chapter_info.chapter_num} - {chapter_info.english_title}

## 本章概述

<!-- TODO: 添加本章概述 -->

---

## {chapter_info.chapter_num}.1 小节标题

### 内容

<!-- 章节内容 -->

### 代码示例

```c
// 示例代码
#include <stdio.h>

int main() {{
    printf("Hello, World!\\n");
    return 0;
}}
```

---

## 本章小结

- 要点 1
- 要点 2
- 要点 3

## 参考资料

- [相关链接]
"""
    return template


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # 读取原始文本文件并转换
        input_file = Path(sys.argv[1])
        if input_file.exists():
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # 检测章节编号
            match = re.search(r'(\d+)-', input_file.name)
            if match:
                from chapter_mapping import CHAPTERS
                chapter_num = match.group(1)
                chapter_info = CHAPTERS.get(chapter_num)
                if chapter_info:
                    md_content = text_to_markdown(text, chapter_info)
                    print(md_content)
                else:
                    print(f"未找到章节 {chapter_num} 的信息")
            else:
                print("无法从文件名检测章节编号")
        else:
            print(f"文件不存在: {input_file}")
    else:
        print("用法: python text_to_markdown.py <原始文本文件>")
        print("示例: python text_to_markdown.py raw_text/01-计算机系统漫游_raw.txt")
