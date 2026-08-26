import os
import io
import tempfile
import markdown
from flask import Flask, request, render_template, send_file, jsonify
from weasyprint import HTML
import pdfplumber
import pypdf
from PIL import Image
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {'md', 'pdf'}

def allowed_file(filename, ext_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ext_set

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files.get('file')
    direction = request.form.get('direction')

    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if direction == 'md2pdf':
        if not allowed_file(file.filename, {'md'}):
            return jsonify({'error': 'Please upload a .md file'}), 400
        return md_to_pdf(file)

    elif direction == 'pdf2md':
        if not allowed_file(file.filename, {'pdf'}):
            return jsonify({'error': 'Please upload a .pdf file'}), 400
        return pdf_to_md(file)

    else:
        return jsonify({'error': 'Invalid conversion direction'}), 400

def md_to_pdf(file):
    md_content = file.read().decode('utf-8')
    html_content = markdown.markdown(md_content, extensions=['extra', 'toc'])
    styled_html = f"""
    <html>
        <head><meta charset="utf-8"><style>body {{ font-family: Arial, sans-serif; margin: 40px; }}</style></head>
        <body>{html_content}</body>
    </html>
    """
    pdf_bytes = HTML(string=styled_html).write_pdf()
    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name='output.pdf',
        mimetype='application/pdf'
    )

def pdf_to_md(file):
    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    md_parts = []

    # --- 1. Extract text using pdfplumber ---
    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    md_parts.append(text)
    except Exception as e:
        md_parts.append(f"*Text extraction error: {str(e)}*")

    # --- 2. Extract images using pypdf ---
    image_placeholders = []
    try:
        reader = pypdf.PdfReader(tmp_path)
        for page_num, page in enumerate(reader.pages):
            for img_obj in page.images:
                # img_obj is a pypdf.generic.IndirectObject with data
                # We can get image bytes
                img_bytes = img_obj.data
                # Determine image format (usually /DCTDecode for JPEG, /FlateDecode for PNG)
                # We'll just treat it as image
                try:
                    # Use PIL to get format
                    pil_img = Image.open(io.BytesIO(img_bytes))
                    format = pil_img.format.lower() if pil_img.format else 'png'
                    # Save to base64
                    buffered = io.BytesIO()
                    pil_img.save(buffered, format=format.upper())
                    b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    mime = f"image/{format}"
                    data_uri = f"data:{mime};base64,{b64}"
                    alt = f"image_page{page_num+1}_{img_obj.name or 'img'}"
                    image_placeholders.append(f"![{alt}]({data_uri})")
                except Exception as inner_e:
                    # If PIL fails, fallback to raw base64
                    b64 = base64.b64encode(img_bytes).decode('utf-8')
                    data_uri = f"data:image/png;base64,{b64}"  # assume PNG
                    alt = f"image_page{page_num+1}_{img_obj.name or 'img'}"
                    image_placeholders.append(f"![{alt}]({data_uri})")
    except Exception as e:
        image_placeholders.append(f"*Image extraction error: {str(e)}*")

    if image_placeholders:
        md_parts.append("\n\n## Extracted Images\n\n")
        md_parts.extend(image_placeholders)

    md_output = "\n\n".join(md_parts)

    os.unlink(tmp_path)

    return send_file(
        io.BytesIO(md_output.encode('utf-8')),
        as_attachment=True,
        download_name='output.md',
        mimetype='text/markdown'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
