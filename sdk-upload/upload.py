#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8765
DIRECTORY = "/var/www/html/taihe2/sdk-upload"

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/upload.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html><head><title>SDK Upload</title></head>
<body><h2>Upload THS SDK</h2>
<form action="/" method="post" enctype="multipart/form-data">
<input type="file" name="file"><br><br>
<input type="submit" value="Upload">
</form></body></html>'''
            self.wfile.write(html.encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        content_type = self.headers.get('Content-Type')
        if 'multipart/form-data' in content_type:
            form_data = self.parse_content_length()
            boundary = content_type.split('boundary=')[1].encode()
            # Simple file save
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            # Find filename
            start = body.find(b'filename="') + 10
            end = body.find(b'"', start)
            filename = body[start:end].decode()
            # Find file content
            data_start = body.find(b'\r\n\r\n') + 4
            data_end = body.rfind(b'\r\n--')
            if filename and data_start < data_end:
                filepath = os.path.join(DIRECTORY, filename)
                with open(filepath, 'wb') as f:
                    f.write(body[data_start:data_end])
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'OK: {filename} uploaded'.encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Upload failed')
    
    def parse_content_length(self):
        return None

os.chdir(DIRECTORY)
with socketserver.TCPServer(('', PORT), UploadHandler) as httpd:
    print(f'Serving on port {PORT}')
    httpd.serve_forever()
