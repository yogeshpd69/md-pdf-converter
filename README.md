# 📄 MD ↔ PDF Converter

A simple web tool to convert Markdown (`.md`) files to PDF and PDF files to Markdown, preserving embedded images as base64 placeholders.

🔗 **Live Demo:** [https://md-pdf-converter.onrender.com/](https://md-pdf-converter.onrender.com/)

## ✨ Features

- **Markdown → PDF** – Converts `.md` files with proper formatting, tables, and embedded images.
- **PDF → Markdown** – Extracts text and embedded images (as base64 data URIs) from PDFs.
- Clean, simple UI – upload and download in one click.
- Handles charts, diagrams, and images (extracted as placeholders).

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **PDF Generation:** weasyprint
- **PDF Parsing:** pdfplumber + pypdf
- **Image Processing:** Pillow
- **Deployment:** Render.com

## 🚀 Local Development

```bash
# Clone the repository
git clone https://github.com/yogeshpd69/md-pdf-converter.git
cd md-pdf-converter

# Create and activate a virtual environment (Python 3.10+)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
