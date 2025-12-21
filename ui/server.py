#!/usr/bin/env python3
"""
Simple HTTP Server for The Twilight Zone Episode Viewer
Properly handles MIME types for all files and serves video files
Usage: python server.py
"""

import http.server
import socketserver
import webbrowser
import os
import urllib.parse
from pathlib import Path

PORT = 8000

# Chemin de base pour les vidéos (modifiez selon votre configuration)
# Par défaut, utilise le chemin réseau Windows
# Vous pouvez aussi utiliser un chemin local comme: r"C:\Videos\Twilight Zone"
# ou un chemin relatif depuis le dossier ui: r"..\videos"
VIDEO_BASE_PATH = r"\\Freebox_Server\Videos\Series\Twilight Zone"

class TwilightZoneHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with proper MIME types and video serving"""

    extensions_map = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'text/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
        '.ttf': 'font/ttf',
        '.eot': 'application/vnd.ms-fontobject',
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.ogg': 'video/ogg',
        '': 'application/octet-stream',
    }

    def do_GET(self):
        """Handle GET requests, including video API endpoint"""
        # Handle video API endpoint
        if self.path.startswith('/api/video/'):
            self.handle_video_request()
            return
        
        # Default file serving
        super().do_GET()

    def handle_video_request(self):
        """Handle video file requests from the API endpoint"""
        try:
            # Extract filename from path and decode URL encoding
            raw_path = self.path.replace('/api/video/', '')
            filename = urllib.parse.unquote(raw_path, encoding='utf-8')
            
            # Log the request
            print(f"\n[VIDEO] ===== Video Request =====")
            print(f"[VIDEO] Raw path: {raw_path}")
            print(f"[VIDEO] Decoded filename: {filename}")
            print(f"[VIDEO] Base path: {VIDEO_BASE_PATH}")
            
            # Construct full path - handle both Path and string paths for network drives
            if os.path.isabs(VIDEO_BASE_PATH) and VIDEO_BASE_PATH.startswith('\\\\'):
                # Network path (UNC path) - use os.path.join
                video_path = os.path.join(VIDEO_BASE_PATH, filename)
            else:
                # Local path - use Path
                video_path = str(Path(VIDEO_BASE_PATH) / filename)
            
            print(f"[VIDEO] Full path: {video_path}")
            print(f"[VIDEO] Path exists: {os.path.exists(video_path)}")
            
            # Check if file exists
            if not os.path.exists(video_path):
                # Try to list files in directory to help debug
                try:
                    if os.path.exists(VIDEO_BASE_PATH):
                        files = os.listdir(VIDEO_BASE_PATH)
                        mp4_files = [f for f in files if f.lower().endswith('.mp4')]
                        print(f"[VIDEO] Available MP4 files in directory ({len(mp4_files)}):")
                        for f in mp4_files[:10]:  # Show first 10
                            print(f"   - {f}")
                        if len(mp4_files) > 10:
                            print(f"   ... and {len(mp4_files) - 10} more")
                        
                        # Try to find similar filename
                        similar = [f for f in mp4_files if 'E02' in f or 'E_02' in f]
                        if similar:
                            print(f"[VIDEO] Similar files found: {similar}")
                    else:
                        print(f"[VIDEO] Base directory does not exist!")
                except Exception as e:
                    print(f"[VIDEO] Error listing directory: {e}")
                
                error_msg = f"Video file not found: {filename}"
                print(f"[ERROR] {error_msg}")
                self.send_error(404, error_msg)
                return
            
            print(f"[VIDEO] File found, size: {os.path.getsize(video_path)} bytes")
            
            # Get file size
            file_size = os.path.getsize(video_path)
            
            # Handle range requests for video streaming
            range_header = self.headers.get('Range')
            if range_header:
                # Parse range header
                range_match = range_header.replace('bytes=', '').split('-')
                start = int(range_match[0]) if range_match[0] else 0
                end = int(range_match[1]) if range_match[1] else file_size - 1
                
                # Send partial content
                self.send_response(206)
                self.send_header('Content-Type', 'video/mp4')
                self.send_header('Content-Length', str(end - start + 1))
                self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                
                # Read and send file chunk
                with open(video_path, 'rb') as f:
                    f.seek(start)
                    chunk_size = 8192
                    remaining = end - start + 1
                    while remaining > 0:
                        chunk = f.read(min(chunk_size, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            else:
                # Send full file
                self.send_response(200)
                self.send_header('Content-Type', 'video/mp4')
                self.send_header('Content-Length', str(file_size))
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                
                # Read and send file
                with open(video_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
        except FileNotFoundError as e:
            error_msg = f"Video file not found: {filename}\nError: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.send_error(404, error_msg)
        except PermissionError as e:
            error_msg = f"Permission denied accessing video: {filename}\nError: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.send_error(403, error_msg)
        except Exception as e:
            error_msg = f"Error serving video: {filename}\nError: {str(e)}\nType: {type(e).__name__}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            self.send_error(500, error_msg)

    def end_headers(self):
        # Add CORS headers if needed
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {args[0]}")

def test_video_path():
    """Test if the video base path is accessible"""
    print(f"\n📁 Testing video path access...")
    print(f"   Path: {VIDEO_BASE_PATH}")
    
    if os.path.isabs(VIDEO_BASE_PATH) and VIDEO_BASE_PATH.startswith('\\\\'):
        print(f"   Type: Network path (UNC)")
    else:
        print(f"   Type: Local path")
    
    if os.path.exists(VIDEO_BASE_PATH):
        print(f"   ✅ Path exists and is accessible")
        try:
            files = os.listdir(VIDEO_BASE_PATH)
            mp4_files = [f for f in files if f.lower().endswith('.mp4')]
            print(f"   📹 Found {len(mp4_files)} MP4 file(s)")
            if mp4_files:
                print(f"   Example: {mp4_files[0]}")
        except Exception as e:
            print(f"   ⚠️  Cannot list files: {e}")
    else:
        print(f"   ❌ Path does not exist or is not accessible")
        print(f"   💡 Tips:")
        print(f"      - Check if the network drive is mapped")
        print(f"      - Try mapping the drive: net use Z: \\\\Freebox_Server\\Videos")
        print(f"      - Or use a local path in server.py")
    print()

def main():
    """Start the server"""
    os.chdir(Path(__file__).parent)
    
    # Test video path accessibility
    test_video_path()

    with socketserver.TCPServer(("", PORT), TwilightZoneHTTPRequestHandler) as httpd:
        print("\n" + "="*52)
        print("   The Twilight Zone - Episode Viewer Server")
        print("="*52 + "\n")
        print(f"🎬 Server running at http://localhost:{PORT}/")
        print(f"📂 Serving files from: {os.getcwd()}")
        print(f"📹 Video path: {VIDEO_BASE_PATH}")
        print(f"\n⏹️  Press Ctrl+C to stop the server\n")

        # Auto-open browser
        webbrowser.open(f'http://localhost:{PORT}')

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped.")
            print("Thank you for visiting The Twilight Zone!\n")

if __name__ == "__main__":
    main()
