#!/usr/bin/env python3
"""
PaddleOCR PDF 提取工作流脚本

用于 CSAPP 书籍翻译项目的完整 PDF 处理工作流：
1. 将 PDF 转换为图片
2. 按章节整理图片
3. 使用 PaddleOCR-VL-1.5 进行 OCR 提取
4. 将提取结果拼接为章节文档

使用方法:
    python ocr_workflow.py --help
    python ocr_workflow.py pdf2img --dpi 300
    python ocr_workflow.py organize --chapters 01 02
    python ocr_workflow.py ocr --chapter 01 --device gpu:0
    python ocr_workflow.py concat --chapter 01
    python ocr_workflow.py pipeline --chapters 01 02
    python ocr_workflow.py status
"""

import argparse
import gc
import json
import logging
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

# 本地导入
from chapter_mapping import CHAPTERS, ChapterInfo, GLOSSARY


# ============================================================================
# 配置
# ============================================================================

@dataclass
class Config:
    """工作流配置"""
    # 基础路径
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent)

    # PDF 文件路径
    @property
    def pdf_path(self) -> Path:
        return self.base_dir / "CSAPP_2016.pdf"

    # 输出目录
    @property
    def images_dir(self) -> Path:
        return self.base_dir / "extract_images"

    @property
    def ocr_texts_dir(self) -> Path:
        return self.base_dir / "paddleocr_texts"

    @property
    def raw_texts_dir(self) -> Path:
        return self.base_dir / "raw_texts"

    @property
    def chapters_dir(self) -> Path:
        return self.base_dir / "chapters"

    # 默认设置
    default_dpi: int = 300
    default_device: str = "gpu:0"
    batch_size: int = 50  # 分批处理大小，用于内存管理


CONFIG = Config()


# ============================================================================
# 日志配置
# ============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """配置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# PDF 转图片
# ============================================================================

class PDFToImageConverter:
    """
    将 PDF 页面转换为 PNG 图片

    主要方案：使用 pdf2image（需要 poppler）
    备用方案：使用 PyMuPDF (fitz)
    """

    def __init__(self, pdf_path: Path, output_dir: Path, dpi: int = 300):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.dpi = dpi
        self.all_images_dir = output_dir / "all"

    def convert_all(self) -> List[Path]:
        """转换整个 PDF 为图片"""
        logger.info(f"开始转换 PDF: {self.pdf_path}")
        logger.info(f"DPI: {self.dpi}, 输出目录: {self.all_images_dir}")

        self.all_images_dir.mkdir(parents=True, exist_ok=True)

        try:
            return self._convert_with_pdf2image()
        except ImportError:
            logger.warning("pdf2image 未安装，尝试使用 PyMuPDF")
            return self._convert_with_pymupdf()

    def convert_range(self, start_page: int, end_page: int) -> List[Path]:
        """转换指定页码范围"""
        logger.info(f"转换页码范围: {start_page}-{end_page}")

        self.all_images_dir.mkdir(parents=True, exist_ok=True)

        try:
            return self._convert_with_pdf2image(pages=(start_page, end_page))
        except ImportError:
            logger.warning("pdf2image 未安装，尝试使用 PyMuPDF")
            return self._convert_with_pymupdf(pages=(start_page, end_page))

    def _convert_with_pdf2image(
        self,
        pages: Optional[Tuple[int, int]] = None
    ) -> List[Path]:
        """使用 pdf2image 转换（主要方案）"""
        from pdf2image import convert_from_path, pdfinfo_from_path

        # 获取 PDF 信息
        info = pdfinfo_from_path(str(self.pdf_path))
        total_pages = info["Pages"]
        logger.info(f"PDF 总页数: {total_pages}")

        start = pages[0] if pages else 1
        end = pages[1] if pages else total_pages

        output_paths = []
        batch_size = CONFIG.batch_size

        # 分批处理以管理内存
        for batch_start in range(start, end + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, end)

            logger.info(f"处理批次: 页码 {batch_start}-{batch_end}")

            images = convert_from_path(
                str(self.pdf_path),
                dpi=self.dpi,
                first_page=batch_start,
                last_page=batch_end,
                fmt="png",
                thread_count=4
            )

            for i, img in enumerate(images):
                page_num = batch_start + i
                output_path = self.all_images_dir / f"{page_num:04d}.png"
                img.save(output_path, "PNG")
                output_paths.append(output_path)
                logger.debug(f"保存: {output_path}")

            # 清理内存
            del images
            gc.collect()

        logger.info(f"转换完成: 共 {len(output_paths)} 张图片")
        return output_paths

    def _convert_with_pymupdf(
        self,
        pages: Optional[Tuple[int, int]] = None
    ) -> List[Path]:
        """使用 PyMuPDF 转换（备用方案）"""
        import fitz

        doc = fitz.open(self.pdf_path)
        total_pages = len(doc)
        logger.info(f"PDF 总页数: {total_pages}")

        # 页码转换：外部使用 1-indexed，fitz 使用 0-indexed
        start = (pages[0] - 1) if pages else 0
        end = pages[1] if pages else total_pages

        output_paths = []
        zoom = self.dpi / 72  # 72 是 PDF 默认分辨率
        mat = fitz.Matrix(zoom, zoom)

        for page_idx in range(start, end):
            page = doc[page_idx]
            pix = page.get_pixmap(matrix=mat)

            page_num = page_idx + 1  # 转回 1-indexed
            output_path = self.all_images_dir / f"{page_num:04d}.png"
            pix.save(str(output_path))
            output_paths.append(output_path)

            if (page_idx - start + 1) % 50 == 0:
                logger.info(f"已处理: {page_idx - start + 1}/{end - start} 页")

        doc.close()
        logger.info(f"转换完成: 共 {len(output_paths)} 张图片")
        return output_paths


