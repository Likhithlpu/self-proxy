import socket
import threading

# Proxy server configuration
proxy_host = '127.0.0.1'  # Proxy listens on localhost
proxy_port = 8888  # Proxy port

def handle_client(client_socket):
    # Receive client request data
    request_data = client_socket.recv(4096)

    # Display the request and ask for user input (accept/decline)
    print("Received request:")
    print(request_data.decode())
    decision = input("Accept this request? (y/n): ")

    if decision.lower() == 'y':
        # If accepted, extract the destination host and port
        dest_host, dest_port = extract_host_port(request_data.decode())

        # Create a socket to connect to the destination server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((dest_host, dest_port))

        # Forward the client request to the destination server
        server_socket.send(request_data)

        while True:
            # Receive data from the destination server
            server_response = server_socket.recv(4096)

            if len(server_response) > 0:
                # Forward the server response to the client
                client_socket.send(server_response)
            else:
                break

        # Close sockets
        client_socket.close()
        server_socket.close()
    else:
        # If declined, close the client connection without forwarding the request
        print("Request declined.")
        client_socket.close()

def extract_host_port(request_str):
    # Parse the request to extract the destination host and port
    lines = request_str.split('\r\n')
    first_line = lines[0]
    parts = first_line.split(' ')

    # Assuming that the destination host and port are in the request line as "GET http://host:port/..."
    url = parts[1]
    http_pos = url.find("://")
    if http_pos == -1:
        temp = url
    else:
        temp = url[(http_pos + 3):]

    port_pos = temp.find(":")
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    dest_host = ""
    dest_port = -1

    if port_pos == -1 or webserver_pos < port_pos:
        dest_port = 80
        dest_host = temp[:webserver_pos]
    else:
        dest_port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        dest_host = temp[:port_pos]

    return dest_host, dest_port


def start_proxy():
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.bind((proxy_host, proxy_port))
    proxy.listen(5)

    print(f"[*] Proxy server listening on {proxy_host}:{proxy_port}")

    while True:
        client_socket, client_addr = proxy.accept()
        print(f"[*] Accepted connecytion from {client_addr[0]}:{client_addr[1]}")

        # Create a thread to handle client requests
        proxy_thread = threading.Thread(target=handle_client, args=(client_socket,))
        proxy_thread.start()

if __name__ == "__main__":
    start_proxy()
