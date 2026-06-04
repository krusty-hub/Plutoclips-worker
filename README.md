# PlutoClips Worker

A production-ready backend service for AI-driven video clip generation. Automatically transcribes videos, identifies viral moments, generates clips, creates captions, and returns downloadable results.

## Overview

PlutoClips Worker is a FastAPI application that:

1. **Accepts video uploads** - Validates and stores video files
2. **Extracts audio** - Uses FFmpeg to extract audio tracks
3. **Transcribes speech** - Uses OpenAI Whisper API for accurate transcription
4. **Detects viral moments** - Uses Claude or GPT to analyze transcripts and identify clip-worthy segments
5. **Generates clips** - Automatically cuts video segments using FFmpeg
6. **Creates captions** - Generates SRT subtitle files with filler word removal
7. **Produces thumbnails** - Creates preview images for each clip
8. **Returns downloadable files** - Provides URLs for all generated content

## Tech Stack

### Backend
- **Python 3.12** - Modern Python with async support
- **FastAPI** - High-performance async web framework
- **Uvicorn** - ASGI server

### Video Processing
- **FFmpeg** - Professional video/audio manipulation
- **ffprobe** - Video metadata extraction

### AI & Transcription
- **OpenAI Whisper API** - State-of-the-art speech transcription
- **OpenAI GPT** - Optional clip analysis fallback
- **Anthropic Claude** - Primary AI for transcript analysis

### Storage & Database
- **Local filesystem** - MVP storage (upgradeable to S3/R2)
- **SQLite** - Job tracking and metadata (upgradeable to PostgreSQL)

### Deployment
- **Docker** - Containerization
- **Railway** - Cloud deployment platform

## Installation

### Prerequisites

- Python 3.12+
- FFmpeg installed system-wide
- OpenAI API key
- Anthropic API key (optional, but recommended)

### System Dependencies

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
apt-get install ffmpeg
```

#### Windows
Download from: https://ffmpeg.org/download.html

### Local Development Setup

1. **Clone repository**
```bash
git clone <repository-url>
cd plutoclips-worker
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` and add:
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key

5. **Run application**
```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | development or production |
| `LOG_LEVEL` | INFO | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `OPENAI_API_KEY` | - | Required: OpenAI API key |
| `ANTHROPIC_API_KEY` | - | Required: Anthropic API key |
| `MAX_UPLOAD_SIZE_MB` | 500 | Maximum file upload size |
| `UPLOAD_DIR` | uploads | Directory for uploaded videos |
| `OUTPUT_DIR` | outputs | Directory for processed files |
| `ALLOWED_ORIGINS` | * | CORS allowed origins |
| `SQLITE_DB_PATH` | plutoclips.db | SQLite database file path |
| `MIN_CLIP_DURATION` | 20 | Minimum clip length (seconds) |
| `MAX_CLIP_DURATION` | 90 | Maximum clip length (seconds) |
| `TARGET_CLIP_COUNT` | 7 | Target number of clips to generate |

## API Endpoints

### Health Check
```
GET /health
```
Simple health check endpoint.

**Response:**
```json
{"status": "ok"}
```

### Upload Video
```
POST /api/v1/upload
Content-Type: multipart/form-data
```

Upload a video file for processing.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@video.mp4"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded",
  "message": "Video uploaded successfully"
}
```

### Start Processing
```
POST /api/v1/process-video
Content-Type: application/json
```

Start processing an uploaded video.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/process-video \
  -H "Content-Type: application/json" \
  -d '{"job_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Processing started"
}
```

### Check Job Status
```
GET /api/v1/job-status/{job_id}
```

Get current processing status and progress.

