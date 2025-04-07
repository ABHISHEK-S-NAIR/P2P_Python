import socket
import threading
import time
import platform
import subprocess
import json
from datetime import datetime
import ipaddress
import psutil

class NetworkManager:
    def __init__(self, ui_components, nickname):
        # Store UI references
        self.message_display = ui_components['message_display']
        self.message_entry = ui_components['message_entry']
        self.send_btn = ui_components['send_btn']
        self.start_btn = ui_components['start_btn']
        self.peers_listbox = ui_components['peers_listbox']
        self.stats_labels = ui_components['stats_labels']
        
        # User identification
        self.nickname = nickname
        
        # Initialize network variables
        self.udp_sock = None
        self.tcp_sock = None
        self.tcp_server = None
        self.running = False
        self.bytes_sent = 0
        self.bytes_received = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.start_time = time.time()
        
        # Network configuration
        self.UDP_PORT = 41234  # For peer discovery
        self.TCP_PORT = 41235  # For messaging
        self.local_ip = self.get_wifi_ip()
        
        # Peer tracking
        self.peers = {}  # {ip: {'nickname': name, 'port': port, 'last_seen': timestamp}}
        
        # Thread management
        self.threads = []
    
    def get_wifi_ip(self):
        """Get the IP address of the Wi-Fi adapter (only 192.168.x.x or 10.x.x.x)"""
        for interface, addrs in psutil.net_if_addrs().items():
            # Check if it's a Wi-Fi interface
            if "Wi-Fi" in interface or "Wireless" in interface or "wlan" in interface:
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        # Check if IP is in the required range
                        if ip.startswith('192.168.') or ip.startswith('10.'):
                            return ip
        
        # Fallback to any IP in the required range
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if ip.startswith('192.168.') or ip.startswith('10.'):
                        return ip
        
        return "127.0.0.1"  # Fallback to localhost if no suitable IP found
    
    def configure_firewall(self):
        """Configure Windows Firewall to allow UDP and TCP on required ports"""
        try:
            if platform.system() == "Windows":
                # Add UDP rule for peer discovery
                udp_cmd = f'netsh advfirewall firewall add rule name="P2P Chat UDP Discovery" protocol=UDP dir=in localport={self.UDP_PORT} action=allow'
                subprocess.run(udp_cmd, shell=True, check=True)
                
                # Add TCP rule for messaging
                tcp_cmd = f'netsh advfirewall firewall add rule name="P2P Chat TCP Messaging" protocol=TCP dir=in localport={self.TCP_PORT} action=allow'
                subprocess.run(tcp_cmd, shell=True, check=True)
                
                return True
            return True  # For non-Windows systems, assume it's ok
        except Exception as e:
            self.log_message(f"Failed to configure firewall: {str(e)}")
            return False
    
    def start_networking(self):
        """Initialize and start all networking components"""
        if not self.configure_firewall():
            return False
        
        try:
            # Start UDP discovery
            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_sock.bind((self.local_ip, self.UDP_PORT))
            
            # Start TCP server
            self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_server.bind((self.local_ip, self.TCP_PORT))
            self.tcp_server.listen(10)
            
            self.running = True
            
            # Start threads
            self.start_udp_discovery()
            self.start_udp_listener()
            self.start_tcp_server()
            
            # Update UI
            self.message_display.insert("end", f"P2P Chat started on {self.local_ip}\n")
            self.message_display.insert("end", f"UDP Discovery: Port {self.UDP_PORT}\n")
            self.message_display.insert("end", f"TCP Messaging: Port {self.TCP_PORT}\n")
            self.message_display.insert("end", f"Your nickname: {self.nickname}\n")
            self.message_display.insert("end", "Discovering peers...\n")
            self.message_display.see("end")
            
            # Enable chat
            self.message_entry.config(state='normal')
            self.send_btn.config(state='normal')
            self.start_btn.config(state='disabled')
            
            return True
        except Exception as e:
            self.log_message(f"Failed to start networking: {str(e)}")
            return False
    
    def start_udp_discovery(self):
        """Start thread to periodically broadcast presence"""
        discovery_thread = threading.Thread(target=self.udp_discovery_loop, daemon=True)
        discovery_thread.start()
        self.threads.append(discovery_thread)
    
    def start_udp_listener(self):
        """Start thread to listen for peer discovery broadcasts"""
        listener_thread = threading.Thread(target=self.udp_listener_loop, daemon=True)
        listener_thread.start()
        self.threads.append(listener_thread)
    
    def start_tcp_server(self):
        """Start thread to accept incoming TCP connections"""
        server_thread = threading.Thread(target=self.tcp_server_loop, daemon=True)
        server_thread.start()
        self.threads.append(server_thread)
    
    def udp_discovery_loop(self):
        """Periodically broadcast presence to network"""
        while self.running:
            try:
                # Create discovery packet
                discovery_data = {
                    "type": "discovery",
                    "nickname": self.nickname,
                    "tcp_port": self.TCP_PORT
                }
                
                # Broadcast to network
                self.udp_sock.sendto(
                    json.dumps(discovery_data).encode(),
                    ('<broadcast>', self.UDP_PORT)
                )
            except Exception as e:
                self.log_message(f"Discovery broadcast error: {str(e)}")
            
            # Wait before next broadcast
            time.sleep(5)  # Broadcast every 5 seconds
    
    def udp_listener_loop(self):
        """Listen for peer discovery broadcasts"""
        while self.running:
            try:
                data, addr = self.udp_sock.recvfrom(1024)
                sender_ip = addr[0]
                
                # Skip our own broadcasts
                if sender_ip == self.local_ip:
                    continue
                
                # Process discovery packet
                try:
                    packet = json.loads(data.decode())
                    
                    if packet.get("type") == "discovery":
                        nickname = packet.get("nickname", "Unknown")
                        tcp_port = packet.get("tcp_port", self.TCP_PORT)
                        
                        # Add or update peer
                        is_new = sender_ip not in self.peers
                        self.peers[sender_ip] = {
                            "nickname": nickname,
                            "tcp_port": tcp_port,
                            "last_seen": time.time()
                        }
                        
                        # Update UI
                        if is_new:
                            self.update_peers_list()
                            self.log_message(f"Discovered new peer: {nickname} ({sender_ip})")
                except Exception as e:
                    self.log_message(f"Error processing discovery packet: {str(e)}")
            
            except Exception as e:
                if not self.running:
                    break
                self.log_message(f"UDP listener error: {str(e)}")
    
    def tcp_server_loop(self):
        """Accept incoming TCP connections"""
        while self.running:
            try:
                client_sock, addr = self.tcp_server.accept()
                client_ip = addr[0]
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(
                    target=self.handle_tcp_client,
                    args=(client_sock, client_ip),
                    daemon=True
                )
                client_thread.start()
                self.threads.append(client_thread)
                
            except Exception as e:
                if not self.running:
                    break
                self.log_message(f"TCP server error: {str(e)}")
    
    def handle_tcp_client(self, client_sock, client_ip):
        """Handle communication with a connected TCP client"""
        try:
            while self.running:
                data = client_sock.recv(1024)
                if not data:
                    break
                
                # Process message
                try:
                    message_data = json.loads(data.decode())
                    message_type = message_data.get("type", "message")
                    
                    if message_type == "message":
                        sender_nickname = message_data.get("nickname", "Unknown")
                        message_text = message_data.get("message", "")
                        timestamp = message_data.get("timestamp", datetime.now().strftime("%H:%M:%S"))
                        
                        # Update statistics
                        self.bytes_received += len(data)
                        self.messages_received += 1
                        
                        # Display message
                        self.display_message(timestamp, sender_nickname, client_ip, message_text)
                except Exception as e:
                    self.log_message(f"Error processing message: {str(e)}")
                
        except Exception as e:
            self.log_message(f"TCP client handler error: {str(e)}")
        finally:
            client_sock.close()
    
    def send_message_to_peer(self, peer_ip, message):
        """Send a message to a specific peer"""
        if not peer_ip in self.peers:
            self.log_message(f"Unknown peer: {peer_ip}")
            return False
        
        peer_info = self.peers[peer_ip]
        peer_port = peer_info.get("tcp_port", self.TCP_PORT)
        
        try:
            # Create TCP socket for sending
            tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_client.connect((peer_ip, peer_port))
            
            # Create message packet
            timestamp = datetime.now().strftime("%H:%M:%S")
            message_data = {
                "type": "message",
                "nickname": self.nickname,
                "message": message,
                "timestamp": timestamp
            }
            
            # Send message
            message_bytes = json.dumps(message_data).encode()
            tcp_client.sendall(message_bytes)
            
            # Update statistics
            self.bytes_sent += len(message_bytes)
            self.messages_sent += 1
            
            # Display in our own chat
            self.display_message(timestamp, "You", peer_ip, message)
            
            tcp_client.close()
            return True
            
        except Exception as e:
            self.log_message(f"Error sending message to {peer_ip}: {str(e)}")
            return False
    
    def send_message_to_selected_peers(self, message):
        """Send a message to all selected peers in the listbox"""
        selected_indices = self.peers_listbox.curselection()
        if not selected_indices:
            self.log_message("No peers selected. Please select one or more peers.")
            return
        
        # Get selected peer IPs
        peer_ips = []
        for index in selected_indices:
            peer_entry = self.peers_listbox.get(index)
            # Extract IP from format "Nickname (IP)"
            ip_start = peer_entry.rfind("(") + 1
            ip_end = peer_entry.rfind(")")
            if ip_start > 0 and ip_end > ip_start:
                peer_ip = peer_entry[ip_start:ip_end]
                peer_ips.append(peer_ip)
        
        # Send to each selected peer
        success_count = 0
        for peer_ip in peer_ips:
            if self.send_message_to_peer(peer_ip, message):
                success_count += 1
        
        if success_count > 0:
            self.log_message(f"Message sent to {success_count} peer(s)")
        else:
            self.log_message("Failed to send message to any selected peers")
    
    def update_peers_list(self):
        """Update the peers listbox with current peers"""
        # Clear current list
        self.peers_listbox.delete(0, "end")
        
        # Add each peer
        for ip, info in self.peers.items():
            nickname = info.get("nickname", "Unknown")
            self.peers_listbox.insert("end", f"{nickname} ({ip})")
    
    def display_message(self, timestamp, sender, sender_ip, message):
        """Display a message in the chat window"""
        self.message_display.insert("end", f"[{timestamp}] {sender} ({sender_ip}): {message}\n")
        self.message_display.see("end")
    
    def log_message(self, message):
        """Log a system message to the chat window"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.message_display.insert("end", f"[{timestamp}] SYSTEM: {message}\n")
        self.message_display.see("end")
    
    def cleanup(self):
        """Clean up resources when shutting down"""
        self.running = False
        
        # Close sockets
        if self.udp_sock:
            self.udp_sock.close()
        
        if self.tcp_server:
            self.tcp_server.close()
        
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(0.5)  # Wait up to 0.5 seconds for each thread
        
        self.log_message("P2P Chat stopped")
