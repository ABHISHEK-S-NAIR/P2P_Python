# P2P Chat Application

A Peer-to-Peer Chat Application that uses both TCP and UDP for peer discovery and messaging over a local Wi-Fi network.

## Features

- **Peer Discovery**: Automatically discovers peers on the local network using UDP broadcasts
- **Messaging**: Sends and receives messages using TCP for reliable communication
- **User-friendly GUI**: Built with Tkinter for easy interaction
- **Multi-peer Messaging**: Send messages to one or multiple peers
- **Automatic IP Detection**: Detects and uses the Wi-Fi adapter IP

## Requirements

- Python 3.6+
- Tkinter (included in standard Python installation)
- Network with Wi-Fi connectivity (configured as Private network)

## Network Configuration

The application uses:
- UDP port 41234 for peer discovery
- TCP port 41235 for messaging

Make sure your Windows Firewall allows these ports.

## How to Run

```
python p2p_chat.py
```

Enter your nickname when prompted and start chatting with peers on your network.
