import argparse
import logging

from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import getsizeof
from typing import Literal, Tuple


class WebServerHandler(BaseHTTPRequestHandler):
    """
    WebServerHandler that reads the content of included files, and does the necessary parsing, serializing for our WebServer
    """
    # exposed directory for webservers
    directory = ''

    def __init__(self, directory, *args):
        self.directory = directory

        super().__init__(*args)

    def do_GET(self):
        """
        Reads request and writes header, status, and file to sockets
        """
        status, content = self.do_HEAD()

        if status == 200:
            self.wfile.write(content)

    def do_HEAD(self):
        """
        Reads request and writes header and status to sockets
        """
        status, content = '', ''
        try:
            status, content = self.read_content()
        except Exception as err:
            # something strange occured
            status = 500
            content = f'Server Error: {err}'

        if status != 200:
            self.send_error(status, content)
            self.end_headers()
        else:
            self.send_response(status)

            self.write_header(content)
            self.end_headers()

            return status, content

    
    def read_content(self) -> Tuple[Literal[200, 404], bytes]:
        """
        Opens attached file path against directory, reads the given file
        and returns a status code and the contents of the file
        """
        status = 200
        content = ''.encode()

        try:
            # update path to "index.html"
            self.path = 'index.html' if self.path == '/' else self.path

            # read content
            with open(f'{self.directory}/{self.path}') as file:
                content = file.read().encode()

        # if file is not found set status to 401
        except FileNotFoundError:
            status = 404
            content = 'Not Found'

        # return values
        return status, content

    def write_header(self, content):
        """
        All http_verbs will need to write headers
        """
        self.send_header("Content-Length", getsizeof(content))
        self.send_header("Content-type", "text/html")
        self.send_header("Connection", "close")

class WebServer(HTTPServer):
    """
    Our webserver, with our specific handler
    """
    def __init__(self, port, directory):
        def handler(*args):
            return WebServerHandler(directory, *args)
        super().__init__(('127.0.0.1', int(port)), handler)


def parse_cmd_line_args():
    parser = argparse.ArgumentParser(description="web_client")
    
    # first argument should be the port to expose
    parser.add_argument('port')

    # second argument is the directory we will list
    parser.add_argument('dir')

    return parser.parse_args()



def main():
    # initialize client
    logging.info("server::web_server::main")
    logger = logging.getLogger("web_server")

    logger.debug('server::web_server::main - parsing included arguments')
    cmd_line_args = parse_cmd_line_args()

    # create a server instance
    server = WebServer(cmd_line_args.port, cmd_line_args.dir)

    try:
        server.serve_forever()
    except KeyboardInterrupt as err:
        # exit 'ok'
        exit(0)
    except Exception as err:
        logger.exception(err)
        exit(1)
    finally:
        server.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
    main()