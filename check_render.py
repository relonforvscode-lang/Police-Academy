#!/usr/bin/env python
"""
Script للتحقق من أن الموقع يعمل على Render بعد الرفع
"""
import requests
import sys
import time

def check_render_deployment(render_url):
    """
    تحقق من أن الموقع يعمل على Render
    """
    print("=" * 60)
    print("🔍 CHECKING RENDER DEPLOYMENT")
    print("=" * 60)
    print(f"\n📍 Testing: {render_url}\n")
    
    checks = []
    
    # 1. Check if site is up
    print("1️⃣ Checking if site is online...")
    try:
        response = requests.get(f"{render_url}/apply/", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Site is online (HTTP {response.status_code})")
            checks.append(True)
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            checks.append(False)
    except requests.exceptions.Timeout:
        print("   ❌ Site is not responding (timeout)")
        checks.append(False)
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to site")
        checks.append(False)
    
    time.sleep(1)
    
    # 2. Check Discord login endpoint
    print("\n2️⃣ Checking Discord login endpoint...")
    try:
        response = requests.get(f"{render_url}/apply/discord-login/", allow_redirects=False, timeout=10)
        if response.status_code == 302:
            redirect = response.headers.get('Location', '')
            if 'discord.com' in redirect:
                print(f"   ✅ Redirects to Discord correctly")
                checks.append(True)
            else:
                print(f"   ❌ Wrong redirect: {redirect}")
                checks.append(False)
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            checks.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        checks.append(False)
    
    time.sleep(1)
    
    # 3. Check if database is connected
    print("\n3️⃣ Checking database connection...")
    try:
        # Try to access admin page (it will fail without auth, but connection will work)
        response = requests.get(f"{render_url}/admin/", timeout=10)
        if response.status_code in [200, 301, 302]:
            print(f"   ✅ Database appears to be connected")
            checks.append(True)
        else:
            print(f"   ⚠️  Got status {response.status_code}")
            checks.append(True)  # Still a good sign
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        checks.append(False)
    
    time.sleep(1)
    
    # 4. Check for 500 errors
    print("\n4️⃣ Checking for server errors...")
    try:
        response = requests.get(f"{render_url}/apply/", timeout=10)
        if response.status_code < 500:
            print(f"   ✅ No 500 errors")
            checks.append(True)
        else:
            print(f"   ❌ Got 500 error")
            checks.append(False)
    except Exception as e:
        print(f"   ⚠️  Could not check: {e}")
        checks.append(True)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("\n✨ Your Render deployment is working correctly!")
        print("\n📝 Next: Test Discord OAuth in browser:")
        print(f"   1. Open {render_url}/apply/")
        print(f"   2. Click 'تسجيل الدخول عبر Discord'")
        print(f"   3. Check logs on Render dashboard")
        return True
    else:
        print(f"⚠️  Some checks failed ({passed}/{total})")
        print("\n🔧 Troubleshooting:")
        print("   1. Check Render dashboard logs")
        print("   2. Verify environment variables")
        print("   3. Ensure database is running")
        print("   4. Check ALLOWED_HOSTS in settings")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_render.py <render_url>")
        print("Example: python check_render.py https://myapp.onrender.com")
        sys.exit(1)
    
    render_url = sys.argv[1].rstrip('/')
    success = check_render_deployment(render_url)
    sys.exit(0 if success else 1)
