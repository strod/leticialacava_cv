"""Rebuild CVs: python3 -m pip install reportlab; python3 scripts/generate_cv.py.

Pass language codes (en pt es) to regenerate only selected versions.
Localized content lives in cv_content.json, curated from index.html,
the original CV, and docs/context.md. Keep dates and skills aligned.
Bundled OFL fonts match the website; generation requires no network access.
"""

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
CONTENT = json.loads((Path(__file__).with_name("cv_content.json")).read_text(encoding="utf-8"))
GREEN = colors.HexColor("#2D4A3E")
TERRACOTTA = colors.HexColor("#A85C3C")
MUTED = colors.HexColor("#4A6B5D")
WARM = colors.HexColor("#FAF7F2")
SAGE = colors.HexColor("#B8CCAF")


def generate(language):
    content = CONTENT[language]
    suffix = "" if language == "en" else f"-{language}"
    output = ROOT / "assets" / f"leticia-la-cava-cv{suffix}.pdf"
    for name, filename in (
        ("Space", "SpaceGrotesk-Regular.ttf"),
        ("SpaceBold", "SpaceGrotesk-SemiBold.ttf"),
        ("Baskerville", "LibreBaskerville-Regular.ttf"),
    ):
        pdfmetrics.registerFont(TTFont(name, str(ROOT / "assets/fonts" / filename)))
    pdfmetrics.registerFontFamily("Space", normal="Space", bold="SpaceBold")

    styles = {
        "name": ParagraphStyle("name", fontName="Baskerville", fontSize=29,
                               leading=38, textColor=GREEN, spaceAfter=6),
        "headline": ParagraphStyle("headline", fontName="SpaceBold", fontSize=11,
                                   leading=16, textColor=TERRACOTTA, spaceAfter=10),
        "contact": ParagraphStyle("contact", fontName="Space", fontSize=9,
                                  leading=14, textColor=GREEN, spaceAfter=3),
        "section": ParagraphStyle("section", fontName="Baskerville", fontSize=13,
                                  leading=19, textColor=GREEN, spaceBefore=15,
                                  spaceAfter=8, keepWithNext=True),
        "body": ParagraphStyle("body", fontName="Space", fontSize=9.7,
                               leading=13.6, textColor=GREEN, spaceAfter=5,
                               alignment=TA_LEFT),
        "role": ParagraphStyle("role", fontName="SpaceBold", fontSize=10.7,
                               leading=15, textColor=GREEN, spaceAfter=2,
                               keepWithNext=True),
        "date": ParagraphStyle("date", fontName="Space", fontSize=9,
                               leading=13, textColor=MUTED, spaceAfter=5,
                               keepWithNext=True),
        "bullet": ParagraphStyle("bullet", fontName="Space", fontSize=9.7,
                                 leading=13.6, textColor=GREEN, leftIndent=10,
                                 firstLineIndent=-10, spaceAfter=4),
    }
    story = []

    def p(text, style="body", markup=False):
        return Paragraph(text if markup else escape(text), styles[style])

    def section(title):
        story.append(p(title, "section"))

    def job(title, company, dates, bullets):
        # Keep the title, employer, dates and first bullet together at page breaks.
        story.append(KeepTogether([
            p(f"{title} | {company}", "role"),
            p(dates, "date"),
            p("- " + bullets[0], "bullet"),
        ]))
        story.extend(p("- " + item, "bullet") for item in bullets[1:])
        story.append(Spacer(1, 6))

    story.extend([
        p("Leticia La Cava", "name"),
        p(content["headline"], "headline"),
        p(escape(content["location"]) + ' | <link href="mailto:leticiamlacava@gmail.com">'
          'leticiamlacava@gmail.com</link> | +55 21 98645-2911', "contact", True),
        p('<link href="https://leticialacava.me">leticialacava.me</link> | '
          '<link href="https://www.linkedin.com/in/leticia-la-cava/">'
          'linkedin.com/in/leticia-la-cava</link>', "contact", True),
    ])
    section(content["summary_heading"])
    story.append(p(content["summary"]))
    section(content["skills_heading"])
    for label, skills in content["skills"]:
        story.append(p(f"<b>{escape(label)}:</b> {escape(skills)}", markup=True))

    section(content["experience_heading"])
    for index, entry in enumerate(content["jobs"]):
        if index == 2:
            story.append(PageBreak())
            section(content["experience_continued"])
        job(entry["title"], entry["company"], entry["dates"], entry["bullets"])

    section(content["education_heading"])
    for title, institution in content["education"]:
        story.extend([p(title, "role"), p(institution), Spacer(1, 5)])
    section(content["languages_heading"])
    story.append(p(content["languages"]))

    def decorate(canvas, doc):
        width, height = A4
        canvas.saveState()
        canvas.setFillColor(WARM)
        if doc.page == 1:
            canvas.rect(0, height - 153, width, 153, fill=1, stroke=0)
        canvas.setFillColor(GREEN)
        canvas.rect(0, height - 5, width, 5, fill=1, stroke=0)
        canvas.setStrokeColor(SAGE)
        canvas.setLineWidth(0.5)
        canvas.line(46, 36, width - 46, 36)
        canvas.setFillColor(MUTED)
        canvas.setFont("Space", 8)
        canvas.drawString(46, 23, f"Leticia La Cava | {content['footer']}")
        canvas.drawRightString(width - 46, 23, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=46, leftMargin=46,
        topMargin=36, bottomMargin=48,
        title=f"Leticia La Cava - {content['headline']}",
        author="Leticia La Cava",
        subject=content["subject"],
        lang=language, pageCompression=1,
    )
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    print(f"Generated {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("languages", nargs="*", help="Languages to regenerate: en pt es (default: all)")
    args = parser.parse_args()
    if any(language not in CONTENT for language in args.languages):
        parser.error("Supported languages: en pt es")
    for language in args.languages or CONTENT:
        generate(language)