# ============================================================================
# 图片整理
# ============================================================================

class ImageOrganizer:
    """
    按章节整理图片

    根据 chapter_mapping.py 中的页码范围，将图片整理到章节文件夹
    """

    def __init__(self, images_dir: Path):
        self.images_dir = images_dir
        self.all_images_dir = images_dir / "all"

    def organize_chapter(self, chapter_num: str, copy: bool = False) -> Path:
        """
        整理指定章节的图片

        Args:
            chapter_num: 章节编号（如 "01", "02"）
            copy: True=复制文件，False=创建符号链接

        Returns:
            章节图片目录路径
        """
        chapter_info = CHAPTERS.get(chapter_num)
        if not chapter_info:
            raise ValueError(f"章节 {chapter_num} 不存在")

        start_page, end_page = chapter_info.page_range
        chapter_dir = self.images_dir / chapter_num
        chapter_dir.mkdir(parents=True, exist_ok=True)

        linked_count = 0
        missing_count = 0

        for page_num in range(start_page, end_page + 1):
            src = self.all_images_dir / f"{page_num:04d}.png"
            dst = chapter_dir / f"{page_num:04d}.png"

            if not src.exists():
                logger.warning(f"源图片不存在: {src}")
                missing_count += 1
                continue

            # 如果目标已存在，先删除
            if dst.exists() or dst.is_symlink():
                dst.unlink()

            if copy:
                shutil.copy2(src, dst)
            else:
                # 创建相对符号链接
                dst.symlink_to(os.path.relpath(src, dst.parent))

            linked_count += 1

        logger.info(
            f"整理章节 {chapter_num} ({chapter_info.chinese_title}): "
            f"页码 {start_page}-{end_page}, "
            f"成功 {linked_count} 页, 缺失 {missing_count} 页"
        )

        return chapter_dir

    def organize_all(self, copy: bool = False) -> Dict[str, Path]:
        """整理所有章节"""
        results = {}
        for chapter_num in CHAPTERS.keys():
            try:
                results[chapter_num] = self.organize_chapter(chapter_num, copy)
            except Exception as e:
                logger.error(f"整理章节 {chapter_num} 失败: {e}")
                results[chapter_num] = None
        return results


# ============================================================================
# OCR 提取
# ============================================================================

