import os
import queue
import time
from PIL import Image

API_KEY = os.getenv("GOOGLE_API_KEY")

model = None
if API_KEY:
    try:
        import google.generativeai as genai

        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
    except ImportError:
        print("Warning: 'google-generativeai' is not installed. AI functionality will be disabled.")
    except Exception as e:
        print(f"Error initializing AI model: {e}")


def send_to_ai_stream(image: Image.Image, q: queue.Queue):
    print("Streaming image to AI for analysis...")
    if not model:
        mock_response = f"AI model not configured. This is a mock response.\nImage size: {image.width}x{image.height}"
        for char in mock_response:
            q.put(char)
            time.sleep(0.05)
        q.put(None)
        return

    try:
        response = model.generate_content(["Describe what you see in this image.", image], stream=True)
        for chunk in response:
            q.put(chunk.text)
        q.put(None)
    except Exception as e:
        error_message = f"Error during AI call: {e}"
        print(error_message)
        q.put(error_message)
        q.put(None)
