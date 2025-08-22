#!/usr/bin/env python3
"""
🔐 RuleIQ Secrets Vault Setup Script
Easily identifiable AWS Secrets Manager setup for production deployment
"""
import os
import json
import secrets
import string
import boto3
from typing import Dict, Any
from botocore.exceptions import ClientError

class SecretsVaultSetup:
    """🔐 Setup AWS Secrets Manager for RuleIQ Production"""
    
    def __init__(self, region_name: str = "us-east-1", secret_name: str = "ruleiq-production-secrets"):
        self.region_name = region_name
        self.secret_name = secret_name
        self.client = boto3.client('secretsmanager', region_name=region_name)
        print(f"🔐 Initializing Secrets Vault Setup for '{secret_name}' in {region_name}")
    
    def generate_secure_key(self, length: int = 32) -> str:
        """Generate cryptographically secure key"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_jwt_secret(self) -> str:
        """Generate secure JWT secret (base64 encoded)"""
        import base64
        random_bytes = secrets.token_bytes(32)
        return base64.b64encode(random_bytes).decode('utf-8')
    
    def generate_fernet_key(self) -> str:
        """Generate Fernet encryption key"""
        from cryptography.fernet import Fernet
        return Fernet.generate_key().decode('utf-8')
    
    def create_production_secrets(self) -> Dict[str, str]:
        """
        🔐 Generate all production secrets for RuleIQ
        IMPORTANT: Review and update these values for actual production use
        """
        print("🔐 Generating secure production secrets...")
        
        secrets_data = {
            # Database - REPLACE WITH ACTUAL PRODUCTION VALUES
            "database_url": "postgresql+asyncpg://prod_user:CHANGE_ME@prod-db.ruleiq.com:5432/ruleiq_prod?sslmode=require",
            "test_database_url": "postgresql+asyncpg://test_user:CHANGE_ME@test-db.ruleiq.com:5432/ruleiq_test?sslmode=require",
            
            # Redis - REPLACE WITH ACTUAL PRODUCTION VALUES
            "redis_url": "redis://prod-redis.ruleiq.com:6379/0",
            "cache_redis_url": "redis://prod-redis.ruleiq.com:6379/1", 
            "session_redis_url": "redis://prod-redis.ruleiq.com:6379/2",
            
            # Security Keys - Auto-generated, secure
            "jwt_secret": self.generate_jwt_secret(),
            "secret_key": self.generate_secure_key(64),
            "encryption_key": self.generate_secure_key(32),
            "fernet_key": self.generate_fernet_key(),
            "credential_master_key": self.generate_secure_key(32),
            
            # Stack Auth - REPLACE WITH ACTUAL PRODUCTION VALUES
            "stack_project_id": "REPLACE_WITH_ACTUAL_STACK_PROJECT_ID",
            "stack_client_key": "REPLACE_WITH_ACTUAL_STACK_CLIENT_KEY",
            "stack_server_key": "REPLACE_WITH_ACTUAL_STACK_SERVER_KEY",
            
            # OAuth Credentials - REPLACE WITH ACTUAL PRODUCTION VALUES
            "google_client_id": "REPLACE_WITH_ACTUAL_GOOGLE_CLIENT_ID",
            "google_client_secret": "REPLACE_WITH_ACTUAL_GOOGLE_CLIENT_SECRET",
            "microsoft_client_id": "REPLACE_WITH_ACTUAL_MICROSOFT_CLIENT_ID",
            "microsoft_client_secret": "REPLACE_WITH_ACTUAL_MICROSOFT_CLIENT_SECRET",
            "okta_client_id": "REPLACE_WITH_ACTUAL_OKTA_CLIENT_ID",
            "okta_client_secret": "REPLACE_WITH_ACTUAL_OKTA_CLIENT_SECRET",
            
            # AI Service API Keys - REPLACE WITH ACTUAL PRODUCTION VALUES
            "openai_api_key": "REPLACE_WITH_ACTUAL_OPENAI_KEY",
            "anthropic_api_key": "REPLACE_WITH_ACTUAL_ANTHROPIC_KEY",
            "google_ai_api_key": "REPLACE_WITH_ACTUAL_GOOGLE_AI_KEY",
            "mistral_api_key": "REPLACE_WITH_ACTUAL_MISTRAL_KEY",
            
            # Email/SMTP - REPLACE WITH ACTUAL PRODUCTION VALUES
            "smtp_host": "smtp.ruleiq.com",
            "smtp_username": "noreply@ruleiq.com",
            "smtp_password": "REPLACE_WITH_ACTUAL_SMTP_PASSWORD",
            
            # AWS Services - REPLACE WITH ACTUAL PRODUCTION VALUES
            "aws_access_key_id": "REPLACE_WITH_ACTUAL_AWS_ACCESS_KEY",
            "aws_secret_access_key": "REPLACE_WITH_ACTUAL_AWS_SECRET_KEY",
            
            # Payment Processing - REPLACE WITH ACTUAL PRODUCTION VALUES
            "stripe_publishable_key": "pk_live_REPLACE_WITH_ACTUAL_STRIPE_PUBLISHABLE_KEY",
            "stripe_secret_key": "sk_live_REPLACE_WITH_ACTUAL_STRIPE_SECRET_KEY",
            "stripe_webhook_secret": "whsec_REPLACE_WITH_ACTUAL_STRIPE_WEBHOOK_SECRET",
            
            # Stripe Price IDs - REPLACE WITH ACTUAL PRODUCTION VALUES
            "stripe_starter_price_id": "price_REPLACE_WITH_ACTUAL_STARTER_PRICE_ID",
            "stripe_professional_price_id": "price_REPLACE_WITH_ACTUAL_PROFESSIONAL_PRICE_ID",
            "stripe_enterprise_price_id": "price_REPLACE_WITH_ACTUAL_ENTERPRISE_PRICE_ID",
            
            # Monitoring - REPLACE WITH ACTUAL PRODUCTION VALUES
            "sentry_dsn": "https://REPLACE_WITH_ACTUAL_SENTRY_DSN@sentry.io/PROJECT_ID",
            "sentry_release": "ruleiq@1.0.0",
            
            # External Services - REPLACE WITH ACTUAL PRODUCTION VALUES
            "langchain_api_key": "REPLACE_WITH_ACTUAL_LANGCHAIN_KEY",
            "jaeger_endpoint": "http://jaeger.ruleiq.com:14268/api/traces",
            "otlp_endpoint": "http://otel-collector.ruleiq.com:4317",
            
            # Neo4j - REPLACE WITH ACTUAL PRODUCTION VALUES
            "neo4j_uri": "bolt://neo4j.ruleiq.com:7687",
            "neo4j_username": "neo4j",
            "neo4j_password": "REPLACE_WITH_ACTUAL_NEO4J_PASSWORD",
            
            # Supabase - REPLACE WITH ACTUAL PRODUCTION VALUES
            "supabase_url": "https://REPLACE_WITH_ACTUAL_PROJECT.supabase.co",
            "supabase_service_key": "REPLACE_WITH_ACTUAL_SUPABASE_SERVICE_KEY",
            "postgres_password": "REPLACE_WITH_ACTUAL_POSTGRES_PASSWORD",
            
            # Celery - REPLACE WITH ACTUAL PRODUCTION VALUES
            "celery_broker_url": "redis://prod-redis.ruleiq.com:6379/3",
            "celery_result_backend": "redis://prod-redis.ruleiq.com:6379/4",
            
            # Backup
            "backup_s3_bucket": "ruleiq-prod-backups"
        }
        
        print(f"✅ Generated {len(secrets_data)} secrets")
        return secrets_data
    
    def create_secret(self, secrets_data: Dict[str, str]) -> bool:
        """Create secret in AWS Secrets Manager"""
        try:
            print(f"🔐 Creating secret '{self.secret_name}' in AWS Secrets Manager...")
            
            response = self.client.create_secret(
                Name=self.secret_name,
                Description=f"RuleIQ Production Secrets - {self.secret_name}",
                SecretString=json.dumps(secrets_data, indent=2),
                Tags=[
                    {'Key': 'Environment', 'Value': 'production'},
                    {'Key': 'Application', 'Value': 'ruleiq'},
                    {'Key': 'ManagedBy', 'Value': 'secrets-vault-setup'},
                    {'Key': 'Project', 'Value': 'ruleiq-compliance-platform'}
                ]
            )
            
            print(f"✅ Secret created successfully!")
            print(f"   ARN: {response['ARN']}")
            print(f"   Version: {response['VersionId']}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceExistsException':
                print(f"⚠️  Secret '{self.secret_name}' already exists. Use update_secret() to modify it.")
                return False
            else:
                print(f"❌ Error creating secret: {error_code} - {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error creating secret: {e}")
            return False
    
    def update_secret(self, secrets_data: Dict[str, str]) -> bool:
        """Update existing secret in AWS Secrets Manager"""
        try:
            print(f"🔐 Updating secret '{self.secret_name}' in AWS Secrets Manager...")
            
            response = self.client.update_secret(
                SecretId=self.secret_name,
                SecretString=json.dumps(secrets_data, indent=2)
            )
            
            print(f"✅ Secret updated successfully!")
            print(f"   ARN: {response['ARN']}")
            print(f"   Version: {response['VersionId']}")
            return True
            
        except ClientError as e:
            print(f"❌ Error updating secret: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error updating secret: {e}")
            return False
    
    def get_secret(self) -> Dict[str, Any]:
        """Retrieve secret from AWS Secrets Manager"""
        try:
            print(f"🔐 Retrieving secret '{self.secret_name}' from AWS Secrets Manager...")
            
            response = self.client.get_secret_value(SecretId=self.secret_name)
            secrets_data = json.loads(response['SecretString'])
            
            print(f"✅ Retrieved secret with {len(secrets_data)} keys")
            return secrets_data
            
        except ClientError as e:
            print(f"❌ Error retrieving secret: {e}")
            return {}
        except Exception as e:
            print(f"❌ Unexpected error retrieving secret: {e}")
            return {}
    
    def delete_secret(self, force_delete: bool = False) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            recovery_days = 7 if not force_delete else 0
            print(f"🗑️  Deleting secret '{self.secret_name}' (recovery window: {recovery_days} days)...")
            
            if force_delete:
                print("⚠️  FORCE DELETE - Secret will be permanently deleted immediately!")
                confirm = input("Type 'CONFIRM' to proceed: ")
                if confirm != 'CONFIRM':
                    print("❌ Operation cancelled")
                    return False
            
            self.client.delete_secret(
                SecretId=self.secret_name,
                RecoveryWindowInDays=recovery_days,
                ForceDeleteWithoutRecovery=force_delete
            )
            
            print(f"✅ Secret deleted successfully!")
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting secret: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error deleting secret: {e}")
            return False
    
    def setup_vault(self, update_if_exists: bool = False) -> bool:
        """🔐 Complete vault setup process"""
        print("🚀 Starting RuleIQ Secrets Vault Setup...")
        print("=" * 50)
        
        # Generate secrets
        secrets_data = self.create_production_secrets()
        
        # Try to create, update if exists and requested
        if not self.create_secret(secrets_data):
            if update_if_exists:
                print("🔄 Attempting to update existing secret...")
                return self.update_secret(secrets_data)
            else:
                print("❌ Secret already exists. Use --update to modify existing secret.")
                return False
        
        print("\n🎉 Secrets Vault Setup Complete!")
        print("=" * 50)
        print("⚠️  IMPORTANT NEXT STEPS:")
        print("1. Review and update placeholder values in AWS Secrets Manager console")
        print("2. Replace 'REPLACE_WITH_ACTUAL_*' values with real production credentials")
        print("3. Set up secret rotation policies")
        print("4. Configure IAM permissions for application access")
        print("5. Test secret retrieval with: python config/secrets_vault.py health")
        
        return True
    
    def create_iam_policy(self) -> str:
        """Generate IAM policy for RuleIQ application to access secrets"""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret"
                    ],
                    "Resource": f"arn:aws:secretsmanager:{self.region_name}:*:secret:{self.secret_name}*"
                }
            ]
        }
        
        print("🔐 IAM Policy for RuleIQ Application:")
        print("=" * 40)
        print(json.dumps(policy, indent=2))
        print("=" * 40)
        print("📝 Save this policy and attach it to your RuleIQ application's IAM role")
        
        return json.dumps(policy, indent=2)


def main():
    """🔐 Main CLI interface for Secrets Vault Setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🔐 RuleIQ Secrets Vault Setup")
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--secret-name', default='ruleiq-production-secrets', help='Secret name')
    parser.add_argument('--update', action='store_true', help='Update existing secret')
    parser.add_argument('--delete', action='store_true', help='Delete secret')
    parser.add_argument('--force-delete', action='store_true', help='Force delete secret immediately')
    parser.add_argument('--get', action='store_true', help='Retrieve and display secret')
    parser.add_argument('--iam-policy', action='store_true', help='Generate IAM policy')
    
    args = parser.parse_args()
    
    setup = SecretsVaultSetup(region_name=args.region, secret_name=args.secret_name)
    
    if args.delete or args.force_delete:
        setup.delete_secret(force_delete=args.force_delete)
    elif args.get:
        secrets = setup.get_secret()
        if secrets:
            print("🔐 Secret Keys Found:")
            for key in secrets.keys():
                print(f"  - {key}")
    elif args.iam_policy:
        setup.create_iam_policy()
    else:
        setup.setup_vault(update_if_exists=args.update)


if __name__ == "__main__":
    main()