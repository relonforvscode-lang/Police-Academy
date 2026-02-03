#!/usr/bin/env python
"""
Render Deployment Verification Script

استخدم هذا السكريبت للتحقق من أن المشروع جاهز للنشر على Render
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print("=" * 60)
print("Render Deployment Verification")
print("=" * 60)

checks = []

# 1. Check requirements.txt
print("\n+ requirements.txt")
req_file = BASE_DIR / "requirements.txt"
if req_file.exists():
    with open(req_file) as f:
        content = f.read()
        checks.append(("requirements.txt exists", True))
        checks.append(("gunicorn in requirements", "gunicorn" in content))
        checks.append(("psycopg2 in requirements", "psycopg2" in content))
        checks.append(("dj-database-url in requirements", "dj-database-url" in content))
        checks.append(("python-dotenv in requirements", "python-dotenv" in content))
else:
    checks.append(("requirements.txt exists", False))

# 2. Check Procfile
print("+ Procfile")
procfile = BASE_DIR / "Procfile"
if procfile.exists():
    with open(procfile) as f:
        content = f.read()
        checks.append(("Procfile exists", True))
        checks.append(("web command in Procfile", "web:" in content))
        checks.append(("gunicorn in Procfile", "gunicorn" in content))
else:
    checks.append(("Procfile exists", False))

# 3. Check runtime.txt
print("+ runtime.txt")
runtime = BASE_DIR / "runtime.txt"
if runtime.exists():
    checks.append(("runtime.txt exists", True))
else:
    checks.append(("runtime.txt exists", False))

# 4. Check render.yaml
print("+ render.yaml")
render_yaml = BASE_DIR / "render.yaml"
if render_yaml.exists():
    checks.append(("render.yaml exists", True))
else:
    checks.append(("render.yaml exists", False))

# 5. Check .env.example
print("+ .env.example")
env_example = BASE_DIR / ".env.example"
if env_example.exists():
    checks.append((".env.example exists", True))
else:
    checks.append((".env.example exists", False))

# 6. Check settings.py
print("+ settings.py")
settings = BASE_DIR / "myproject" / "settings.py"
if settings.exists():
    with open(settings) as f:
        content = f.read()
        checks.append(("settings.py exists", True))
        checks.append(("dj_database_url imported", "dj_database_url" in content))
        checks.append(("load_dotenv used", "load_dotenv" in content))
        checks.append(("ALLOWED_HOSTS configured", "ALLOWED_HOSTS" in content))
        checks.append(("STATIC_ROOT configured", "STATIC_ROOT" in content))
        checks.append(("DEBUG from environment", "os.getenv('DEBUG'" in content))
else:
    checks.append(("settings.py exists", False))

# 7. Check build directory
print("+ build directory")
build_dir = BASE_DIR / "build"
if build_dir.exists():
    checks.append(("build directory exists", True))
    build_script = build_dir / "build.sh"
    checks.append(("build.sh exists", build_script.exists()))
else:
    checks.append(("build directory exists", False))

# Print results
print("\n" + "=" * 60)
print("📋 Verification Results:")
print("=" * 60)

passed = 0
failed = 0

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if result:
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 60)

if failed == 0:
    print("\n🎉 All checks passed! Ready for Render deployment.")
    sys.exit(0)
else:
    print(f"\n⚠️  {failed} check(s) failed. Please fix before deploying.")
    sys.exit(1)
