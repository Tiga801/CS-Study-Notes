---
description: 翻译 CSAPP 章节文档。将英文原文翻译成中文，保持格式和术语一致性。
argument-hint: <文件路径>
---

# CSAPP 章节翻译命令

## 任务

将文件 `$ARGUMENTS` 的内容翻译成中文。

## 翻译规范

### 1. 术语表（必须严格遵守）

| 英文 | 中文 |
|------|------|
| byte | 字节 |
| bit | 位 |
| word | 字 |
| memory | 内存 |
| cache | 高速缓存 |
| register | 寄存器 |
| stack | 栈 |
| heap | 堆 |
| virtual memory | 虚拟内存 |
| physical memory | 物理内存 |
| address | 地址 |
| pointer | 指针 |
| CPU | CPU |
| processor | 处理器 |
| ALU | 算术逻辑单元 |
| PC | 程序计数器 |
| instruction | 指令 |
| process | 进程 |
| thread | 线程 |
| context switch | 上下文切换 |
| exception | 异常 |
| interrupt | 中断 |
| signal | 信号 |
| compiler | 编译器 |
| assembler | 汇编器 |
| linker | 链接器 |
| loader | 加载器 |
| object file | 目标文件 |
| executable | 可执行文件 |
| file | 文件 |
| descriptor | 描述符 |
| buffer | 缓冲区 |
| stream | 流 |
| socket | 套接字 |
| client | 客户端 |
| server | 服务器 |
| protocol | 协议 |
| concurrency | 并发 |
| parallelism | 并行 |
| mutex | 互斥锁 |
| semaphore | 信号量 |
| deadlock | 死锁 |
| race condition | 竞态条件 |

### 2. 格式保持

- 保留所有 Markdown 格式（标题、列表、代码块、引用等）
- 代码块内容不翻译，保持原样
- 保留图片引用和链接格式
- 保留数学公式

### 3. 文档分割策略

当文档较大时（超过 3000 字），按以下方式分割：

1. 首先识别文档中的一级标题（`#`）或二级标题（`##`）
2. 将文档按标题分割成多个部分
3. 逐部分翻译，每翻译完一部分后询问是否继续
4. 保持各部分之间的连贯性

### 4. 翻译风格

- 使用正式、学术的中文表达
- 保持原文的技术准确性
- 长句适当拆分，符合中文阅读习惯
- 专有名词首次出现时可保留英文原文（如：虚拟内存 (Virtual Memory)）

## 执行步骤

1. 读取指定文件内容
2. 评估文档大小，决定是否需要分割
3. 如需分割，按标题划分各部分
4. 逐部分翻译，应用术语表
5. 输出翻译结果
