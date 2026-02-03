# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CS-Study-Notes is a repository for translating and organizing computer science learning resources. The primary focus is translating CSAPP (Computer Systems: A Programmer's Perspective, 3rd Edition) from English to Chinese.

## Common Commands

```bash
# Activate Python environment
conda activate book

# List all CSAPP chapters with page ranges
python Books/CSAPP/convert_csapp.py --list

# Extract and convert a specific chapter
python Books/CSAPP/convert_csapp.py -c 01

# Extract multiple chapters
python Books/CSAPP/convert_csapp.py -c 01 02 03

# Generate chapter templates only (no content)
python Books/CSAPP/convert_csapp.py -c 01 --template

# Preview extracted raw text
python Books/CSAPP/extract_chapters.py 01
```

## CSAPP Translation Workflow

1. **Extract** chapter from PDF → generates `raw_text/XX-章节名_raw.txt`
2. **Translate** using `/translate-csapp <file>` command with terminology glossary
3. **Update** corresponding `chapters/XX-章节名.md` file
4. **Commit** with format: `feat: CSAPP 第XX章中文翻译`

## Key Files

| File | Purpose |
|------|---------|
| `Books/CSAPP/chapter_mapping.py` | Chapter metadata, page ranges, and 60+ term glossary |
| `Books/CSAPP/convert_csapp.py` | Main conversion orchestrator |
| `Books/CSAPP/extract_chapters.py` | PDF text extraction (PyMuPDF) |
| `Books/CSAPP/.claude/commands/translate-csapp.md` | Translation command with glossary |

## Translation Glossary (Mandatory Terms)

These terms from `chapter_mapping.GLOSSARY` must be used consistently:

- **Memory**: cache=高速缓存, register=寄存器, stack=栈, heap=堆, virtual memory=虚拟内存
- **Processor**: instruction=指令, PC=程序计数器, ALU=算术逻辑单元
- **Programs**: process=进程, thread=线程, context switch=上下文切换, exception=异常
- **Compilation**: compiler=编译器, linker=链接器, object file=目标文件
- **Concurrency**: mutex=互斥锁, semaphore=信号量, deadlock=死锁, race condition=竞态条件

## Translation Rules

- Preserve all Markdown formatting, code blocks, and links
- Do NOT translate content inside code blocks
- For documents >3000 chars, split by `##` headers and translate in parts
- Use formal, academic Chinese style

## Environment

Python 3.10 with `conda activate book`. Required packages: pymupdf (fitz), pdfplumber.
