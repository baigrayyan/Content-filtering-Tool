# Content-filtering-Tool
# SafeFlix 🎬🛡️

**SafeFlix** is an intelligent video filtering tool that automatically detects and removes inappropriate content from videos, making them safe for family viewing. Using advanced AI models for NSFW detection, kissing scene recognition, and profanity filtering, SafeFlix creates clean versions of your videos while preserving all appropriate content.

## ✨ Features

- **🔞 NSFW Content Detection**: Automatically detects and removes explicit nudity and sexual content using NudeNet AI
- **💋 Kissing Scene Detection**: Identifies and filters out kissing scenes using face proximity analysis
- **🤬 Profanity Filtering**: Transcribes audio using OpenAI Whisper and removes segments containing profane language
- **🎥 Smart Video Editing**: Seamlessly stitches together clean segments while maintaining video quality
- **🌐 Web Interface**: Easy-to-use Flask-based web application for uploading and processing videos
- **⚡ Local Processing**: All processing happens locally on your machine - no cloud uploads required

## 🛠️ Technology Stack

- **Backend**: Python 3.x with Flask
- **AI Models**: 
  - NudeNet for NSFW detection
  - OpenCV for video processing
  - OpenAI Whisper for audio transcription
- **Video Processing**: MoviePy
- **Profanity Detection**: better-profanity library

## 📋 Prerequisites

- Python 3.8 or higher
- FFmpeg (required by MoviePy)
- At least 4GB RAM (8GB recommended for processing longer videos)
- ~500MB disk space for AI models (downloaded automatically on first run)

## 🚀 Installation

### 1. Clone or Download the Repository

```bash
cd safeflix
```

### 2. Install FFmpeg

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add FFmpeg to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: On first run, NudeNet will automatically download its detection models (~200MB) to `C:\Users\<username>\.NudeNet\`. This is a one-time download.

## 🎯 Usage

### Starting the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Processing a Video

1. Open your browser and navigate to `http://localhost:5000`
2. Click "Choose File" and select a video (MP4, MOV, AVI, or MKV)
3. Click "Upload and Process"
4. Wait for processing to complete (progress shown in terminal)
5. Download your cleaned video from the results page

### Supported Video Formats

- MP4
- MOV
- AVI
- MKV

### Limitations

- **Maximum file size**: 500 MB
- **Maximum duration**: 30 minutes
- Processing time varies based on video length and content (approximately 2-5x real-time)

## 📁 Project Structure

```
safeflix/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── utils/
│   ├── detector.py       # NSFW, kissing, and profanity detection
│   └── editor.py         # Video editing and interval merging
├── templates/
│   ├── index.html        # Upload page
│   └── result.html       # Results/download page
└── static/
    ├── uploads/          # Temporary storage for uploaded videos
    ├── processed/        # Cleaned output videos
    └── css/
        └── style.css     # Application styling
```

## ⚙️ Configuration

Edit `config.py` to customize settings:

```python
# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL = "base"  # Larger = more accurate but slower

# Maximum upload size (in bytes)
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB

# Maximum video duration (in seconds)
MAX_DURATION = 1800  # 30 minutes
```

### Detection Sensitivity

You can adjust detection thresholds in `utils/detector.py`:

```python
# NSFW Detection
detect_nsfw_frames(video_path, threshold=0.2, sample_every_sec=0.5)

# Kissing Scene Detection
detect_kissing_scenes(video_path, threshold=0.2, sample_every_sec=0.3, proximity_threshold=250)
```

- **Lower threshold** = More sensitive (may have false positives)
- **Higher threshold** = Less sensitive (may miss some content)

## 🔍 How It Works

### 1. NSFW Detection
- Samples video frames at regular intervals (default: every 0.5 seconds)
- Uses NudeNet AI to detect explicit body parts
- Flags intervals containing:
  - Exposed genitalia
  - Exposed female breasts
  - Exposed buttocks
  - Other explicit content

### 2. Kissing Scene Detection
- Detects faces in video frames using OpenCV's Haar Cascade
- Calculates proximity between detected faces
- Flags scenes where faces are very close together (indicating kissing)

### 3. Profanity Detection
- Extracts audio from video
- Transcribes audio using OpenAI Whisper
- Scans transcription for profane words
- Identifies time segments containing profanity

### 4. Video Editing
- Merges all flagged intervals (NSFW + kissing + profanity)
- Removes overlapping intervals
- Extracts clean segments
- Concatenates segments into final video
- Preserves original video quality and audio

## 🐛 Troubleshooting

### Models Not Downloading
If NudeNet models fail to download:
1. Check your internet connection
2. Ensure you have write permissions to `C:\Users\<username>\.NudeNet\`
3. Try manually downloading models from the NudeNet repository

### Video Processing Fails
- Ensure FFmpeg is properly installed and in PATH
- Check that video file is not corrupted
- Verify video format is supported
- Try with a shorter video first

### High Memory Usage
- Close other applications
- Use a smaller Whisper model (`tiny` or `base`)
- Process shorter videos or reduce sampling frequency

### File Handle Errors (Windows)
The application includes automatic garbage collection to prevent file handle issues. If problems persist:
- Restart the application
- Ensure no other programs are accessing the video files

## 🔒 Privacy & Security

- **100% Local Processing**: All video processing happens on your machine
- **No Cloud Uploads**: Videos never leave your computer
- **Automatic Cleanup**: Original uploads are deleted after processing
- **No Data Collection**: SafeFlix doesn't collect or transmit any user data

## 📝 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional content detection types
- Performance optimizations
- UI/UX enhancements
- Support for more video formats
- Batch processing capabilities

## ⚠️ Disclaimer

SafeFlix uses AI models that may not be 100% accurate. Always review processed videos before sharing, especially with children. The tool is designed to assist with content filtering but should not be relied upon as the sole method of content moderation.

## 📧 Support

For issues, questions, or feature requests, please check the troubleshooting section above or review the code comments in the source files.

---

**Made with ❤️ for safer family viewing**
