"""
Test script to verify NudeNet detection is working
Run this to test if the detector can find NSFW content
"""
from nudenet import NudeDetector
import sys

print("=" * 60)
print("Testing NudeNet Detector")
print("=" * 60)

# Initialize detector
print("\n1. Initializing NudeDetector...")
detector = NudeDetector()
print("   ✅ Detector initialized")

# Test with a video file
if len(sys.argv) > 1:
    video_path = sys.argv[1]
    print(f"\n2. Testing with video: {video_path}")
    
    import cv2
    import tempfile
    import os
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"   Video FPS: {fps}")
    print(f"   Sampling frames at 30s, 60s, 90s, 120s...")
    
    test_times = [30, 60, 90, 120]  # Test at these timestamps
    
    for test_sec in test_times:
        frame_num = int(test_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        
        if not ret:
            print(f"   ⚠️ Could not read frame at {test_sec}s")
            continue
        
        # Save frame and detect
        temp_path = tempfile.mktemp(suffix='.jpg')
        cv2.imwrite(temp_path, frame)
        
        detections = detector.detect(temp_path)
        os.unlink(temp_path)
        
        print(f"\n   Frame at {test_sec}s:")
        if detections:
            print(f"   Found {len(detections)} detections:")
            for det in detections:
                print(f"      - {det['class']}: {det['score']:.3f}")
        else:
            print(f"   No detections found")
    
    cap.release()
else:
    print("\n❌ No video file provided")
    print("Usage: python test_detector.py <path_to_video>")
    print("\nExample:")
    print("  python test_detector.py static/uploads/your_video.mp4")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
