import tkinter as tk
from tkinter import ttk, scrolledtext

class AppStyles:
    @staticmethod
    def configure_styles():
        # Configure style for a modern look
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelframe", background="#f0f0f0")
        style.configure("TLabelframe.Label", background="#f0f0f0")
        style.configure("TButton", padding=5)
    
    @staticmethod
    def configure_chat_display(message_display):
        # Configure chat display colors
        message_display.configure(
            background="#ffffff",
            foreground="#000000",
            selectbackground="#0078d7",
            selectforeground="#ffffff",
            font=("Segoe UI", 10)
        )
    
    @staticmethod
    def configure_edu_panel(edu_text):
        # Configure educational panel
        edu_text.configure(
            background="#f8f8f8",
            foreground="#333333",
            font=("Segoe UI", 10)
        )
    
    @staticmethod
    def create_educational_content():
        return """🔹 P2P Chat Application:
- Uses both TCP and UDP protocols
- UDP for peer discovery (broadcast)
- TCP for reliable messaging

🔹 TCP (Transmission Control Protocol):
- Connection-oriented protocol
- Reliable, ordered delivery
- Error checking and retransmission
- Perfect for chat applications

🔹 UDP (User Datagram Protocol):
- Connectionless protocol
- Used for peer discovery broadcasts
- Fast but less reliable than TCP

🔹 Socket Programming:
- Enables network communication
- Uses IP addresses and ports
- Allows data exchange between peers

🔹 IPv4 Addressing:
- Format: xxx.xxx.xxx.xxx
- Each number: 0-255
- Used to identify devices on network

Enter your nickname and click 'Start' to join the P2P network!"""

    @staticmethod
    def build_ui_components(root):
        # Create main container
        main_container = ttk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create left panel (Chat Area)
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Connection Frame
        connection_frame = ttk.LabelFrame(left_panel, text="P2P Settings")
        connection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Nickname Entry
        ttk.Label(connection_frame, text="Your Nickname:").pack(side=tk.LEFT, padx=5)
        nickname_entry = ttk.Entry(connection_frame)
        nickname_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        nickname_entry.insert(0, "User")
        
        # Start Button placeholder (will be configured in main)
        start_btn = ttk.Button(connection_frame, text="Start")
        start_btn.pack(side=tk.LEFT, padx=5)
        
        # Chat Area
        chat_frame = ttk.LabelFrame(left_panel, text="Chat")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message Display
        message_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, height=20)
        message_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message Entry
        message_frame = ttk.Frame(chat_frame)
        message_frame.pack(fill=tk.X, padx=5, pady=5)
        
        message_entry = ttk.Entry(message_frame)
        message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        message_entry.config(state='disabled')
        
        send_btn = ttk.Button(message_frame, text="Send")
        send_btn.pack(side=tk.LEFT, padx=5)
        send_btn.config(state='disabled')
        
        # Create right panel (Peers and Statistics)
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # Peers List Frame
        peers_frame = ttk.LabelFrame(right_panel, text="Discovered Peers")
        peers_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Peers Listbox with scrollbar
        peers_list_frame = ttk.Frame(peers_frame)
        peers_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        peers_scrollbar = ttk.Scrollbar(peers_list_frame)
        peers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        peers_listbox = tk.Listbox(peers_list_frame, yscrollcommand=peers_scrollbar.set)
        peers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        peers_scrollbar.config(command=peers_listbox.yview)
        
        # Network Statistics
        stats_frame = ttk.LabelFrame(right_panel, text="Network Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Statistics Labels
        stats_labels = {}
        stats = [
            "Status", "Local IP", "UDP Port", "TCP Port",
            "Messages Sent", "Messages Received",
            "Peers Discovered", "Session Duration"
        ]
        
        for stat in stats:
            frame = ttk.Frame(stats_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=f"{stat}:").pack(side=tk.LEFT)
            stats_labels[stat] = ttk.Label(frame, text="---")
            stats_labels[stat].pack(side=tk.RIGHT)
        
        # Educational Panel
        edu_frame = ttk.LabelFrame(right_panel, text="Network Concepts")
        edu_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        edu_text = scrolledtext.ScrolledText(edu_frame, wrap=tk.WORD, height=10)
        edu_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        edu_text.insert(tk.END, AppStyles.create_educational_content())
        edu_text.config(state='disabled')
        
        # Apply styles
        AppStyles.configure_chat_display(message_display)
        AppStyles.configure_edu_panel(edu_text)
        
        # Return all UI components as a dictionary
        return {
            'main_container': main_container,
            'left_panel': left_panel,
            'right_panel': right_panel,
            'connection_frame': connection_frame,
            'nickname_entry': nickname_entry,
            'start_btn': start_btn,
            'chat_frame': chat_frame,
            'message_display': message_display,
            'message_entry': message_entry,
            'send_btn': send_btn,
            'peers_frame': peers_frame,
            'peers_listbox': peers_listbox,
            'stats_frame': stats_frame,
            'stats_labels': stats_labels,
            'edu_frame': edu_frame,
            'edu_text': edu_text
        }
