#!/usr/bin/env python3
"""
PDF 章节提取脚本

使用 PyMuPDF (fitz) 从 PDF 文件中提取指定页码范围的文本内容。
"""

import os
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from chapter_mapping import CHAPTERS, ChapterInfo, get_chapter_filename


# 配置
PDF_PATH = Path(__file__).parent / "CSAPP_2016.pdf"
OUTPUT_DIR = Path(__file__).parent / "chapters"
RAW_OUTPUT_DIR = Path(__file__).parent / "raw_text"


def extract_pages(pdf_path: Path, start_page: int, end_page: int) -> str:
    """
    从 PDF 中提取指定页码范围的文本

    Args:
        pdf_path: PDF 文件路径
        start_page: 起始页码 (1-indexed)
        end_page: 结束页码 (1-indexed, inclusive)

    Returns:
        提取的文本内容
    """
    doc = fitz.open(pdf_path)
    text_parts = []

    # PDF 页码是 0-indexed
    for page_num in range(start_page - 1, end_page):
        if page_num < len(doc):
            page = doc[page_num]
            text = page.get_text("text")
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

    doc.close()
    return "\n\n".join(text_parts)


def extract_chapter(chapter_num: str, save_raw: bool = True) -> Optional[str]:
    """
    提取指定章节的文本

    Args:
        chapter_num: 章节编号 (如 "01", "02")
        save_raw: 是否保存原始文本到文件

    Returns:
        提取的文本内容，如果章节不存在则返回 None
    """
    chapter_info = CHAPTERS.get(chapter_num)
    if not chapter_info:
        print(f"章节 {chapter_num} 不存在")
        return None

    start_page, end_page = chapter_info.page_range
    print(f"提取章节 {chapter_num}: {chapter_info.chinese_title}")
    print(f"  页码范围: {start_page}-{end_page}")

    text = extract_pages(PDF_PATH, start_page, end_page)

    if save_raw:
        # 保存原始文本
        RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        raw_file = RAW_OUTPUT_DIR / f"{chapter_num}-{chapter_info.chinese_title}_raw.txt"
        with open(raw_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  原始文本已保存: {raw_file}")

    return text


def extract_all_chapters(save_raw: bool = True) -> dict:
    """
    提取所有章节的文本

    Args:
        save_raw: 是否保存原始文本到文件

    Returns:
        章节编号到文本内容的映射字典
    """
    results = {}
    for chapter_num in CHAPTERS.keys():
        text = extract_chapter(chapter_num, save_raw)
        if text:
            results[chapter_num] = text
    return results


def get_pdf_info(pdf_path: Path) -> dict:
    """
    获取 PDF 文件信息

    Args:
        pdf_path: PDF 文件路径

    Returns:
        PDF 元数据字典
    """
    doc = fitz.open(pdf_path)
    info = {
        "page_count": len(doc),
        "metadata": doc.metadata,
        "is_encrypted": doc.is_encrypted,
    }
    doc.close()
    return info


def preview_page(pdf_path: Path, page_num: int, max_chars: int = 500) -> str:
    """
    预览指定页面的内容

    Args:
        pdf_path: PDF 文件路径
        page_num: 页码 (1-indexed)
        max_chars: 最大显示字符数

    Returns:
        页面文本预览
    """
    doc = fitz.open(pdf_path)
    if page_num < 1 or page_num > len(doc):
        return f"页码 {page_num} 超出范围 (1-{len(doc)})"

    page = doc[page_num - 1]
    text = page.get_text("text")
    doc.close()

    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


if __name__ == "__main__":
    import sys

    # 检查 PDF 文件是否存在
    if not PDF_PATH.exists():
        print(f"错误: PDF 文件不存在: {PDF_PATH}")
        sys.exit(1)

    # 显示 PDF 信息
    info = get_pdf_info(PDF_PATH)
    print(f"PDF 文件: {PDF_PATH}")
    print(f"总页数: {info['page_count']}")
    print()

    # 如果有命令行参数，提取指定章节
    if len(sys.argv) > 1:
        chapter_num = sys.argv[1]
        text = extract_chapter(chapter_num)
        if text:
            print(f"\n提取完成，共 {len(text)} 字符")
    else:
        # 显示帮助信息
        print("用法: python extract_chapters.py [章节编号]")
        print("示例: python extract_chapters.py 01")
        print()
        print("可用章节:")
        for num, info in CHAPTERS.items():
            print(f"  {num}: {info.chinese_title} (第{info.page_range[0]}-{info.page_range[1]}页)")
