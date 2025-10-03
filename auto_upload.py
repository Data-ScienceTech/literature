"""
🚀 Automated Upload Script for research.datasciencetech.ca
Multiple upload methods with credential management
"""

import os
import sys
import ftplib
import json
from pathlib import Path
from getpass import getpass
import time

class UploadAutomation:
    """Automated upload to research.datasciencetech.ca"""
    
    def __init__(self):
        self.deploy_dir = Path('deploy')
        self.config_file = Path('upload_config.json')
        self.credentials = {}
        
    def load_or_create_config(self):
        """Load saved credentials or create new config."""
        print("\n" + "="*60)
        print("🔐 FTP CREDENTIALS CONFIGURATION")
        print("="*60)
        
        if self.config_file.exists():
            print("\n📋 Found existing configuration file.")
            use_saved = input("Use saved credentials? (y/n): ").lower().strip()
            
            if use_saved == 'y':
                with open(self.config_file, 'r') as f:
                    self.credentials = json.load(f)
                print("✅ Loaded saved credentials")
                return True
        
        print("\n📝 Let's set up your FTP credentials...")
        print("(You can find these in your hosting provider's cPanel)")
        
        self.credentials = {
            'host': input("\nFTP Server (e.g., ftp.datasciencetech.ca): ").strip(),
            'username': input("FTP Username: ").strip(),
            'password': getpass("FTP Password (hidden): "),
            'port': input("FTP Port (default 21): ").strip() or "21",
            'remote_path': input("Remote path (e.g., /public_html/research/): ").strip()
        }
        
        save = input("\n💾 Save credentials for future use? (y/n): ").lower().strip()
        if save == 'y':
            # Save without password for security
            save_data = self.credentials.copy()
            save_data['password'] = '***SAVED_LOCALLY***'
            with open(self.config_file, 'w') as f:
                json.dump(self.credentials, f, indent=2)
            print("✅ Credentials saved to upload_config.json")
        
        return True
    
    def test_connection(self):
        """Test FTP connection before upload."""
        print("\n" + "="*60)
        print("🔌 TESTING FTP CONNECTION")
        print("="*60)
        
        try:
            print(f"\nConnecting to {self.credentials['host']}...")
            
            ftp = ftplib.FTP()
            ftp.connect(self.credentials['host'], int(self.credentials['port']))
            ftp.login(self.credentials['username'], self.credentials['password'])
            
            print("✅ Connected successfully!")
            
            # Try to change to remote directory
            try:
                ftp.cwd(self.credentials['remote_path'])
                print(f"✅ Found remote directory: {self.credentials['remote_path']}")
            except Exception as e:
                print(f"⚠️  Remote directory not found: {self.credentials['remote_path']}")
                print(f"   Will attempt to create it during upload...")
            
            ftp.quit()
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nPlease check:")
            print("  - FTP server address is correct")
            print("  - Username and password are correct")
            print("  - Port is correct (usually 21)")
            print("  - Your firewall allows FTP connections")
            return False
    
    def create_remote_directory(self, ftp, path):
        """Create remote directory if it doesn't exist."""
        try:
            ftp.cwd(path)
        except:
            print(f"📁 Creating remote directory: {path}")
            try:
                # Try to create parent directories
                parts = path.strip('/').split('/')
                current = ''
                for part in parts:
                    current += '/' + part
                    try:
                        ftp.cwd(current)
                    except:
                        try:
                            ftp.mkd(current)
                            print(f"   Created: {current}")
                        except:
                            pass
            except Exception as e:
                print(f"⚠️  Could not create directory: {e}")
    
    def upload_files(self):
        """Upload all files via FTP."""
        print("\n" + "="*60)
        print("📤 UPLOADING FILES TO RESEARCH.DATASCIENCETECH.CA")
        print("="*60)
        
        if not self.deploy_dir.exists():
            print(f"\n❌ Deploy directory not found: {self.deploy_dir}")
            print("   Run: python deploy_to_web.py first")
            return False
        
        files = list(self.deploy_dir.glob('*'))
        files = [f for f in files if f.is_file()]
        
        if not files:
            print(f"\n❌ No files found in {self.deploy_dir}")
            return False
        
        print(f"\n📋 Found {len(files)} files to upload")
        print(f"🎯 Target: {self.credentials['host']}{self.credentials['remote_path']}")
        print()
        
        proceed = input("Proceed with upload? (y/n): ").lower().strip()
        if proceed != 'y':
            print("Upload cancelled.")
            return False
        
        try:
            # Connect to FTP
            print(f"\n🔌 Connecting to {self.credentials['host']}...")
            ftp = ftplib.FTP()
            ftp.connect(self.credentials['host'], int(self.credentials['port']))
            ftp.login(self.credentials['username'], self.credentials['password'])
            print("✅ Connected!")
            
            # Create/navigate to remote directory
            self.create_remote_directory(ftp, self.credentials['remote_path'])
            ftp.cwd(self.credentials['remote_path'])
            
            # Upload files
            success_count = 0
            failed_count = 0
            
            print(f"\n📤 Uploading files...")
            print("-" * 60)
            
            for file in files:
                try:
                    print(f"📄 {file.name}...", end=' ')
                    
                    with open(file, 'rb') as f:
                        ftp.storbinary(f'STOR {file.name}', f)
                    
                    print("✅")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed: {e}")
                    failed_count += 1
            
            ftp.quit()
            
            # Summary
            print("-" * 60)
            print(f"\n✅ Upload Complete!")
            print(f"   Successful: {success_count}/{len(files)}")
            if failed_count > 0:
                print(f"   Failed: {failed_count}/{len(files)}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Upload failed: {e}")
            return False
    
    def verify_deployment(self):
        """Provide verification steps."""
        print("\n" + "="*60)
        print("✅ VERIFICATION STEPS")
        print("="*60)
        
        base_url = "https://research.datasciencetech.ca"
        
        print(f"\n🌐 Your dashboard should now be live!")
        print(f"\nTest these URLs:")
        print(f"  1. Main page: {base_url}/")
        print(f"  2. Papers DB: {base_url}/papers_database.html")
        print(f"  3. All streams: {base_url}/all_streams.html")
        print(f"  4. Methodology: {base_url}/methodology.html")
        print(f"  5. Stream 0: {base_url}/stream_0.html")
        
        print(f"\n📋 Checklist:")
        print(f"  [ ] Main page loads")
        print(f"  [ ] Navigation works")
        print(f"  [ ] Search functions")
        print(f"  [ ] Charts display")
        print(f"  [ ] Mobile responsive")
        
        print(f"\n🎉 Congratulations! Your dashboard is live!")
    
    def run(self):
        """Run the automated upload process."""
        print("\n" + "="*60)
        print("🚀 AUTOMATED UPLOAD TO RESEARCH.DATASCIENCETECH.CA")
        print("="*60)
        print()
        
        try:
            # Step 1: Load/create config
            if not self.load_or_create_config():
                return False
            
            # Step 2: Test connection
            if not self.test_connection():
                print("\n❌ Cannot proceed without valid FTP connection")
                retry = input("\nRetry with different credentials? (y/n): ").lower().strip()
                if retry == 'y':
                    self.config_file.unlink(missing_ok=True)
                    return self.run()
                return False
            
            # Step 3: Upload files
            if not self.upload_files():
                return False
            
            # Step 4: Verification
            self.verify_deployment()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Upload cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main upload automation."""
    uploader = UploadAutomation()
    success = uploader.run()
    
    if success:
        print("\n✅ Upload successful!")
        return 0
    else:
        print("\n❌ Upload failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
