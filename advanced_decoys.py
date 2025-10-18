"""
PhantomGuard Advanced Decoy Generator
Creates realistic, high-fidelity decoys for various attack scenarios.
"""
import os
import random
import time
import json
from pathlib import Path
from typing import Optional


class AdvancedDecoyGenerator:
    """Generates advanced, realistic decoys."""
    
    @staticmethod
    def create_aws_credentials(path: str = "/tmp/.aws/credentials") -> str:
        """Create fake AWS credentials file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1

[production]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
region = us-west-2
"""
        
        with open(p, 'w') as f:
            f.write(content)
        
        # Set realistic timestamps (1-30 days old)
        ts = time.time() - random.randint(86400, 86400 * 30)
        os.utime(p, (ts, ts))
        
        # Make it readable but not executable
        os.chmod(p, 0o600)
        
        return str(p)
    
    @staticmethod
    def create_database_config(path: str = "/tmp/.env") -> str:
        """Create fake database connection string."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""# Database Configuration
DB_HOST=prod-db-01.internal.company.com
DB_PORT=5432
DB_NAME=production_app
DB_USER=app_service
DB_PASSWORD=P@ssw0rd123!SecureDB
DB_SSL_MODE=require

# Redis Cache
REDIS_HOST=redis-cluster.internal.company.com
REDIS_PORT=6379
REDIS_PASSWORD=RedisP@ss2024!

# API Keys
STRIPE_SECRET_KEY=sk_live_51HxBkPHM3pQ4vXx4A8wKLMExample
SENDGRID_API_KEY=SG.xQxK7X8pRBqExample.k8wYExampleKey
JWT_SECRET=super-secret-jwt-key-do-not-share

# External Services
OPENAI_API_KEY=sk-proj-abcdef123456789Example
AWS_S3_BUCKET=company-production-backups
"""
        
        with open(p, 'w') as f:
            f.write(content)
        
        ts = time.time() - random.randint(3600, 86400 * 7)
        os.utime(p, (ts, ts))
        os.chmod(p, 0o640)
        
        return str(p)
    
    @staticmethod
    def create_ssh_private_key(path: str = "/tmp/.ssh/id_rsa") -> str:
        """Create fake SSH private key."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        # Realistic looking (but invalid) RSA private key
        content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEAzXk5hqGmBkZQ5vN8F4pL7TxJ9YrN1wP3vZ5Qc8J6kR0+fVx9Dp
Z4Y3mH7bK5E8gT6wV1pX9YhN2Qs8aW0eL7pD5Zm9rT6fE2Nt5qP7aH8kJ0+eX1qB7Yh
4zQ8+eN5pW9hT7kJ8+dV1nB0eR5yP2aK7gS6fJ9+cT1vN8pR0+bJ5wD4eW9zQ7+aL5h
EXAMPLEKEYDONOTUSEINPRODUCTIONTHISISAFAKEDECOY
-----END OPENSSH PRIVATE KEY-----
"""
        
        with open(p, 'w') as f:
            f.write(content)
        
        # SSH keys should be 600 perms
        os.chmod(p, 0o600)
        
        ts = time.time() - random.randint(86400 * 7, 86400 * 180)
        os.utime(p, (ts, ts))
        
        # Also create public key
        pub_path = str(p) + '.pub'
        pub_content = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDNeTmGoaYGRlDm83wXikvtPEn1is3XA/e9nlBzwnqRHT59XH0OlnhjeYftsrkTyBPrBXWlf1iE3ZCzxpbR4vukPlmb2tPp8TY23mo/tofyQnT55fWoHtiHjNDz543mlb2FPuQnz51XWcHR5HnI/ZoruBLp8n35xPW83ylHT5snnAPh5b3NDv5ovmFhZG1pbkBob3N0bmFtZQ== admin@production-server user@example.com"
        with open(pub_path, 'w') as f:
            f.write(pub_content)
        os.chmod(pub_path, 0o644)
        
        return str(p)
    
    @staticmethod
    def create_docker_config(path: str = "/tmp/.docker/config.json") -> str:
        """Create fake Docker registry credentials."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "auths": {
                "https://index.docker.io/v1/": {
                    "auth": "dXNlcm5hbWU6cGFzc3dvcmQxMjM="  # base64("username:password123")
                },
                "registry.company.com": {
                    "auth": "Y29tcGFueXVzZXI6Q29tcGFueVBAc3Mh"
                }
            },
            "credsStore": "desktop"
        }
        
        with open(p, 'w') as f:
            json.dump(config, f, indent=2)
        
        ts = time.time() - random.randint(86400, 86400 * 60)
        os.utime(p, (ts, ts))
        os.chmod(p, 0o600)
        
        return str(p)
    
    @staticmethod
    def create_git_credentials(path: str = "/tmp/.git-credentials") -> str:
        """Create fake Git credentials file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        content = """https://user:ghp_examplePersonalAccessToken1234@github.com
https://gitlab-user:glpat-exampleGitLabToken5678@gitlab.com
https://devops:pat_bitbucket_example9012@bitbucket.org
"""
        
        with open(p, 'w') as f:
            f.write(content)
        
        os.chmod(p, 0o600)
        ts = time.time() - random.randint(86400 * 14, 86400 * 90)
        os.utime(p, (ts, ts))
        
        return str(p)
    
    @staticmethod
    def create_api_tokens(path: str = "/tmp/.config/tokens.json") -> str:
        """Create fake API tokens file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        tokens = {
            "github_token": "ghp_ExamplePersonalAccessToken1234567890ABCDEF",
            "slack_webhook": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            "datadog_api_key": "abcdef0123456789abcdef0123456789",
            "pagerduty_token": "u+ExampleToken-ABCD1234",
            "twilio_auth_token": "1234567890abcdef1234567890abcdef",
            "created_at": "2024-01-15T10:30:00Z",
            "last_rotated": "2024-08-20T14:22:00Z"
        }
        
        with open(p, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        os.chmod(p, 0o600)
        ts = time.time() - random.randint(86400 * 30, 86400 * 120)
        os.utime(p, (ts, ts))
        
        return str(p)
    
    @staticmethod
    def create_backup_sql(path: str = "/tmp/backups/db_backup.sql") -> str:
        """Create fake database backup file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        # Realistic SQL dump header
        content = """-- MySQL dump 10.13  Distrib 8.0.33, for Linux (x86_64)
--
-- Host: prod-db-01.internal    Database: production_app
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8mb4 */;

-- Table structure for table `users`
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Partial data dump (decoy)
INSERT INTO `users` VALUES (1,'admin','admin@company.com','$2b$12$ExampleHashDoNotUseInProduction','2024-01-01 00:00:00');

-- End of dump
"""
        
        with open(p, 'w') as f:
            f.write(content)
        
        ts = time.time() - random.randint(3600, 86400 * 7)  # Recent backup
        os.utime(p, (ts, ts))
        os.chmod(p, 0o640)
        
        return str(p)
    
    @staticmethod
    def create_certificate(path: str = "/tmp/certs/server.key") -> str:
        """Create fake SSL/TLS private key."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        content = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8xKzQGuQJFH7m
ExamplePrivateKeyDataDoNotUseInProductionThisIsADecoy
ExampleDataExampleDataExampleDataExampleDataExampleData
-----END PRIVATE KEY-----
"""
        
        with open(p, 'w') as f:
            f.write(content)
        
        os.chmod(p, 0o600)
        ts = time.time() - random.randint(86400 * 30, 86400 * 365)
        os.utime(p, (ts, ts))
        
        return str(p)
    
    @staticmethod
    def create_npm_authtoken(path: str = "/tmp/.npmrc") -> str:
        """Create fake NPM authentication token."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        content = """//registry.npmjs.org/:_authToken=npm_ExampleTokenABCD1234567890
