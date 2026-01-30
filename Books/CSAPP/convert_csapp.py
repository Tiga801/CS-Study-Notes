#!/usr/bin/env python3
"""
CSAPP PDF 转 Markdown 主脚本

将 CSAPP PDF 文件按章节提取并转换为 Markdown 格式。
支持单章节转换或批量转换所有章节。
"""

import argparse
import sys
from pathlib import Path

from chapter_mapping import CHAPTERS, get_chapter_filename
from extract_chapters import extract_chapter, get_pdf_info, PDF_PATH
from text_to_markdown import text_to_markdown, create_chapter_template


# 输出目录
OUTPUT_DIR = Path(__file__).parent / "chapters"
RAW_DIR = Path(__file__).parent / "raw_text"


def convert_chapter(chapter_num: str, use_template: bool = False) -> Path:
    """
    转换单个章节

    Args:
        chapter_num: 章节编号
        use_template: 是否使用模板而不是提取的内容

    Returns:
        输出文件路径
    """
    chapter_info = CHAPTERS.get(chapter_num)
    if not chapter_info:
        print(f"错误: 章节 {chapter_num} 不存在")
        return None

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / get_chapter_filename(chapter_num)

    if use_template:
        # 使用模板
        md_content = create_chapter_template(chapter_info)
    else:
        # 提取并转换
        print(f"\n处理章节 {chapter_num}: {chapter_info.chinese_title}")
        print("=" * 50)

        # 提取文本
        text = extract_chapter(chapter_num, save_raw=True)
        if not text:
            return None

        # 转换为 Markdown
        md_content = text_to_markdown(text, chapter_info)

    # 保存 Markdown 文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Markdown 文件已保存: {output_file}")
    return output_file


def convert_all_chapters(use_template: bool = False) -> list:
    """
    转换所有章节

    Args:
        use_template: 是否使用模板

    Returns:
        生成的文件路径列表
    """
    output_files = []
    total = len(CHAPTERS)

    for i, chapter_num in enumerate(CHAPTERS.keys(), 1):
        print(f"\n[{i}/{total}] ", end="")
        output_file = convert_chapter(chapter_num, use_template)
        if output_file:
            output_files.append(output_file)

    return output_files


def show_chapters():
    """显示所有可用章节"""
    print("\nCSAPP 章节列表:")
    print("-" * 70)
    print(f"{'编号':<6} {'中文标题':<20} {'页码范围':<12} {'页数':<6}")
    print("-" * 70)

    for num, info in CHAPTERS.items():
        start, end = info.page_range
        pages = end - start + 1
        print(f"{num:<6} {info.chinese_title:<20} {start}-{end:<8} {pages:<6}")

    print("-" * 70)
    print(f"共 {len(CHAPTERS)} 个章节")


def show_pdf_info():
    """显示 PDF 文件信息"""
    if not PDF_PATH.exists():
        print(f"错误: PDF 文件不存在: {PDF_PATH}")
        return

    info = get_pdf_info(PDF_PATH)
    print(f"\nPDF 文件信息:")
    print(f"  路径: {PDF_PATH}")
    print(f"  总页数: {info['page_count']}")
    print(f"  加密: {'是' if info['is_encrypted'] else '否'}")

    if info['metadata']:
        print(f"  元数据:")
        for key, value in info['metadata'].items():
            if value:
                print(f"    {key}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="CSAPP PDF 转 Markdown 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python convert_csapp.py --list           # 列出所有章节
  python convert_csapp.py --info           # 显示 PDF 信息
  python convert_csapp.py -c 01            # 转换第 1 章
  python convert_csapp.py -c 01 02 03      # 转换多个章节
  python convert_csapp.py --all            # 转换所有章节
  python convert_csapp.py --all --template # 生成所有章节模板
"""
    )

    parser.add_argument(
        "-c", "--chapter",
        nargs="+",
        help="要转换的章节编号 (如: 01, 02, ...)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="转换所有章节"
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="生成空白模板而不是提取内容"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用章节"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="显示 PDF 文件信息"
    )

    args = parser.parse_args()

    # 处理命令
    if args.list:
        show_chapters()
        return

    if args.info:
        show_pdf_info()
        return

    if not PDF_PATH.exists():
        print(f"错误: PDF 文件不存在: {PDF_PATH}")
        print("请将 CSAPP PDF 文件放置在此目录下。")
        sys.exit(1)

    if args.all:
        print("开始转换所有章节...")
        output_files = convert_all_chapters(args.template)
        print(f"\n转换完成! 共生成 {len(output_files)} 个文件")
        print(f"输出目录: {OUTPUT_DIR}")

    elif args.chapter:
        for chapter_num in args.chapter:
            convert_chapter(chapter_num, args.template)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
