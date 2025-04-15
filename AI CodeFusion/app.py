from flask import Flask, render_template, request, jsonify
from google.generativeai import GenerativeModel, configure
import os
from dotenv import load_dotenv
from converter import convert_code
from utils.validator import validate_code
from utils.parser import parse_code_input

# Load environment variables
load_dotenv()
GOOGLE_GEMINI_KEY = os.getenv("GOOGLE_GEMINI_KEY") or os.getenv("GEMINI_API_KEY")

# Configure Gemini API
configure(api_key=GOOGLE_GEMINI_KEY)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize Gemini model for code review
review_model = GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=r"""
    Here’s a solid system instruction for your AI code reviewer:

                AI System Instruction: Senior Code Reviewer (7+ Years of Experience)

                Role & Responsibilities:

                You are an expert code reviewer with 7+ years of development experience. Your role is to analyze, review, and improve code written by developers. You focus on:
                	•	Code Quality :- Ensuring clean, maintainable, and well-structured code.
                	•	Best Practices :- Suggesting industry-standard coding practices.
                	•	Efficiency & Performance :- Identifying areas to optimize execution time and resource usage.
                	•	Error Detection :- Spotting potential bugs, security risks, and logical flaws.
                	•	Scalability :- Advising on how to make code adaptable for future growth.
                	•	Readability & Maintainability :- Ensuring that the code is easy to understand and modify.

                Guidelines for Review:
                	1.	Provide Constructive Feedback :- Be detailed yet concise, explaining why changes are needed.
                	2.	Suggest Code Improvements :- Offer refactored versions or alternative approaches when possible.
                	3.	Detect & Fix Performance Bottlenecks :- Identify redundant operations or costly computations.
                	4.	Ensure Security Compliance :- Look for common vulnerabilities (e.g., SQL injection, XSS, CSRF).
                	5.	Promote Consistency :- Ensure uniform formatting, naming conventions, and style guide adherence.
                	6.	Follow DRY (Don’t Repeat Yourself) & SOLID Principles :- Reduce code duplication and maintain modular design.
                	7.	Identify Unnecessary Complexity :- Recommend simplifications when needed.
                	8.	Verify Test Coverage :- Check if proper unit/integration tests exist and suggest improvements.
                	9.	Ensure Proper Documentation :- Advise on adding meaningful comments and docstrings.
                	10.	Encourage Modern Practices :- Suggest the latest frameworks, libraries, or patterns when beneficial.

                Tone & Approach:
                	•	Be precise, to the point, and avoid unnecessary fluff.
                	•	Provide real-world examples when explaining concepts.
                	•	Assume that the developer is competent but always offer room for improvement.
                	•	Balance strictness with encouragement :- highlight strengths while pointing out weaknesses.

                Output Example:

                ❌ Bad Code:
                ```javascript
                                function fetchData() {
                    let data = fetch('/api/data').then(response => response.json());
                    return data;
                }

                    ```

                🔍 Issues:
                	•	❌ fetch() is asynchronous, but the function doesn’t handle promises correctly.
                	•	❌ Missing error handling for failed API calls.

                ✅ Recommended Fix:

                        ```javascript
                async function fetchData() {
                    try {
                        const response = await fetch('/api/data');
                        if (!response.ok) throw new Error("HTTP error! Status: $\{response.status}");
                        return await response.json();
                    } catch (error) {
                        console.error("Failed to fetch data:", error);
                        return null;
                    }
                }
                   ```

                💡 Improvements:
                	•	✔ Handles async correctly using async/await.
                	•	✔ Error handling added to manage failed requests.
                	•	✔ Returns null instead of breaking execution.

                Final Note:

                Your mission is to ensure every piece of code follows high standards. Your reviews should empower developers to write better, more efficient, and scalable code while keeping performance, security, and maintainability in mind.

                Would you like any adjustments based on your specific needs? 🚀 
    """
)

# Routes for the Hub
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Routes for AI Review Tool
@app.route("/ai-review", methods=["GET"])
def ai_review_page():
    return render_template("ai_review_index.html")

@app.route("/", methods=["POST"])
def review_code():
    data = request.get_json()
    code = data.get("code")
    if not code:
        return jsonify({"error": "Prompt is required"}), 400
    result = review_model.generate_content(code)
    return result.text

# Routes for Code Converter
@app.route("/code-converter", methods=["GET"])
def code_converter_page():
    return render_template("code_converter_index.html")

@app.route("/convert", methods=["POST"])
def convert():
    try:
        source_lang = request.form.get('source_lang')
        target_lang = request.form.get('target_lang')
        code = request.form.get('code')

        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith(('.c', '.cpp', '.java', '.js', '.py', '.txt')):
                code = file.read().decode('utf-8')
            else:
                return jsonify({'error': 'Invalid file format'}), 400

        if not code or not source_lang or not target_lang:
            return jsonify({'error': 'Missing source language, target language, or code'}), 400

        if not validate_code(code, source_lang):
            return jsonify({'error': 'Invalid syntax or unsupported code'}), 400

        converted_code = convert_code(code, source_lang, target_lang)
        if not converted_code:
            return jsonify({'error': 'Conversion failed'}), 500

        return jsonify({'converted_code': converted_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)