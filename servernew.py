import socket
import threading
import time

# Server settings
HOST = 'localhost'
PORT = 65432

# Store client connections
clients = []
client_lock = threading.Lock()

def broadcast(message, sender_socket=None):
    """Send message to all clients except the sender"""
    with client_lock:
        for client in clients:
            # Don't send message back to sender
            if client != sender_socket:
                try:
                    client.sendall(message)
                except:
                    # Remove broken connection
                    if client in clients:
                        clients.remove(client)

def handle_client(client_socket, client_address):
    """Handle individual client connection"""
    print(f"New connection from {client_address}")
    
    try:
        while True:
            # Receive data from client
            data = client_socket.recv(1024)
            if not data:
                break
                
            message = data.decode('utf-8')
            print(f"Received from {client_address}: {message}")
            
            # Broadcast message to all other clients
            broadcast(data, client_socket)
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        # Clean up when client disconnects
        with client_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        print(f"Connection from {client_address} closed")
        broadcast(f"User from {client_address[0]}:{client_address[1]} has left the chat".encode('utf-8'))

def main():
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind and listen
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server started on {HOST}:{PORT}")
        
        while True:
            # Accept new connection
            client_socket, client_address = server_socket.accept()
            
            # Add to client list
            with client_lock:
                clients.append(client_socket)
            
            # Start client thread
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True
            )
            client_thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        # Clean up
        for client in clients:
            try:
                client.close()
            except:
                pass
        server_socket.close()
        print("Server shutdown complete")

if __name__ == "__main__":
    main()
