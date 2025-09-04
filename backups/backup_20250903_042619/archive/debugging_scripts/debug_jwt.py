"""
Standalone JWT test script to verify token generation and verification.
This helps isolate JWT issues from the rest of the application.
"""
import logging
logger = logging.getLogger(__name__)
import os
from pathlib import Path
from dotenv import load_dotenv
logger.info('Testing JWT libraries...')
try:
    import jwt as pyjwt
    logger.info('✓ PyJWT imported successfully')
except ImportError:
    logger.info('✗ PyJWT not installed')
    pyjwt = None
try:
    from jose import jwt as jose_jwt
    logger.info('✓ python-jose imported successfully')
except ImportError:
    logger.info('✗ python-jose not installed')
    jose_jwt = None
logger.info('\n' + '=' * 50)
logger.info('\nTesting environment variable loading...')
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
    jwt_secret_1 = os.getenv('JWT_SECRET')
    logger.info(f"Method 1 (.env.local): JWT_SECRET = {(jwt_secret_1[:10] if jwt_secret_1 else 'None')}...")
env_path = Path(__file__).parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)
    jwt_secret_2 = os.getenv('JWT_SECRET')
    logger.info(f"Method 2 (absolute path): JWT_SECRET = {(jwt_secret_2[:10] if jwt_secret_2 else 'None')}...")
jwt_secret_3 = os.getenv('JWT_SECRET')
logger.info(f"Method 3 (direct env): JWT_SECRET = {(jwt_secret_3[:10] if jwt_secret_3 else 'None')}...")
logger.info('\n' + '=' * 50)
JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
logger.info(f'\nUsing JWT_SECRET: {JWT_SECRET[:20]}...')
logger.info('\n' + '=' * 50)
logger.info('\nTesting token creation and verification...')
test_payload = {'test': 'data', 'sub': 'testuser@example.com'}
if pyjwt:
    logger.info('\nTesting with PyJWT:')
    try:
        token = pyjwt.encode(test_payload, JWT_SECRET, algorithm='HS256')
        logger.info(f'✓ Token created: {token[:50]}...')
        decoded = pyjwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        logger.info(f'✓ Token verified: {decoded}')
    except Exception as e:
        logger.info(f'✗ PyJWT error: {e}')
if jose_jwt:
    logger.info('\nTesting with python-jose:')
    try:
        token = jose_jwt.encode(test_payload, JWT_SECRET, algorithm='HS256')
        logger.info(f'✓ Token created: {token[:50]}...')
        decoded = jose_jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        logger.info(f'✓ Token verified: {decoded}')
    except Exception as e:
        logger.info(f'✗ python-jose error: {e}')
if pyjwt and jose_jwt:
    logger.info('\n' + '=' * 50)
    logger.info('\nTesting cross-library compatibility...')
    try:
        token_pyjwt = pyjwt.encode(test_payload, JWT_SECRET, algorithm='HS256')
        decoded_jose = jose_jwt.decode(token_pyjwt, JWT_SECRET, algorithms=['HS256'])
        logger.info('✓ PyJWT -> python-jose: Success')
        token_jose = jose_jwt.encode(test_payload, JWT_SECRET, algorithm='HS256')
        decoded_pyjwt = pyjwt.decode(token_jose, JWT_SECRET, algorithms=['HS256'])
        logger.info('✓ python-jose -> PyJWT: Success')
    except Exception as e:
        logger.info(f'✗ Cross-library compatibility error: {e}')
logger.info('\n' + '=' * 50)
logger.info('\nSummary:')
logger.info(f'- Working directory: {os.getcwd()}')
logger.info(f"- .env.local exists: {os.path.exists('.env.local')}")
logger.info(f"- JWT_SECRET is set: {('Yes' if os.getenv('JWT_SECRET') else 'No')}")
logger.info(f"- Both JWT libraries work: {('Yes' if pyjwt and jose_jwt else 'No')}")