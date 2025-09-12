#!/usr/bin/env python3
"""
Environment Configuration Test Script
Tests all required environment variables and service connections
"""

import os
import sys
import asyncio
import asyncpg
import redis
import requests
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env', override=False)

def print_success(message):
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.CYAN}ℹ️  {message}{Style.RESET_ALL}")

def print_section(title):
    print(f"\n{Fore.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Style.RESET_ALL}")

async def test_postgresql():
    """Test PostgreSQL database connection"""
    print_section("Testing PostgreSQL Connection")
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print_error("DATABASE_URL not found in environment")
        return False
    
    # Convert to asyncpg format
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    try:
        conn = await asyncpg.connect(db_url)
        version = await conn.fetchval('SELECT version()')
        print_success("PostgreSQL connection successful!")
        print_info(f"Database version: {version[:60]}...")
        
        # Test table access
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            LIMIT 5
        """)
        if tables:
            print_info(f"Found {len(tables)} tables in public schema")
        
        await conn.close()
        return True
    except Exception as e:
        print_error(f"PostgreSQL connection failed: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    print_section("Testing Redis Connection")
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        # Parse Redis URL
        if redis_url.startswith('redis://'):
            parts = redis_url.replace('redis://', '').split(':')
            host = parts[0]
            if len(parts) > 1:
                port_db = parts[1].split('/')
                port = int(port_db[0])
                db = int(port_db[1]) if len(port_db) > 1 else 0
            else:
                port = 6379
                db = 0
        else:
            host = 'localhost'
            port = 6379
            db = 0
        
        r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        r.ping()
        print_success("Redis connection successful!")
        
        # Test set and get
        r.set('test_key', 'test_value', ex=10)  # Expires in 10 seconds
        value = r.get('test_key')
        if value == 'test_value':
            print_info("Read/Write test passed")
        r.delete('test_key')
        
        # Get Redis info
        info = r.info()
        print_info(f"Redis version: {info.get('redis_version', 'Unknown')}")
        print_info(f"Connected clients: {info.get('connected_clients', 'Unknown')}")
        
        return True
    except redis.ConnectionError as e:
        print_error(f"Redis connection failed: {e}")
        print_warning("Make sure Redis is running: sudo service redis-server start")
        return False
    except Exception as e:
        print_error(f"Redis error: {e}")
        return False

def test_google_ai():
    """Test Google AI API connection"""
    print_section("Testing Google AI API")
    
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print_error("GOOGLE_AI_API_KEY not found in environment")
        return False
    
    if api_key.startswith('your-'):
        print_warning("GOOGLE_AI_API_KEY appears to be a placeholder")
        return False
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print_success("Google AI API connection successful!")
            models = response.json().get('models', [])
            print_info(f"Available models: {len(models)} models found")
            
            # Show first few model names
            gemini_models = [m for m in models if 'gemini' in m.get('name', '').lower()]
            if gemini_models:
                print_info(f"Gemini models available: {len(gemini_models)}")
                for model in gemini_models[:3]:
                    print_info(f"  - {model.get('name', 'Unknown')}")
            
            return True
        else:
            print_error(f"Google AI API connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Google AI API error: {e}")
        return False

def test_openai():
    """Test OpenAI API connection"""
    print_section("Testing OpenAI API")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print_warning("OPENAI_API_KEY not found in environment")
        return False
    
    if api_key.startswith('your-') or api_key.startswith('sk-your'):
        print_warning("OPENAI_API_KEY appears to be a placeholder")
        return False
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print_success("OpenAI API connection successful!")
            models = response.json().get('data', [])
            gpt_models = [m for m in models if 'gpt' in m.get('id', '').lower()]
            print_info(f"Available GPT models: {len(gpt_models)}")
            return True
        elif response.status_code == 401:
            print_error("OpenAI API authentication failed - check API key")
            return False
        else:
            print_error(f"OpenAI API connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"OpenAI API error: {e}")
        return False

def test_smtp():
    """Test SMTP configuration"""
    print_section("Testing SMTP Configuration")
    
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = os.getenv('SMTP_PORT')
    
    if not smtp_host:
        print_warning("SMTP_HOST not configured")
        return False
    
    print_info(f"SMTP Host: {smtp_host}")
    print_info(f"SMTP Port: {smtp_port}")
    print_info(f"SMTP From: {os.getenv('SMTP_FROM_EMAIL', 'Not set')}")
    
    if smtp_host == 'localhost' and smtp_port == '1025':
        print_warning("Using local development SMTP server")
        print_info("For testing, you can run: python -m smtpd -n -c DebuggingServer localhost:1025")
    
    return True

def test_stripe():
    """Test Stripe configuration"""
    print_section("Testing Stripe Configuration")
    
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    secret_key = os.getenv('STRIPE_SECRET_KEY')
    
    if not publishable_key or not secret_key:
        print_warning("Stripe keys not configured")
        return False
    
    if publishable_key.startswith('pk_test_'):
        print_success("Stripe test keys configured")
        print_info("Using Stripe test mode")
    elif publishable_key.startswith('pk_live_'):
        print_warning("Stripe LIVE keys configured - be careful!")
    else:
        print_warning("Stripe keys appear to be placeholders")
    
    return True

def check_required_vars():
    """Check all required environment variables"""
    print_section("Checking Required Environment Variables")
    
    required_vars = [
        'DATABASE_URL',
        'REDIS_URL',
        'JWT_SECRET',
        'SECRET_KEY',
        'GOOGLE_AI_API_KEY',
        'NEXT_PUBLIC_API_URL',
        'API_HOST',
        'API_PORT'
    ]
    
    missing = []
    placeholders = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print_error(f"{var}: Not set")
        elif value.startswith('your-') or value == 'change-me':
            placeholders.append(var)
            print_warning(f"{var}: Placeholder value")
        else:
            print_success(f"{var}: Configured")
    
    return len(missing) == 0

async def main():
    """Run all environment tests"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print("RuleIQ Environment Configuration Test")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    print_info(f"Environment: {os.getenv('ENVIRONMENT', 'Not set')}")
    print_info(f"Debug mode: {os.getenv('DEBUG', 'Not set')}")
    
    # Check required variables
    vars_ok = check_required_vars()
    
    # Test connections
    results = []
    
    # PostgreSQL
    pg_result = await test_postgresql()
    results.append(('PostgreSQL', pg_result))
    
    # Redis
    redis_result = test_redis()
    results.append(('Redis', redis_result))
    
    # Google AI
    google_result = test_google_ai()
    results.append(('Google AI', google_result))
    
    # OpenAI
    openai_result = test_openai()
    results.append(('OpenAI', openai_result))
    
    # SMTP
    smtp_result = test_smtp()
    results.append(('SMTP', smtp_result))
    
    # Stripe
    stripe_result = test_stripe()
    results.append(('Stripe', stripe_result))
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for service, result in results:
        if result:
            print_success(f"{service}: PASSED")
        else:
            print_error(f"{service}: FAILED")
    
    print(f"\n{Fore.CYAN}Overall: {passed}/{total} services configured{Style.RESET_ALL}")
    
    if passed == total and vars_ok:
        print_success("\n🎉 All environment configurations are working!")
        return 0
    else:
        print_warning("\n⚠️  Some configurations need attention")
        if not vars_ok:
            print_info("Check the missing or placeholder environment variables")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)