class PaddleOCRExtractor:
    """
    使用 PaddleOCR-VL-1.5 提取文本

    支持 GPU 和 CPU 模式，优先使用 GPU
    """

    def __init__(
        self,
        output_dir: Path,
        device: str = "gpu:0",
        use_layout_detection: bool = True,
        use_doc_orientation_classify: bool = True,
    ):
        self.output_dir = output_dir
        self.device = device
        self.use_layout_detection = use_layout_detection
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.pipeline = None

    def _init_pipeline(self):
        """延迟初始化 PaddleOCR pipeline"""
        if self.pipeline is not None:
            return

        try:
            from paddleocr import PaddleOCRVL

            self.pipeline = PaddleOCRVL(
                device=self.device,
                use_layout_detection=self.use_layout_detection,
                use_doc_orientation_classify=self.use_doc_orientation_classify,
            )
            logger.info(f"PaddleOCR-VL 初始化成功，设备: {self.device}")

        except Exception as e:
            if "gpu" in self.device.lower():
                logger.warning(f"GPU 不可用 ({e})，回退到 CPU")
                from paddleocr import PaddleOCRVL
                self.pipeline = PaddleOCRVL(
                    device="cpu",
                    use_layout_detection=self.use_layout_detection,
                    use_doc_orientation_classify=self.use_doc_orientation_classify,
                )
                logger.info("PaddleOCR-VL 初始化成功，设备: CPU")
            else:
                raise

    def extract_image(self, image_path: Path, chapter_num: str) -> Dict[str, Any]:
        """
        提取单张图片的文本

        Args:
            image_path: 图片路径
            chapter_num: 章节编号

        Returns:
            包含 'text', 'markdown_path', 'json_path' 的字典
        """
        self._init_pipeline()

        page_num = image_path.stem  # 例如 "0031"
        chapter_output_dir = self.output_dir / chapter_num
        chapter_output_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "image_path": str(image_path),
            "page_num": page_num,
            "markdown_path": None,
            "json_path": None,
            "error": None
        }

        try:
            output = self.pipeline.predict(str(image_path))

            for res in output:
                # 保存为 Markdown
                md_path = chapter_output_dir / f"{page_num}.md"
                res.save_to_markdown(save_path=str(chapter_output_dir))
                result["markdown_path"] = str(md_path)

                # 保存为 JSON（包含结构化数据）
                json_path = chapter_output_dir / f"{page_num}.json"
                res.save_to_json(save_path=str(chapter_output_dir))
                result["json_path"] = str(json_path)

        except Exception as e:
            logger.error(f"OCR 提取失败 ({image_path}): {e}")
            result["error"] = str(e)

        return result

    def extract_chapter(
        self,
        chapter_num: str,
        images_dir: Path,
        skip_existing: bool = True
    ) -> List[Dict[str, Any]]:
        """
        提取整个章节的所有图片

        Args:
            chapter_num: 章节编号
            images_dir: 图片根目录
            skip_existing: 是否跳过已存在的结果

        Returns:
            提取结果列表
        """
        chapter_images_dir = images_dir / chapter_num
        if not chapter_images_dir.exists():
            raise ValueError(f"章节图片目录不存在: {chapter_images_dir}")

        # 获取排序后的图片列表
        images = sorted(chapter_images_dir.glob("*.png"))
        total = len(images)

        if total == 0:
            raise ValueError(f"章节 {chapter_num} 没有图片")

        logger.info(f"开始处理章节 {chapter_num}: 共 {total} 张图片")

        results = []
        success_count = 0
        skip_count = 0
        error_count = 0

        for i, image_path in enumerate(images, 1):
            page_num = image_path.stem

            # 检查是否已存在
            if skip_existing:
                existing_md = self.output_dir / chapter_num / f"{page_num}.md"
                if existing_md.exists():
                    logger.debug(f"跳过已存在: {page_num}")
                    skip_count += 1
                    continue

            result = self.extract_image(image_path, chapter_num)
            results.append(result)

            if result["error"]:
                error_count += 1
            else:
                success_count += 1

            # 进度显示
            if i % 10 == 0 or i == total:
                logger.info(f"进度: [{i}/{total}] 成功={success_count}, 跳过={skip_count}, 错误={error_count}")

        logger.info(
            f"章节 {chapter_num} 处理完成: "
            f"成功={success_count}, 跳过={skip_count}, 错误={error_count}"
        )

        return results


# ============================================================================
# 文档拼接
# ============================================================================

