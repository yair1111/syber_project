"""
the purpose of the following code is to help a third side party be a middle man
bitween my computer and the internet
"""
import socket
import sys
import _thread
import traceback

# BUFFER_SIZE determines how big the chunks of data are we going to receive.
LISTEN_PORT, BUFFER_SIZE, MAX_CONNECTIONS = 3128, 10000, 10000
IP_ADDRESS = "ec2-52-202-14-225.compute-1.amazonaws.com"


def main():
    """
    this function is in charge of the creation of the socket and intercepting the traffic
    of the user
    """

    try:
        # creating the socket and making it listen for traffic
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Re-use the socket
        my_socket.bind((IP_ADDRESS, LISTEN_PORT))  # bind the socket to a public host, and a port
        my_socket.listen(MAX_CONNECTIONS)  # become a server socket
        print("[*] Intializing socket. Done.")
        print("[*] Socket binded successfully...")
        print(f"[*] Server started successfully [{LISTEN_PORT}]")
    except Exception as ex:
        print(ex)
        sys.exit(2)

    # keeping the connection alive until getting signal to stop.

    while True:
        try:
            conn, address = my_socket.accept()  # Establish the connection
            data = conn.recv(BUFFER_SIZE)  # get the request from browser
            _thread.start_new_thread(conn_string, (conn, data, address))
        except KeyboardInterrupt:
            my_socket.close()
            print("\n[*] Shutting down...")
            sys.exit(1)
    my_socket.close()


def conn_string(conn, data, addr):
    """
    this function is in-charge of analyzing the user searches.
    it finds out to which server does the user want to browse an finds the port of
    that server.
    """
    # Client Browser requests
    try:
        print(addr)
        first_line = data.decode("utf-8").split("\n")[0]  # parse the first line
        print(first_line)
        url = first_line.split(" ")[1]  # get url

        http_pos = url.find("://")  # find pos of ://
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]  # get the rest of url

        port_pos = temp.find(":")  # find the port pos (if any)
        webserver_pos = temp.find("/")  # find end of web server
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos:
            # default port
            port = 80
            webserver = temp[:webserver_pos]
        else:
            # specific port
            port = int(temp[(port_pos + 1):][:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]

        print(webserver)
        proxy_server(webserver, port, conn, data, addr)
    except Exception as ex:
        print(ex)
        traceback.print_exc()


def proxy_server(web_server: str, port:int, conn:int, data:str, addr:str):
    """
    this is the function that is incharge of what is happening in the user side.
    creating a socket to the proxy, sending and receiving data
    """
    print(f"{web_server} {port} {conn} {addr}")
    try:
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        user_socket.connect((web_server, port))
        user_socket.send(data)
        while True:
            # receive data from web server
            reply = user_socket.recv(BUFFER_SIZE)

            if len(reply) > 0:
                # send to browser/client
                conn.sendall(reply)
                print(f"[*] Request sent: {addr[0]} > {web_server}")
            else:
                break

        user_socket.close()
        conn.close()

    except Exception as ex:
        print(ex)
        traceback.print_exc()
        user_socket.close()
        conn.close()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

