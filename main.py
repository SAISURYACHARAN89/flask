from flask import Flask, request, jsonify
import requests
import math

app = Flask(__name__)

# Replace with your actual Face++ API credentials
API_KEY = 'SG6IeU3wbQAkGA_ZcP7v9AN83ZmzG_k_'
API_SECRET = 'owpSJX-AkNkfOIxDn11awPAjA4Iy6CSl'
FACE_API_URL = 'https://api-us.faceplusplus.com/facepp/v3/detect'

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    # Get the image file
    image_file = request.files['image']

    # Prepare the payload for Face++ API
    data = {
        'api_key': API_KEY,
        'api_secret': API_SECRET,
        'return_landmark': 2,
        'return_attributes': 'age,gender,emotion'
    }
    files = {'image_file': image_file}

    # Send a request to the Face++ API
    response = requests.post(FACE_API_URL, data=data, files=files)

    # Handle the API response
    if response.status_code == 200:
        analysis = response.json()

        if 'faces' in analysis:
            # Example: Process the first detected face
            face = analysis['faces'][0]

            # Extract landmarks and calculate face shape
            landmarks = face['landmark']
            chin = landmarks['contour_chin']
            left_ear = landmarks['contour_left1']
            right_ear = landmarks['contour_right1']

            jawline_width = math.dist([left_ear['x'], left_ear['y']], [right_ear['x'], right_ear['y']])
            forehead = landmarks['left_eyebrow_upper_middle']
            face_height = math.dist([chin['x'], chin['y']], [forehead['x'], forehead['y']])
            ratio = jawline_width / face_height

            if ratio > 1.4:
                face_shape = "Square"
            elif ratio < 1.1:
                face_shape = "Oval"
            else:
                face_shape = "Round"

            return jsonify({
                "age": face['attributes']['age']['value'],
                "gender": face['attributes']['gender']['value'],
                "emotion": face['attributes']['emotion'],
                "face_shape": face_shape
            })
        else:
            return jsonify({"error": "No faces detected"}), 400
    else:
        return jsonify({"error": "Face++ API error", "details": response.json()}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