registry=https://registry.npmjs.org/
@company:registry=https://npm.company.com/
//npm.company.com/:_authToken=CompanyNpmTokenExample123
"""
        
        with open(p, 'w') as f:
            f.write(content)
        
        os.chmod(p, 0o644)
        ts = time.time() - random.randint(86400 * 7, 86400 * 60)
        os.utime(p, (ts, ts))
        
        return str(p)


def generate_all_advanced_decoys(base_dir: str = "/tmp/phantomguard-decoys"):
    """Generate all advanced decoy types."""
    print("🎭 Generating advanced decoys...\n")
    
    generator = AdvancedDecoyGenerator()
    decoys_created = []
    
    decoy_functions = [
        ("AWS Credentials", lambda: generator.create_aws_credentials(f"{base_dir}/.aws/credentials")),
        ("Database Config", lambda: generator.create_database_config(f"{base_dir}/.env")),
        ("SSH Private Key", lambda: generator.create_ssh_private_key(f"{base_dir}/.ssh/id_rsa")),
        ("Docker Config", lambda: generator.create_docker_config(f"{base_dir}/.docker/config.json")),
        ("Git Credentials", lambda: generator.create_git_credentials(f"{base_dir}/.git-credentials")),
        ("API Tokens", lambda: generator.create_api_tokens(f"{base_dir}/.config/tokens.json")),
        ("SQL Backup", lambda: generator.create_backup_sql(f"{base_dir}/backups/db_backup.sql")),
        ("SSL Certificate", lambda: generator.create_certificate(f"{base_dir}/certs/server.key")),
        ("NPM Auth Token", lambda: generator.create_npm_authtoken(f"{base_dir}/.npmrc")),
    ]
    
    for name, func in decoy_functions:
        try:
            path = func()
            print(f"✅ {name:20} -> {path}")
            decoys_created.append(path)
        except Exception as e:
            print(f"❌ {name:20} -> Failed: {e}")
    
    print(f"\n✨ Created {len(decoys_created)} advanced decoys")
    return decoys_created


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate advanced PhantomGuard decoys")
    parser.add_argument('--dir', default='/tmp/phantomguard-decoys',
                       help='Base directory for decoys')
    args = parser.parse_args()
    
    generate_all_advanced_decoys(args.dir)