**Request:**
```bash
curl http://localhost:8000/api/v1/job-status/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "error": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

**Status Values:**
- `uploaded` - File received
- `processing` - Starting processing
- `transcribing` - Extracting and transcribing audio
- `analyzing` - AI analysis of transcript
- `generating` - Generating clips
- `completed` - Processing finished successfully
- `failed` - Processing failed

### Get Generated Clips
```
GET /api/v1/clips/{job_id}
```

Retrieve all generated clips for a completed job.

**Request:**
```bash
curl http://localhost:8000/api/v1/clips/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_clips": 7,
  "clips": [
    {
      "clip_id": "clip_001",
      "title": "Mind-Blowing AI Breakthrough That Changed Everything",
      "url": "/api/v1/download/clip_001.mp4",
      "duration": 54.7,
      "thumbnail_url": "/api/v1/download/clip_001_thumb.jpg",
      "captions_url": "/api/v1/download/clip_001.srt",
      "moment_type": "viral",
      "reason": "Unexpected revelation about AI capabilities that sparks curiosity"
    }
  ],
  "video_duration": 3600.0,
  "processing_time": 125.5
}
```

### Download Files
```
GET /api/v1/download/{file_path}
```

Download a clip video, caption file, or thumbnail.

**Examples:**
```bash
# Download clip video
curl -O http://localhost:8000/api/v1/download/clip_001.mp4

# Download captions
curl -O http://localhost:8000/api/v1/download/clip_001.srt

# Download thumbnail
curl -O http://localhost:8000/api/v1/download/clip_001_thumb.jpg
```

## Project Structure

```
plutoclips-worker/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker container config
├── railway.json                     # Railway deployment config
├── .env.example                     # Environment template
├── README.md                        # This file
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/                        # Core functionality
│   │   ├── config.py               # Configuration management
│   │   ├── logger.py               # Logging setup
│   │   └── exceptions.py           # Custom exceptions
│   │
│   ├── api/                         # API routes
│   │   └── routes.py               # FastAPI endpoints
│   │
│   ├── schemas/                     # Pydantic models
│   │   └── __init__.py             # Request/response schemas
│   │
│   ├── services/                    # Business logic
│   │   ├── ai.py                   # Transcription & clip detection
│   │   └── video.py                # Video processing orchestration
│   │
│   ├── database/                    # Data persistence
│   │   └── sqlite.py               # SQLite models & repositories
│   │
│   ├── storage/                     # File storage
│   │   └── local.py                # Local filesystem storage
│   │
│   └── utils/                       # Utility functions
│       ├── ffmpeg.py               # FFmpeg operations
│       └── captions.py             # Caption/SRT handling
│
├── uploads/                         # Uploaded video storage
└── outputs/                         # Processed files storage
```

## Usage Example

### Complete Workflow

```bash
# 1. Upload a video
UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/upload \
  -F "file=@my_video.mp4")

JOB_ID=$(echo $UPLOAD_RESPONSE | jq -r '.job_id')
echo "Uploaded with job ID: $JOB_ID"

# 2. Start processing
curl -X POST http://localhost:8000/api/v1/process-video \
  -H "Content-Type: application/json" \
  -d "{\"job_id\": \"$JOB_ID\"}"

