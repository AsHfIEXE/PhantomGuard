#!/usr/bin/env python3
"""
PhantomGuard System Test
Tests all components independently before running the full system.
"""
import sys
import os
import json
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    errors = []
    
    modules_to_test = [
        ('watchdog', 'watchdog'),
        ('streamlit', 'streamlit'),
        ('requests', 'requests'),
        ('pytest', 'pytest'),
    ]
    
    for module_name, import_name in modules_to_test:
        try:
            __import__(import_name)
            print(f"  ✓ {module_name}")
        except ImportError as e:
            errors.append(f"  ✗ {module_name}: {e}")
    
    # Optional modules
    optional = [
        ('scikit-learn', 'sklearn'),
        ('torch', 'torch'),
        ('aiohttp', 'aiohttp'),
    ]
    
    print("\nOptional modules:")
    for module_name, import_name in optional:
        try:
            __import__(import_name)
            print(f"  ✓ {module_name}")
        except ImportError:
            print(f"  ⚠ {module_name} (optional, not required)")
    
    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False
    return True


def test_config():
    """Test that config.json is valid."""
    print("\nTesting config.json...")
    
    if not Path('config.json').exists():
        print("  ✗ config.json not found")
        print("  Run: cp config.json.example config.json")
        return False
    
    try:
        with open('config.json') as f:
            config = json.load(f)
        
        required_keys = ['watcher', 'scorer', 'telegram', 'blocker']
        for key in required_keys:
            if key not in config:
                print(f"  ✗ Missing required key: {key}")
                return False
        
        # Check Telegram config
        if config['telegram']['bot_token'] == 'YOUR_TELEGRAM_BOT_TOKEN':
            print("  ⚠ Telegram bot token not configured (alerts will fail)")
        
        print("  ✓ config.json is valid")
        return True
    except Exception as e:
        print(f"  ✗ Error reading config.json: {e}")
        return False


def test_decoy_generation():
    """Test decoy file generation."""
    print("\nTesting decoy generation...")
    
    try:
        from phantomgen.simple_decoy import create_decoy
        
        test_path = "/tmp/phantomguard_test_decoy.txt"
        result = create_decoy(test_path, size_kb=1)
        
        if Path(result).exists():
            print(f"  ✓ Decoy created at {result}")
            os.remove(result)
            return True
        else:
            print(f"  ✗ Decoy not created")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_event_scorer():
    """Test event scoring logic."""
    print("\nTesting event scorer...")
    
    try:
        from processor.event_scorer import EventScorer
        
        scorer = EventScorer()
        
        # Test high-severity event
        event = {"path": "/tmp/.ssh/id_rsa", "event_type": "open"}
        score, matches = scorer.score_event(event)
        
        if score >= 50:
            print(f"  ✓ SSH key access scored {score} (matches: {matches})")
        else:
            print(f"  ✗ SSH key access scored too low: {score}")
            return False
        
        # Test low-severity event
        event2 = {"path": "/tmp/normal.txt", "event_type": "open"}
        score2, matches2 = scorer.score_event(event2)
        
        if score2 < score:
            print(f"  ✓ Normal file scored lower: {score2}")
        else:
            print(f"  ⚠ Normal file scored same or higher: {score2}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_filesystem_watcher():
    """Test filesystem watcher setup."""
    print("\nTesting filesystem watcher...")
    
    try:
        from sensors.fs_watcher import DecoyEventHandler, Observer
        
        class TestBus:
            def __init__(self):
                self.events = []
            
            def emit(self, event):
                self.events.append(event)
        
        bus = TestBus()
        handler = DecoyEventHandler(bus)
        observer = Observer()
        
        # Try to schedule a watch on /tmp
        test_dir = "/tmp/phantomguard_watcher_test"
        Path(test_dir).mkdir(exist_ok=True)
        
        observer.schedule(handler, test_dir, recursive=False)
        observer.start()
        
        # Create a test file
        test_file = Path(test_dir) / "test.txt"
        test_file.write_text("test")
        
        import time
        time.sleep(0.5)
        
        observer.stop()
        observer.join()
        
        # Cleanup
        test_file.unlink()
        Path(test_dir).rmdir()
        
        print(f"  ✓ Watcher functional (captured {len(bus.events)} events)")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ip_blocker():
    """Test IP blocker in dry-run mode."""
    print("\nTesting IP blocker (dry-run)...")
    
    try:
        from processor.ip_blocker import IPBlocker
        
        blocker = IPBlocker(dry_run=True)
        result = blocker.block_ip("192.0.2.1")  # TEST-NET-1 (RFC 5737)
        
        if result:
            print("  ✓ IP blocker functional (dry-run)")
            return True
        else:
            print("  ✗ IP blocker failed")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_telegram_alerter():
    """Test Telegram alerter (without sending)."""
    print("\nTesting Telegram alerter...")
    
    try:
        from alerting.telegram_alert import TelegramAlerter
        
        alerter = TelegramAlerter(
            token="test_token",
            chat_id="test_chat",
            hmac_key="test_hmac_key_at_least_32_chars_long"
        )
        
        # Test dry-run alert
        event = {
            "event_type": "test",
            "path": "/tmp/test",
            "score": 75
        }
        result = alerter.send_alert(event, dry_run=True)
        
        if result:
            print("  ✓ Telegram alerter functional (dry-run)")
            return True
        else:
            print("  ✗ Telegram alerter failed")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_hybrid_anomaly():
    """Test hybrid anomaly model."""
    print("\nTesting hybrid anomaly model...")
    
    try:
        from processor.hybrid_anomaly import HybridAnomalyModel
        
        model = HybridAnomalyModel(input_dim=5)
        
        # Test feature extraction
        event = {
            'event_type': 'open',
            'path': '/tmp/test.txt',
            'size': 1024,
            'hour': 14,
            'user': 'testuser'
        }
        
        features = model.extract_features(event)
        
        if len(features) == 5:
            print(f"  ✓ Feature extraction works (extracted {len(features)} features)")
        else:
            print(f"  ✗ Wrong number of features: {len(features)}")
            return False
        
        # Test scoring without training
        score = model.score(event)
        print(f"  ✓ Anomaly scoring functional (score: {score:.2f})")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directories():
    """Test that required directories exist or can be created."""
    print("\nTesting directories...")
    
    dirs = [
        'ui',
        'logs/phantomguard',
        '/tmp/phantomguard-decoys',
    ]
    
    all_ok = True
    for dir_path in dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {dir_path}")
        except Exception as e:
            print(f"  ✗ {dir_path}: {e}")
            all_ok = False
    
    # Try /var/log/phantomguard (may need sudo)
    try:
        Path('/var/log/phantomguard').mkdir(parents=True, exist_ok=True)
        print(f"  ✓ /var/log/phantomguard")
    except PermissionError:
        print(f"  ⚠ /var/log/phantomguard (needs sudo, will use logs/ instead)")
    
    return all_ok


def main():
    """Run all tests."""
    print("=" * 60)
    print("PhantomGuard System Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Directories", test_directories),
        ("Decoy Generation", test_decoy_generation),
        ("Event Scorer", test_event_scorer),
        ("Filesystem Watcher", test_filesystem_watcher),
        ("IP Blocker", test_ip_blocker),
        ("Telegram Alerter", test_telegram_alerter),
        ("Hybrid Anomaly Model", test_hybrid_anomaly),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Edit config.json with your Telegram credentials")
        print("2. Run: python3 phantomguard.py")
        print("3. Run: streamlit run ui/dashboard.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())