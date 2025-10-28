import cv2
import base64
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

def extract_frames(video_path, frames_per_second=1):
    """Efficiently extracts frames from a video file by jumping to specific frame numbers and returns them as a list of base64 encoded strings."""
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return []

    try:
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return []

        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)

        if fps == 0 or total_frames == 0:
            print("Error: Cannot get video properties (FPS or total frames). Unable to proceed.")
            return []

        # Calculate the indices of frames to extract
        frame_interval = fps / frames_per_second
        frame_indices = [int(i * frame_interval) for i in range(int(total_frames / frame_interval))]

        base64_frames = []
        
        for frame_index in frame_indices:
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = video.read()
            if success:
                _, buffer = cv2.imencode(".jpg", frame)
                base64_frame = base64.b64encode(buffer).decode("utf-8")
                base64_frames.append(base64_frame)

    finally:
        if 'video' in locals() and video.isOpened():
            video.release()

    print(f"Extracted {len(base64_frames)} frames for analysis.")
    return base64_frames

def analyze_video_frames(base64_frames):
    """Sends frames to Gemini API for analysis and returns a JSON string."""
    model = genai.GenerativeModel('gemini-2.5-pro')

    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "scene_number": {"type": "integer", "description": "Sequential scene number, starting at 1."},
                "start_time": {"type": "string", "description": "Scene start time in MM:SS format."},
                "end_time": {"type": "string", "description": "Scene end time in MM:SS format."},
                "name": {"type": "string", "description": "A concise and descriptive name for the scene."},
                "genre": {"type": "string", "description": "The genre of the scene (e.g., Drama, Comedy, Action, Suspense, Romance)."},
                "description": {"type": "string", "description": "A brief summary of key events, actions, and dialogue in the scene."},
                "characters": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of characters present and active in the scene."
                },
                "setting": {"type": "string", "description": "The main location or setting of the scene."},
                "mood": {"type": "string", "description": "The overall emotional tone of the scene (e.g., Tense, Joyful, Somber)."}
            },
            "required": ["scene_number", "start_time", "end_time", "name", "genre", "description"]
        }
    }

    prompt_text = '''
    As an expert film analyst, your task is to analyze a sequence of video frames and generate detailed scene-by-scene metadata.
    The frames are extracted at a rate of one frame per second, so the number of frames equals the video's duration in seconds. For example, 120 frames mean the video is 2 minutes long.
    Please identify distinct scenes. A scene is a continuous action in a single location. A change of location or a significant jump in time indicates a new scene.
    For each scene, provide the requested metadata. The output MUST be a valid JSON array of objects, conforming to the provided schema.

    Analyze the following frames and generate the metadata.
    '''

    image_parts = [{"inline_data": {"mime_type": "image/jpeg", "data": frame}} for frame in base64_frames]
    contents = [prompt_text] + image_parts

    try:
        print("\nCalling Gemini API for analysis... This may take several minutes depending on the video length.")
        response = model.generate_content(
            contents,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.2
            )
        )
        print("Analysis complete.")
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None