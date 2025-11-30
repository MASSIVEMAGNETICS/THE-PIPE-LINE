"""
🚀 THE-PIPE-LINE Desktop Launcher 🚀

Windows 10 / Cross-platform desktop application launcher.
Opens the web application in a native window using the default browser
or a webview if available.
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path


def find_available_port(start_port: int = 5000, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port."""
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise RuntimeError("No available port found")


def launch_browser(port: int, delay: float = 1.5):
    """Launch browser after a delay."""
    time.sleep(delay)
    url = f"http://localhost:{port}"
    print(f"\n🌐 Opening browser at {url}")
    webbrowser.open(url)


def main():
    """Main desktop application entry point."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🚀 THE-PIPE-LINE - AI Music Video Generator 🚀                 ║
║                                                                  ║
║   Production-Ready Desktop Application                           ║
║   Windows 10 / macOS / Linux Compatible                          ║
║                                                                  ║
║   © 2024 MASSIVEMAGNETICS - All Rights Reserved                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Find available port
    port = find_available_port()
    print(f"✅ Found available port: {port}")
    
    # Import and start the web application
    from .webapp.app import run_server
    
    # Launch browser in background thread
    browser_thread = threading.Thread(target=launch_browser, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start server (this blocks)
    print("\n🚀 Starting THE-PIPE-LINE server...")
    print("Press Ctrl+C to stop\n")
    
    try:
        run_server(host='127.0.0.1', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 THE-PIPE-LINE shutting down. Goodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
