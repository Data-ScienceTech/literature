"""
Launch the IS Research Streams Dashboard in the default browser.
"""

import webbrowser
import os
from pathlib import Path
import http.server
import socketserver
import threading
import time

def main():
    """Launch the dashboard."""
    print("🚀 LAUNCHING IS RESEARCH STREAMS DASHBOARD")
    print("="*60)
    
    # Check if dashboard exists
    dashboard_path = Path("dashboard.html")
    
    if not dashboard_path.exists():
        print("❌ Dashboard not found! Looking for dashboard.html...")
        return
    
    # Get absolute path
    abs_path = dashboard_path.absolute()
    
    print(f"\n📂 Dashboard location: {abs_path}")
    print("\n📊 Opening dashboard in your default browser...")
    
    # Open in default browser
    webbrowser.open(f"file:///{abs_path.as_posix()}")
    
    print("\n✅ Dashboard opened successfully!")
    print("\n" + "="*60)
    print("� DASHBOARD FEATURES:")
    print("  • 📈 Interactive research stream explorer")
    print("  • 🔍 Real-time search and filtering")
    print("  • 📊 Visual analytics and charts")
    print("  • 📚 Top papers and citations")
    print("  • 🔥 Emerging topics tracking")
    print("  • ⭐ Most impactful streams")
    
    print("\n💡 NAVIGATION TIPS:")
    print("  • Use tabs to switch between different views")
    print("  • Search box to find specific topics")
    print("  • Filter buttons to show specific stream types")
    print("  • Click stream cards for detailed information")
    
    print("\n" + "="*60)
    print("✨ Enjoy exploring your IS research insights!")
    print("="*60)
    
    # Offer to run local server
    print("\n� Optional: Run local web server for enhanced experience?")
    print("   (Better image loading, no CORS issues)")
    run_server = input("   Start server? (y/n): ").lower().strip()
    
    if run_server == 'y':
        PORT = 8000
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(Path.cwd()), **kwargs)
            
            def log_message(self, format, *args):
                pass  # Suppress logging
        
        print(f"\n🌐 Starting local server on http://localhost:{PORT}")
        print(f"📊 Dashboard URL: http://localhost:{PORT}/dashboard.html")
        print("\n   Press Ctrl+C to stop the server...")
        
        # Open server version
        time.sleep(0.5)
        webbrowser.open(f"http://localhost:{PORT}/dashboard.html")
        
        try:
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Thanks for exploring!")
        except OSError as e:
            print(f"\n⚠️  Port {PORT} already in use. Dashboard still accessible via file:// URL")

if __name__ == "__main__":
    main()
