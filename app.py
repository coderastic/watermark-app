from flask import Flask, request, send_file, render_template
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    video_file = request.files['video']
    watermark_text = request.form['watermark']

    processed_video = add_watermark(video_file, watermark_text)

    output_filename = 'output_video.mp4'
    processed_video.write_videofile(output_filename, codec='libx264')

    return send_file(output_filename, as_attachment=True)

def add_watermark(video_file, watermark_text):
    clip = VideoFileClip(video_file.stream)

    txt_clip = TextClip(watermark_text, fontsize=70, color='white')
    txt_mov = txt_clip.set_position(lambda t: ('center', 50*t)).set_duration(clip.duration)

    video = CompositeVideoClip([clip, txt_mov])

    return video

if __name__ == '__main__':
    app.run(debug=True)
