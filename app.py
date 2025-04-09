import os
import json # Import the json library
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
from openai import OpenAI

app = Flask(__name__)

# Configure CORS - Allow specific origins for the /analyze route
CORS(app, resources={r"/analyze": {"origins": ["https://twitter.com", "https://x.com"]}})

# Configure OpenAI client
# Ensure the OPENAI_API_KEY environment variable is set
client = OpenAI()

MAX_INPUT_LENGTH = 300 # To avoid sending large payloads to openai

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/analyze', methods=['POST'])
def analyze_text():
    if not request.is_json:
        return jsonify({"success": False, "data": None, "error": "Request must be JSON"}), 400

    data = request.get_json()
    input_text = data.get('text')

    if not input_text:
        return jsonify({"success": False, "data": None, "error": "Missing 'text' field in request body"}), 400

    # Check input length
    if len(input_text) > MAX_INPUT_LENGTH:
        input_text = input_text[:MAX_INPUT_LENGTH] # Truncate the input text

    # Updated prompt for JSON output
    prompt = f'''Analyze the following text. First, determine if the text is primarily political in nature.
If it is political, classify its leaning as "left", "centre", or "right" based on its perspective (economics, social issues, government role, etc.).
Respond ONLY with a JSON object adhering strictly to this format:
{{
  "is_political": <true_or_false>,
  "political_leaning": <"left" | "centre" | "right" | null>
}}
- "political_leaning" MUST be null if "is_political" is false.
- "political_leaning" MUST be one of "left", "centre", or "right" if "is_political" is true.
Do not include any other text, explanation, or reasoning outside the JSON object.

Text to analyze:
{input_text}'''

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}, # Enable JSON mode
            max_tokens=50, # Increased max_tokens for JSON structure
            temperature=0 # For deterministic output
        )
        
        response_content = response.choices[0].message.content

        # Parse the JSON response from OpenAI
        try:
            analysis_data = json.loads(response_content)
        except json.JSONDecodeError:
            app.logger.error(f"Failed to decode JSON response from OpenAI: {response_content}")
            return jsonify({"success": False, "data": None, "error": "Invalid JSON response from analysis model"}), 500

        # Validate the structure and content of the parsed JSON
        if not isinstance(analysis_data, dict) or 'is_political' not in analysis_data or not isinstance(analysis_data['is_political'], bool):
            app.logger.error(f"Invalid structure or type in OpenAI response: {analysis_data}")
            return jsonify({"success": False, "data": None, "error": "Invalid data structure received from analysis model"}), 500

        is_political = analysis_data['is_political']
        political_leaning = analysis_data.get('political_leaning') # Use .get() for safety

        if is_political:
            # If political, leaning must be one of the specific strings
            valid_leanings = ["left", "centre", "right"]
            if 'political_leaning' not in analysis_data or political_leaning not in valid_leanings:
                 app.logger.error(f"Invalid political_leaning value when is_political is true: {analysis_data}")
                 return jsonify({"success": False, "data": None, "error": "Invalid political leaning value received from analysis model"}), 500

        # Construct the final successful response using the validated data
        result = {
            "success": True,
            "data": analysis_data, # Use the dictionary directly
            "error": None
        }
        return jsonify(result), 200

    except Exception as e:
        # Log the exception for debugging
        # This catches API errors, network issues, etc.
        app.logger.error(f"Error during OpenAI call or processing: {e}")
        return jsonify({"success": False, "data": None, "error": "Failed to analyze text due to an internal error"}), 500

if __name__ == '__main__':
    # When running locally, Flask dev server handles CORS differently.
    # Gunicorn relies on the CORS configuration above.
    # Make sure to set the OPENAI_API_KEY environment variable before running
    app.run(debug=True) 