"""
🚀 Automated GitHub Pages Deployment
Deploy your Research Streams Dashboard to GitHub Pages (FREE hosting)
"""

import os
import sys
import subprocess
from pathlib import Path
import json
from datetime import datetime

class GitHubPagesDeployment:
    """Automated deployment to GitHub Pages"""
    
    def __init__(self):
        self.deploy_dir = Path('deploy')
        self.repo_name = 'research-streams'
        self.branch = 'gh-pages'
        
    def check_git_installed(self):
        """Check if git is installed."""
        print("\n" + "="*60)
        print("🔍 CHECKING PREREQUISITES")
        print("="*60)
        
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Git installed: {result.stdout.strip()}")
                return True
            else:
                print("❌ Git not found")
                return False
        except FileNotFoundError:
            print("❌ Git is not installed")
            print("\n📥 Please install Git:")
            print("   Download from: https://git-scm.com/download/win")
            return False
    
    def check_github_auth(self):
        """Check GitHub authentication."""
        print("\n🔐 Checking GitHub authentication...")
        
        try:
            result = subprocess.run(
                ['git', 'config', 'user.name'],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                print(f"✅ Git user configured: {result.stdout.strip()}")
                return True
            else:
                print("⚠️  Git user not configured")
                return self.configure_git()
                
        except Exception as e:
            print(f"❌ Error checking git config: {e}")
            return False
    
    def configure_git(self):
        """Configure git user."""
        print("\n📝 Let's configure your Git identity...")
        
        name = input("Your name: ").strip()
        email = input("Your email: ").strip()
        
        try:
            subprocess.run(['git', 'config', '--global', 'user.name', name])
            subprocess.run(['git', 'config', '--global', 'user.email', email])
            print("✅ Git configured successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to configure git: {e}")
            return False
    
    def initialize_git_repo(self):
        """Initialize git repository if needed."""
        print("\n" + "="*60)
        print("📁 INITIALIZING GIT REPOSITORY")
        print("="*60)
        
        git_dir = Path('.git')
        
        if git_dir.exists():
            print("✅ Git repository already initialized")
            return True
        
        try:
            subprocess.run(['git', 'init'], check=True, capture_output=True)
            print("✅ Git repository initialized")
            
            # Create .gitignore
            gitignore_content = """# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class

# Data files
*.npy
*.pkl
*.csv
data/

# Environment
venv/
env/
ENV/

# Credentials
upload_config.json
*.pem
*.key

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Keep deploy folder but ignore zip
research_streams_dashboard.zip
"""
            
            with open('.gitignore', 'w') as f:
                f.write(gitignore_content)
            
            print("✅ Created .gitignore file")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize git: {e}")
            return False
    
    def prepare_gh_pages_branch(self):
        """Prepare gh-pages branch with deployment files."""
        print("\n" + "="*60)
        print("📦 PREPARING GITHUB PAGES DEPLOYMENT")
        print("="*60)
        
        if not self.deploy_dir.exists():
            print(f"❌ Deploy directory not found: {self.deploy_dir}")
            print("   Run: python deploy_to_web.py first")
            return False
        
        try:
            # Check if gh-pages branch exists
            result = subprocess.run(
                ['git', 'rev-parse', '--verify', 'gh-pages'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ gh-pages branch exists")
                # Checkout existing branch
                subprocess.run(['git', 'checkout', 'gh-pages'], check=True, capture_output=True)
            else:
                print("📝 Creating gh-pages branch...")
                # Create orphan branch (no history)
                subprocess.run(['git', 'checkout', '--orphan', 'gh-pages'], check=True, capture_output=True)
                # Remove all files from staging
                subprocess.run(['git', 'rm', '-rf', '.'], capture_output=True)
            
            print("✅ On gh-pages branch")
            return True
            
        except Exception as e:
            print(f"❌ Failed to prepare branch: {e}")
            return False
    
    def copy_deploy_files(self):
        """Copy files from deploy/ to repository root."""
        print("\n📋 Copying deployment files...")
        
        try:
            import shutil
            
            # Copy all files from deploy/ to current directory
            for item in self.deploy_dir.iterdir():
                if item.is_file():
                    dest = Path(item.name)
                    shutil.copy2(item, dest)
                    print(f"  ✅ {item.name}")
            
            print("✅ All files copied")
            return True
            
        except Exception as e:
            print(f"❌ Failed to copy files: {e}")
            return False
    
    def commit_and_push(self, github_url):
        """Commit files and push to GitHub."""
        print("\n" + "="*60)
        print("📤 COMMITTING AND PUSHING TO GITHUB")
        print("="*60)
        
        try:
            # Add all files
            print("📝 Adding files to git...")
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            
            # Commit
            commit_msg = f"Deploy dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            print(f"💾 Committing: {commit_msg}")
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True)
            print("✅ Committed")
            
            # Add remote if needed
            result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
            if 'origin' not in result.stdout:
                print(f"🔗 Adding remote: {github_url}")
                subprocess.run(['git', 'remote', 'add', 'origin', github_url], check=True, capture_output=True)
            else:
                print("✅ Remote already configured")
            
            # Push
            print("🚀 Pushing to GitHub...")
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'gh-pages', '--force'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Pushed successfully!")
                return True
            else:
                print(f"❌ Push failed: {result.stderr}")
                if "authentication" in result.stderr.lower() or "permission" in result.stderr.lower():
                    print("\n🔐 Authentication required!")
                    print("   Please authenticate with GitHub (browser will open)")
                    print("   Or create a Personal Access Token:")
                    print("   https://github.com/settings/tokens")
                return False
                
        except Exception as e:
            print(f"❌ Failed to commit/push: {e}")
            return False
    
    def show_github_pages_instructions(self, username, repo_name):
        """Show instructions for enabling GitHub Pages."""
        print("\n" + "="*60)
        print("🌐 ENABLE GITHUB PAGES")
        print("="*60)
        
        print(f"\n📋 Follow these steps:")
        print(f"\n1. Go to your repository:")
        print(f"   https://github.com/{username}/{repo_name}")
        
        print(f"\n2. Click 'Settings' tab")
        
        print(f"\n3. Click 'Pages' in left sidebar")
        
        print(f"\n4. Under 'Source':")
        print(f"   - Branch: gh-pages")
        print(f"   - Folder: / (root)")
        print(f"   - Click 'Save'")
        
        print(f"\n5. Wait 2-3 minutes for deployment")
        
        print(f"\n6. Your dashboard will be live at:")
        print(f"   https://{username}.github.io/{repo_name}/")
        
        print(f"\n" + "="*60)
        print(f"🎉 OPTIONAL: CUSTOM DOMAIN")
        print("="*60)
        
        print(f"\nTo use research.datasciencetech.ca:")
        
        print(f"\n1. In GitHub Pages settings:")
        print(f"   - Custom domain: research.datasciencetech.ca")
        print(f"   - Click 'Save'")
        
        print(f"\n2. In Squarespace DNS Settings:")
        print(f"   - Add CNAME record:")
        print(f"     Host: research")
        print(f"     Points to: {username}.github.io")
        
        print(f"\n3. Wait 15-30 minutes for DNS propagation")
        
        print(f"\n4. Your dashboard will be at:")
        print(f"   https://research.datasciencetech.ca/")
        
    def run(self):
        """Run complete GitHub Pages deployment."""
        print("\n" + "="*70)
        print(" " * 15 + "🚀 GITHUB PAGES DEPLOYMENT")
        print(" " * 10 + "Free hosting for your Research Streams Dashboard")
        print("="*70)
        
        # Check prerequisites
        if not self.check_git_installed():
            return False
        
        if not self.check_github_auth():
            return False
        
        # Get GitHub details
        print("\n" + "="*60)
        print("📝 GITHUB REPOSITORY INFORMATION")
        print("="*60)
        
        print("\nYou'll need a GitHub repository for hosting.")
        print("Don't have one? Create it at: https://github.com/new")
        print()
        
        username = input("Your GitHub username: ").strip()
        
        use_default_name = input(f"Use repository name '{self.repo_name}'? (y/n): ").lower().strip()
        if use_default_name != 'y':
            self.repo_name = input("Repository name: ").strip()
        
        github_url = f"https://github.com/{username}/{self.repo_name}.git"
        
        print(f"\n✅ Repository: {github_url}")
        
        # Initialize git
        if not self.initialize_git_repo():
            return False
        
        # Prepare gh-pages branch
        if not self.prepare_gh_pages_branch():
            return False
        
        # Copy files
        if not self.copy_deploy_files():
            return False
        
        # Commit and push
        if not self.commit_and_push(github_url):
            print("\n⚠️  Push failed. You may need to:")
            print("   1. Create the repository on GitHub first")
            print("   2. Authenticate with GitHub")
            print("   3. Try again")
            return False
        
        # Show instructions
        self.show_github_pages_instructions(username, self.repo_name)
        
        # Return to main branch
        try:
            subprocess.run(['git', 'checkout', 'main'], capture_output=True)
        except:
            pass
        
        print("\n" + "="*60)
        print("✅ DEPLOYMENT COMPLETE!")
        print("="*60)
        print(f"\n🌐 Your dashboard will be live in 2-3 minutes at:")
        print(f"   https://{username}.github.io/{self.repo_name}/")
        print()
        
        return True


def main():
    """Main GitHub Pages deployment."""
    deployer = GitHubPagesDeployment()
    success = deployer.run()
    
    if success:
        print("✅ GitHub Pages deployment successful!")
        return 0
    else:
        print("❌ GitHub Pages deployment failed!")
        print("\nTry manual deployment with Netlify Drop instead:")
        print("   1. Go to: https://app.netlify.com/drop")
        print("   2. Drag research_streams_dashboard.zip")
        print("   3. Done!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
