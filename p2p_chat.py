import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

from ui_styles import AppStyles
from network_manager import NetworkManager

class P2PChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Chat Application")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configure UI styles
        AppStyles.configure_styles()
        
        # Build UI components
        self.ui_components = AppStyles.build_ui_components(root)
        
        # Get references to important UI components
        self.message_display = self.ui_components['message_display']
        self.message_entry = self.ui_components['message_entry']
        self.send_btn = self.ui_components['send_btn']
        self.nickname_entry = self.ui_components['nickname_entry']
        self.start_btn = self.ui_components['start_btn']
        self.peers_listbox = self.ui_components['peers_listbox']
        
        # Set up event handlers
        self.message_entry.bind("<Return>", self.send_message)
        self.send_btn.config(command=lambda: self.send_message(None))
        self.start_btn.config(command=self.start_p2p)
        
        # Initialize network manager (will be created when user starts the app)
        self.network_manager = None
        
        # Start statistics update thread
        self.stats_update_thread = threading.Thread(target=self.update_statistics, daemon=True)
        self.stats_update_thread.start()
        
        # Initial UI state
        self.message_entry.config(state='disabled')
        self.send_btn.config(state='disabled')
        
        # Welcome message
        self.message_display.insert(tk.END, f"Welcome to P2P Chat Application!\n")
        self.message_display.insert(tk.END, f"Enter your nickname and click 'Start' to join the P2P network.\n")
        self.message_display.see(tk.END)
    
    def start_p2p(self):
        """Initialize the P2P network with the given nickname"""
        nickname = self.nickname_entry.get().strip()
        if not nickname:
            messagebox.showerror("Error", "Please enter a nickname")
            return
        
        # Initialize network manager with UI components and nickname
        self.network_manager = NetworkManager(self.ui_components, nickname)
        
        # Start networking
        if self.network_manager.start_networking():
            # Disable nickname entry
            self.nickname_entry.config(state='disabled')
            
            # Update start time for session duration
            self.start_time = time.time()
        else:
            messagebox.showerror("Error", "Failed to start P2P networking")
    
    def send_message(self, event):
        """Send a message to selected peers"""
        if not self.network_manager:
            self.message_display.insert(tk.END, "Please start the chat first!\n")
            self.message_display.see(tk.END)
            return
        
        message = self.message_entry.get().strip()
        if message:
            # Send message to selected peers
            self.network_manager.send_message_to_selected_peers(message)
            
            # Clear message entry
            self.message_entry.delete(0, tk.END)
    
    def update_statistics(self):
        """Update statistics in the UI"""
        while True:
            if self.network_manager:
                stats = {
                    "Status": "Connected" if self.network_manager.running else "Disconnected",
                    "Local IP": self.network_manager.local_ip,
                    "UDP Port": str(self.network_manager.UDP_PORT),
                    "TCP Port": str(self.network_manager.TCP_PORT),
                    "Messages Sent": str(self.network_manager.messages_sent),
                    "Messages Received": str(self.network_manager.messages_received),
                    "Peers Discovered": str(len(self.network_manager.peers)),
                    "Session Duration": f"{int(time.time() - self.network_manager.start_time)} seconds"
                }
                
                for key, value in stats.items():
                    if key in self.ui_components['stats_labels']:
                        self.ui_components['stats_labels'][key].config(text=value)
                
                # Check for peers that haven't been seen in a while (60 seconds)
                current_time = time.time()
                peers_to_remove = []
                
                for ip, info in self.network_manager.peers.items():
                    last_seen = info.get("last_seen", 0)
                    if current_time - last_seen > 60:  # 60 seconds timeout
                        peers_to_remove.append(ip)
                
                # Remove timed-out peers
                if peers_to_remove:
                    for ip in peers_to_remove:
                        del self.network_manager.peers[ip]
                    self.network_manager.update_peers_list()
                    self.network_manager.log_message(f"Removed {len(peers_to_remove)} inactive peer(s)")
            
            time.sleep(1)
    
    def on_close(self):
        """Handle window close event"""
        if self.network_manager:
            self.network_manager.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = P2PChatApp(root)
    root.mainloop()
