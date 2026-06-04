# PlutoClips Worker - Quick Start Guide

Get up and running in 5 minutes.

## 1. Prerequisites

- Python 3.12+
- FFmpeg (`brew install ffmpeg` on macOS, `apt-get install ffmpeg` on Ubuntu)
- OpenAI API key (get at https://platform.openai.com/api-keys)
- Anthropic API key (get at https://console.anthropic.com)

## 2. Setup

### Clone & Install
```bash
git clone <repo-url>
cd plutoclips-worker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure
```bash
# Copy env template
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

## 3. Run Locally

```bash
# Start development server
uvicorn main:app --reload

# Server runs at http://localhost:8000
```

## 4. Try It Out

### Upload a video
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@my_video.mp4"
```

You'll get back:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded",
  "message": "Video uploaded successfully"
}
```

### Start processing
```bash
curl -X POST http://localhost:8000/api/v1/process-video \
  -H "Content-Type: application/json" \
  -d '{"job_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

### Check status (repeat until "completed")
```bash
curl http://localhost:8000/api/v1/job-status/550e8400-e29b-41d4-a716-446655440000
```

### Get results
```bash
curl http://localhost:8000/api/v1/clips/550e8400-e29b-41d4-a716-446655440000 | jq
```

### Download a clip
```bash
curl -O http://localhost:8000/api/v1/download/clip_01.mp4
```

## 5. Deploy to Railway

1. Push to GitHub
```bash
git push origin main
```

2. Go to https://railway.app/dashboard
   - New Project → Deploy from GitHub
   - Select your repo

3. Set environment variables in Railway:
   - `OPENAI_API_KEY=sk-...`
   - `ANTHROPIC_API_KEY=sk-ant-...`
   - `ENVIRONMENT=production`

4. Railway auto-deploys! 🚀

Your app is now live at: `https://your-app.railway.app`

## API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Docker (Optional)

```bash
# Build image
docker build -t plutoclips-worker .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  plutoclips-worker
```

## Troubleshooting

### FFmpeg not found?
```bash
# macOS
brew install ffmpeg

# Ubuntu
apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### API key errors?
- Check `.env` file exists in project root
- Verify keys are correct and have quota
- Restart server after changing `.env`

### Memory issues with large videos?
- Use shorter videos for testing
- Increase system RAM
- Reduce video bitrate: `VIDEO_BITRATE=1500k`

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [API endpoints](README.md#api-endpoints) for all available endpoints
- Explore [project structure](README.md#project-structure) to understand the codebase
- See [configuration options](README.md#configuration) for customization

## Help

- Check logs: `docker logs <container_id>`
- Review errors in Railway dashboard
- See detailed troubleshooting in README.md
