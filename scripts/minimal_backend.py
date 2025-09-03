from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Constants
HTTP_UNAUTHORIZED = 401

app = FastAPI(title='RuleIQ Emergency Backend')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:3000'],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get('/health')
async def health_check() ->Dict[str, Any]:
    return {'status': 'ok', 'message': 'Emergency backend running'}

@app.get('/api/dashboard')
async def get_dashboard() ->Dict[str, Any]:
    return {'message': 'Dashboard data would go here', 'user': {'id':
        'test-user', 'email': 'test@example.com'}, 'stats': {'assessments':
        0, 'policies': 0, 'compliance_score': 0}}

@app.get('/api/assessments')
async def get_assessments() ->Dict[str, Any]:
    return {'assessments': [], 'total': 0, 'page': 1, 'page_size': 50}

@app.get('/api/policies')
async def get_policies() ->Dict[str, Any]:
    return {'policies': [], 'total': 0, 'page': 1, 'page_size': 50}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post('/api/auth/login')
async def login(request: LoginRequest) ->Dict[str, Any]:
    if (request.username == 'test@example.com' and request.password ==
        'password'):
        return {'access_token': 'fake-jwt-token', 'refresh_token':
            'fake-refresh-token', 'token_type': 'bearer'}
    raise HTTPException(status_code=HTTP_UNAUTHORIZED, detail=
        'Invalid credentials')

@app.get('/api/auth/me')
async def get_me() ->Dict[str, Any]:
    return {'id': 1, 'email': 'test@example.com', 'full_name': 'Test User',
        'is_active': True}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
