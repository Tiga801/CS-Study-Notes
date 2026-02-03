"""
CSAPP (Computer Systems: A Programmer's Perspective) 章节映射配置

包含每个章节的页码范围、中英文标题等信息。
页码基于 CSAPP 第3版 (2016) PDF 文件。
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class ChapterInfo:
    """章节信息数据类"""
    chapter_num: str        # 章节编号 (如 "01", "02")
    chinese_title: str      # 中文标题
    english_title: str      # 英文标题
    page_range: Tuple[int, int]  # 页码范围 (起始页, 结束页)


# CSAPP 章节映射
CHAPTERS = {
    "00": ChapterInfo(
        chapter_num="00",
        chinese_title="前言",
        english_title="Preface",
        page_range=(15, 30)
    ),
    "01": ChapterInfo(
        chapter_num="01",
        chinese_title="计算机系统漫游",
        english_title="A Tour of Computer Systems",
        page_range=(31, 58)
    ),
    "02": ChapterInfo(
        chapter_num="02",
        chinese_title="信息的表示和处理",
        english_title="Representing and Manipulating Information",
        page_range=(60, 190)
    ),
    "03": ChapterInfo(
        chapter_num="03",
        chinese_title="程序的机器级表示",
        english_title="Machine-Level Representation of Programs",
        page_range=(191, 378)
    ),
    "04": ChapterInfo(
        chapter_num="04",
        chinese_title="处理器体系结构",
        english_title="Processor Architecture",
        page_range=(379, 522)
    ),
    "05": ChapterInfo(
        chapter_num="05",
        chinese_title="优化程序性能",
        english_title="Optimizing Program Performance",
        page_range=(523, 606)
    ),
    "06": ChapterInfo(
        chapter_num="06",
        chinese_title="存储器层次结构",
        english_title="The Memory Hierarchy",
        page_range=(607, 694)
    ),
    "07": ChapterInfo(
        chapter_num="07",
        chinese_title="链接",
        english_title="Linking",
        page_range=(696, 746)
    ),
    "08": ChapterInfo(
        chapter_num="08",
        chinese_title="异常控制流",
        english_title="Exceptional Control Flow",
        page_range=(747, 825)
    ),
    "09": ChapterInfo(
        chapter_num="09",
        chinese_title="虚拟内存",
        english_title="Virtual Memory",
        page_range=(826, 910)
    ),
    "10": ChapterInfo(
        chapter_num="10",
        chinese_title="系统级I/O",
        english_title="System-Level I/O",
        page_range=(912, 939)
    ),
    "11": ChapterInfo(
        chapter_num="11",
        chinese_title="网络编程",
        english_title="Network Programming",
        page_range=(940, 992)
    ),
    "12": ChapterInfo(
        chapter_num="12",
        chinese_title="并发编程",
        english_title="Concurrent Programming",
        page_range=(993, 1062)
    ),
    "appendix": ChapterInfo(
        chapter_num="appendix",
        chinese_title="错误处理",
        english_title="Error Handling",
        page_range=(1063, 1067)
    ),
}


# 术语表 - 保持翻译一致性
GLOSSARY = {
    # 基础概念
    "byte": "字节",
    "bit": "位",
    "word": "字",

    # 内存相关
    "memory": "内存",
    "cache": "高速缓存",
    "register": "寄存器",
    "stack": "栈",
    "heap": "堆",
    "virtual memory": "虚拟内存",
    "physical memory": "物理内存",
    "address": "地址",
    "pointer": "指针",

    # 处理器相关
    "CPU": "CPU",
    "processor": "处理器",
    "ALU": "算术逻辑单元",
    "PC": "程序计数器",
    "instruction": "指令",

    # 程序相关
    "process": "进程",
    "thread": "线程",
    "context switch": "上下文切换",
    "exception": "异常",
    "interrupt": "中断",
    "signal": "信号",

    # 编译相关
    "compiler": "编译器",
    "assembler": "汇编器",
    "linker": "链接器",
    "loader": "加载器",
    "object file": "目标文件",
    "executable": "可执行文件",

    # I/O 相关
    "file": "文件",
    "descriptor": "描述符",
    "buffer": "缓冲区",
    "stream": "流",

    # 网络相关
    "socket": "套接字",
    "client": "客户端",
    "server": "服务器",
    "protocol": "协议",

    # 并发相关
    "concurrency": "并发",
    "parallelism": "并行",
    "mutex": "互斥锁",
    "semaphore": "信号量",
    "deadlock": "死锁",
    "race condition": "竞态条件",
}


def get_chapter_info(chapter_num: str) -> ChapterInfo:
    """获取指定章节的信息"""
    return CHAPTERS.get(chapter_num)


def get_all_chapters() -> dict:
    """获取所有章节信息"""
    return CHAPTERS


def get_chapter_filename(chapter_num: str) -> str:
    """生成章节文件名"""
    info = CHAPTERS.get(chapter_num)
    if info:
        return f"{info.chapter_num}-{info.chinese_title}.md"
    return None


if __name__ == "__main__":
    # 打印所有章节信息
    print("CSAPP 章节列表：")
    print("-" * 60)
    for num, info in CHAPTERS.items():
        start, end = info.page_range
        print(f"第{info.chapter_num}章: {info.chinese_title}")
        print(f"       ({info.english_title})")
        print(f"       页码: {start}-{end} (共{end-start+1}页)")
        print()
