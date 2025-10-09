#!/usr/bin/env python3
"""
Quick script to check current environment configuration
Run this to verify which environment the application will use
"""

import json
from app.config import (
    get_environment, 
    get_environment_info, 
    get_config,
    is_local,
    is_mirror,
    is_render,
    requires_auth
)

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_feature_table(features):
    """Print features in a formatted table"""
    print("\n{:<30} {:>10}".format("Feature", "Status"))
    print("-" * 42)
    for feature, enabled in features.items():
        status = "✅ Enabled" if enabled else "❌ Disabled"
        print("{:<30} {:>10}".format(feature.replace('_', ' ').title(), status))

def main():
    """Display comprehensive environment information"""
    
    # Get environment info
    env = get_environment()
    env_info = get_environment_info()
    config = get_config()
    
    # Header
    print_section("🚀 DOOR APPLICATION - ENVIRONMENT CHECK")
    
    # Current Environment
    print(f"\n🌍 Current Environment: {env.upper()}")
    print(f"   {env_info['environment_name']}")
    print(f"   {env_info['description']}")
    
    # Environment Indicators
    print_section("🔍 ENVIRONMENT DETECTION")
    print("\nEnvironment Type Checks:")
    print(f"  ├─ LOCAL:  {'✅ YES' if is_local() else '❌ NO'}")
    print(f"  ├─ MIRROR: {'✅ YES' if is_mirror() else '❌ NO'}")
    print(f"  └─ RENDER: {'✅ YES' if is_render() else '❌ NO'}")
    
    # Detection Info
    detection = env_info['detection_info']
    print("\nDetection Information:")
    print(f"  ├─ Hostname: {detection['hostname']}")
    print(f"  ├─ Port: {detection['port']}")
    print(f"  ├─ Main File: {detection['main_file']}")
    print(f"  ├─ Working Directory: {detection['working_directory']}")
    print(f"  ├─ RENDER env var: {'✅ Set' if detection['render_env_var'] else '❌ Not set'}")
    print(f"  ├─ Neon Database: {'✅ Configured' if detection['neon_host'] else '❌ Not configured'}")
    print(f"  └─ USE_NEON: {detection['use_neon']}")
    
    # Configuration
    print_section("⚙️  CONFIGURATION")
    print(f"\n📊 Database: {config['database']}")
    print(f"🔌 Port: {config['port']}")
    print(f"🏠 Host: {config['host']}")
    print(f"🔐 Authentication: {'✅ REQUIRED' if config['authentication_required'] else '❌ Disabled'}")
    print(f"🐛 Debug Mode: {'✅ Enabled' if config['debug'] else '❌ Disabled'}")
    print(f"🔄 Auto Reload: {'✅ Enabled' if config['auto_reload'] else '❌ Disabled'}")
    print(f"🌐 Access: {config['access']}")
    
    # Features
    print_section("🎛️  FEATURES")
    print_feature_table(config['features'])
    
    # Restrictions
    print_section("🚫 RESTRICTIONS")
    restrictions = config['restrictions']
    print("\n{:<30} {:>20}".format("Area", "Restriction"))
    print("-" * 52)
    for area, restriction in restrictions.items():
        print("{:<30} {:>20}".format(area.replace('_', ' ').title(), restriction))
    
    # Recommendations
    print_section("💡 RECOMMENDATIONS")
    
    if is_local():
        print("\n✅ LOCAL Development Environment Detected")
        print("  • Perfect for development and testing")
        print("  • Database sync will run automatically on startup")
        print("  • No authentication required")
        print("  • Hot reload enabled for fast development")
        print("\n🚀 Start with: python main.py")
        
    elif is_mirror():
        print("\n✅ MIRROR Production Environment Detected")
        print("  • Internal production server")
        print("  • Use stable features only")
        print("  • Database can sync with LOCAL")
        print("  • No authentication (trusted network)")
        print("\n🚀 Deploy with: docker-compose -f deployment/docker-compose.mirror.yml up -d")
        
    elif is_render():
        print("\n✅ RENDER Cloud Environment Detected")
        print("  • Public cloud deployment")
        print("  • Authentication REQUIRED on all pages")
        print("  • Uses Neon cloud database")
        print("  • SSL enabled automatically")
        print("\n⚠️  Make sure to configure:")
        print("  • NEON_HOST, NEON_USER, NEON_PASSWORD")
        print("  • AUTH_USERNAME, AUTH_PASSWORD")
        print("  • SECRET_KEY (use strong random value)")
    
    # Footer
    print_section("📚 DOCUMENTATION")
    print("\n  • README.md - Project overview and quick reference")
    print("  • docs/DEPLOYMENT_GUIDE.md - Complete deployment guide")
    print("  • docs/QUICK_START.md - Quick start and common tasks")
    print("  • docs/REORGANIZATION_SUMMARY.md - Project reorganization")
    print("  • deployment/README.md - Deployment files documentation")
    print("  • docs/ - All documentation (13 files)")
    
    print("\n" + "="*80)
    print("  ✨ Environment check complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

