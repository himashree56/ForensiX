"""
Test script for the Deepfake Detection API
"""
import requests
import sys
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed!")
            print(f"   Status: {data['status']}")
            print(f"   Model loaded: {data['model_loaded']}")
            print(f"   Device: {data['device']}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print("   Make sure the backend server is running on port 8000")
        return False

def test_upload(video_path: str, fps: int = 5):
    """Test video upload endpoint"""
    print(f"\n🔍 Testing video upload...")
    print(f"   Video: {video_path}")
    print(f"   FPS: {fps}")
    
    if not Path(video_path).exists():
        print(f"❌ Video file not found: {video_path}")
        return False
    
    try:
        with open(video_path, 'rb') as f:
            files = {'file': f}
            data = {'fps': fps}
            
            print("   Uploading and analyzing...")
            response = requests.post(
                f"{API_URL}/upload-video",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis complete!")
            print(f"\n📊 Results:")
            print(f"   Prediction: {result['prediction']}")
            print(f"   Confidence: {result['confidence']:.2%}")
            print(f"   Mean Score: {result['mean_score']:.4f}")
            print(f"   Total Frames: {result['total_frames']}")
            print(f"   Fake Frames: {result['fake_frames']}")
            print(f"   Real Frames: {result['real_frames']}")
            print(f"   Uncertain Frames: {result['uncertain_frames']}")
            
            # Show first few frame predictions
            print(f"\n🎞️  First 5 Frame Predictions:")
            for frame in result['frame_predictions'][:5]:
                print(f"   Frame {frame['frame_number']}: {frame['prediction']} (score: {frame['score']:.4f})")
            
            return True
        else:
            error = response.json()
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"   Error: {error.get('detail', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Deepfake Detection API Test Suite")
    print("=" * 60)
    
    # Test health endpoint
    if not test_health():
        print("\n❌ Health check failed. Exiting...")
        sys.exit(1)
    
    # Test upload if video path provided
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        fps = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        
        if not test_upload(video_path, fps):
            print("\n❌ Upload test failed.")
            sys.exit(1)
    else:
        print("\n💡 To test video upload, run:")
        print("   python test_api.py <path_to_video.mp4> [fps]")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
