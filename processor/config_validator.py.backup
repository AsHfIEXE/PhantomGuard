"""
PhantomGuard Configuration Validator
Validates configuration files with detailed error reporting.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


class ConfigValidator:
    """Validates PhantomGuard configuration with detailed error reporting."""
    
    @staticmethod
    def validate_and_print(config: Dict[str, Any]) -> bool:
        """
        Validate configuration and print results.
        Returns True if valid, False otherwise.
        """
        valid = True
        errors: List[str] = []
        warnings: List[str] = []
        
        def add_error(msg: str):
            nonlocal valid
            valid = False
            errors.append(msg)
            
        def add_warning(msg: str):
            warnings.append(msg)
        
        # Required sections
        required_sections = ['watcher', 'scorer', 'telegram', 'blocker']
        for section in required_sections:
            if section not in config:
                add_error(f"Missing required section: {section}")
                continue
        
        # Watcher config
        if 'watcher' in config:
            w = config['watcher']
            if not isinstance(w.get('paths', []), list):
                add_error("watcher.paths must be a list")
            else:
                for path in w.get('paths', []):
                    parent = Path(path).parent
                    if not parent.exists():
                        add_warning(f"Watch path parent does not exist: {parent}")
        
        # Scorer config
        if 'scorer' in config:
            s = config['scorer']
            if 'threshold' not in s:
                add_error("scorer.threshold is required")
            elif not isinstance(s['threshold'], (int, float)):
                add_error("scorer.threshold must be a number")
            elif s['threshold'] < 0 or s['threshold'] > 100:
                add_error("scorer.threshold must be between 0 and 100")
                
            if 'rules' not in s:
                add_error("scorer.rules is required")
            elif not isinstance(s['rules'], list):
                add_error("scorer.rules must be a list")
            else:
                for i, rule in enumerate(s['rules']):
                    if not isinstance(rule, dict):
                        add_error(f"Rule {i} must be an object")
                        continue
                    for field in ['name', 'weight', 'pattern']:
                        if field not in rule:
                            add_error(f"Rule {i} missing required field: {field}")
        
        # Telegram config
        if 'telegram' in config:
            t = config['telegram']
            for field in ['bot_token', 'chat_id', 'hmac_key']:
                if field not in t:
                    add_error(f"telegram.{field} is required")
                elif not t[field] or t[field] in ['YOUR_TOKEN', 'YOUR_CHAT_ID']:
                    add_warning(f"telegram.{field} appears to be a placeholder")
            
            if 'hmac_key' in t and len(t['hmac_key']) < 32:
                add_error("telegram.hmac_key must be at least 32 characters")
        
        # Blocker config
        if 'blocker' in config:
            b = config['blocker']
            if 'enabled' not in b:
                add_error("blocker.enabled is required")
            if 'dry_run' not in b:
                add_error("blocker.dry_run is required")
            if not b.get('dry_run', True):
                add_warning("⚠️ IP blocker is in ACTIVE mode (not dry-run)")
            if 'whitelist' in b and not isinstance(b['whitelist'], list):
                add_error("blocker.whitelist must be a list")
        
        # Print results
        if errors:
            print("\n❌ Configuration Errors:")
            for error in errors:
                print(f"  • {error}")
        
        if warnings:
            print("\n⚠️ Configuration Warnings:")
            for warning in warnings:
                print(f"  • {warning}")
        
        if valid:
            print("\n✅ Configuration validation passed")
        
        return valid