"""
Test suite for PlutoClips Worker.

Run with: pytest tests/ -v
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Import application
from main import app
from app.core.config import settings
from app.core.exceptions import ValidationError, VideoProcessingError


client = TestClient(app)


class TestHealthCheck:
    """Health check endpoint tests."""
    
    def test_health_check_returns_ok(self):
        """Health check should return ok status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestUploadEndpoint:
    """Video upload endpoint tests."""
    
    def test_upload_missing_file(self):
        """Upload should fail without file."""
        response = client.post("/api/v1/upload")
        assert response.status_code == 422
    
    def test_upload_invalid_file_type(self):
        """Upload should reject non-video files."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", b"test content", "text/plain")}
        )
        assert response.status_code == 400
        assert "not supported" in response.json()["detail"].lower()
    
    def test_upload_valid_video_file(self):
        """Upload should accept valid video files."""
        # Create a minimal MP4 file (just for testing purposes)
        with patch('app.services.video.VideoProcessingService.create_job') as mock_job:
            mock_job.return_value = "test-job-id"
            
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test.mp4", b"test video data", "video/mp4")}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == "test-job-id"
            assert data["status"] == "uploaded"


class TestProcessingEndpoint:
    """Video processing endpoint tests."""
    
    def test_process_video_starts_background_task(self):
        """Process video should start background task."""
        with patch('app.services.video.VideoProcessingService.get_job_status') as mock_status:
            mock_status.return_value = {"status": "uploaded"}
            
            response = client.post(
                "/api/v1/process-video",
                json={"job_id": "test-job-id"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == "test-job-id"
            assert data["status"] == "processing"


class TestJobStatusEndpoint:
    """Job status endpoint tests."""
    
    def test_get_job_status_success(self):
        """Get job status should return job details."""
        with patch('app.services.video.VideoProcessingService.get_job_status') as mock_status:
            mock_status.return_value = {
                "id": "test-job-id",
                "status": "processing",
                "progress": 50,
                "error": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:35:00Z"
            }
            
            response = client.get("/api/v1/job-status/test-job-id")
            
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == "test-job-id"
            assert data["status"] == "processing"
            assert data["progress"] == 50
    
    def test_get_job_status_not_found(self):
        """Get job status should return 404 for missing job."""
        with patch('app.services.video.VideoProcessingService.get_job_status') as mock_status:
            mock_status.side_effect = Exception("Job not found")
            
            response = client.get("/api/v1/job-status/nonexistent-job")
            
            assert response.status_code == 404


class TestClipsEndpoint:
    """Get clips endpoint tests."""
    
    def test_get_clips_success(self):
        """Get clips should return generated clips."""
        with patch('app.services.video.VideoProcessingService.get_clips') as mock_clips:
            mock_clips.return_value = {
                "job_id": "test-job-id",
                "status": "completed",
                "total_clips": 1,
                "clips": [
                    {
                        "clip_id": "clip_001",
                        "title": "Test Clip",
                        "url": "/api/v1/download/clip_001.mp4",
                        "duration": 60.0,
                        "moment_type": "viral",
                        "reason": "Test reason"
                    }
                ],
                "video_duration": 600.0
            }
            
            response = client.get("/api/v1/clips/test-job-id")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_clips"] == 1
            assert len(data["clips"]) == 1


class TestDownloadEndpoint:
    """Download file endpoint tests."""
    
    def test_download_file_not_found(self):
        """Download should return 404 for missing file."""
        response = client.get("/api/v1/download/nonexistent/file.mp4")
        assert response.status_code == 404
    
    def test_download_path_traversal_protection(self):
        """Download should prevent path traversal attacks."""
        response = client.get("/api/v1/download/../../etc/passwd")
        assert response.status_code in [403, 404]


class TestFFmpegUtils:
    """FFmpeg utility functions tests."""
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        from app.utils.captions import format_timestamp, parse_timestamp
        
        timestamp = format_timestamp(125.5)
        assert timestamp == "00:02:05,500"
        
        # Round trip test
        seconds = parse_timestamp(timestamp)
        assert abs(seconds - 125.5) < 0.01
    
    def test_clean_text_removes_fillers(self):
        """Test filler word removal."""
        from app.utils.captions import clean_text
        
        text = "Um, like, you know, this is a test, basically."
        cleaned = clean_text(text, remove_fillers=True)
        
        assert "um" not in cleaned.lower()
        assert "like" not in cleaned.lower()
        assert "you know" not in cleaned.lower()
        assert "basically" not in cleaned.lower()


class TestExceptionHandling:
    """Exception handling tests."""
    
    def test_validation_error_status_code(self):
        """ValidationError should return 400."""
        from app.core.exceptions import ValidationError
        
        error = ValidationError("Test error")
        assert error.status_code == 400
    
    def test_video_processing_error_status_code(self):
        """VideoProcessingError should return 422."""
        from app.core.exceptions import VideoProcessingError
        
        error = VideoProcessingError("Test error")
        assert error.status_code == 422


class TestDatabaseOperations:
    """Database repository tests."""
    
    @pytest.mark.skip(reason="Requires SQLite setup")
    def test_create_job_record(self):
        """Test job creation in database."""
        from app.database.sqlite import JobRepository
        
        repo = JobRepository()
        repo.create_job(
            job_id="test-123",
            original_filename="test.mp4",
            file_path="/uploads/test.mp4"
        )
        
        job = repo.get_job("test-123")
        assert job is not None
        assert job["original_filename"] == "test.mp4"


class TestIntegration:
    """Integration tests."""
    
    def test_api_documentation_available(self):
        """API documentation endpoints should be available."""
        # Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema(self):
        """OpenAPI schema should be available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "paths" in schema
        assert "/api/v1/upload" in schema["paths"]


# Run tests with: pytest tests/test_main.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
