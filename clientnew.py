import socket
import threading
import sys
from googletrans import Translator

# Server connection details
HOST = 'localhost'  # Change to server IP if needed
PORT = 65432

# Available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'zh-cn': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi'
}

def print_language_options():
    print("\nAvailable languages:")
    for code, name in LANGUAGES.items():
        print(f"  {code}: {name}")

def main():
    # Initialize socket and translator
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    translator = Translator()
    
    # Get username
    username = input("Enter your username: ")
    
    # Select languages
    print_language_options()
    input_language = input("Select your input language code (default: en): ").strip() or "en"
    display_language = input("Select language to display received messages (default: en): ").strip() or "en"
    
    # Validate language selections
    if input_language not in LANGUAGES:
        print(f"Invalid input language. Using English instead.")
        input_language = "en"
    if display_language not in LANGUAGES:
        print(f"Invalid display language. Using English instead.")
        display_language = "en"
    
    auto_translate = input("Auto-translate incoming messages? (y/n, default: y): ").strip().lower() != "n"
    
    print(f"\nConnecting to {HOST}:{PORT}...")
    
    # Connect to server
    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected! You are chatting as: {username}")
        print(f"Your input language: {LANGUAGES[input_language]}")
        print(f"Messages will be displayed in: {LANGUAGES[display_language]}")
        print("Type your messages and press Enter to send. Type 'quit' to exit.")
        print("-" * 50)
        
        # Send initial username message
        client_socket.sendall(f"User {username} has joined the chat".encode('utf-8'))
    except Exception as e:
        print(f"Unable to connect to server: {e}")
        sys.exit(1)
    
    # Function to receive messages
    def receive_messages():
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print("Disconnected from server")
                    break
                
                message = data.decode('utf-8')
                
                # Extract sender information if present
                if ": " in message:
                    sender, content = message.split(": ", 1)
                    prefix = f"{sender}: "
                else:
                    content = message
                    prefix = "Server: "
                
                # Translate if needed
                try:
                    if auto_translate:
                        detected = translator.detect(content)
                        if detected.lang != display_language:
                            translated = translator.translate(
                                content,
                                src=detected.lang,
                                dest=display_language
                            ).text
                            display_msg = f"{prefix}{translated} (Original: {content})"
                        else:
                            display_msg = f"{prefix}{content}"
                    else:
                        display_msg = f"{prefix}{content}"
                except Exception as e:
                    display_msg = f"{prefix}{content} (Translation error: {str(e)})"
                
                print(display_msg)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
    
    # Start receiving thread
    receive_thread = threading.Thread(target=receive_messages, daemon=True)
    receive_thread.start()
    
    # Main loop for sending messages
    try:
        while True:
            message = input()
            if message.lower() == 'quit':
                print("Disconnecting...")
                break
            
            # Format message with username
            formatted_message = f"{username}: {message}"
            
            # Send message
            try:
                client_socket.sendall(formatted_message.encode('utf-8'))
            except Exception as e:
                print(f"Failed to send message: {e}")
                break
    except KeyboardInterrupt:
        print("\nDisconnecting due to keyboard interrupt...")
    finally:
        # Close the connection
        try:
            client_socket.close()
        except:
            pass
        print("Disconnected")

if __name__ == "__main__":
    main()
