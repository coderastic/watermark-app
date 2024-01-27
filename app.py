import os
import cv2
import tempfile
import numpy as np
from flask import Flask, request, send_file, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    video_file = request.files['video']
    watermark_text = request.form['watermark']
    output_filename = 'output_video.mp4'

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        video_file.save(temp_video)
        temp_video_path = temp_video.name

    try:
        add_watermark(temp_video_path, watermark_text, output_filename)
        return send_file(output_filename, as_attachment=True)
    finally:
        os.remove(temp_video_path)
        if os.path.exists(output_filename):
            os.remove(output_filename)

def add_watermark(input_video_path, watermark_text, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (255, 255, 255)
    font_thickness = 2

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, watermark_text, (50, 50), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
        out.write(frame)

    cap.release()
    out.release()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
