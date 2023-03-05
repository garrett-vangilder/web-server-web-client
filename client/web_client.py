import argparse
import socket
from typing import Optional
from urllib.parse import urlparse
import logging

CRLF = "\r\n\r\n"
NL = "\r\n"

class WebClient:
    """
    Our WebClient, used to interface with webservers via HTTP
    """
    address = ''

    http_verb = ''

    logger = None

    def __init__(self, address, http_verb='GET', logger=None):
        # initialize logger
        self.logger = logger if logger else logging.getLogger('WebClient')

        # set necessary arguments to call Web Server
        self.address = address
        self.http_verb = http_verb
    
    def __call__(self):
        return self.make_request()
    
    def make_request(self) -> Optional[str]:
        """
        Performs socket based HTTP requests
        """
        self.logger.debug('client::web_client::WebClient::make_request')

        url = urlparse(self.address)
        path = url.path

        if path == '':
            path = '/'

        # parsed values
        HOST = url.hostname
        PORT = url.port or 80

        # create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # set the timeout (taken from example)
        sock.settimeout(0.30)

        # prevent known issue if address is already in use
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # connect to target
        self.logger.debug(f'client::web_client::WebClient::connecting to - sending {HOST} {PORT}')
        sock.connect((HOST, PORT,))

        # configure our request
        host_header = f"Host: {HOST}:{PORT}"

        req = f"{self.http_verb} {path} HTTP/1.1{NL}{host_header}{CRLF}"

        b_req = req.encode()
        self.logger.debug(f'client::web_client::WebClient::make_request - sending {req}')
        
        sock.send(b_req)

        return self.event_loop(sock)
    
    def event_loop(self, sock:socket.socket=None) -> Optional[str]:
        if not sock:
            raise ValueError("client::web_client::WebClient::event_loop - sock required")
        
        # start our event loop to wait for the resp
        while True:
            resp = ''
            try:
                resp = sock.recv(10000000)
                # close the connection
                sock.shutdown(1)
                sock.close()

            except TimeoutError:
                self.logger.debug(f'client::web_client::WebClient::make_request - failed to receive message')
                break

            # return our resp
            if resp:
                return resp.decode()


def parse_cmd_line_args():
    parser = argparse.ArgumentParser(description="web_client")
    
    # first argument should be the address <host>:<port>/<path>
    parser.add_argument('address')

    # second argument is the HTTP verb
    parser.add_argument('http_verb', nargs='?', default='GET')

    return parser.parse_args()


def main():
    # initialize client
    logging.info("client::web_client::main")
    logger = logging.getLogger("web_client")

    logger.debug('client::web_client::main - parsing included arguments')
    cmd_line_args = parse_cmd_line_args()

    client = WebClient(cmd_line_args.address, cmd_line_args.http_verb, logger=logger)

    response = client()
    if not response:
        return

    logger.debug('client::web_client::main - received\n')
    
    # log to stdout
    print(response)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
    main()