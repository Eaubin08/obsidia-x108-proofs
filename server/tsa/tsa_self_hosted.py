#!/usr/bin/env python3
"""
TSA Self-Hosted — Serveur RFC3161 local avec OpenSSL
Permet de tester RFC3161 status "verified" en local
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

class TSARequestHandler(BaseHTTPRequestHandler):
    """Handler pour requêtes RFC3161 (application/timestamp-query)"""
    
    def do_POST(self):
        """Traiter POST /api/timestamp"""
        if self.path != '/api/timestamp':
            self.send_error(404)
            return
        
        # Lire la TSQ
        content_length = int(self.headers.get('Content-Length', 0))
        tsq_data = self.rfile.read(content_length)
        
        if not tsq_data:
            self.send_error(400, "Empty TSQ")
            return
        
        try:
            # Générer TSR avec openssl ts -reply
            tsr_data = self._generate_tsr(tsq_data)
            
            # Retourner TSR
            self.send_response(200)
            self.send_header('Content-Type', 'application/timestamp-reply')
            self.send_header('Content-Length', len(tsr_data))
            self.end_headers()
            self.wfile.write(tsr_data)
            
        except Exception as e:
            self.send_error(500, f"TSA error: {str(e)}")
    
    def _generate_tsr(self, tsq_data):
        """Générer TSR depuis TSQ avec openssl ts -reply"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tsq_file = os.path.join(tmpdir, 'request.tsq')
            tsr_file = os.path.join(tmpdir, 'response.tsr')
            
            # Écrire TSQ
            with open(tsq_file, 'wb') as f:
                f.write(tsq_data)
            
            # Générer TSR
            cmd = [
                'openssl', 'ts', '-reply',
                '-queryfile', tsq_file,
                '-out', tsr_file,
                '-token_in', '-token_out',
                '-text'  # Mode texte pour debug
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0:
                raise Exception(f"openssl ts -reply failed: {result.stderr.decode()}")
            
            # Lire TSR
            with open(tsr_file, 'rb') as f:
                return f.read()
    
    def log_message(self, format, *args):
        """Supprimer logs HTTP par défaut"""
        pass

def start_tsa_server(host='127.0.0.1', port=3161):
    """Démarrer serveur TSA local"""
    server = HTTPServer((host, port), TSARequestHandler)
    print(f"✅ TSA Server started on {host}:{port}")
    print(f"   Endpoint: http://{host}:{port}/api/timestamp")
    print(f"   Status: ready for RFC3161 requests")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ TSA Server stopped")
        server.shutdown()

if __name__ == '__main__':
    start_tsa_server()
