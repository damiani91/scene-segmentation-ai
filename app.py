from flask import Flask, render_template, request, jsonify
import os
from video_analyzer import extract_frames, analyze_video_frames
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']

    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Create a temporary directory to store the uploaded video
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    video_path = os.path.join(upload_folder, video_file.filename)
    video_file.save(video_path)

    try:
        # Extract frames from the video
        video_frames = extract_frames(video_path, frames_per_second=1)

        if not video_frames:
            return jsonify({'error': 'Could not extract frames from the video.'}), 500

        # Analyze the frames with Gemini
        metadata_json_string = analyze_video_frames(video_frames)

        if not metadata_json_string:
            return jsonify({'error': 'Failed to get analysis from Gemini.'}), 500

        # Parse the JSON output
        metadata = json.loads(metadata_json_string)

        return jsonify(metadata)

    finally:
        # Clean up the uploaded video file
        if os.path.exists(video_path):
            os.remove(video_path)

if __name__ == '__main__':
    app.run(debug=True)
