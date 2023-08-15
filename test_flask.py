from flask import Flask, request, jsonify
import easyocr
import io
from PIL import Image
import re
import requests 
from roboflow import Roboflow
import numpy as np
from sklearn.cluster import DBSCAN
import cv2
app = Flask(__name__)
reader = easyocr.Reader(['vi'])
rf = Roboflow(api_key="Ih6MZ6ozUZB94IqcBKij")
project = rf.workspace("ocr-l5oxq").project("testorc")

model = project.version(2).model



def sort_words_by_coordinates(words):
    centers = [np.mean(np.array(coords), axis=0) for coords, _, _ in words]
    sorted_words = sorted(zip(centers, words), key=lambda x: x[0][1])
    lines = []
    current_line = []
    current_y = sorted_words[0][0][1]
    for center, word in sorted_words:
        if abs(center[1] - current_y) < 10:
            current_line.append(word)
        else:
            lines.append(sorted(current_line, key=lambda x: np.mean(np.array(x[0]), axis=0)[0]))
            current_line = [word]
            current_y = center[1]
    lines.append(sorted(current_line, key=lambda x: np.mean(np.array(x[0]), axis=0)[0]))
    return lines
def sort_words_by_coordinates_date(words):
    centers = [np.mean(np.array(coords), axis=0) for coords, _, _ in words]
    y_coords = [center[1] for center in centers]
    avg_height = np.mean([max(coords, key=lambda x: x[1])[1] - min(coords, key=lambda x: x[1])[1] for coords, _, _ in words])
    lines = []
    current_line = [words[0]]
    current_y = y_coords[0]
    for i in range(1, len(words)):
        if abs(y_coords[i] - current_y) < avg_height:
            current_line.append(words[i])
        else:
            lines.append(sorted(current_line, key=lambda x: np.mean(np.array(x[0]), axis=0)[0]))
            current_line = [words[i]]
            current_y = y_coords[i]
    lines.append(sorted(current_line, key=lambda x: np.mean(np.array(x[0]), axis=0)[0]))
    return lines
@app.route('/process', methods=['POST'])

def process():
        if 'image' not in request.files:
                return jsonify({"error": "No image part"})
        
        image = request.files['image']
        if image.filename == '':
                return jsonify({"error": "No selected image"})
        
        image_data = image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        alpha = 2.0
        beta = -160

        new = alpha * img + beta
        new = np.clip(new, 0, 255).astype(np.uint8)

        image_pil = Image.fromarray(cv2.cvtColor(new, cv2.COLOR_BGR2RGB))
        #image_pil = Image.open(io.BytesIO(image_data))
        image_np = np.array(image_pil)
        prediction_response = model.predict(image_np, confidence=50, overlap=30).json()
        image = image_pil
        cropped_images = []
        results = []
        for prediction in prediction_response["predictions"]:
                x1 = prediction["x"] - prediction["width"] / 2
                y1 = prediction["y"] - prediction["height"] / 2
                x2 = prediction["x"] + prediction["width"] / 2
                y2 = prediction["y"] + prediction["height"] / 2

                cropped_image = image.crop((x1, y1, x2, y2))
                width, height = cropped_image.size
                new_width = int(width * 2.5)
                new_height = int(height * 2.5)
                cropped_image = cropped_image.resize((new_width, new_height))

                class_name = prediction["class"]

                cropped_images.append((class_name, cropped_image))
        for class_name, cropped_image in cropped_images:
            text_result = reader.readtext(np.array(cropped_image))
            print(class_name)
            print(text_result)
            if class_name == "ngay":
                sorted_text_result = sort_words_by_coordinates_date(text_result)
            else:
                sorted_text_result = sort_words_by_coordinates(text_result)
            for line in sorted_text_result:
                text = ' '.join([text for _, text, _ in line])
                result = {"class": class_name, "text": text}
                results.append(result)
        
        print(results)
        return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)

