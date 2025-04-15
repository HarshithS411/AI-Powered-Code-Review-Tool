from flask import Flask, request, jsonify, render_template
from converter import convert_code
import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route for the root URL to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Optional: Handle favicon.ico to suppress 404 error
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Get data from request
        source_lang = request.form.get('source_lang')
        target_lang = request.form.get('target_lang')
        code = request.form.get('code')

        # Handle file upload if present
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith(('.c', '.cpp', '.java', '.js', '.py', '.txt')):
                code = file.read().decode('utf-8')
            else:
                return jsonify({'error': 'Invalid file format. Use .c, .cpp, .java, .js, .py, or .txt'}), 400

        if not code or not source_lang or not target_lang:
            return jsonify({'error': 'Missing source language, target language, or code'}), 400

        # Validate code (basic check)
        from utils.validator import validate_code
        if not validate_code(code, source_lang):
            return jsonify({'error': 'Invalid syntax or unsupported code for the source language'}), 400

        # Convert code using AI
        converted_code = convert_code(code, source_lang, target_lang)

        if not converted_code:
            return jsonify({'error': 'Conversion failed. Unsupported conversion or error in AI processing'}), 500

        return jsonify({'converted_code': converted_code})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)