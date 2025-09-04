"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

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

    def __init__(self, region_name: str='us-east-1', secret_name: str=
        'ruleiq-production-secrets'):
        self.region_name = region_name
        self.secret_name = secret_name
        self.client = boto3.client('secretsmanager', region_name=region_name)
        print(
            f"🔐 Initializing Secrets Vault Setup for '{secret_name}' in {region_name}",
            )

    def generate_secure_key(self, length: int=32) ->str: alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def generate_jwt_secret(self) ->str: import base64
        random_bytes = secrets.token_bytes(32)
        return base64.b64encode(random_bytes).decode('utf-8')

    def generate_fernet_key(self) ->str: from cryptography.fernet import Fernet
        return Fernet.generate_key().decode('utf-8')

    def create_production_secrets(self) ->Dict[str, str]: 🔐 Generate all production secrets for RuleIQ
        IMPORTANT: Review and update these values for actual production use
        """
        logger.info('🔐 Generating secure production secrets...')
        secrets_data = {'database_url':
            'postgresql+asyncpg://prod_user:CHANGE_ME@prod-db.ruleiq.com:5432/ruleiq_prod?sslmode=require'
            , 'test_database_url':
            'postgresql+asyncpg://test_user:CHANGE_ME@test-db.ruleiq.com:5432/ruleiq_test?sslmode=require'
            , 'redis_url': 'redis://prod-redis.ruleiq.com:6379/0',
            'cache_redis_url': 'redis://prod-redis.ruleiq.com:6379/1',
            'session_redis_url': 'redis://prod-redis.ruleiq.com:6379/2',
            'jwt_secret': self.generate_jwt_secret(), 'secret_key': self.
            generate_secure_key(64), 'encryption_key': self.
            generate_secure_key(32), 'fernet_key': self.generate_fernet_key
            (), 'credential_master_key': self.generate_secure_key(32),
            'stack_project_id': 'REPLACE_WITH_ACTUAL_STACK_PROJECT_ID',
            'stack_client_key': 'REPLACE_WITH_ACTUAL_STACK_CLIENT_KEY',
            'stack_server_key': 'REPLACE_WITH_ACTUAL_STACK_SERVER_KEY',
            'google_client_id': 'REPLACE_WITH_ACTUAL_GOOGLE_CLIENT_ID',
            'google_client_secret':
            'REPLACE_WITH_ACTUAL_GOOGLE_CLIENT_SECRET',
            'microsoft_client_id':
            'REPLACE_WITH_ACTUAL_MICROSOFT_CLIENT_ID',
            'microsoft_client_secret':
            'REPLACE_WITH_ACTUAL_MICROSOFT_CLIENT_SECRET', 'okta_client_id':
            'REPLACE_WITH_ACTUAL_OKTA_CLIENT_ID', 'okta_client_secret':
            'REPLACE_WITH_ACTUAL_OKTA_CLIENT_SECRET', 'openai_api_key':
            'REPLACE_WITH_ACTUAL_OPENAI_KEY', 'anthropic_api_key':
            'REPLACE_WITH_ACTUAL_ANTHROPIC_KEY', 'google_ai_api_key':
            'REPLACE_WITH_ACTUAL_GOOGLE_AI_KEY', 'mistral_api_key':
            'REPLACE_WITH_ACTUAL_MISTRAL_KEY', 'smtp_host':
            'smtp.ruleiq.com', 'smtp_username': 'noreply@ruleiq.com',
            'smtp_password': 'REPLACE_WITH_ACTUAL_SMTP_PASSWORD',
            'aws_access_key_id': 'REPLACE_WITH_ACTUAL_AWS_ACCESS_KEY',
            'aws_secret_access_key': 'REPLACE_WITH_ACTUAL_AWS_SECRET_KEY',
            'stripe_publishable_key':
            'pk_live_REPLACE_WITH_ACTUAL_STRIPE_PUBLISHABLE_KEY',
            'stripe_secret_key':
            'sk_live_REPLACE_WITH_ACTUAL_STRIPE_SECRET_KEY',
            'stripe_webhook_secret':
            'whsec_REPLACE_WITH_ACTUAL_STRIPE_WEBHOOK_SECRET',
            'stripe_starter_price_id':
            'price_REPLACE_WITH_ACTUAL_STARTER_PRICE_ID',
            'stripe_professional_price_id':
            'price_REPLACE_WITH_ACTUAL_PROFESSIONAL_PRICE_ID',
            'stripe_enterprise_price_id':
            'price_REPLACE_WITH_ACTUAL_ENTERPRISE_PRICE_ID', 'sentry_dsn':
            'https://REPLACE_WITH_ACTUAL_SENTRY_DSN@sentry.io/PROJECT_ID',
            'sentry_release': 'ruleiq@1.0.0', 'langchain_api_key':
            'REPLACE_WITH_ACTUAL_LANGCHAIN_KEY', 'jaeger_endpoint':
            'http://jaeger.ruleiq.com:14268/api/traces', 'otlp_endpoint':
            'http://otel-collector.ruleiq.com:4317', 'neo4j_uri':
            'bolt://neo4j.ruleiq.com:7687', 'neo4j_username': 'neo4j',
            'neo4j_password': 'REPLACE_WITH_ACTUAL_NEO4J_PASSWORD',
            'supabase_url':
            'https://REPLACE_WITH_ACTUAL_PROJECT.supabase.co',
            'supabase_service_key':
            'REPLACE_WITH_ACTUAL_SUPABASE_SERVICE_KEY', 'postgres_password':
            'REPLACE_WITH_ACTUAL_POSTGRES_PASSWORD', '            'redis://prod-redis.ruleiq.com:6379/3', '            'redis://prod-redis.ruleiq.com:6379/4', 'backup_s3_bucket':
            'ruleiq-prod-backups'}
        logger.info('✅ Generated %s secrets' % len(secrets_data))
        return secrets_data

    def create_secret(self, secrets_data: Dict[str, str]) ->bool: try:
            logger.info("🔐 Creating secret '%s' in AWS Secrets Manager..." %
                self.secret_name)
            response = self.client.create_secret(Name=self.secret_name,
                Description=
                f'RuleIQ Production Secrets - {self.secret_name}',
                SecretString=json.dumps(secrets_data, indent=2), Tags=[{
                'Key': 'Environment', 'Value': 'production'}, {'Key':
                'Application', 'Value': 'ruleiq'}, {'Key': 'ManagedBy',
                'Value': 'secrets-vault-setup'}, {'Key': 'Project', 'Value':
                'ruleiq-compliance-platform'}])
            logger.info('✅ Secret created successfully!')
            logger.info('   ARN: %s' % response['ARN'])
            logger.info('   Version: %s' % response['VersionId'])
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceExistsException':
                print(
                    f"⚠️  Secret '{self.secret_name}' already exists. Use update_secret() to modify it.",
                    )
                return False
            else:
                logger.info('❌ Error creating secret: %s - %s' % (
                    error_code, e))
                return False
        except Exception as e:
            logger.info('❌ Unexpected error creating secret: %s' % e)
            return False

    def update_secret(self, secrets_data: Dict[str, str]) ->bool: try:
            logger.info("🔐 Updating secret '%s' in AWS Secrets Manager..." %
                self.secret_name)
            response = self.client.update_secret(SecretId=self.secret_name,
                SecretString=json.dumps(secrets_data, indent=2))
            logger.info('✅ Secret updated successfully!')
            logger.info('   ARN: %s' % response['ARN'])
            logger.info('   Version: %s' % response['VersionId'])
            return True
        except ClientError as e:
            logger.info('❌ Error updating secret: %s' % e)
            return False
        except Exception as e:
            logger.info('❌ Unexpected error updating secret: %s' % e)
            return False

    def get_secret(self) ->Dict[str, Any]: try:
            print(
                f"🔐 Retrieving secret '{self.secret_name}' from AWS Secrets Manager...",
                )
            response = self.client.get_secret_value(SecretId=self.secret_name)
            secrets_data = json.loads(response['SecretString'])
            logger.info('✅ Retrieved secret with %s keys' % len(secrets_data))
            return secrets_data
        except ClientError as e:
            logger.info('❌ Error retrieving secret: %s' % e)
            return {}
        except Exception as e:
            logger.info('❌ Unexpected error retrieving secret: %s' % e)
            return {}

    def delete_secret(self, force_delete: bool=False) ->bool: try:
            recovery_days = 7 if not force_delete else 0
            print(
                f"🗑️  Deleting secret '{self.secret_name}' (recovery window: {recovery_days} days)...",
                )
            if force_delete:
                print(
                    '⚠️  FORCE DELETE - Secret will be permanently deleted immediately!',
                    )
                confirm = input("Type 'CONFIRM' to proceed: ")
                if confirm != 'CONFIRM':
                    logger.info('❌ Operation cancelled')
                    return False
            self.client.delete_secret(SecretId=self.secret_name,
                RecoveryWindowInDays=recovery_days,
                ForceDeleteWithoutRecovery=force_delete)
            logger.info('✅ Secret deleted successfully!')
            return True
        except ClientError as e:
            logger.info('❌ Error deleting secret: %s' % e)
            return False
        except Exception as e:
            logger.info('❌ Unexpected error deleting secret: %s' % e)
            return False

    def setup_vault(self, update_if_exists: bool=False) ->bool: logger.info('🚀 Starting RuleIQ Secrets Vault Setup...')
        logger.info('=' * 50)
        secrets_data = self.create_production_secrets()
        if not self.create_secret(secrets_data):
            if update_if_exists:
                logger.info('🔄 Attempting to update existing secret...')
                return self.update_secret(secrets_data)
            else:
                print(
                    '❌ Secret already exists. Use --update to modify existing secret.',
                    )
                return False
        logger.info('\n🎉 Secrets Vault Setup Complete!')
        logger.info('=' * 50)
        logger.info('⚠️  IMPORTANT NEXT STEPS:')
        logger.info(
            '1. Review and update placeholder values in AWS Secrets Manager console',
            )
        print(
            "2. Replace 'REPLACE_WITH_ACTUAL_*' values with real production credentials",
            )
        logger.info('3. Set up secret rotation policies')
        logger.info('4. Configure IAM permissions for application access')
        logger.info(
            '5. Test secret retrieval with: python config/secrets_vault.py health',
            )
        return True

    def create_iam_policy(self) ->str: policy = {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow',
            'Action': ['secretsmanager:GetSecretValue',
            'secretsmanager:DescribeSecret'], 'Resource':
            f'arn:aws:secretsmanager:{self.region_name}:*:secret:{self.secret_name}*'
            }]}
        logger.info('🔐 IAM Policy for RuleIQ Application:')
        logger.info('=' * 40)
        logger.info(json.dumps(policy, indent=2))
        logger.info('=' * 40)
        logger.info(
            "📝 Save this policy and attach it to your RuleIQ application's IAM role",
            )
        return json.dumps(policy, indent=2)


def main() ->None: import argparse
    parser = argparse.ArgumentParser(description='🔐 RuleIQ Secrets Vault Setup',
        )
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--secret-name', default=
        'ruleiq-production-secrets', help='Secret name')
    parser.add_argument('--update', action='store_true', help=
        'Update existing secret')
    parser.add_argument('--delete', action='store_true', help='Delete secret')
    parser.add_argument('--force-delete', action='store_true', help=
        'Force delete secret immediately')
    parser.add_argument('--get', action='store_true', help=
        'Retrieve and display secret')
    parser.add_argument('--iam-policy', action='store_true', help=
        'Generate IAM policy')
    args = parser.parse_args()
    setup = SecretsVaultSetup(region_name=args.region, secret_name=args.
        secret_name)
    if args.delete or args.force_delete:
        setup.delete_secret(force_delete=args.force_delete)
    elif args.get:
        secrets = setup.get_secret()
        if secrets:
            logger.info('🔐 Secret Keys Found:')
            for key in secrets.keys():
                logger.info('  - %s' % key)
    elif args.iam_policy:
        setup.create_iam_policy()
    else:
        setup.setup_vault(update_if_exists=args.update)


if __name__ == '__main__':
    main()
