"""
PhantomGuard Configuration Validator
Validates config.json and provides helpful error messages.
"""
from pathlib import Path
from typing import List, Dict, Any
import re


class ConfigValidator:
    """Validates PhantomGuard configuration files."""
    
    @staticmethod
    def validate(config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration and return list of errors.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check required top-level keys
        required_keys = ['watcher', 'scorer', 'telegram', 'blocker']
        for key in required_keys:
            if key not in config:
                errors.append(f"❌ Missing required section: '{key}'")
        
        # Validate watcher configuration
        if 'watcher' in config:
            watcher_errors = ConfigValidator._validate_watcher(config['watcher'])
            errors.extend(watcher_errors)
        
        # Validate scorer configuration
        if 'scorer' in config:
            scorer_errors = ConfigValidator._validate_scorer(config['scorer'])
            errors.extend(scorer_errors)
        
        # Validate Telegram configuration
        if 'telegram' in config:
            telegram_errors = ConfigValidator._validate_telegram(config['telegram'])
            errors.extend(telegram_errors)
        
        # Validate blocker configuration
        if 'blocker' in config:
            blocker_errors = ConfigValidator._validate_blocker(config['blocker'])
            errors.extend(blocker_errors)
        
        return errors
    
    @staticmethod
    def _validate_watcher(watcher: Dict[str, Any]) -> List[str]:
        """Validate watcher configuration."""
        errors = []
        
        if 'paths' not in watcher:
            errors.append("❌ watcher.paths is required")
            return errors
        
        paths = watcher['paths']
        if not isinstance(paths, list) or len(paths) == 0:
            errors.append("❌ watcher.paths must be a non-empty list")
            return errors
        
        # Check if paths exist or can be created
        for path in paths:
            p = Path(path)
            parent = p.parent if not p.exists() else p
            
            if not parent.exists():
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                    print(f"✓ Created directory: {parent}")
                except PermissionError:
                    errors.append(f"❌ Cannot create directory: {parent} (permission denied)")
                except Exception as e:
                    errors.append(f"❌ Cannot create directory: {parent} ({e})")
        
        return errors
    
    @staticmethod
    def _validate_scorer(scorer: Dict[str, Any]) -> List[str]:
        """Validate scorer configuration."""
        errors = []
        
        if 'threshold' not in scorer:
            errors.append("⚠️  scorer.threshold not set (will use default)")
        elif not isinstance(scorer['threshold'], int):
            errors.append("❌ scorer.threshold must be an integer")
        elif scorer['threshold'] < 0 or scorer['threshold'] > 200:
            errors.append("⚠️  scorer.threshold should be between 0 and 200")
        
        if 'rules' not in scorer:
            errors.append("❌ scorer.rules is required")
            return errors
        
        rules = scorer['rules']
        if not isinstance(rules, list) or len(rules) == 0:
            errors.append("❌ scorer.rules must be a non-empty list")
            return errors
        
        # Validate each rule
        for i, rule in enumerate(rules):
            if 'name' not in rule:
                errors.append(f"❌ scorer.rules[{i}] missing 'name'")
            if 'weight' not in rule:
                errors.append(f"❌ scorer.rules[{i}] missing 'weight'")
            elif not isinstance(rule['weight'], int):
                errors.append(f"❌ scorer.rules[{i}].weight must be an integer")
            if 'pattern' not in rule:
                errors.append(f"❌ scorer.rules[{i}] missing 'pattern'")
            else:
                # Validate regex pattern
                try:
                    re.compile(rule['pattern'])
                except re.error as e:
                    errors.append(f"❌ scorer.rules[{i}].pattern is invalid regex: {e}")
        
        return errors
    
    @staticmethod
    def _validate_telegram(telegram: Dict[str, Any]) -> List[str]:
        """Validate Telegram configuration."""
        errors = []
        
        if 'bot_token' not in telegram:
            errors.append("❌ telegram.bot_token is required")
        elif telegram['bot_token'] in ['YOUR_TELEGRAM_BOT_TOKEN', '', None]:
            errors.append("❌ telegram.bot_token not configured (get from @BotFather)")
        elif not telegram['bot_token'].count(':') == 1:
            errors.append("⚠️  telegram.bot_token format looks invalid (should be 'NUMBER:STRING')")
        
        if 'chat_id' not in telegram:
            errors.append("❌ telegram.chat_id is required")
        elif telegram['chat_id'] in ['YOUR_TELEGRAM_CHAT_ID', '', None]:
            errors.append("❌ telegram.chat_id not configured (get from @userinfobot)")
        
        if 'hmac_key' not in telegram:
            errors.append("❌ telegram.hmac_key is required")
        elif len(telegram['hmac_key']) < 32:
            errors.append("❌ telegram.hmac_key must be at least 32 characters for security")
        elif telegram['hmac_key'] in ['a-very-secret-hmac-key-change-me', 'change-this-to-a-secret-key-min-32-chars']:
            errors.append("❌ telegram.hmac_key must be changed from default value")
        
        return errors
    
    @staticmethod
    def _validate_blocker(blocker: Dict[str, Any]) -> List[str]:
        """Validate blocker configuration."""
        errors = []
        
        if 'dry_run' not in blocker:
            errors.append("⚠️  blocker.dry_run not set (will use default: true)")
        elif not isinstance(blocker['dry_run'], bool):
            errors.append("❌ blocker.dry_run must be a boolean (true/false)")
        elif blocker['dry_run'] is False:
            errors.append("⚠️  blocker.dry_run is disabled - REAL IP BLOCKING IS ACTIVE!")
        
        return errors
    
    @staticmethod
    def validate_and_print(config: Dict[str, Any]) -> bool:
        """
        Validate config and print results. Returns True if valid.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if configuration is valid, False otherwise
        """
        errors = ConfigValidator.validate(config)
        
        if not errors:
            print("✅ Configuration is valid!")
            return True
        
        print("❌ Configuration validation failed:\n")
        for error in errors:
            print(f"  {error}")
        
        print("\n💡 Fix these issues in config.json before starting PhantomGuard.")
        return False
