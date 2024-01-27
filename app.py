import os
import tempfile
from flask import Flask, request, send_file, render_template
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

app = Flask(__name__)

@app.route('/')
def index():
    # Render the main page with the form to upload a video and enter watermark text
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    video_file = request.files['video']
    watermark_text = request.form['watermark']

    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        video_file.save(temp_video)
        temp_video_path = temp_video.name

    try:
        processed_video = add_watermark(temp_video_path, watermark_text)

        output_filename = 'output_video.mp4'
        processed_video.write_videofile(output_filename, codec='libx264', audio_codec='aac')

        return send_file(output_filename, as_attachment=True)
    finally:
        # Clean up: remove the temporary files
        os.remove(temp_video_path)
        if os.path.exists(output_filename):
            os.remove(output_filename)

def add_watermark(video_file_path, watermark_text):
    # Process the video and add a floating watermark
    clip = VideoFileClip(video_file_path)

    txt_clip = TextClip(watermark_text, fontsize=70, color='white')
    txt_mov = txt_clip.set_position(lambda t: ('center', 50*t)).set_duration(clip.duration)

    video = CompositeVideoClip([clip, txt_mov])

    return video

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT environment variable if available, else default to 5000
    app.run(host='0.0.0.0', port=port)


