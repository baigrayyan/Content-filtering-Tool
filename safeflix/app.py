from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import uuid
import time
import gc
from datetime import datetime
from utils.detector import detect_nsfw_frames, detect_profanity_audio, detect_kissing_scenes
from utils.editor import create_clean_video, merge_intervals
from config import Config
import moviepy.editor as mp

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        flash('No file uploaded')
        return redirect(request.url)

    file = request.files['video']
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file type')
        return redirect(request.url)

    # Save original
    orig_filename = f"{uuid.uuid4().hex}_{file.filename}"
    orig_path = os.path.join(app.config['UPLOAD_FOLDER'], orig_filename)
    file.save(orig_path)

    # Check duration
    clip = None
    try:
        clip = mp.VideoFileClip(orig_path)
        duration = clip.duration
        clip.close()
        clip = None
        
        if duration > Config.MAX_DURATION:
            flash('Video too long! Max 10 minutes.')
            time.sleep(0.5)  # Give Windows time to release file handle
            gc.collect()
            try:
                os.remove(orig_path)
            except:
                pass
            return redirect('/')
    except Exception as e:
        if clip:
            clip.close()
        flash(f'Error reading video: {str(e)}')
        time.sleep(0.5)
        gc.collect()
        try:
            os.remove(orig_path)
        except:
            pass
        return redirect('/')

    # Process in background (simple sync for FYP)
    try:
        print(f"\n{'='*60}")
        print(f"🎬 Processing video: {orig_filename}")
        print(f"{'='*60}")
        
        nsfw_bad = detect_nsfw_frames(orig_path)
        print(f"\n📊 NSFW Detection Results: {len(nsfw_bad)} bad intervals")
        if nsfw_bad:
            for i, interval in enumerate(nsfw_bad, 1):
                print(f"   {i}. {interval[0]:.1f}s - {interval[1]:.1f}s")
        
        kissing_bad = detect_kissing_scenes(orig_path)
        print(f"\n📊 Kissing Scene Detection Results: {len(kissing_bad)} bad intervals")
        if kissing_bad:
            for i, interval in enumerate(kissing_bad, 1):
                print(f"   {i}. {interval[0]:.1f}s - {interval[1]:.1f}s")
        
        profanity_bad = detect_profanity_audio(orig_path)
        print(f"\n📊 Profanity Detection Results: {len(profanity_bad)} bad intervals")
        if profanity_bad:
            for i, interval in enumerate(profanity_bad, 1):
                print(f"   {i}. {interval[0]:.1f}s - {interval[1]:.1f}s")
        
        all_bad = nsfw_bad + kissing_bad + profanity_bad
        print(f"\n📊 Total bad intervals to remove: {len(all_bad)}")

        processed_filename = f"cleaned_{uuid.uuid4().hex}.mp4"
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)

        print(f"\n✂️ Creating clean video...")
        success = create_clean_video(orig_path, all_bad, processed_path)
        
        # Force garbage collection to release file handles
        gc.collect()
        time.sleep(0.5)

        if success and os.path.exists(processed_path) and os.path.getsize(processed_path) > 1024:
            print(f"✅ Success! Clean video created: {processed_filename}")
            print(f"   Size: {os.path.getsize(processed_path) / 1024 / 1024:.2f} MB")
            print(f"{'='*60}\n")
            # Clean up original file
            try:
                os.remove(orig_path)
            except:
                pass  # If we can't delete, that's okay
            return redirect(url_for('result', filename=processed_filename))
        else:
            print(f"❌ Failed to create clean video or file too small")
            print(f"{'='*60}\n")
            flash('No clean content found or error occurred.')
            try:
                os.remove(orig_path)
            except:
                pass
            return redirect('/')
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        print(f"{'='*60}\n")
        flash(f'Error: {str(e)}')
        gc.collect()
        time.sleep(0.5)
        try:
            if os.path.exists(orig_path):
                os.remove(orig_path)
        except:
            pass
        return redirect('/')

@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Disable auto-reload to prevent interrupting video processing
    app.run(debug=True, use_reloader=False)