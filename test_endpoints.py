#!/usr/bin/env python
"""Test Discord OAuth endpoints"""

import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
os.environ['DEBUG'] = 'True'

import django
django.setup()

from django.test import Client
from unittest.mock import patch, Mock

print('=' * 70)
print('🧪 TESTING DISCORD OAUTH IMPLEMENTATION')
print('=' * 70)

client = Client()

# Test 1: Apply page
print('\n1️⃣ Testing /apply/ page...')
response = client.get('/apply/')
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    print('   ✅ Page loads successfully')
    print(f'   Content length: {len(response.content)} bytes')
else:
    print(f'   ❌ Error: {response.status_code}')

# Test 2: Discord login redirect
print('\n2️⃣ Testing /apply/discord-login/ redirect...')
response = client.get('/apply/discord-login/', follow=False)
print(f'   Status: {response.status_code}')
if response.status_code in [301, 302, 307]:
    print(f'   ✅ Redirects correctly to Discord OAuth')
    location = response.get('Location', 'N/A')
    if location:
        if 'discord.com' in location:
            print(f'   ✅ Redirects to Discord domain')
        else:
            print(f'   Redirect target: {location[:80]}')
else:
    print(f'   ❌ Unexpected status: {response.status_code}')

# Test 3: Callback with code parameter (no auth)
print('\n3️⃣ Testing /apply/discord-callback/ with code...')
response = client.get('/apply/discord-callback/?code=test_code_12345', follow=False)
print(f'   Status: {response.status_code}')
if response.status_code in [301, 302]:
    print(f'   ✅ Callback endpoint responds with redirect')
    location = response.get('Location', '')
    if 'apply' in location:
        print(f'   ✅ Redirects back to apply page')
elif response.status_code == 200:
    print(f'   ✅ Callback endpoint responds with 200')
else:
    print(f'   Status: {response.status_code}')

# Test 4: Callback with error parameter
print('\n4️⃣ Testing /apply/discord-callback/ with error...')
response = client.get('/apply/discord-callback/?error=access_denied', follow=False)
print(f'   Status: {response.status_code}')
if response.status_code in [301, 302]:
    print(f'   ✅ Handles error parameter correctly')
    # Check session for error message
    if 'error_message' in response.wsgi_request.session:
        print(f'   ✅ Error message stored in session')
else:
    print(f'   Status: {response.status_code}')

# Test 5: Mock Discord callback with success
print('\n5️⃣ Testing complete flow with mock Discord...')
with patch('main.views.requests.post') as mock_post, \
     patch('main.views.requests.get') as mock_get:
    
    # Mock token response
    mock_token = Mock()
    mock_token.status_code = 200
    mock_token.json.return_value = {'access_token': 'test_token_xyz'}
    
    # Mock user response
    mock_user = Mock()
    mock_user.status_code = 200
    mock_user.json.return_value = {'id': '987654321', 'username': 'testuser'}
    
    mock_post.return_value = mock_token
    mock_get.return_value = mock_user
    
    response = client.get('/apply/discord-callback/?code=real_test_code', follow=False)
    print(f'   Status: {response.status_code}')
    
    if response.status_code in [301, 302]:
        print(f'   ✅ Complete flow succeeds')
        # Check if session was updated
        session = response.wsgi_request.session
        if 'discord_id' in session:
            print(f'   ✅ Discord ID stored in session: {session.get("discord_id")}')
        if 'discord_username' in session:
            print(f'   ✅ Discord username stored: {session.get("discord_username")}')
    else:
        print(f'   ❌ Unexpected status: {response.status_code}')

print('\n' + '=' * 70)
print('✅ ALL TESTS COMPLETE')
print('=' * 70)
print('\n📝 Next Steps:')
print('   1. Open http://127.0.0.1:8000/apply/ in your browser')
print('   2. Click "تسجيل الدخول عبر Discord"')
print('   3. Authorize in Discord')
print('   4. Check Terminal for debug logs')
print('=' * 70)
