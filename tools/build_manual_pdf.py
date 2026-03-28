#!/usr/bin/env python3
"""
Build a readable PDF manual from docs/CampusNexus-360_Manual.md.

We intentionally use a small markdown subset so the PDF is deterministic:
- Headings (#, ##, ###)
- Bullets (- ...)
- Code fences (``` ... ```)
- Normal paragraphs

Output:
  docs/CampusNexus-360_Manual.pdf
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted,
    PageBreak,
)


@dataclass
class Block:
    kind: str  # heading|para|bullet|code|hr|pagebreak
    text: str
    level: int = 0


def parse_md(md_text: str) -> List[Block]:
    blocks: List[Block] = []
    in_code = False
    code_lines: List[str] = []

    def flush_code():
        nonlocal code_lines
        if code_lines:
            blocks.append(Block(kind="code", text="\n".join(code_lines)))
            code_lines = []

    lines = md_text.splitlines()
    for raw in lines:
        line = raw.rstrip("\n")

        if line.strip().startswith("```"):
            if in_code:
                in_code = False
                flush_code()
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if line.strip() == "---":
            blocks.append(Block(kind="hr", text=""))
            continue

        if line.strip() == "":
            blocks.append(Block(kind="para", text=""))  # spacer
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            blocks.append(Block(kind="heading", text=text, level=level))
            continue

        if line.lstrip().startswith("- "):
            blocks.append(Block(kind="bullet", text=line.lstrip()[2:].strip()))
            continue

        # Paragraph line (we will merge consecutive paragraph lines later)
        blocks.append(Block(kind="para", text=line.strip()))

    if in_code:
        flush_code()

    # Merge consecutive paragraphs into one block, keep blank para blocks as spacers.
    merged: List[Block] = []
    buf: List[str] = []

    def flush_para_buf():
        nonlocal buf
        if buf:
            merged.append(Block(kind="para", text=" ".join(buf)))
            buf = []

    for b in blocks:
        if b.kind == "para" and b.text != "":
            buf.append(b.text)
            continue
        flush_para_buf()
        merged.append(b)
    flush_para_buf()

    return merged


def build_pdf(md_path: str, pdf_path: str) -> None:
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    blocks = parse_md(md_text)

    styles = getSampleStyleSheet()
    base = styles["BodyText"]
    base.fontName = "Helvetica"
    base.fontSize = 10.5
    base.leading = 14

    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=24, spaceAfter=10)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=15, leading=18, spaceBefore=10, spaceAfter=8)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=12.5, leading=16, spaceBefore=8, spaceAfter=6)
    bullet = ParagraphStyle("Bullet", parent=base, leftIndent=14, bulletIndent=6, spaceBefore=0, spaceAfter=2)
    code = ParagraphStyle("Code", parent=base, fontName="Courier", fontSize=9.2, leading=12, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=10)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="CampusNexus-360 Manual",
        author="CampusNexus-360",
    )

    story = []

    for b in blocks:
        if b.kind == "heading":
            if b.level <= 1:
                story.append(Paragraph(b.text, h1))
            elif b.level == 2:
                story.append(Paragraph(b.text, h2))
            else:
                story.append(Paragraph(b.text, h3))
            continue

        if b.kind == "hr":
            story.append(Spacer(1, 10))
            continue

        if b.kind == "bullet":
            story.append(Paragraph(f"&bull; {b.text}", bullet))
            continue

        if b.kind == "code":
            story.append(Preformatted(b.text, code))
            continue

        if b.kind == "para":
            if b.text == "":
                story.append(Spacer(1, 8))
            else:
                # Minimal escaping for reportlab Paragraph
                safe = (
                    b.text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                story.append(Paragraph(safe, base))
                story.append(Spacer(1, 4))
            continue

        if b.kind == "pagebreak":
            story.append(PageBreak())
            continue

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    doc.build(story)


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path = os.path.join(repo_root, "docs", "CampusNexus-360_Manual.md")
    pdf_path = os.path.join(repo_root, "docs", "CampusNexus-360_Manual.pdf")

    if not os.path.exists(md_path):
        raise SystemExit(f"Missing markdown file: {md_path}")

    build_pdf(md_path, pdf_path)
    print(f"Wrote: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

