"""Rebuild the downloadable CV: python3 -m pip install reportlab; python3 scripts/generate_cv.py.

Content is curated from index.html, the original CV, and docs/context.md.
Keep employment dates, education status, and skills aligned with those sources.
Bundled OFL fonts match the website; generation requires no network access.
"""

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
OUTPUT = ROOT / "assets" / "leticia-la-cava-cv.pdf"
GREEN = colors.HexColor("#2D4A3E")
TERRACOTTA = colors.HexColor("#A85C3C")
MUTED = colors.HexColor("#4A6B5D")
WARM = colors.HexColor("#FAF7F2")
SAGE = colors.HexColor("#B8CCAF")


def generate():
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
        p("Data Analytics & Data Visualization Consultant", "headline"),
        p('São Paulo, Brazil | <link href="mailto:leticiamlacava@gmail.com">'
          'leticiamlacava@gmail.com</link> | +55 21 98645-2911', "contact", True),
        p('<link href="https://leticialacava.me">leticialacava.me</link> | '
          '<link href="https://www.linkedin.com/in/leticia-la-cava/">'
          'linkedin.com/in/leticia-la-cava</link>', "contact", True),
    ])
    section("Professional Summary")
    story.append(p(
        "Industrial engineer and data analytics consultant with 7+ years of experience "
        "turning business data into dashboards, automated processes, and actionable insights. "
        "Experience across chemicals distribution, consumer goods, sales, digital marketing, "
        "and supply chain at Levaco Brasil, Reckitt Benckiser, and L'Oreal. "
        "Delivered 20+ freelance projects; rated 4.95/5 on Workana and 5.0/5 on Upwork."
    ))
    section("Technical Skills")
    for label, skills in [
        ("Business intelligence", "Power BI, DAX, Power Query (M), Looker Studio (Google Data Studio), Excel, Google Sheets"),
        ("Data and analytics", "SQL, Google BigQuery, Python (Pandas, NumPy, Matplotlib), data modeling, ETL, Supermetrics"),
        ("Automation and integration", "VBA, Google Apps Script, APIs, web scraping, JavaScript, Outlook, SharePoint"),
        ("Business domains", "Sales and marketing analytics, financial analysis, S&OP, demand planning, forecasting, inventory optimization"),
    ]:
        story.append(p(f"<b>{escape(label)}:</b> {escape(skills)}", markup=True))

    section("Professional Experience")
    job("Supply and Financial Analytics", "Levaco Brasil Ltda.", "2026 - Present", [
        "Built the analytics function from scratch for the Brazilian subsidiary of Levaco Chemicals GmbH, Germany.",
        "Designed purchase planning connecting sales forecasts, third-party warehouse inventory, import lead times, and landed costs.",
        "Rebuilt shipment-level and SKU-level costing, allocating logistics and clearing expenses by weight, tax gross-up, and net cost per kilo.",
        "Developed monthly BRL/EUR performance reporting with FX decomposition. Presented demand, cost, FX, and accounting variance analysis to Brazilian and German leadership.",
    ])
    job("Data Analytics & Visualization Consultant", "Freelance", "Jun 2021 - Present", [
        "Delivered 20+ projects across sales, digital marketing, and supply chain, building dashboards with Power BI, Looker Studio, BigQuery, SQL, Supermetrics, and Excel.",
        "Automated business processes using Python, Excel, and Google Apps Script; built data pipelines integrating Outlook, SharePoint, and Power BI.",
        "Implemented BigQuery, developed web scrapers and API integrations, and built marketing dashboards using YouTube, Facebook, Google, and Active Campaign data.",
    ])

    story.append(PageBreak())
    section("Professional Experience (continued)")
    job("Demand Planning Coordinator", "Reckitt Benckiser", "Sep 2019 - Jun 2021", [
        "Led regional Sales and Operations Planning (S&OP) cycle optimization, time series analysis, and inventory optimization.",
        "Built the BI area from scratch and automated supply chain dashboards and processes using Power BI and Python.",
        "Analyzed sell-in, sell-out, stock, market share, price elasticity, and promotion calendars. Participated in an AI forecasting project that improved service level and forecast accuracy.",
        'Received the "Struggling for Excellence" award.',
    ])
    job("Supply Chain Analyst", "L'Oreal", "Oct 2018 - Sep 2019", [
        "Implemented the division's retail S&OP cycle and managed forecasting and inventory processes.",
        "Led the Demand Planning BI cell, standardized reporting and analytics, and developed a forecasting tool that improved forecast accuracy.",
    ])
    job("Supply Chain Analyst", "Technos Group", "Sep 2017 - Oct 2018", [
        "Managed international suppliers and procurement; developed a Balanced Scorecard (BSC) to evaluate supplier performance.",
        "Led supply chain PDCA initiatives, designed finance strategies to reduce the cash conversion cycle, and performed financial forecasting.",
    ])
    job("Media Finance Intern", "L'Oreal", "Jun 2016 - Oct 2018", [
        "Managed media investment and budget tracking for multiple brands; implemented a media investment management tool and analyzed media contracts and KPIs.",
        "Automated repetitive processes using VBA and SQL, reducing processing time by 70%.",
    ])

    section("Education")
    story.extend([
        p("MicroMasters Program in Supply Chain Management", "role"),
        p("MIT via edX | Jun 2021 - Present (in progress)", "body"),
        Spacer(1, 5),
        p("Bachelor's Degree in Industrial Engineering", "role"),
        p("CEFET | 2012 - 2017", "body"),
    ])
    section("Languages")
    story.append(p("Portuguese: Native | English: Advanced / Professional"))

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
        canvas.drawString(46, 23, "Leticia La Cava | Curriculum Vitae")
        canvas.drawRightString(width - 46, 23, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=46, leftMargin=46,
        topMargin=36, bottomMargin=48,
        title="Leticia La Cava - Data Analytics & Visualization CV",
        author="Leticia La Cava",
        subject="Professional experience, technical skills, education, and languages",
        lang="en", pageCompression=1,
    )
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    generate()