class ChapterConcatenator:
    """
    将 OCR 提取的每页文本拼接为章节文档
    """

    def __init__(self, ocr_texts_dir: Path, output_dir: Path):
        self.ocr_texts_dir = ocr_texts_dir
        self.output_dir = output_dir

    def concatenate_chapter(self, chapter_num: str) -> Path:
        """
        拼接章节的所有页面文本

        Returns:
            输出文件路径
        """
        chapter_info = CHAPTERS.get(chapter_num)
        if not chapter_info:
            raise ValueError(f"章节 {chapter_num} 不存在")

        chapter_texts_dir = self.ocr_texts_dir / chapter_num
        if not chapter_texts_dir.exists():
            raise ValueError(f"OCR 文本目录不存在: {chapter_texts_dir}")

        # 获取排序后的 Markdown 文件列表
        md_files = sorted(chapter_texts_dir.glob("*.md"))

        if not md_files:
            raise ValueError(f"章节 {chapter_num} 没有 OCR 文本文件")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成安全的文件名
        safe_title = chapter_info.english_title.replace(" ", "_").replace(":", "").replace(",", "")
        output_path = self.output_dir / f"{chapter_num}-{safe_title}.md"

        # 构建文档头部
        content_parts = [
            f"# Chapter {chapter_num}: {chapter_info.english_title}",
            "",
            f"> **中文标题**: {chapter_info.chinese_title}",
            f"> **页码范围**: {chapter_info.page_range[0]}-{chapter_info.page_range[1]}",
            f"> **OCR 提取**: PaddleOCR-VL-1.5",
            "",
            "---",
            ""
        ]

        # 拼接每页内容
        for md_file in md_files:
            page_num = md_file.stem

            try:
                page_content = md_file.read_text(encoding="utf-8")

                content_parts.append(f"<!-- Page {page_num} -->")
                content_parts.append("")
                content_parts.append(page_content.strip())
                content_parts.append("")
                content_parts.append("---")
                content_parts.append("")

            except Exception as e:
                logger.warning(f"读取页面 {page_num} 失败: {e}")
                content_parts.append(f"<!-- Page {page_num} - 读取失败: {e} -->")
                content_parts.append("")

        # 写入输出文件
        output_content = "\n".join(content_parts)
        output_path.write_text(output_content, encoding="utf-8")

        logger.info(
            f"章节 {chapter_num} 拼接完成: "
            f"{len(md_files)} 页 -> {output_path}"
        )

        return output_path


# ============================================================================
# 工作流编排
# ============================================================================

class WorkflowPipeline:
    """
    完整工作流编排器
    """

    def __init__(self, config: Config):
        self.config = config

    def run_full_pipeline(
        self,
        chapters: List[str],
        dpi: int = 300,
        device: str = "gpu:0",
        skip_existing: bool = True,
        copy_images: bool = False
    ) -> Dict[str, Any]:
        """
        运行完整工作流

        Steps:
        1. 将 PDF 转换为图片（如果不存在）
        2. 按章节整理图片
        3. 运行 OCR 提取
        4. 拼接章节文档
        """
        logger.info(f"开始工作流，章节: {chapters}")

        results = {
            "chapters": {},
            "errors": []
        }

        # 步骤 1: PDF 转图片
        converter = PDFToImageConverter(
            self.config.pdf_path,
            self.config.images_dir,
            dpi=dpi
        )

        all_images_dir = self.config.images_dir / "all"
        if not all_images_dir.exists() or not list(all_images_dir.glob("*.png")):
            logger.info("=" * 60)
            logger.info("步骤 1: 将 PDF 转换为图片")
            logger.info("=" * 60)
            try:
                converter.convert_all()
            except Exception as e:
                logger.error(f"PDF 转换失败: {e}")
                results["errors"].append(f"PDF 转换失败: {e}")
                return results
        else:
            logger.info("步骤 1: 跳过（图片已存在）")

        # 初始化其他组件
        organizer = ImageOrganizer(self.config.images_dir)
        extractor = PaddleOCRExtractor(
            self.config.ocr_texts_dir,
            device=device
        )
        concatenator = ChapterConcatenator(
            self.config.ocr_texts_dir,
            self.config.raw_texts_dir
        )

        # 处理每个章节
        for chapter_num in chapters:
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"处理章节 {chapter_num}")
            logger.info("=" * 60)

            chapter_result = {
                "status": "success",
                "images_dir": None,
                "ocr_results": None,
                "output_path": None,
                "error": None
            }

            try:
                # 步骤 2: 整理图片
                logger.info(f"步骤 2: 整理章节 {chapter_num} 图片")
                chapter_result["images_dir"] = str(
                    organizer.organize_chapter(chapter_num, copy=copy_images)
                )

                # 步骤 3: OCR 提取
                logger.info(f"步骤 3: OCR 提取章节 {chapter_num}")
                chapter_result["ocr_results"] = extractor.extract_chapter(
                    chapter_num,
                    self.config.images_dir,
                    skip_existing=skip_existing
                )

                # 步骤 4: 拼接文档
                logger.info(f"步骤 4: 拼接章节 {chapter_num} 文档")
                chapter_result["output_path"] = str(
                    concatenator.concatenate_chapter(chapter_num)
                )

            except Exception as e:
                logger.error(f"章节 {chapter_num} 处理失败: {e}")
                chapter_result["status"] = "error"
                chapter_result["error"] = str(e)
                results["errors"].append(f"章节 {chapter_num}: {e}")

            results["chapters"][chapter_num] = chapter_result

        return results


