import os
import cv2
import tempfile
import subprocess
from flask import Flask, request, send_file, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    video_file = request.files['video']
    watermark_text = request.form['watermark']
    output_filename = 'watermarked_video.mp4'
    final_output_filename = 'final_output_with_audio.mp4'
    temp_audio_file = 'temp_audio.mp3'

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        video_file.save(temp_video)
        temp_video_path = temp_video.name

    try:
        add_watermark(temp_video_path, watermark_text, output_filename, temp_audio_file, final_output_filename)
        return send_file(final_output_filename, as_attachment=True)
    finally:
        cleanup_files([temp_video_path, output_filename, temp_audio_file, final_output_filename])

def add_watermark(input_video_path, watermark_text, output_video_path, temp_audio_path, final_output_filename):
    # Extract audio from the original video
    subprocess.run(['ffmpeg', '-i', input_video_path, '-q:a', '0', '-map', 'a', temp_audio_path], check=True)

    # Process video to add watermark
    cap = cv2.VideoCapture(input_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (255, 255, 255)
    font_thickness = 2

    # Initial position for floating watermark
    x, y = 50, 50
    move_x, move_y = 2, 2
    # ... [Continuation from the previous part] ...

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Static watermark
        cv2.putText(frame, watermark_text, (50, height - 50), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
        
        # Floating watermark
        cv2.putText(frame, watermark_text, (x, y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
        
        # Update position for floating watermark
        x += move_x
        y += move_y
        if x + 200 > width or x < 0:
            move_x = -move_x
        if y + 50 > height or y < 0:
            move_y = -move_y

        out.write(frame)

    cap.release()
    out.release()

    # Merge audio back into the watermarked video
    subprocess.run(['ffmpeg', '-i', output_video_path, '-i', temp_audio_path, '-c', 'copy', '-map', '0:v', '-map', '1:a', '-shortest', final_output_filename], check=True)

def cleanup_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


