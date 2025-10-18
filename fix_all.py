#!/usr/bin/env python3
"""
PhantomGuard Auto-Fix Script
Automatically fixes all known issues in the codebase.
Run this before using PhantomGuard.
"""
import os
import shutil
from pathlib import Path


def create_missing_init_files():
    """Create missing __init__.py files."""
    print("📁 Creating missing __init__.py files...")
    
    init_files = [
        'phantomgen/__init__.py',
        'api/__init__.py',
    ]
    
    for init_file in init_files:
        path = Path(init_file)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# Package init file\n')
            print(f"  ✓ Created {init_file}")
        else:
            print(f"  ✓ {init_file} already exists")


def move_advanced_decoys():
    """Move advanced_decoys.py to correct location."""
    print("\n📦 Moving files to correct locations...")
    
    source = Path('advanced_decoys.py')
    dest = Path('phantomgen/advanced_decoys.py')
    
    if source.exists() and not dest.exists():
        shutil.move(str(source), str(dest))
        print(f"  ✓ Moved advanced_decoys.py to phantomgen/")
    elif dest.exists():
        print(f"  ✓ phantomgen/advanced_decoys.py already in place")
        if source.exists():
            source.unlink()
            print(f"  ✓ Removed duplicate advanced_decoys.py from root")
    else:
        print(f"  ⚠️  advanced_decoys.py not found")


def move_config_validator():
    """Move config_validator.py to correct location."""
    source = Path('config_validator.py')
    dest = Path('processor/config_validator.py')
    
    if source.exists():
        if dest.exists():
            # Backup existing
            backup = Path('processor/config_validator.py.backup')
            shutil.copy(str(dest), str(backup))
            print(f"  ✓ Backed up existing config_validator.py")
        
        shutil.copy(str(source), str(dest))
        source.unlink()
        print(f"  ✓ Moved config_validator.py to processor/")
    else:
        print(f"  ✓ config_validator.py already in place")


def fix_gitignore():
    """Fix .gitignore to be more comprehensive."""
    print("\n🔒 Updating .gitignore...")
    
    gitignore_content = """# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
.venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log
/var/log/phantomguard/

# Config (sensitive)
config.json

# OS
.DS_Store
Thumbs.db

# PhantomGuard specific
/processor/__pycache__/
ui/fp_state.json
ui/labels.jsonl
"""
    
    Path('.gitignore').write_text(gitignore_content)
    print("  ✓ Updated .gitignore")


def create_directories():
    """Create all necessary directories."""
    print("\n📂 Creating necessary directories...")
    
    directories = [
        'logs/phantomguard',
        'ui',
        '/tmp/.ssh',
        '/tmp/phantomguard-decoys',
        '/tmp/.aws',
        '/tmp/.config',
        '/tmp/.decoy-home/user/.config',
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created {directory}")
        except PermissionError:
            print(f"  ⚠️  Cannot create {directory} (permission denied)")


def validate_structure():
    """Validate that all required files exist."""
    print("\n🔍 Validating project structure...")
    
    required_files = [
        'phantomguard.py',
        'start.py',
        'config.json.example',
        'requirements.txt',
        'phantomgen/decoy_engine.py',
        'sensors/fs_watcher.py',
        'sensors/http_honeypot.py',
        'sensors/ssh_banner.py',
        'processor/event_scorer.py',
        'processor/config_validator.py',
        'alerting/telegram_alert.py',
        'ui/dashboard.py',
    ]
    
    all_good = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} MISSING!")
            all_good = False
    
    return all_good


def main():
    """Main execution."""
    print("=" * 60)
    print("PhantomGuard Auto-Fix Script")
    print("=" * 60 + "\n")
    
    # Run fixes
    create_missing_init_files()
    move_advanced_decoys()
    move_config_validator()
    fix_gitignore()
    create_directories()
    
    # Validate
    print()
    if validate_structure():
        print("\n" + "=" * 60)
        print("✅ All fixes applied successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Edit config.json (cp config.json.example config.json)")
        print("2. Run: python start.py")
    else:
        print("\n" + "=" * 60)
        print("⚠️  Some files are missing!")
        print("=" * 60)
        print("\nPlease ensure all required files are present.")


if __name__ == "__main__":
    main()
