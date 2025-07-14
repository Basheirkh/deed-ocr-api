import flask
from flask import request, jsonify
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import os
import tempfile

app = flask.Flask(__name__)

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    if ext in ['.jpg', '.jpeg', '.png']:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang="ara")
    elif ext == '.pdf':
        images = convert_from_path(file_path)
        for img in images:
            text += pytesseract.image_to_string(img, lang="ara")
    return text

def extract_deed_data(text):
    data = {}
    data['document_number'] = re.search(r'رقم الوثيقة[:\s]*([0-9]+)', text)
    data['document_date'] = re.search(r'تاريخ الوثيقة[:\s]*([0-9/\-]+)', text)
    data['owner_name'] = re.search(r'الاسم[:\s]*([^\n]+)', text)
    data['owner_id'] = re.search(r'رقم الهوية[:\s]*([0-9]+)', text)
    data['area'] = re.search(r'المساحة[:\s]*([0-9]+)', text)
    # ... يمكنك إضافة المزيد من الحقول حسب رغبتك
    result = {}
    for k, v in data.items():
        result[k] = v.group(1) if v else ""
    return result

@app.route('/extract_deed', methods=['POST'])
def extract_deed():
    file = request.files['file']
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        file.save(tmp.name)
        text = extract_text_from_file(tmp.name)
        os.unlink(tmp.name)
    data = extract_deed_data(text)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)