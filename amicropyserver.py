"""
MicroPyServer is a simple HTTP server for MicroPython projects.

@see https://github.com/troublegum/micropyserver

The MIT License

Copyright (c) 2019 troublegum. https://github.com/troublegum/micropyserver

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import re
import socket
import sys
import io
import uasyncio as asyncio


class aMicroPyServer(object):

    def __init__(self, host="0.0.0.0", port=80, backlog=5, timeout=20):
        """ Constructor """
        self._host = host
        self._port = port

        self._routes = []
        self._on_request_handler = None
        
        self.backlog = backlog
        self.timeout = timeout
        
        self.swriter = None

    async def start(self):
        """ Start server """
        print('Awaiting client connection.')
        self.server = await asyncio.start_server(self.run_client, self._host, self._port, self.backlog)
        while True:
            await asyncio.sleep(100)

    async def run_client(self, sreader, swriter):
        print('Got connection from client', self, sreader, swriter)
        #self.sreader = sreader
        self.swriter = swriter
        '''
        while True:
            try:
                self._connect, address = sock.accept()
                request = self._get_request()
                if len(request) == 0:
                    self._connect.close()
                    continue
                if self._on_request_handler:
                    if not self._on_request_handler(request, address):
                        continue
                route = self.find_route(request)
                if route:
                    route["handler"](request)
                else:
                    self.not_found()
            except Exception as e:
                    self.internal_error(e)
            finally:
                self._connect.close()
        '''
        try:
            while True:
                try:
                    res = await asyncio.wait_for(sreader.readline(), self.timeout)
                except asyncio.TimeoutError:
                    res = b''
                if res == b'':
                    raise OSError
                print('Received {} from client {}'.format(res, 12345))
                
                request = str(res, "utf8")
                try:
                    route = self.find_route(request)
                    print("route", route)
                    if route:
                        route["handler"](request)
                    else:
                        self.not_found()
                except Exception as e:
                    print(e)
                    self.internal_error(e)
                    raise
                        
        except OSError:
            pass
        print('Client {} disconnect.'.format(self))
        await sreader.wait_closed()
        print('Client {} socket closed.'.format(self))

    def close(self):
        print('Closing server')
        self.server.close()
        await self.server.wait_closed()
        print('Server closed')

    def add_route(self, path, handler, method="GET"):
        """ Add new route  """
        self._routes.append({"path": path, "handler": handler, "method": method})

    def _write(self, response):
        self.swriter.write(response)
        await self.swriter.drain() 
        
    def send(self, response, status=200, content_type="Content-Type: text/plain", extra_headers=[]):
        """ Send response to client """

        if self.swriter is None:
            raise Exception("Can't send response, no connection instance")

        status_message = {200: "OK", 400: "Bad Request", 403: "Forbidden", 404: "Not Found",
                          500: "Internal Server Error"}
        self._write("HTTP/1.0 " + str(status) + " " + status_message[status] + "\r\n")
        self._write(content_type + "\r\n")
        for header in extra_headers:
            self._write(header + "\r\n")
        self._write("X-Powered-By: MicroPyServer\r\n")
        self._write("\r\n")
        self._write(response)
        
    def find_route(self, request):
        """ Find route """
        print('self._routes', self._routes)
        print(type(request), '>>>', request, '<<<')
        lines = request.split("\r\n")
        print('lines', lines)
        if len(lines[0]) > 0:
            method = re.search("^([A-Z]+)", lines[0]).group(1)
            for route in self._routes:
                if method != route["method"]:
                    continue
                path = re.search("^[A-Z]+\\s+(/[-a-zA-Z0-9_.]*)", lines[0]).group(1)
                if path == route["path"]:
                    return route
                else:
                    match = re.search("^" + route["path"] + "$", path)
                    if match:
                        print(method, path, route["path"])
                        return route
        return None
    
    def not_found(self):
        """ Not found action """
        self.send("404", status=404)

    def internal_error(self, error):
        """ Catch error action """
        output = io.StringIO()
        #sys.print_exception(error, output)
        print(error)
        str_error = output.getvalue()
        output.close()
        self.send("Error: " + str_error, status=500)

    def on_request(self, handler):
        """ Set request handler """
        self._on_request_handler = handler

    def _get_request(self):
        """ Return request body """
        return str(self._connect.recv(4096), "utf8")

