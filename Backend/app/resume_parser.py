from pypdf import PdfReader
import io


def extract_resume_text(pdf_bytes: bytes) -> str:
    """
    Extract text from an uploaded PDF resume.
    """

    pdf = PdfReader(io.BytesIO(pdf_bytes))

    resume_text = ""

    for page in pdf.pages:
        text = page.extract_text()

        if text:
            resume_text += text + "\n"

    return resume_text.strip()