import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Configure OpenAI client
# Ensure the OPENAI_API_KEY environment variable is set
client = OpenAI()

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

    prompt = f'''You are a political ideology classifier. Analyze the following text and categorize it as either "left", "centre", or "right" leaning based on its political perspective. Consider the text's stance on economics, social issues, role of government, tradition vs. change, and hierarchical vs. egalitarian values.
Respond with exactly one word only: "left", "centre", or "right". Do not include any other text, explanation, or reasoning in your response.
Text to classify:
{input_text}'''

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=5, # Allow a few tokens for the single word response
            temperature=0 # For deterministic output
        )
        classification = response.choices[0].message.content.strip().lower()

        # Validate the response from OpenAI
        if classification not in ["left", "centre", "right"]:
            # You might want to handle this case differently, e.g., log it, or try again.
            # For now, we'll return an error indicating an unexpected response.
            return jsonify({
                "success": False,
                "data": None,
                "error": f"Unexpected response from classification model: {classification}"
            }), 500

        result = {
            "success": True,
            "data": {
                "is_political": True, # Based on the prompt, we assume it's political if classified
                "political_leaning": classification
            },
            "error": None
        }
        return jsonify(result), 200

    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"Error calling OpenAI API: {e}")
        return jsonify({"success": False, "data": None, "error": "Failed to analyze text due to an internal error"}), 500

if __name__ == '__main__':
    # Make sure to set the OPENAI_API_KEY environment variable before running
    app.run(debug=True) 