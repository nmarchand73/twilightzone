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
import unicodedata
import urllib.request
from pathlib import Path

PORT = 8000

# Chemin de base pour les vidéos (modifiez selon votre configuration)
# Par défaut, utilise le chemin réseau Windows
# Vous pouvez aussi utiliser un chemin local comme: r"C:\Videos\Twilight Zone"
# ou un chemin relatif depuis le dossier ui: r"..\videos"
VIDEO_BASE_PATH = r"\\Freebox_Server\Videos\Series\Twilight Zone"

class TwilightZoneHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with proper MIME types and video serving"""

    def normalize_error_message(self, message):
        """Normalize error message to ASCII-only for HTTP error responses"""
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '\u2019': "'",  # Right single quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u201C': '"',  # Left double quotation mark
            '\u201D': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u00E9': 'e',  # é
            '\u00E8': 'e',  # è
            '\u00EA': 'e',  # ê
            '\u00EB': 'e',  # ë
            '\u00E0': 'a',  # à
            '\u00E2': 'a',  # â
            '\u00E4': 'a',  # ä
            '\u00E7': 'c',  # ç
            '\u00F9': 'u',  # ù
            '\u00FB': 'u',  # û
            '\u00FC': 'u',  # ü
            '\u00EE': 'i',  # î
            '\u00EF': 'i',  # ï
            '\u00F4': 'o',  # ô
            '\u00F6': 'o',  # ö
        }
        
        # First, try to replace known problematic characters
        normalized = message
        for unicode_char, ascii_char in replacements.items():
            normalized = normalized.replace(unicode_char, ascii_char)
        
        # Then, use NFKD normalization and remove non-ASCII characters
        try:
            # Normalize to NFKD (decompose) then encode to ASCII, ignoring errors
            normalized = unicodedata.normalize('NFKD', normalized)
            normalized = normalized.encode('ascii', 'ignore').decode('ascii')
        except Exception:
            # Fallback: just remove non-ASCII characters
            normalized = ''.join(char for char in normalized if ord(char) < 128)
        
        return normalized

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
        # Handle Internet Archive proxy endpoint
        if self.path.startswith('/api/archive/'):
            self.handle_archive_proxy()
            return
        
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
                self.send_error(404, self.normalize_error_message(error_msg))
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
            self.send_error(404, self.normalize_error_message(error_msg))
        except PermissionError as e:
            error_msg = f"Permission denied accessing video: {filename}\nError: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.send_error(403, self.normalize_error_message(error_msg))
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            # Client closed connection - this is normal, don't log as error
            error_type = type(e).__name__
            print(f"[INFO] Client closed connection while serving: {filename} ({error_type})")
            # Don't send error response as connection is already closed
            return
        except Exception as e:
            error_msg = f"Error serving video: {filename}\nError: {str(e)}\nType: {type(e).__name__}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            # Only send error if connection is still open
            try:
                # Normalize error message to avoid Unicode encoding issues
                self.send_error(500, self.normalize_error_message(error_msg))
            except (ConnectionResetError, BrokenPipeError, OSError):
                # Connection already closed, can't send error
                print(f"[INFO] Could not send error response - connection closed")

    def handle_archive_proxy(self):
        """Proxy pour les vidéos Internet Archive avec support CORS"""
        try:
            # Extraire l'URL encodée depuis le chemin
            encoded_url = self.path.replace('/api/archive/', '')
            target_url = urllib.parse.unquote(encoded_url)
            
            print(f"\n[ARCHIVE PROXY] ===== Archive Request =====")
            print(f"[ARCHIVE PROXY] Target URL: {target_url}")
            
            # Vérifier que c'est bien une URL Internet Archive
            if not target_url.startswith('https://') or 'archive.org' not in target_url:
                self.send_error(400, "Invalid archive URL")
                return
            
            # Récupérer le header Range si présent
            range_header = self.headers.get('Range')
            
            # Préparer la requête vers Internet Archive
            req = urllib.request.Request(target_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Si on a un Range header, le transmettre
            if range_header:
                req.add_header('Range', range_header)
            
            try:
                # Ouvrir la connexion vers Internet Archive
                with urllib.request.urlopen(req, timeout=30) as response:
                    # Récupérer les headers de la réponse
                    content_type = response.headers.get('Content-Type', 'video/mp4')
                    content_length = response.headers.get('Content-Length')
                    content_range = response.headers.get('Content-Range')
                    status_code = response.getcode()
                    
                    print(f"[ARCHIVE PROXY] Status: {status_code}")
                    print(f"[ARCHIVE PROXY] Content-Type: {content_type}")
                    print(f"[ARCHIVE PROXY] Content-Length: {content_length}")
                    
                    # Envoyer les headers de réponse avec CORS
                    self.send_response(status_code)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Range')
                    self.send_header('Access-Control-Expose-Headers', 'Content-Length, Content-Range, Accept-Ranges')
                    self.send_header('Accept-Ranges', 'bytes')
                    
                    if content_length:
                        self.send_header('Content-Length', content_length)
                    if content_range:
                        self.send_header('Content-Range', content_range)
                    
                    self.end_headers()
                    
                    # Streamer les données
                    chunk_size = 8192
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        try:
                            self.wfile.write(chunk)
                        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                            print(f"[ARCHIVE PROXY] Client closed connection")
                            return
                            
            except urllib.error.HTTPError as e:
                print(f"[ARCHIVE PROXY] HTTP Error: {e.code} - {e.reason}")
                self.send_error(e.code, f"Archive proxy error: {e.reason}")
            except urllib.error.URLError as e:
                print(f"[ARCHIVE PROXY] URL Error: {e.reason}")
                self.send_error(502, f"Failed to connect to archive: {e.reason}")
            except Exception as e:
                print(f"[ARCHIVE PROXY] Error: {str(e)}")
                self.send_error(500, f"Archive proxy error: {str(e)}")
                
        except Exception as e:
            error_msg = f"Error in archive proxy: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            try:
                self.send_error(500, self.normalize_error_message(error_msg))
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                print(f"[ARCHIVE PROXY] Could not send error response - connection closed")

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Range')
        self.send_header('Access-Control-Max-Age', '3600')
        self.end_headers()

    def handle_archive_proxy(self):
        """Proxy pour les vidéos Internet Archive avec support CORS"""
        try:
            # Extraire l'URL encodée depuis le chemin
            encoded_url = self.path.replace('/api/archive/', '')
            target_url = urllib.parse.unquote(encoded_url)
            
            print(f"\n[ARCHIVE PROXY] ===== Archive Request =====")
            print(f"[ARCHIVE PROXY] Target URL: {target_url}")
            
            # Vérifier que c'est bien une URL Internet Archive
            if not target_url.startswith('https://') or 'archive.org' not in target_url:
                self.send_error(400, "Invalid archive URL")
                return
            
            # Récupérer le header Range si présent
            range_header = self.headers.get('Range')
            
            # Préparer la requête vers Internet Archive
            req = urllib.request.Request(target_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Si on a un Range header, le transmettre
            if range_header:
                req.add_header('Range', range_header)
            
            try:
                # Ouvrir la connexion vers Internet Archive
                with urllib.request.urlopen(req, timeout=30) as response:
                    # Récupérer les headers de la réponse
                    content_type = response.headers.get('Content-Type', 'video/mp4')
                    content_length = response.headers.get('Content-Length')
                    content_range = response.headers.get('Content-Range')
                    status_code = response.getcode()
                    
                    print(f"[ARCHIVE PROXY] Status: {status_code}")
                    print(f"[ARCHIVE PROXY] Content-Type: {content_type}")
                    print(f"[ARCHIVE PROXY] Content-Length: {content_length}")
                    
                    # Envoyer les headers de réponse avec CORS
                    self.send_response(status_code)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Range')
                    self.send_header('Access-Control-Expose-Headers', 'Content-Length, Content-Range, Accept-Ranges')
                    self.send_header('Accept-Ranges', 'bytes')
                    
                    if content_length:
                        self.send_header('Content-Length', content_length)
                    if content_range:
                        self.send_header('Content-Range', content_range)
                    
                    self.end_headers()
                    
                    # Streamer les données
                    chunk_size = 8192
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        try:
                            self.wfile.write(chunk)
                        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                            print(f"[ARCHIVE PROXY] Client closed connection")
                            return
                            
            except urllib.error.HTTPError as e:
                print(f"[ARCHIVE PROXY] HTTP Error: {e.code} - {e.reason}")
                self.send_error(e.code, f"Archive proxy error: {e.reason}")
            except urllib.error.URLError as e:
                print(f"[ARCHIVE PROXY] URL Error: {e.reason}")
                self.send_error(502, f"Failed to connect to archive: {e.reason}")
            except Exception as e:
                print(f"[ARCHIVE PROXY] Error: {str(e)}")
                self.send_error(500, f"Archive proxy error: {str(e)}")
                
        except Exception as e:
            error_msg = f"Error in archive proxy: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            try:
                self.send_error(500, self.normalize_error_message(error_msg))
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                print(f"[ARCHIVE PROXY] Could not send error response - connection closed")

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Range')
        self.send_header('Access-Control-Max-Age', '3600')
        self.end_headers()

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
