# Twitter/X Political Bias Analyzer Backend

## Overview

This is a simple Flask backend API designed to analyze text snippets (e.g., tweets) to determine if they are political in nature and classify their political leaning (left, centre, right). It utilizes the OpenAI API for the analysis.

The primary use case is for a browser extension that analyzes content directly on Twitter/X.

## Features

*   Analyzes text input for political content and leaning.
*   Provides a simple JSON response.
*   Configured with CORS to allow requests specifically from `https://twitter.com` and `https://x.com`.
*   Ready for deployment (e.g., on Railway).

## API Endpoint

The main endpoint is `/analyze`.

*   **Method:** `POST`
*   **Request Body:** `{ "text": "Text to analyze" }`
*   **Success Response (200):** `{ "success": true, "data": { "is_political": <boolean>, "political_leaning": <"left"|"centre"|"right"|null> }, "error": null }`
*   **Error Responses:** Returns `400` for bad requests (e.g., missing text) and `500` for internal server errors (e.g., OpenAI issues).

See the full API specification for more details.

## Running Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/adrish96/twtr-bias-detector.git
    cd twtr-bias-detector
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set environment variables:**
    You need to set your OpenAI API key. Create a `.env` file or export it:
    ```bash
    export OPENAI_API_KEY='your_openai_api_key'
    ```
5.  **Run the Flask app:**
    ```bash
    python app.py
    ```
    The app will be running on `http://127.0.0.1:5000`.

## Deployment

This project includes a `Procfile` for easy deployment on platforms like Heroku or Railway:
```
web: gunicorn app:app
```
Ensure the `OPENAI_API_KEY` environment variable is set in your deployment environment.

## CORS Configuration

The backend is configured using `Flask-CORS` to only allow requests to the `/analyze` endpoint from `https://twitter.com` and `https://x.com`.

## Dependencies

*   Flask
*   Flask-CORS
*   OpenAI
*   Gunicorn (for deployment)