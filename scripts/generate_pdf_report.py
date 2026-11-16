"""Build a polished PDF from the reproducible 2022 resume-dataset EDA outputs."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Flowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "reports" / "figures"
OUTPUT = ROOT / "output" / "pdf" / "2022-resume-dataset-report.pdf"


class ArchitectureDiagram(Flowable):
    """Simple vector architecture diagram so the PDF has no external renderer dependency."""

    def __init__(self, width: float = 16.5 * cm, height: float = 9.2 * cm):
        super().__init__()
        self.width, self.height = width, height

    def draw_box(self, canvas, x, y, width, height, text, fill):
        canvas.setFillColor(fill)
        canvas.setStrokeColor(colors.HexColor("#B7C3D0"))
        canvas.roundRect(x, y, width, height, 5, fill=1, stroke=1)
        canvas.setFillColor(colors.HexColor("#17324D"))
        canvas.setFont("Helvetica-Bold", 8)
        lines = text.split("\n")
        text_y = y + height / 2 + (len(lines) - 1) * 4
        for line in lines:
            canvas.drawCentredString(x + width / 2, text_y, line)
            text_y -= 9

    def arrow(self, canvas, x1, y1, x2, y2, label=None):
        canvas.setStrokeColor(colors.HexColor("#46637F"))
        canvas.setFillColor(colors.HexColor("#46637F"))
        canvas.setLineWidth(1.1)
        canvas.line(x1, y1, x2, y2)
        canvas.saveState()
        canvas.translate(x2, y2)
        angle = 0 if x2 >= x1 else 180
        canvas.rotate(angle)
        path = canvas.beginPath()
        path.moveTo(0, 0)
        path.lineTo(-5, 3)
        path.lineTo(-5, -3)
        path.close()
        canvas.drawPath(path, fill=1, stroke=0)
        canvas.restoreState()
        if label:
            canvas.setFont("Helvetica", 7)
            canvas.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 4, label)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        blue = colors.HexColor("#E8F1FA")
        teal = colors.HexColor("#E7F5F2")
        gold = colors.HexColor("#FFF4D6")
        red = colors.HexColor("#FBEAEC")
        box_w, box_h = 2.95 * cm, 1.15 * cm
        y = h - 2.3 * cm
        positions = [0, 3.35 * cm, 6.7 * cm, 10.05 * cm, 13.4 * cm]
        labels = ["Recruiter\nuploads PDF", "Flask\n/screen", "Text extraction\nand validation", "Rules scorer or\nstructured LLM", "Zapier Catch\nHook"]
        fills = [blue, blue, gold, teal, teal]
        for x, label, fill in zip(positions, labels, fills):
            self.draw_box(c, x, y, box_w, box_h, label, fill)
        for i in range(4):
            self.arrow(c, positions[i] + box_w, y + box_h / 2, positions[i + 1], y + box_h / 2)
        self.draw_box(c, 13.4 * cm, y - 2.2 * cm, box_w, box_h, "Sheets, ATS,\nor Slack", teal)
        self.arrow(c, 14.88 * cm, y, 14.88 * cm, y - 1.05 * cm)
        self.draw_box(c, 3.35 * cm, y - 2.2 * cm, box_w, box_h, "422: OCR or\ntext PDF needed", red)
        self.arrow(c, 4.83 * cm, y, 4.83 * cm, y - 1.05 * cm, "no text")
        self.draw_box(c, 7.15 * cm, 0.25 * cm, 3.8 * cm, 1.15 * cm, "2022 public dataset -> local aggregate EDA\n(informs criteria; not sent to Zapier)", gold)
        self.arrow(c, 9.05 * cm, 1.4 * cm, 9.05 * cm, y - 1.05 * cm, "EDA")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7E0EA"))
    canvas.line(doc.leftMargin, 1.25 * cm, A4[0] - doc.rightMargin, 1.25 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5D6D7E"))
    canvas.drawString(doc.leftMargin, 0.85 * cm, "AI Resume Screening Automation - 2022 Dataset EDA Report")
    canvas.drawRightString(A4[0] - doc.rightMargin, 0.85 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=colors.HexColor("#17324D"), alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle(name="Subtitle", parent=styles["BodyText"], alignment=TA_CENTER, textColor=colors.HexColor("#5D6D7E"), leading=16, spaceAfter=20))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#17324D"), spaceBefore=14, spaceAfter=7))
    styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11, textColor=colors.HexColor("#5D6D7E"), spaceAfter=6))
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=1.75 * cm, leftMargin=1.75 * cm, topMargin=1.65 * cm, bottomMargin=1.8 * cm)
    body = styles["BodyCustom"]
    story = [
        Spacer(1, 1.0 * cm),
        Paragraph("AI Resume Screening Automation", styles["TitleCustom"]),
        Paragraph("2022 Resume Dataset - Exploratory Data Analysis Report", styles["Subtitle"]),
        Table([[Paragraph("Purpose", styles["Small"]), Paragraph("Use a real public resume dataset to validate data handling, explore corpus structure, and document the limits of automated screening.", body)]], colWidths=[3.1 * cm, 13.0 * cm], style=TableStyle([("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#E8F1FA")), ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F7FAFC")), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D7E5")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)])),
        Paragraph("Data source and governance", styles["Section"]),
        Paragraph("The analysis uses the public Resume Dataset published by Snehaan Bhawal (2022), accessed through a Hugging Face CSV mirror for reproducible download. It contains resume examples originally scraped from LiveCareer, with text, HTML, an ID, and a job-category label. Raw resumes, IDs, HTML, PDFs, and contact data are deliberately excluded from this repository; only aggregate charts are retained.", body),
        Paragraph("Original source: https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset<br/>Download mirror: https://huggingface.co/datasets/Divyaamith/Kaggle-Resume", styles["Small"]),
        Paragraph("Dataset profile", styles["Section"]),
        Table([["Measure", "Result"], ["Records", "2,484"], ["Labeled job categories", "24"], ["Median resume length", "757 words"], ["95th percentile length", "1,398.7 words"], ["Exact duplicate texts", "2"]], colWidths=[8.0 * cm, 8.0 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DEE8")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]), ("PADDING", (0, 0), (-1, -1), 7)])),
        Spacer(1, 10),
        Image(str(FIGURES / "category-distribution.png"), width=16.2 * cm, height=13.5 * cm),
        Paragraph("Finding: the categories are imbalanced. Information Technology and Business Development have 120 records each, while BPO has 22 and Automobile has 36. Any category model should use stratified splits and per-category reporting.", body),
        PageBreak(),
        Paragraph("Resume text length", styles["Section"]),
        Image(str(FIGURES / "resume-length-distribution.png"), width=16.2 * cm, height=9.0 * cm),
        Paragraph("The broad length distribution means a fixed prompt or context limit can truncate longer resumes. The application uses explicit PDF text validation and the LLM path limits input to 18,000 characters to keep requests bounded.", body),
        Paragraph("Keyword-signal exploration", styles["Section"]),
        Image(str(FIGURES / "skill-signal-prevalence.png"), width=16.2 * cm, height=9.0 * cm),
        Paragraph("These are corpus-wide keyword frequencies, not measures of candidate quality. Excel appears in 38.65% of resumes, project management in 22.38%, Python in 1.61%, and AWS in 0.89%. The variation shows why scoring must be role-specific rather than based on one universal skills threshold.", body),
        PageBreak(),
        Paragraph("Data quality and extractable signals", styles["Section"]),
        Image(str(FIGURES / "data-quality-signals.png"), width=16.2 * cm, height=9.0 * cm),
        Paragraph("Only 0.04% of records have missing resume text and no category labels are missing. An email pattern is extractable from 0.76% of records and an explicit experience pattern from 37.72%, so the API treats email as an optional flag and never invents experience when it is not disclosed.", body),
        Paragraph("System architecture", styles["Section"]),
        ArchitectureDiagram(),
        Paragraph("The dataset is used only for local aggregate EDA. Candidate PDFs submitted to the API are validated, screened against explicit criteria, and then sent as structured event data to a Zapier Catch Hook. A human reviewer retains the final decision.", body),
        PageBreak(),
        Paragraph("Held-out role-category classification baseline", styles["Section"]),
        Paragraph("A concrete supervised benchmark was added using the dataset's 24 job-category labels. This is a role-category classification task, not a prediction of employment outcomes or candidate suitability. After removing one blank-text record, 2,483 resumes were split into 1,986 training and 497 held-out test records using an 80/20 stratified split with random seed 42.", body),
        Table([["Metric", "Held-out result"], ["Accuracy", "70.62%"], ["Macro precision", "69.91%"], ["Macro recall", "66.19%"], ["Macro F1", "65.55%"], ["Weighted F1", "69.12%"]], colWidths=[8.0 * cm, 8.0 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DEE8")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]), ("PADDING", (0, 0), (-1, -1), 7)])),
        Spacer(1, 10),
        Paragraph("Model: English-stopword-filtered TF-IDF unigrams and bigrams, capped at 15,000 features, followed by a LinearSVC classifier. The macro F1 score is reported alongside accuracy because it gives every category equal weight, including smaller categories.", body),
        Image(str(FIGURES / "category-f1-by-class.png"), width=16.2 * cm, height=13.1 * cm),
        PageBreak(),
        Paragraph("Classification error pattern", styles["Section"]),
        Image(str(FIGURES / "category-confusion-matrix.png"), width=15.5 * cm, height=13.1 * cm),
        Paragraph("Performance varies by category: Designer has held-out F1 of 0.86 and Information Technology 0.84, while BPO has F1 of 0.00 on only four held-out examples. This is why the project reports macro F1 and per-category performance rather than relying on accuracy alone.", body),
        PageBreak(),
        Paragraph("Findings, limitations, and responsible-use boundary", styles["Section"]),
        Paragraph("1. The data is appropriate for text-extraction checks, category exploration, and varied-format testing.<br/>2. The Category field is a job-domain label, not an employment outcome or ground-truth job-fit score.<br/>3. The dataset cannot support a credible claim about screening precision, recall, fairness, or employment-outcome accuracy.<br/>4. Production evaluation requires consented, role-specific resume-job pairs with independent human suitability labels, followed by held-out precision, recall, false-positive/negative, calibration, and disparate-impact analysis.", body),
        Paragraph("Reproducibility", styles["Section"]),
        Paragraph("Download the CSV locally, install the EDA dependencies, then run <font name=\"Courier\">python scripts/run_eda.py</font>. The script regenerates all figures from source data and writes only local aggregate metrics. See the repository README for the full commands.", body),
        Paragraph("Conclusion", styles["Section"]),
        Paragraph("This project demonstrates an auditable resume-screening workflow with a custom Flask API, explicit PDF validation, transparent rule-based scoring, an optional constrained LLM mode, Zapier delivery, automated tests, and real-dataset EDA. It is configured as decision support, not as an automated employment-decision system.", body),
    ]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
