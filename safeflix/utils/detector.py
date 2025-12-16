import cv2
import numpy as np
from nudenet import NudeDetector
import whisper
from better_profanity import profanity
import moviepy.editor as mp
import os
import tempfile
from config import Config

# Initialize NudeNet detector (lazy loading to avoid re-downloading models)
# Models are cached in: C:\Users\<username>\.NudeNet\
# First run will download models (~200MB), subsequent runs use cached models
detector = None

def get_detector():
    global detector
    if detector is None:
        print("🔧 Initializing NudeNet detector (first time only)...")
        detector = NudeDetector()
        print("✅ NudeNet detector ready!")
    return detector

# Define explicit nudity classes to flag (sexual body parts only)
# Ignore: faces, covered body parts, exposed feet, armpits, belly, male breasts
# Using actual NudeNet class names as they appear in detections
EXPLICIT_NUDITY_CLASSES = {
    'FEMALE_BREAST_EXPOSED',      # Exposed female breasts
    'FEMALE_GENITALIA_EXPOSED',   # Exposed female genitalia
    'MALE_GENITALIA_EXPOSED',     # Exposed male genitalia
    'BUTTOCKS_EXPOSED',           # Exposed buttocks
    'ANUS_EXPOSED',               # Exposed anus
    'FEMALE_BREAST_COVERED',      # TEMPORARY: Sometimes exposed breasts are misclassified as covered
}

def detect_nsfw_frames(video_path, threshold=0.2, sample_every_sec=0.5):
    print(f"🔍 Starting NSFW detection on: {video_path}")
    print(f"   Threshold: {threshold}, Sampling every {sample_every_sec} seconds")
    print(f"   Looking for: {', '.join(EXPLICIT_NUDITY_CLASSES)}")
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    bad_intervals = []
    frame_idx = 0
    frames_checked = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        current_sec = frame_idx / fps
        if int(current_sec * 10) % int(sample_every_sec * 10) == 0:
            frames_checked += 1
            # Save frame temporarily for NudeNet
            temp_frame_path = tempfile.mktemp(suffix='.jpg')
            cv2.imwrite(temp_frame_path, frame)
            
            # Detect NSFW content
            detections = get_detector().detect(temp_frame_path)
            os.unlink(temp_frame_path)
            
            # Debug: print all detections
            if detections:
                print(f"   Frame at {current_sec:.1f}s: {len(detections)} detections")
                for det in detections:
                    print(f"      - {det['class']}: {det['score']:.2f}")
                
                # PRECISE MODE: Only flag explicit nudity classes
                # Filter for actual exposed nudity (not faces, covered parts, etc.)
                explicit_detections = [
                    det for det in detections 
                    if det['class'] in EXPLICIT_NUDITY_CLASSES and det['score'] > threshold
                ]
                
                # Show what was filtered out
                filtered_out = [
                    det for det in detections
                    if det['class'] not in EXPLICIT_NUDITY_CLASSES or det['score'] <= threshold
                ]
                if filtered_out:
                    filtered_info = [(d['class'], round(d['score'], 2)) for d in filtered_out]
                    print(f"      Ignored (not explicit nudity): {filtered_info}")
                
                if explicit_detections:
                    # Smaller buffer zone around actual nudity
                    interval = (max(0, current_sec - 2), current_sec + 3)
                    bad_intervals.append(interval)
                    flagged_info = [(d['class'], round(d['score'], 2)) for d in explicit_detections]
                    print(f"   ⚠️ EXPLICIT NUDITY detected! Marking interval: {interval}")
                    print(f"      Flagged: {flagged_info}")
        
        frame_idx += 1
    cap.release()
    
    print(f"✅ Detection complete. Checked {frames_checked} frames, found {len(bad_intervals)} NSFW intervals")
    return bad_intervals

