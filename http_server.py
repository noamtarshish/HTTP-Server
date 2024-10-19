# Ex 4.4 - HTTP Server Shell

# TO DO: import modules
import socket
import os

# TO DO: set constants
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1
ROOT_DIR = "C:\\Users\\noamt\\networks\\work\\http_server - 4.4\\webroot"
DEFAULT_URL = "index.html"

FORBIDDEN_FILES = ['secret.txt', 'top_secret.txt']
REDIRECT_FILES = {'oldPage.html': 'newPage.html'}


def get_file_data(filename):
    """ Get data from file """
    filepath = os.path.join(ROOT_DIR, filename)

    try:
        with open(filepath, 'rb') as file:
            return file.read() #read the file data - binary mode
    except FileNotFoundError:
        return None #return None if the file is not found


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""

    if resource == '/':
        resource = 'index.html'  # Default to index.html if root is requested

    # Construct the full path to the requested file
    requested_file = resource.strip('/')
    filepath = os.path.join(ROOT_DIR, requested_file)

    # Checks for different status codes
    # check for 403 forbidden
    if requested_file in FORBIDDEN_FILES:
        response = "HTTP/1.0 403 Forbidden\r\nContent-Type: text/html\r\n\r\nForbidden"
        client_socket.sendall(response.encode())
        client_socket.close()
        return

    # check for 302 redirection
    if requested_file in REDIRECT_FILES:
        response = f"HTTP/1.0 302 Found\r\nLocation: {REDIRECT_FILES[requested_file]}\r\n\r\n"
        client_socket.sendall(response.encode())
        client_socket.close()
        return

    # Check if the requested file exists and is a file
    if os.path.isfile(filepath):
        # Open the file and send its contents
        try:
            # Here we read the file's contents
            file_data = get_file_data(filepath)

            # Determine the correct content type based on the file extension
            if filepath.endswith('.html') or filepath.endswith('.htm'):
                content_type = 'text/html; charset=utf-8'
            elif filepath.endswith('.jpg') or filepath.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif filepath.endswith('.png'):
                content_type = 'image/png'
            elif filepath.endswith('.css'):
                content_type = 'text/css'
            elif filepath.endswith('.js'):
                content_type = 'text/javascript; charset=UTF-8'
            elif filepath.endswith('.txt'):
                content_type = 'text/plain; charset=utf-8'
            else:
                content_type = 'application/octet-stream'  # Fallback for unknown file types

            content_length = len(file_data)

            # Build the HTTP response with headers
            response_headers = f"HTTP/1.0 200 OK\r\nContent-Type: {content_type}\r\nContent-length: {content_length}\r\n\r\n"
            client_socket.sendall(response_headers.encode())  # Send headers

            # Send the actual file content
            client_socket.sendall(file_data)  # Send the file data (binary)
        except Exception as e:
            # 500 Internal Server Error
            response_headers = "HTTP/1.0 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\nInternal Server Error"
            client_socket.sendall(response_headers.encode())
            print(f"Error serving file: {e}")
            client_socket.close()
    else:
        # File not found, close the connection
        response = "HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\nFile not found"
        client_socket.sendall(response.encode())
        client_socket.close()

    """
    # TO DO: check if URL had been redirected, not available or other error code. For example:
    if url in REDIRECTION_DICTIONARY:
        # TO DO: send 302 redirection response

    # TO DO: read the data from the file
    data = get_file_data(filename)
    http_response = http_header + data
    client_socket.send(http_response.encode())
    """
    return

def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    parts = request.split()
    if len(parts) < 3: # (method, URL, HTTP version)
        return False, None

    method, url, version = parts[0], parts[1], parts[2]

    if (method != 'GET') or (version != 'HTTP/1.1'):
        return False, None
    else:
        return True, url

def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    try:
        # Receive request from the client
        request = client_socket.recv(1024).decode()
        print(f"Client Request: {request}")

        # Validate the HTTP request using validate_http_request function
        valid, url = validate_http_request(request)

        if valid:
            # If the request is valid, send a response
            handle_client_request(url, client_socket)
        else:
            # If it's not a valid request, close the connection
            print("Invalid request, closing connection.")
            client_socket.close()
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()