"""
Launch the interactive research streams dashboard in the default browser.
"""

import webbrowser
import os
from pathlib import Path

def main():
    """Launch the dashboard."""
    print("🚀 Launching Research Streams Dashboard...")
    
    # Check if dashboard exists
    dashboard_path = Path("research_streams_dashboard.html")
    
    if not dashboard_path.exists():
        print("❌ Dashboard not found! Please run:")
        print("   python generate_dashboard.py")
        return
    
    # Get absolute path
    abs_path = dashboard_path.absolute()
    
    print(f"📂 Opening: {abs_path}")
    
    # Open in default browser
    webbrowser.open(f"file://{abs_path}")
    
    print("🌐 Dashboard opened in your default browser!")
    print("\n📋 Available Pages:")
    print("   • Main Dashboard: research_streams_dashboard.html")
    print("   • All Streams: all_streams.html")
    print("   • Methodology: methodology.html")
    print("   • Individual Streams: stream_0.html, stream_1.html, etc.")
    
    print("\n🎯 What you can explore:")
    print("   • Interactive charts and visualizations")
    print("   • Detailed research stream analysis")
    print("   • Comprehensive methodology documentation")
    print("   • Individual paper listings by stream")
    print("   • Temporal trends and journal distributions")

if __name__ == "__main__":
    main()
