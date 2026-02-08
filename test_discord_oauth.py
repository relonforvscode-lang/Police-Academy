#!/usr/bin/env python
"""Test Discord OAuth callback function"""

import os
import sys
import django
from unittest.mock import Mock, patch, MagicMock
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.insert(0, 'c:\\Users\\Gaming\\Desktop\\Newww')

django.setup()

# Add testserver to ALLOWED_HOSTS for testing
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import RequestFactory, TestCase
from main.views import discord_oauth_callback
import requests


def test_successful_callback():
    """Test successful Discord OAuth callback"""
    print("\n✅ Testing successful Discord OAuth callback...")
    
    factory = RequestFactory()
    request = factory.get('/apply/discord-callback/?code=test_code_123')
    request.session = {}
    
    # Mock the make_request_with_retry function
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {
        'access_token': 'test_access_token',
        'token_type': 'Bearer'
    }
    
    mock_user_response = Mock()
    mock_user_response.status_code = 200
    mock_user_response.json.return_value = {
        'id': '123456789',
        'username': 'testuser'
    }
    
    with patch('main.views.requests.post') as mock_post, \
         patch('main.views.requests.get') as mock_get, \
         patch.dict(os.environ, {
             'DISCORD_CLIENT_ID': 'test_client_id',
             'DISCORD_CLIENT_SECRET': 'test_client_secret'
         }):
        
        mock_post.return_value = mock_token_response
        mock_get.return_value = mock_user_response
        
        response = discord_oauth_callback(request)
        
        # Check that we got a redirect response
        assert response.status_code == 302, f"Expected status 302, got {response.status_code}"
        print("✓ Successfully handled callback")
        print(f"✓ Discord ID stored: {request.session.get('discord_id')}")
        print(f"✓ Discord username stored: {request.session.get('discord_username')}")


def test_missing_discord_credentials():
    """Test callback when Discord credentials are missing"""
    print("\n✅ Testing missing Discord credentials...")
    
    factory = RequestFactory()
    request = factory.get('/apply/discord-callback/?code=test_code_123')
    request.session = {}
    
    with patch.dict(os.environ, {}, clear=False):
        # Remove Discord credentials
        os.environ.pop('DISCORD_CLIENT_ID', None)
        os.environ.pop('DISCORD_CLIENT_SECRET', None)
        
        response = discord_oauth_callback(request)
        
        assert response.status_code == 302, f"Expected redirect"
        assert 'error_message' in request.session
        print(f"✓ Error message: {request.session['error_message']}")


def test_missing_authorization_code():
    """Test callback when authorization code is missing"""
    print("\n✅ Testing missing authorization code...")
    
    factory = RequestFactory()
    request = factory.get('/apply/discord-callback/')  # No code parameter
    request.session = {}
    
    response = discord_oauth_callback(request)
    
    assert response.status_code == 302, f"Expected redirect"
    assert 'error_message' in request.session
    print(f"✓ Error message: {request.session['error_message']}")


def test_discord_error_response():
    """Test callback when Discord returns an error"""
    print("\n✅ Testing Discord error response...")
    
    factory = RequestFactory()
    request = factory.get('/apply/discord-callback/?error=access_denied&error_description=User%20cancelled')
    request.session = {}
    
    response = discord_oauth_callback(request)
    
    assert response.status_code == 302, f"Expected redirect"
    assert 'error_message' in request.session
    print(f"✓ Error message: {request.session['error_message']}")


def test_rate_limit_with_retry():
    """Test that rate limiting is handled with retry logic"""
    print("\n✅ Testing rate limit handling with retries...")
    
    factory = RequestFactory()
    request = factory.get('/apply/discord-callback/?code=test_code_123')
    request.session = {}
    
    # First response: 429 (rate limited)
    # Second response: 200 (success)
    mock_responses = [
        Mock(status_code=429, headers={'Retry-After': '1'}),
        Mock(status_code=200, json=lambda: {'access_token': 'token', 'token_type': 'Bearer'})
    ]
    
    mock_user_response = Mock()
    mock_user_response.status_code = 200
    mock_user_response.json.return_value = {
        'id': '987654321',
        'username': 'ratelimituser'
    }
    
    call_count = [0]
    
    def mock_post_side_effect(*args, **kwargs):
        result = mock_responses[min(call_count[0], 1)]
        call_count[0] += 1
        return result
    
    with patch('main.views.requests.post') as mock_post, \
         patch('main.views.requests.get') as mock_get, \
         patch.dict(os.environ, {
             'DISCORD_CLIENT_ID': 'test_client_id',
             'DISCORD_CLIENT_SECRET': 'test_client_secret'
         }), \
         patch('time.sleep'):  # Mock sleep to avoid actual delays
        
        mock_post.side_effect = mock_post_side_effect
        mock_get.return_value = mock_user_response
        
        response = discord_oauth_callback(request)
        
        # Check that retry worked (we got a success response)
        assert response.status_code == 302, f"Expected redirect, got {response.status_code}"
        assert 'discord_id' in request.session, "Discord ID should be stored"
        print(f"✓ Rate limit handled with retry")
        print(f"✓ Final result: discordID={request.session.get('discord_id')}")


def test_invalid_token_response():
    """Test handling of invalid token response from Discord"""
    print("\n✅ Testing invalid token response...")
    
    factory = RequestFactory()
    request = factory.get('/apply/discord-callback/?code=test_code_123')
    request.session = {}
    
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {
        'access_token': None  # Invalid: no access token
    }
    
    with patch('main.views.requests.post') as mock_post, \
         patch.dict(os.environ, {
             'DISCORD_CLIENT_ID': 'test_client_id',
             'DISCORD_CLIENT_SECRET': 'test_client_secret'
         }):
        
        mock_post.return_value = mock_token_response
        
        response = discord_oauth_callback(request)
        
        assert response.status_code == 302, f"Expected redirect"
        assert 'error_message' in request.session
        print(f"✓ Invalid response handled: {request.session['error_message']}")


def test_401_unauthorized():
    """Test handling of 401 Unauthorized from Discord"""
    print("\n✅ Testing 401 Unauthorized response...")
    
    factory = RequestFactory()
    request = factory.get('/apply/discord-callback/?code=test_code_123')
    request.session = {}
    
    mock_token_response = Mock()
    mock_token_response.status_code = 401
    mock_token_response.text = "Invalid client"
    
    with patch('main.views.requests.post') as mock_post, \
         patch.dict(os.environ, {
             'DISCORD_CLIENT_ID': 'test_client_id',
             'DISCORD_CLIENT_SECRET': 'test_client_secret'
         }):
        
        mock_post.return_value = mock_token_response
        
        response = discord_oauth_callback(request)
        
        assert response.status_code == 302, f"Expected redirect"
        assert 'Invalid Discord credentials' in request.session['error_message']
        print(f"✓ 401 error handled correctly: {request.session['error_message']}")


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Discord OAuth Callback Function")
    print("=" * 60)
    
    try:
        test_missing_authorization_code()
        test_discord_error_response()
        test_missing_discord_credentials()
        test_invalid_token_response()
        test_401_unauthorized()
        test_rate_limit_with_retry()
        test_successful_callback()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
