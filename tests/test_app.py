import io

from app import app
from pypdf import PdfWriter


def test_rejects_missing_resume():
    response = app.test_client().post("/screen", data={"requirements": "{}"})
    assert response.status_code == 400
    assert response.json["error"] == "missing_resume"


def test_rejects_image_only_pdf():
    blank_pdf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(blank_pdf)
    response = app.test_client().post("/screen", data={"requirements": "{}", "resume": (io.BytesIO(blank_pdf.getvalue()), "resume.pdf")})
    assert response.status_code == 422
    assert response.json["error"] == "image_only_or_empty_pdf"
