import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import random
import string
import json
import time

class IPExchangeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure IP Exchange")
        self.root.geometry("600x500")  # Increased height to accommodate all elements
        self.root.resizable(False, False)
        
        # Network variables
        self.my_ip = self.get_local_ip()
        self.peer_ip = None
        self.listen_port = 65432
        self.server_socket = None
        self.is_server_running = False
        self.server_thread = None
        self.otp = None
        self.peer_otp = None
        self.connection_verified = False
        
        # Setup UI
        self.setup_ui()
        
        # Start listener for incoming connections
        self.start_server()
    
    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Connect to an external server (doesn't actually send anything)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"  # Fallback to localhost
    
    def setup_ui(self):
        """Create the user interface"""
        # Configure style for better visibility
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'))
        
        # Main frame with scrollbar to ensure all elements are visible
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Add canvas with scrollbar for better display on all screen sizes
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main frame
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status information section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_frame, text=f"Your IP: {self.my_ip}").pack(anchor=tk.W)
        
        self.status_label = ttk.Label(status_frame, text="Waiting for connection...")
        self.status_label.pack(anchor=tk.W)
        
        # Connection section
        conn_frame = ttk.LabelFrame(main_frame, text="Connect to Peer", padding="10")
        conn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(conn_frame, text="Peer IP Address:").pack(anchor=tk.W)
        
        ip_frame = ttk.Frame(conn_frame)
        ip_frame.pack(fill=tk.X, pady=5)
        
        self.ip_entry = ttk.Entry(ip_frame)
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.connect_btn = ttk.Button(ip_frame, text="Connect", command=self.connect_to_peer)
        self.connect_btn.pack(side=tk.RIGHT)
        
        # OTP section
        otp_frame = ttk.LabelFrame(main_frame, text="OTP Verification", padding="10")
        otp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Generate OTP section
        generate_frame = ttk.Frame(otp_frame)
        generate_frame.pack(fill=tk.X, pady=5)
        
        self.my_otp_label = ttk.Label(generate_frame, text="Your OTP: Not generated")
        self.my_otp_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.generate_btn = ttk.Button(generate_frame, text="Generate OTP", command=self.generate_otp)
        self.generate_btn.pack(side=tk.RIGHT)
        
        # Enter peer OTP section
        verify_frame = ttk.Frame(otp_frame)
        verify_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(verify_frame, text="Peer OTP:").pack(side=tk.LEFT)
        
        self.peer_otp_entry = ttk.Entry(verify_frame)
        self.peer_otp_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.verify_btn = ttk.Button(verify_frame, text="Verify", command=self.verify_otp)
        self.verify_btn.pack(side=tk.RIGHT)
        
        # IP Exchange Button (initially disabled with visual indication)
        exchange_frame = ttk.Frame(main_frame)
        exchange_frame.pack(fill=tk.X, padx=5, pady=20)
        
        self.exchange_btn = ttk.Button(
            exchange_frame, 
            text="Exchange IP Addresses", 
            command=self.exchange_ip,
            state=tk.DISABLED
        )
        self.exchange_btn.pack(fill=tk.X, expand=True)
        
        # Status label for exchange button
        self.exchange_status = ttk.Label(
            exchange_frame, 
            text="⚠️ Verify OTP first to enable exchange", 
            foreground="red"
        )
        self.exchange_status.pack(pady=(5, 0))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Exchange Results", padding="10")
        results_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.results_label = ttk.Label(results_frame, text="No exchange performed yet")
        self.results_label.pack(anchor=tk.W)
    
    def start_server(self):
        """Start a TCP server to listen for incoming connections"""
        if self.is_server_running:
            return
            
        self.is_server_running = True
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
    
    def run_server(self):
        """Server thread to handle incoming connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.listen_port))
            self.server_socket.settimeout(1.0)  # 1 second timeout for checking shutdown
            self.server_socket.listen(1)
            
            while self.is_server_running:
                try:
                    client_socket, client_addr = self.server_socket.accept()
                    # Handle client connection in a new thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_addr),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    # This is just so we can check is_server_running periodically
                    continue
                except Exception as e:
                    print(f"Server error: {e}")
        except Exception as e:
            print(f"Failed to start server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            self.is_server_running = False
    
    def handle_client(self, client_socket, client_addr):
        """Handle communication with a connected client"""
        try:
            client_socket.settimeout(10.0)  # 10 second timeout for operations
            
            # Receive message
            data = client_socket.recv(1024)
            if not data:
                return
                
            message = json.loads(data.decode('utf-8'))
            
            if 'type' not in message:
                return
                
            # Handle different message types
            if message['type'] == 'connect':
                # Initial connection from peer
                response = {
                    'type': 'connected',
                    'status': 'success',
                    'ip': self.my_ip
                }
                self.peer_ip = message.get('ip')
                
                # Update UI from the main thread
                self.root.after(0, lambda: self.update_connection_status(self.peer_ip))
                
            elif message['type'] == 'verify_otp':
                # Peer is verifying OTP
                received_otp = message.get('otp')
                
                if self.otp and received_otp == self.otp:
                    response = {
                        'type': 'verify_otp_response',
                        'status': 'success'
                    }
                    # Mark as verified from main thread
                    self.root.after(0, self.mark_verified)
                else:
                    response = {
                        'type': 'verify_otp_response',
                        'status': 'failed'
                    }
                    
            elif message['type'] == 'exchange_ip':
                # Peer wants to exchange IPs
                response = {
                    'type': 'exchange_ip_response',
                    'status': 'success',
                    'ip': self.my_ip
                }
                peer_ip = message.get('ip')
                
                # Update results in main thread
                self.root.after(0, lambda: self.update_exchange_results(peer_ip))
                
            else:
                response = {
                    'type': 'error',
                    'message': 'Unknown message type'
                }
                
            # Send response
            client_socket.sendall(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error handling client {client_addr}: {e}")
        finally:
            client_socket.close()
    
    def update_connection_status(self, peer_ip):
        """Update the UI with connection status"""
        self.peer_ip = peer_ip
        self.status_label.config(text=f"Connected to peer: {peer_ip}")
    
    def mark_verified(self):
        """Mark the connection as verified after successful OTP check"""
        self.connection_verified = True
        messagebox.showinfo("Verification", "OTP verified successfully!")
        self.exchange_btn.config(state=tk.NORMAL)
        self.exchange_status.config(text="✓ Verification complete - Exchange enabled", foreground="green")
    
    def update_exchange_results(self, peer_ip):
        """Update the results section after IP exchange"""
        self.results_label.config(text=f"Exchange completed successfully!\nPeer IP: {peer_ip}")
    
    def connect_to_peer(self):
        """Connect to the peer using the IP entered in the input field"""
        peer_ip = self.ip_entry.get().strip()
        if not peer_ip:
            messagebox.showerror("Error", "Please enter a valid IP address")
            return
            
        try:
            # Create a socket and connect to the peer
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5.0)  # 5 second timeout
            client_socket.connect((peer_ip, self.listen_port))
            
            # Send connection message
            message = {
                'type': 'connect',
                'ip': self.my_ip
            }
            client_socket.sendall(json.dumps(message).encode('utf-8'))
            
            # Receive response
            data = client_socket.recv(1024)
            response = json.loads(data.decode('utf-8'))
            
            if response.get('status') == 'success':
                self.peer_ip = peer_ip
                self.status_label.config(text=f"Connected to peer: {peer_ip}")
                messagebox.showinfo("Connection", "Connected successfully to peer!")
            else:
                messagebox.showerror("Error", "Failed to connect to peer")
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
        finally:
            client_socket.close()
    
    def generate_otp(self):
        """Generate a random OTP and display it"""
        # Generate a 6-digit OTP
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.my_otp_label.config(text=f"Your OTP: {self.otp}")
        messagebox.showinfo("OTP Generated", f"Your OTP is: {self.otp}\nShare this with your peer for verification.")
    
    def verify_otp(self):
        """Verify the OTP entered by the user against the peer's OTP"""
        if not self.peer_ip:
            messagebox.showerror("Error", "Not connected to a peer")
            return
            
        # Check if we have generated our own OTP first
        if not self.otp:
            messagebox.showerror("Error", "Generate your OTP first before verifying")
            return
            
        peer_otp = self.peer_otp_entry.get().strip()
        if not peer_otp:
            messagebox.showerror("Error", "Please enter the peer's OTP")
            return
            
        try:
            # Create a socket and connect to the peer
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5.0)  # 5 second timeout
            client_socket.connect((self.peer_ip, self.listen_port))
            
            # Send verification message
            message = {
                'type': 'verify_otp',
                'otp': peer_otp
            }
            client_socket.sendall(json.dumps(message).encode('utf-8'))
            
            # Receive response
            data = client_socket.recv(1024)
            response = json.loads(data.decode('utf-8'))
            
            if response.get('status') == 'success':
                self.connection_verified = True
                self.exchange_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Verification", "OTP verified successfully!")
            else:
                messagebox.showerror("Verification Failed", "The OTP you entered is incorrect")
                
        except Exception as e:
            messagebox.showerror("Verification Error", f"Failed to verify OTP: {e}")
        finally:
            client_socket.close()
    
    def exchange_ip(self):
        """Exchange IP addresses with the peer after verification"""
        if not self.peer_ip:
            messagebox.showerror("Error", "Not connected to a peer")
            return
            
        if not self.connection_verified:
            messagebox.showerror("Error", "Connection not verified. Please verify OTP first.")
            return
            
        try:
            # Simulate some processing
            self.exchange_btn.config(state=tk.DISABLED)
            self.exchange_btn.config(text="Processing...")
            self.root.update()
            
            # Add a small delay to simulate processing
            time.sleep(1)
            
            # Create a socket and connect to the peer
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5.0)  # 5 second timeout
            client_socket.connect((self.peer_ip, self.listen_port))
            
            # Send exchange message
            message = {
                'type': 'exchange_ip',
                'ip': self.my_ip
            }
            client_socket.sendall(json.dumps(message).encode('utf-8'))
            
            # Receive response
            data = client_socket.recv(1024)
            response = json.loads(data.decode('utf-8'))
            
            if response.get('status') == 'success':
                peer_ip = response.get('ip')
                self.results_label.config(text=f"Exchange completed successfully!\nPeer IP: {peer_ip}")
                messagebox.showinfo("IP Exchange", "IP addresses exchanged successfully!")
            else:
                messagebox.showerror("Exchange Failed", "Failed to exchange IP addresses")
                
        except Exception as e:
            messagebox.showerror("Exchange Error", f"Failed to exchange IPs: {e}")
        finally:
            client_socket.close()
            self.exchange_btn.config(text="Exchange IP Addresses")
            self.exchange_btn.config(state=tk.NORMAL)
    
    def cleanup(self):
        """Clean up resources before closing"""
        self.is_server_running = False
        if self.server_socket:
            self.server_socket.close()

def main():
    root = tk.Tk()
    # Set app icon and make it more visually appealing
    root.configure(bg='#f0f0f0')
    
    # Try to set a nicer theme if available
    try:
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
    except Exception:
        pass  # If theme setting fails, continue with default
    
    app = IPExchangeApp(root)
    
    # Handle window close event
    root.protocol("WM_DELETE_WINDOW", lambda: [app.cleanup(), root.destroy()])
    
    # Center the window on screen
    window_width = 600
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()