# ============================================================================
# 状态显示
# ============================================================================

def show_status(config: Config):
    """显示所有章节的工作流状态"""
    print("\n" + "=" * 80)
    print("CSAPP OCR 工作流状态")
    print("=" * 80)
    print(f"\n{'章节':<10} {'标题':<20} {'图片':<12} {'OCR':<12} {'原始文档':<12}")
    print("-" * 80)

    for num, info in CHAPTERS.items():
        # 检查图片
        images_dir = config.images_dir / num
        if images_dir.exists():
            img_count = len(list(images_dir.glob("*.png")))
            img_status = f"{img_count} 文件"
        else:
            img_status = "---"

        # 检查 OCR 结果
        ocr_dir = config.ocr_texts_dir / num
        if ocr_dir.exists():
            ocr_count = len(list(ocr_dir.glob("*.md")))
            ocr_status = f"{ocr_count} 文件"
        else:
            ocr_status = "---"

        # 检查原始文档
        safe_title = info.english_title.replace(" ", "_").replace(":", "").replace(",", "")
        raw_path = config.raw_texts_dir / f"{num}-{safe_title}.md"
        raw_status = "已生成" if raw_path.exists() else "---"

        print(f"{num:<10} {info.chinese_title:<20} {img_status:<12} {ocr_status:<12} {raw_status:<12}")

    print("-" * 80)

    # 显示路径信息
    print(f"\n目录路径:")
    print(f"  PDF 文件:     {config.pdf_path}")
    print(f"  图片目录:     {config.images_dir}")
    print(f"  OCR 文本:     {config.ocr_texts_dir}")
    print(f"  原始文档:     {config.raw_texts_dir}")
    print(f"  翻译文档:     {config.chapters_dir}")
    print()


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="PaddleOCR PDF 提取工作流 (CSAPP)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python ocr_workflow.py status                          # 显示状态
  python ocr_workflow.py pdf2img --dpi 300               # 转换 PDF
  python ocr_workflow.py organize --chapters 01 02       # 整理图片
  python ocr_workflow.py ocr --chapter 01                # OCR 提取
  python ocr_workflow.py concat --chapter 01             # 拼接文档
  python ocr_workflow.py pipeline --chapters 01          # 完整流程
        """
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # status 命令
    subparsers.add_parser("status", help="显示工作流状态")

    # pdf2img 命令
    pdf2img_parser = subparsers.add_parser("pdf2img", help="将 PDF 转换为图片")
    pdf2img_parser.add_argument(
        "--dpi", type=int, default=300,
        help="图片 DPI (默认: 300)"
    )
    pdf2img_parser.add_argument(
        "--pages", nargs=2, type=int, metavar=("START", "END"),
        help="页码范围 (如: --pages 31 58)"
    )

    # organize 命令
    organize_parser = subparsers.add_parser("organize", help="按章节整理图片")
    organize_parser.add_argument(
        "--chapters", nargs="+",
        help="章节编号 (如: --chapters 01 02 或 --chapters all)"
    )
    organize_parser.add_argument(
        "--all", action="store_true",
        help="整理所有章节"
    )
    organize_parser.add_argument(
        "--copy", action="store_true",
        help="复制文件而非创建符号链接"
    )

    # ocr 命令
    ocr_parser = subparsers.add_parser("ocr", help="运行 OCR 提取")
    ocr_parser.add_argument(
        "--chapter", required=True,
        help="章节编号 (如: --chapter 01 或 --chapter all)"
    )
    ocr_parser.add_argument(
        "--device", default="gpu:0",
        help="设备 (gpu:0, cpu, 默认: gpu:0)"
    )
    ocr_parser.add_argument(
        "--force", action="store_true",
        help="强制重新提取（不跳过已存在）"
    )

    # concat 命令
    concat_parser = subparsers.add_parser("concat", help="拼接章节文档")
    concat_parser.add_argument(
        "--chapter", required=True,
        help="章节编号 (如: --chapter 01 或 --chapter all)"
    )

    # pipeline 命令
    pipeline_parser = subparsers.add_parser("pipeline", help="运行完整工作流")
    pipeline_parser.add_argument(
        "--chapters", nargs="+", required=True,
        help="章节编号列表"
    )
    pipeline_parser.add_argument(
        "--dpi", type=int, default=300,
        help="图片 DPI"
    )
    pipeline_parser.add_argument(
        "--device", default="gpu:0",
        help="OCR 设备"
    )
    pipeline_parser.add_argument(
        "--force", action="store_true",
        help="强制重新处理"
    )
    pipeline_parser.add_argument(
        "--copy", action="store_true",
        help="复制图片而非符号链接"
    )

    args = parser.parse_args()

    # 配置日志
    if args.verbose:
        setup_logging(verbose=True)

    # 执行命令
    if args.command == "status":
        show_status(CONFIG)

    elif args.command == "pdf2img":
        converter = PDFToImageConverter(
            CONFIG.pdf_path,
            CONFIG.images_dir,
            dpi=args.dpi
        )
        if args.pages:
            converter.convert_range(args.pages[0], args.pages[1])
        else:
            converter.convert_all()

    elif args.command == "organize":
        organizer = ImageOrganizer(CONFIG.images_dir)
        if args.all:
            organizer.organize_all(copy=args.copy)
        elif args.chapters:
            # 支持 "all" 关键字
            chapters = list(CHAPTERS.keys()) if "all" in args.chapters else args.chapters
            for ch in chapters:
                organizer.organize_chapter(ch, copy=args.copy)
        else:
            print("错误: 请指定 --chapters 或 --all")
            sys.exit(1)

    elif args.command == "ocr":
        # 支持 "all" 关键字
        chapters_to_process = list(CHAPTERS.keys()) if args.chapter == "all" else [args.chapter]

        extractor = PaddleOCRExtractor(
            CONFIG.ocr_texts_dir,
            device=args.device
        )

        for ch in chapters_to_process:
            print(f"\n{'='*60}")
            print(f"处理章节: {ch} - {CHAPTERS[ch].chinese_title}")
            print(f"{'='*60}")
            try:
                extractor.extract_chapter(
                    ch,
                    CONFIG.images_dir,
                    skip_existing=not args.force
                )
            except Exception as e:
                logger.error(f"章节 {ch} 提取失败: {e}")

    elif args.command == "concat":
        # 支持 "all" 关键字
        chapters_to_process = list(CHAPTERS.keys()) if args.chapter == "all" else [args.chapter]

        concatenator = ChapterConcatenator(
            CONFIG.ocr_texts_dir,
            CONFIG.raw_texts_dir
        )

        for ch in chapters_to_process:
            try:
                output_path = concatenator.concatenate_chapter(ch)
                print(f"[✓] 章节 {ch}: {output_path}")
            except Exception as e:
                print(f"[✗] 章节 {ch}: {e}")

    elif args.command == "pipeline":
        pipeline = WorkflowPipeline(CONFIG)
        results = pipeline.run_full_pipeline(
            chapters=args.chapters,
            dpi=args.dpi,
            device=args.device,
            skip_existing=not args.force,
            copy_images=args.copy
        )

        print("\n" + "=" * 60)
        print("工作流结果")
        print("=" * 60)
        for ch, result in results["chapters"].items():
            status = "✓" if result["status"] == "success" else "✗"
            output = result.get("output_path", result.get("error", "未知"))
            print(f"  [{status}] 章节 {ch}: {output}")

        if results["errors"]:
            print("\n错误:")
            for err in results["errors"]:
                print(f"  - {err}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
