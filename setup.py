#!/usr/bin/env python3
"""
Streamify - Quick Setup Script
Run this after installing requirements to set up the project.
"""
import os
import subprocess
import sys


def run(cmd, description=""):
    print(f"\n{'=' * 50}")
    if description:
        print(f"  {description}")
    print(f"  $ {cmd}")
    print('=' * 50)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"  ⚠️  Command failed (exit code {result.returncode})")
    return result.returncode == 0


def main():
    print("\n🎵 Streamify Setup Script")
    print("=" * 50)

    # Check if .env exists
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("\n✅ Created .env from .env.example")
            print("   ⚠️  Please edit .env and set your database credentials!")
            input("   Press Enter when ready to continue...")
        else:
            print("❌ .env.example not found!")
            sys.exit(1)

    # Run migrations
    run("python manage.py makemigrations", "Creating migrations")
    run("python manage.py migrate", "Running database migrations")

    # Load initial data
    run("python manage.py loaddata initial_data.json", "Loading initial genres and subscription plans")

    # Collect static files
    run("python manage.py collectstatic --noinput", "Collecting static files")

    # Create superuser
    print("\n" + "=" * 50)
    print("  Creating Admin User")
    print("=" * 50)
    run("python manage.py createsuperuser", "Create your admin account")

    print("\n" + "=" * 50)
    print("✅ Setup Complete!")
    print("=" * 50)
    print("\nStart the development server with:")
    print("  python manage.py runserver")
    print("\nThen visit:")
    print("  http://localhost:8000         - Main site")
    print("  http://localhost:8000/admin/  - Admin panel")
    print("  http://localhost:8000/api/v1/ - REST API")
    print()


if __name__ == '__main__':
    main()
