#!/usr/bin/env python3
"""
图片垂直合成脚本

将多张图片在垂直方向拼接为一张图像，用于汇总查看原始书页。

使用方法:
    # 从目录合并（默认按文件名排序）
    python Books/CSAPP/merge_images.py dir --input Books/CSAPP/extract_images/02 --output merged_ch02.png

    # 指定统一宽度缩放
    python Books/CSAPP/merge_images.py dir --input Books/CSAPP/extract_images/02 --output merged_ch02.png --width 1200

    # 从文件列表合并
    python Books/CSAPP/merge_images.py files --input "image1.png image2.png" --output out.png

    # 合并项目根目录下所有 PNG（不指定 --input 时默认为项目根目录）
    python Books/CSAPP/merge_images.py dir --output merged.png
"""

import argparse
import glob
import logging
import sys
from pathlib import Path
from typing import List, Optional

# 项目根目录：脚本位于 Books/CSAPP/，往上两级
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


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
# ImageMerger 核心类
# ============================================================================

class ImageMerger:
    """
    图片垂直合成器

    支持从目录或文件列表读取图片，按垂直方向拼接后保存。
    可选统一宽度缩放，保持宽高比。
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or PROJECT_ROOT
        logger.debug(f"ImageMerger 初始化，根目录: {self.root_dir}")

    def merge_from_files(
        self,
        image_paths: List[Path],
        output_path: Path,
        resize_width: int = 0,
        quality: int = 95,
    ) -> Path:
        """
        从文件路径列表垂直合并图片。

        Args:
            image_paths: 图片路径列表（按顺序合并）
            output_path: 输出文件路径
            resize_width: 统一缩放宽度，0 表示不缩放
            quality: JPEG 输出质量（仅对 .jpg 有效）

        Returns:
            输出文件的绝对路径
        """
        if not image_paths:
            raise ValueError("图片路径列表为空，无法合并")

        logger.info(f"合并 {len(image_paths)} 张图片 → {output_path}")

        images = [self._load_and_resize(p, resize_width) for p in image_paths]
        merged = self._merge_vertical(images)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs = {}
        if output_path.suffix.lower() in (".jpg", ".jpeg"):
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True

        merged.save(str(output_path), **save_kwargs)
        logger.info(f"已保存: {output_path}  尺寸: {merged.size[0]}x{merged.size[1]}")
        return output_path.resolve()

    def merge_from_dir(
        self,
        input_dir: Path,
        output_path: Path,
        pattern: str = "*.png",
        sort: bool = True,
        resize_width: int = 0,
        quality: int = 95,
    ) -> Path:
        """
        从目录中读取图片并垂直合并。

        Args:
            input_dir: 输入目录
            output_path: 输出文件路径
            pattern: 文件匹配模式（如 *.png）
            sort: 是否按文件名排序
            resize_width: 统一缩放宽度，0 表示不缩放
            quality: JPEG 输出质量

        Returns:
            输出文件的绝对路径
        """
        input_dir = Path(input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")

        matched = list(input_dir.glob(pattern))
        if not matched:
            raise FileNotFoundError(
                f"目录 {input_dir} 中未找到匹配 '{pattern}' 的文件"
            )

        if sort:
            matched.sort(key=lambda p: p.name)

        logger.info(f"从目录 {input_dir} 找到 {len(matched)} 张图片（模式: {pattern}）")
        return self.merge_from_files(matched, output_path, resize_width, quality)

    def _load_and_resize(self, path: Path, target_width: int):
        """
        加载图片，可选按比例缩放至统一宽度。

        Args:
            path: 图片文件路径
            target_width: 目标宽度，0 表示不缩放

        Returns:
            PIL.Image 对象（RGB 模式）
        """
        try:
            from PIL import Image
        except ImportError:
            logger.error("Pillow 未安装，请运行: pip install Pillow")
            sys.exit(1)

        img = Image.open(str(path)).convert("RGB")
        logger.debug(f"加载: {path.name}  原始尺寸: {img.size[0]}x{img.size[1]}")

        if target_width > 0 and img.width != target_width:
            ratio = target_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((target_width, new_height), Image.LANCZOS)
            logger.debug(f"  缩放至: {img.size[0]}x{img.size[1]}")

        return img

    def _merge_vertical(self, images):
        """
        核心合并逻辑：计算总高度，将所有图片垂直粘贴到画布上。

        Args:
            images: PIL.Image 对象列表

        Returns:
            合并后的 PIL.Image 对象
        """
        try:
            from PIL import Image
        except ImportError:
            logger.error("Pillow 未安装，请运行: pip install Pillow")
            sys.exit(1)

        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images)
        logger.debug(f"画布尺寸: {max_width}x{total_height}（共 {len(images)} 张）")

        canvas = Image.new("RGB", (max_width, total_height), color=(255, 255, 255))

        y_offset = 0
        for img in images:
            # 若图片宽度不足，居中粘贴
            x_offset = (max_width - img.width) // 2
            canvas.paste(img, (x_offset, y_offset))
            y_offset += img.height

        return canvas


# ============================================================================
# 命令行接口
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="图片垂直合成工具 - 将多张图片拼接为一张",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从目录合并所有 PNG
  python merge_images.py dir --input Books/CSAPP/extract_images/02 --output merged_ch02.png

  # 统一缩放宽度为 1200px
  python merge_images.py dir --input Books/CSAPP/extract_images/02 --output merged.png --width 1200

  # 从文件列表合并
  python merge_images.py files --input "image1.png image2.png image3.png" --output out.png

  # 合并当前目录所有 PNG（默认路径为项目根目录）
  python merge_images.py dir --output merged.png
        """,
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="输出调试信息")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- dir 子命令 ----
    dir_parser = subparsers.add_parser("dir", help="从目录合并图片")
    dir_parser.add_argument(
        "--input", "-i",
        type=Path,
        default=None,
        help="输入目录（默认：项目根目录）",
    )
    dir_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("merged_output.png"),
        help="输出文件路径（默认：merged_output.png）",
    )
    dir_parser.add_argument(
        "--pattern", "-p",
        default="*.png",
        help="文件匹配模式（默认：*.png）",
    )
    dir_parser.add_argument(
        "--width", "-w",
        type=int,
        default=0,
        help="统一缩放宽度，0 表示不缩放（默认：0）",
    )
    dir_parser.add_argument(
        "--quality", "-q",
        type=int,
        default=95,
        help="JPEG 输出质量，仅对 .jpg 有效（默认：95）",
    )
    dir_parser.add_argument(
        "--no-sort",
        action="store_true",
        help="禁用按文件名排序（默认：启用排序）",
    )

    # ---- files 子命令 ----
    files_parser = subparsers.add_parser("files", help="从文件列表合并图片")
    files_parser.add_argument(
        "--input", "-i",
        required=True,
        help='空格分隔的图片路径或 glob 模式（用引号括起）',
    )
    files_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("merged_output.png"),
        help="输出文件路径（默认：merged_output.png）",
    )
    files_parser.add_argument(
        "--width", "-w",
        type=int,
        default=0,
        help="统一缩放宽度，0 表示不缩放（默认：0）",
    )
    files_parser.add_argument(
        "--quality", "-q",
        type=int,
        default=95,
        help="JPEG 输出质量，仅对 .jpg 有效（默认：95）",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        global logger
        logger = setup_logging(verbose=True)

    merger = ImageMerger()

    if args.command == "dir":
        input_dir = args.input if args.input is not None else PROJECT_ROOT
        merger.merge_from_dir(
            input_dir=input_dir,
            output_path=args.output,
            pattern=args.pattern,
            sort=not args.no_sort,
            resize_width=args.width,
            quality=args.quality,
        )

    elif args.command == "files":
        # 解析空格分隔的文件列表，支持 glob 展开
        raw_tokens = args.input.split()
        image_paths: List[Path] = []
        for token in raw_tokens:
            expanded = glob.glob(token)
            if expanded:
                image_paths.extend(Path(p) for p in sorted(expanded))
            else:
                image_paths.append(Path(token))

        if not image_paths:
            logger.error("未找到任何图片文件，请检查 --input 参数")
            sys.exit(1)

        merger.merge_from_files(
            image_paths=image_paths,
            output_path=args.output,
            resize_width=args.width,
            quality=args.quality,
        )


if __name__ == "__main__":
    main()