def detect_kissing_scenes(video_path, threshold=0.2, sample_every_sec=0.3, proximity_threshold=250):
    """
    Detect kissing scenes by analyzing face proximity.
    When 2+ faces are very close together, it likely indicates kissing.
    
    AGGRESSIVE MODE: Lower threshold and larger proximity to catch partially obscured faces.
    """
    print(f"💋 Starting kissing scene detection on: {video_path}")
    print(f"   Face threshold: {threshold}, Proximity threshold: {proximity_threshold}px")
    print(f"   Sampling every {sample_every_sec}s (AGGRESSIVE MODE)")
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    kissing_intervals = []
    frame_idx = 0
    frames_checked = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        current_sec = frame_idx / fps
        if int(current_sec * 10) % int(sample_every_sec * 10) == 0:
            frames_checked += 1
            # Save frame temporarily for NudeNet
            temp_frame_path = tempfile.mktemp(suffix='.jpg')
            cv2.imwrite(temp_frame_path, frame)
            
            # Detect faces using NudeNet
            detections = get_detector().detect(temp_frame_path)
            os.unlink(temp_frame_path)
            
            # Filter for face detections (both male and female faces)
            faces = [det for det in detections if 'FACE' in det['class'] and det['score'] > threshold]
            
            if len(faces) >= 2:
                print(f"   Frame at {current_sec:.1f}s: Found {len(faces)} faces")
                # Check if any two faces are very close (potential kissing)
                for i in range(len(faces)):
                    for j in range(i + 1, len(faces)):
                        face1 = faces[i]['box']
                        face2 = faces[j]['box']
                        
                        # Calculate center points of faces
                        center1_x = face1[0] + face1[2] / 2
                        center1_y = face1[1] + face1[3] / 2
                        center2_x = face2[0] + face2[2] / 2
                        center2_y = face2[1] + face2[3] / 2
                        
                        # Calculate distance between face centers
                        distance = np.sqrt((center1_x - center2_x)**2 + (center1_y - center2_y)**2)
                        
                        print(f"      Face distance: {distance:.1f}px")
                        
                        if distance < proximity_threshold:
                            # Longer buffer zone to catch the entire scene
                            interval = (max(0, current_sec - 4), current_sec + 6)
                            kissing_intervals.append(interval)
                            print(f"   💋 KISSING SCENE DETECTED at {current_sec:.1f}s! Distance: {distance:.1f}px")
                            print(f"      Faces: {faces[i]['class']} + {faces[j]['class']}")
                            print(f"      Marking interval: {interval}")
                            break  # Only mark once per frame
            elif len(faces) == 1:
                # Even single face detection might indicate intimate scene if confidence is high
                if faces[0]['score'] > 0.5:
                    print(f"   Frame at {current_sec:.1f}s: Single face detected (score: {faces[0]['score']:.2f})")
        
        frame_idx += 1
    cap.release()
    
    print(f"✅ Kissing detection complete. Checked {frames_checked} frames, found {len(kissing_intervals)} kissing intervals")
    return kissing_intervals

def detect_profanity_audio(video_path):
    """
    Detect profanity in video audio using Whisper for transcription
    and better-profanity for detection. Runs completely locally.
    """
    print("🎤 Starting audio profanity detection with Whisper...")
    
    # Initialize profanity detector
    profanity.load_censor_words()
    
    # Extract audio
    audio_path = None
    clip = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_path = tmp.name
        
        clip = mp.VideoFileClip(video_path)
        if clip.audio is None:
            print("   No audio track found in video")
            clip.close()
            return []
        
        print("   Extracting audio from video...")
        clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
        clip.close()
        clip = None

        # Load Whisper model and transcribe
        print(f"   Loading Whisper model ({Config.WHISPER_MODEL})...")
        model = whisper.load_model(Config.WHISPER_MODEL)
        
        print("   Transcribing audio...")
        result = model.transcribe(audio_path, word_timestamps=True)
        
        # Detect profanity in transcribed text
        bad_intervals = []
        if result.get('segments'):
            for segment in result['segments']:
                segment_text = segment['text']
                
                # Check if segment contains profanity
                if profanity.contains_profanity(segment_text):
                    # Add buffer around profane segment
                    start = max(0, segment['start'] - 2)
                    end = segment['end'] + 2
                    bad_intervals.append((start, end))
                    print(f"   ⚠️ Profanity detected at {start:.1f}s - {end:.1f}s")
                    print(f"      Text: {profanity.censor(segment_text)}")
        
        print(f"✅ Audio analysis complete. Found {len(bad_intervals)} profane segments")
        return bad_intervals
        
    except Exception as e:
        print(f"⚠️ Error during audio profanity detection: {e}")
        return []
    finally:
        # Ensure cleanup happens even if there's an error
        if clip is not None:
            clip.close()
        if audio_path and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
            except:
                pass