# 3. Poll for completion (wait until status is "completed")
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/job-status/$JOB_ID | jq -r '.status')
  PROGRESS=$(curl -s http://localhost:8000/api/v1/job-status/$JOB_ID | jq -r '.progress')
  
  echo "Status: $STATUS, Progress: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ]; then
    break
  fi
  
  sleep 10
done

# 4. Get clips
CLIPS=$(curl -s http://localhost:8000/api/v1/clips/$JOB_ID)
echo $CLIPS | jq '.'

# 5. Download clips
echo $CLIPS | jq -r '.clips[] | .url' | while read url; do
  curl -O http://localhost:8000$url
done
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t plutoclips-worker:latest .
```

### Run Docker Container

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  plutoclips-worker:latest
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  plutoclips:
    build: .
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: production
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Railway Deployment

### Prerequisites

- Railway account (https://railway.app)
- GitHub account with repository access

### Deployment Steps

1. **Push code to GitHub**
```bash
git push origin main
```

2. **Connect Railway to GitHub**
   - Go to https://railway.app/dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**
   - In Railway dashboard, go to project Variables
   - Add required variables:
     - `OPENAI_API_KEY`
     - `ANTHROPIC_API_KEY`
     - `ENVIRONMENT=production`
     - `LOG_LEVEL=INFO`

4. **Deploy**
   - Railway automatically deploys on GitHub push
   - Monitor deployment status in dashboard

5. **Access Application**
   - Railway provides a public URL
   - Access health check: `https://your-railway-url.up.railway.app/health`
   - Access API docs: `https://your-railway-url.up.railway.app/docs`

### Railway Storage

For production, configure persistent storage:

1. Add PostgreSQL plugin in Railway
2. Update database configuration to use Railway PostgreSQL
3. Volume support available for file storage

## Testing

### API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test Video

Create a simple test video:

```bash
ffmpeg -f lavfi -i color=c=blue:s=320x240:d=10 -f lavfi -i sine=f=1000:d=10 test_video.mp4
```

Or use a sample video from:
- https://www.sample-videos.com/
- https://www.videosample.org/

## Monitoring & Logging

### Logs

Application logs are sent to stdout and can be viewed:

```bash
# Docker
docker logs <container_id>

# Railway
View in Railway dashboard under "Logs"
```

### Metrics

Current implementation tracks:
- Job creation and status
- Processing step durations
- Error messages and timestamps

For production monitoring, integrate:
- Sentry for error tracking
- DataDog for performance monitoring
- Custom metrics collection

## Future Enhancements

### Planned Features

- [ ] YouTube/Twitch URL ingestion
- [ ] Real-time livestream processing
- [ ] Multiple language support
- [ ] Custom clip duration preferences
- [ ] Subtitle style customization
- [ ] Batch processing
- [ ] Email notifications
- [ ] Webhook callbacks
- [ ] User accounts and API keys
- [ ] Usage analytics dashboard

### Technology Upgrades

- [ ] PostgreSQL migration (replace SQLite)
- [ ] Redis caching layer
- [ ] Celery task queue for horizontal scaling
- [ ] Cloudflare R2/AWS S3 storage
- [ ] GPU-accelerated video encoding
- [ ] Multi-model AI fallback chain

## Troubleshooting

### FFmpeg Not Found

```
FFmpeg not found: FFmpeg must be installed and in PATH
```

**Solution:** Install FFmpeg on your system (see Prerequisites)

### Transcription Timeout

```
TranscriptionError: Transcription timeout
```

**Solution:** 
- Increase `TRANSCRIPTION_TIMEOUT` in `.env`
- Use shorter videos for testing
- Check OpenAI API status

### Out of Memory

```
MemoryError or process killed
```

**Solution:**
- Increase available RAM
- Process shorter videos first
- Split large files using FFmpeg

### API Key Issues

```
ConfigurationError: OpenAI API key not configured
```

**Solution:**
- Verify `.env` file exists and is in project root
- Check `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` values
- Ensure keys are valid and have sufficient quota

## Performance Optimization

### For Large Videos

1. **Increase timeouts**
   ```
   TRANSCRIPTION_TIMEOUT=1200
   CLIP_GENERATION_TIMEOUT=600
   ```

2. **Reduce output quality**
   ```
   VIDEO_BITRATE=1500k
   AUDIO_BITRATE=96k
   ```

3. **Use concurrent processing**
   - Deploy multiple instances behind load balancer
   - Use Redis for job queue

### For High Load

1. **Implement job queue** (Celery/RQ)
2. **Add Redis caching**
3. **Use PostgreSQL** for reliability
4. **Deploy horizontally** with load balancing
5. **Enable gzip compression**

## Security

### Current Implementation

- ✅ File type validation
- ✅ File size limits
- ✅ Filename sanitization
- ✅ Path traversal protection
- ✅ CORS configuration
- ⚠️ Rate limiting (ready for implementation)

### Production Checklist

- [ ] Enable HTTPS/TLS
- [ ] Set `ALLOWED_ORIGINS` to specific domains
- [ ] Implement API key authentication
- [ ] Add rate limiting middleware
- [ ] Enable request logging
- [ ] Regular security audits
- [ ] Keep dependencies updated

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: support@plutoclips.dev
- Documentation: https://docs.plutoclips.dev

## Changelog

### Version 0.1.0 (Initial Release)
- Core MVP functionality
- Video upload and processing
- AI-driven clip detection
- FFmpeg integration
- SQLite database
- Local file storage
- Docker support
- Railway deployment ready
