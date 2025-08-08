#!/usr/bin/env python3
"""
Test AI chat conversation creation to debug 500 error
"""
import requests
import json

def test_chat_creation():
    try:
        print('Testing AI chat conversation creation...')
        
        # Login first
        login_response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            json={'email': 'test@ruleiq.dev', 'password': 'TestPassword123!'},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            print('✅ Login successful')
            
            # Test conversation creation without initial message first
            print('\nCreating conversation without initial message...')
            conv_response = requests.post(
                'http://localhost:8000/api/v1/chat/conversations',
                json={'title': 'Test Chat'},
                headers=headers,
                timeout=10
            )
            
            print(f'Status: {conv_response.status_code}')
            if conv_response.status_code != 200:
                print(f'Error response: {conv_response.text}')
                return False
            else:
                print('✅ Conversation created successfully without initial message')
                
            # Now test with initial message
            print('\nCreating conversation with initial message...')
            conv_response2 = requests.post(
                'http://localhost:8000/api/v1/chat/conversations',
                json={'title': 'Test Chat 2', 'initial_message': 'Hello, I need help with GDPR compliance.'},
                headers=headers,
                timeout=30
            )
            
            print(f'Status: {conv_response2.status_code}')
            if conv_response2.status_code != 200:
                print(f'Error response: {conv_response2.text}')
                return False
            else:
                print('✅ Conversation created successfully with initial message')
                return True
            
        else:
            print(f'❌ Login failed: {login_response.status_code}')
            print(f'Response: {login_response.text}')
            return False
            
    except requests.exceptions.ConnectionError:
        print('❌ Cannot connect to backend server. Is it running?')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    test_chat_creation()
