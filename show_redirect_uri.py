#!/usr/bin/env python
"""
Script لاعرض الـ Redirect URI الصحيح للـ Discord OAuth
تستخدم هذا لتحديث Discord console
"""
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from django.test import RequestFactory

def get_redirect_uris():
    """اعرض الـ redirect URIs للـ environments المختلفة"""
    factory = RequestFactory()
    
    print("\n" + "="*70)
    print("🔐 DISCORD OAUTH REDIRECT URI HELPER")
    print("="*70)
    
    # Local development
    print("\n📍 FOR LOCAL DEVELOPMENT:")
    request = factory.get('/apply/discord-callback/')
    request.META['HTTP_HOST'] = '127.0.0.1:8000'
    local_uri = request.build_absolute_uri('/apply/discord-callback/')
    print(f"   {local_uri}")
    print(f"   ✅ Add this to Discord Console")
    
    # Localhost variant
    print("\n📍 OR FOR LOCALHOST:")
    request.META['HTTP_HOST'] = 'localhost:8000'
    localhost_uri = request.build_absolute_uri('/apply/discord-callback/')
    print(f"   {localhost_uri}")
    
    # Production (Render)
    print("\n📍 FOR RENDER DEPLOYMENT:")
    print("   Replace 'your-service' with your actual Render service name")
    print("   " + "─" * 55)
    
    render_domain = os.getenv('RENDER_EXTERNAL_URL', '')
    if render_domain:
        print(f"   auto-detected: {render_domain.rstrip('/')}/apply/discord-callback/")
        print(f"   ✅ This will be used automatically")
    else:
        print("   https://your-service.onrender.com/apply/discord-callback/")
        print("   ⚠️  Set RENDER_EXTERNAL_URL in Render environment")
    
    # Instructions
    print("\n" + "="*70)
    print("📝 STEPS TO FIX:")
    print("="*70)
    print("""
1. Copy one of the URIs above (depending on where you're testing)

2. Go to Discord Developer Portal:
   https://discord.com/developers/applications

3. Select your application

4. Go to OAuth2 → General

5. Find "Redirects" section

6. Click "Add Redirect"

7. Paste the URI you copied (MUST match exactly)

8. Save

9. Test again - should work now!

⚠️  IMPORTANT:
   ✓ Must match EXACTLY (including protocol, domain, and path)
   ✓ No trailing spaces
   ✓ Include the trailing /
   ✓ Use HTTP:// for local, HTTPS:// for production
""")
    
    # Environment check
    print("="*70)
    print("🔧 ENVIRONMENT VARIABLES:")
    print("="*70)
    
    client_id = os.getenv('DISCORD_CLIENT_ID', '').strip()
    client_secret = os.getenv('DISCORD_CLIENT_SECRET', '').strip()
    
    print(f"   DISCORD_CLIENT_ID: {'✅ Set' if client_id else '❌ Not set'}")
    print(f"   DISCORD_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Not set'}")
    print(f"   RENDER_EXTERNAL_URL: {os.getenv('RENDER_EXTERNAL_URL', 'Not set')}")
    
    if not client_id or not client_secret:
        print("\n   ⚠️  Missing credentials! Add them to .env file")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    get_redirect_uris()
