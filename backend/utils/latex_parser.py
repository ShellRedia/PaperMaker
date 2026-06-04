"""LaTeX 结构解析工具"""

import re
from typing import List
from dataclasses import dataclass, field


@dataclass
class Section:
    """论文章节节点"""
    title: str
    level: int  # 0=chapter, 1=section, 2=subsection, 3=subsubsection
    start_line: int
    end_line: int = 0
    children: List["Section"] = field(default_factory=list)


def parse_latex_sections(content: str) -> List[Section]:
    """
    解析 LaTeX 文档结构，提取章节层级。
    支持 \\section{}, \\subsection{}, \\subsubsection{}
    """
    pattern = re.compile(
        r'\\(section|subsection|subsubsection)\{([^}]*)\}',
        re.MULTILINE,
    )
    level_map = {"section": 1, "subsection": 2, "subsubsection": 3}

    sections: List[Section] = []
    stack: List[Section] = []

    for match in pattern.finditer(content):
        cmd = match.group(1)
        title = match.group(2)
        line = content[: match.start()].count("\n")
        level = level_map.get(cmd, 1)

        sec = Section(title=title, level=level, start_line=line)

        # 找到合适的父级
        while stack and stack[-1].level >= level:
            stack.pop()

        if stack:
            stack[-1].children.append(sec)
        else:
            sections.append(sec)

        stack.append(sec)

    return sections


def parse_markdown_sections(content: str) -> List[Section]:
    """
    解析 Markdown 文档结构，提取标题层级。
    """
    pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    sections: List[Section] = []
    stack: List[Section] = []

    for match in pattern.finditer(content):
        level = len(match.group(1))
        title = match.group(2).strip()
        line = content[: match.start()].count("\n")

        sec = Section(title=title, level=level, start_line=line)

        while stack and stack[-1].level >= level:
            stack.pop()

        if stack:
            stack[-1].children.append(sec)
        else:
            sections.append(sec)

        stack.append(sec)

    return sections
