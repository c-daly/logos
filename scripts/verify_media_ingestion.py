#!/usr/bin/env python3
"""
Quick verification script for media ingestion service.

This script tests that the media ingestion service can be imported and
basic functionality works without requiring external services.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from logos_perception import (
            MediaIngestService,
            JEPARunner,
            JEPAConfig,
            SimulationRequest,
            create_media_api,
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_jepa_runner():
    """Test JEPA runner can be instantiated."""
    print("\nTesting JEPA runner...")
    try:
        from logos_perception import JEPARunner, JEPAConfig
        
        config = JEPAConfig(model_version="test-v1", embedding_dim=256)
        runner = JEPARunner(config)
        
        result = runner.simulate(
            capability_id="test-capability",
            context={"test": "context"},
            k_steps=3
        )
        
        assert result.process.capability_id == "test-capability"
        assert len(result.states) == 3
        assert result.states[0].confidence == 1.0
        
        print("✅ JEPA runner works")
        return True
    except Exception as e:
        print(f"❌ JEPA runner test failed: {e}")
        return False


def test_api_creation():
    """Test API can be created with mock driver."""
    print("\nTesting API creation...")
    try:
        from unittest.mock import Mock
        from logos_perception import create_media_api
        
        mock_driver = Mock()
        router = create_media_api(mock_driver, Path("/tmp/test_media"))
        
        # Check that router has expected endpoints
        routes = [route.path for route in router.routes]
        expected_paths = [
            "/media/health",
            "/media/upload",
            "/media/stream/start",
            "/media/stream/{stream_id}/stop",
            "/media/frames/{frame_id}"
        ]
        
        for path in expected_paths:
            if path not in routes:
                print(f"❌ Missing expected route: {path}")
                return False
        
        print(f"✅ API created with {len(routes)} routes")
        return True
    except Exception as e:
        print(f"❌ API creation failed: {e}")
        return False


def test_app_module():
    """Test that the standalone app module exists and has app object."""
    print("\nTesting app module...")
    try:
        from logos_perception.app import app
        
        # Check that app has expected attributes
        assert hasattr(app, 'title')
        assert "Media Ingestion" in app.title
        
        print(f"✅ App module exists: {app.title}")
        return True
    except Exception as e:
        print(f"❌ App module test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("="*60)
    print("Media Ingestion Service - Quick Verification")
    print("="*60)
    
    tests = [
        test_imports,
        test_jepa_runner,
        test_api_creation,
        test_app_module,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    if all(results):
        print("✅ All verification tests passed!")
        print("="*60)
        print("\nNext steps:")
        print("1. Start Neo4j: docker compose -f infra/docker-compose.hcg.dev.yml up -d neo4j")
        print("2. Run service: uvicorn logos_perception.app:app --port 8002")
        print("3. Test health: curl http://localhost:8002/health")
        print("4. View docs: http://localhost:8002/docs")
        return 0
    else:
        print("❌ Some tests failed")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
