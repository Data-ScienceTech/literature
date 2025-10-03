"""
🚀 ONE-CLICK DEPLOYMENT: Prepare & Upload to research.datasciencetech.ca
Complete automation - from files to live website
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print welcome banner."""
    print("\n" + "="*70)
    print(" " * 15 + "🚀 ONE-CLICK DEPLOYMENT AUTOMATION")
    print(" " * 10 + "research.datasciencetech.ca")
    print("="*70)
    print()

def check_prerequisites():
    """Check if required files exist."""
    print("📋 Checking prerequisites...")
    
    required_files = [
        'research_streams_dashboard.html',
        'all_streams.html',
        'papers_database.html',
        'methodology.html'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print("❌ Missing required files:")
        for file in missing:
            print(f"   - {file}")
        print("\nPlease generate your dashboard first.")
        return False
    
    print("✅ All required files found")
    return True

def run_deployment_prep():
    """Run deployment preparation script."""
    print("\n" + "="*70)
    print("STEP 1: Preparing Deployment Package")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, 'deploy_to_web.py'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Deployment package prepared successfully!")
            return True
        else:
            print("\n❌ Deployment preparation failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during preparation: {e}")
        return False

def run_upload():
    """Run upload script."""
    print("\n" + "="*70)
    print("STEP 2: Uploading to Server")
    print("="*70)
    print()
    
    upload_method = input("""Choose upload method:
  1. Python FTP upload (interactive, cross-platform)
  2. PowerShell upload (Windows, enhanced features)
  3. Skip upload (I'll upload manually)
  
Enter choice (1-3): """).strip()
    
    if upload_method == '1':
        # Python FTP upload
        try:
            result = subprocess.run(
                [sys.executable, 'auto_upload.py'],
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"\n❌ Upload failed: {e}")
            return False
            
    elif upload_method == '2':
        # PowerShell upload
        try:
            print("\n🔄 Launching PowerShell upload script...")
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'upload_interactive.ps1'],
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"\n❌ PowerShell upload failed: {e}")
            print("   Try running: .\\upload_interactive.ps1 manually")
            return False
            
    elif upload_method == '3':
        print("\n📦 Upload skipped.")
        print("   Files are ready in deploy/ folder")
        print("   Upload manually using:")
        print("     - cPanel File Manager")
        print("     - FileZilla FTP client")
        print("     - Your preferred method")
        return True
        
    else:
        print("\n❌ Invalid choice")
        return False

def show_summary():
    """Show deployment summary."""
    print("\n" + "="*70)
    print("✅ DEPLOYMENT SUMMARY")
    print("="*70)
    
    deploy_dir = Path('deploy')
    if deploy_dir.exists():
        files = list(deploy_dir.glob('*'))
        print(f"\n📁 Deployment package: {deploy_dir.absolute()}")
        print(f"📄 Total files: {len(files)}")
        
        zip_file = Path('research_streams_dashboard.zip')
        if zip_file.exists():
            size_mb = zip_file.stat().st_size / (1024 * 1024)
            print(f"📦 ZIP package: {zip_file.name} ({size_mb:.2f} MB)")
    
    print("\n🌐 Your live URLs:")
    base_url = "https://research.datasciencetech.ca"
    print(f"   Main: {base_url}/")
    print(f"   Papers: {base_url}/papers_database.html")
    print(f"   Streams: {base_url}/all_streams.html")
    print(f"   Methods: {base_url}/methodology.html")
    
    print("\n📋 Next steps:")
    print("   1. Visit your live site")
    print("   2. Test all pages load correctly")
    print("   3. Verify search functionality")
    print("   4. Share your dashboard!")
    
    print("\n🎉 Your Research Streams Dashboard is ready!")
    print("="*70 + "\n")

def main():
    """Main one-click deployment."""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    print()
    proceed = input("🚀 Ready to deploy to research.datasciencetech.ca? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Deployment cancelled.")
        return 0
    
    # Step 1: Prepare deployment
    if not run_deployment_prep():
        print("\n❌ Deployment preparation failed. Please check errors above.")
        return 1
    
    # Step 2: Upload
    if not run_upload():
        print("\n⚠️  Upload step incomplete.")
        print("   Files are prepared in deploy/ folder.")
        print("   You can upload manually or run: python auto_upload.py")
    
    # Show summary
    show_summary()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
