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
import sys
import io
import utime
import gc
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

        self._counter = 0  # Remove it in the production release.

    async def start(self):
        """ Start server """
        print('Awaiting client connection on {}:{}'.format(self._host, self._port))
        self.server = await asyncio.start_server(self.run_client, self._host, self._port, self.backlog)
        while True:
            await asyncio.sleep(1)

    async def run_client(self, sreader, swriter):
        self.start_time = utime.ticks_ms()
        print('Got connection from client', self, sreader, sreader.s.fileno(), sreader.e['peername'])
        self.swriter = swriter
        try:
            if sreader.s.fileno() != -1:
                request = b''
                while True:
                    try:
                        res = await asyncio.wait_for(sreader.readline(), self.timeout)
                        request += res
                        if res == b'\r\n':  # end of HTTP request
                            break
                    except asyncio.TimeoutError as e:
                        print(1, e, "asyncio.TimeoutError", self.timeout)
                        res = b''
                    if res == b'':  # socket connection broken
                        print('raise OSError')
                        raise OSError
                
                if request:
                    request = str(request, "utf8")
                    print('request >>>>{}<<<<'.format(request))
                    
                    try:
                        route = self.find_route(request)
                        if route:
                            #print("route", route)
                            await route["handler"](request)
                        else:
                            await self.not_found()
                    except Exception as e:
                        print(2, e)
                        self.internal_error(e)
                        raise
                        
        except OSError as e:
            print(3, e)
            pass
        if swriter.s.fileno() != -1:
            print('Client disconnect.', self, swriter, swriter.s.fileno(), swriter.e['peername'])
            await swriter.wait_closed()
            await asyncio.sleep(0.2)
            print('Client socket closed.', self, swriter, swriter.s.fileno(), swriter.e['peername'])
        print('Render time: %i ms' % utime.ticks_diff(utime.ticks_ms(), self.start_time))
            
        gc.collect()
        print('----------------------------------------------------------------------------------')

    async def close(self):
        print('Closing server...')
        self.server.close()
        await self.server.wait_closed()
        print('Server is closed.')

    def add_route(self, path, handler, method="GET"):
        """ Add new route  """
        self._routes.append({"path": path, "handler": handler, "method": method})

    async def _write(self, response):
        print(response)
        self.swriter.write(response)
        
    async def send(self, response, status=200, content_type="Content-Type: text/plain", extra_headers=[]):
        """ Send response to client """

        if self.swriter is None:
            raise Exception("Can't send response, no connection instance")

        status_message = {200: "OK", 400: "Bad Request", 403: "Forbidden", 404: "Not Found",
                          500: "Internal Server Error"}
        await self._write("HTTP/1.0 " + str(status) + " " + status_message[status] + "\r\n")
        await self._write(content_type + "\r\n")
        for header in extra_headers:
            await self._write(header + "\r\n")
        ### await self._write("X-Powered-By: MicroPyServer\r\n")  # not required, vainglory
        await self._write("Cache-Control: no-store\r\n")  # The response may not be stored in any cache.
                                                          # This is necessary to execute the code on the server:
                                                          # switch PIN ON and switch PIN OFF.
                                                          # This prevents showing the cashed text
                                                          # when a user presses the "Backward/Forward" button in a browser.
        await self._write("\r\n")  # end of HTTP header
        self._counter += 1
        await self._write(str(self._counter) + ' ' + response)
        
        #print("swriter.out_buf >>>", self.swriter.out_buf, '<<<')
        await self.swriter.drain()
        print("swriter.out_buf >>>", self.swriter.out_buf, '<<<')
        print("Finished processing request.")
        
        
    def find_route(self, request):
        """ Find route """
        lines = request.split("\r\n")
        #print('lines', lines)
        if len(lines[0]) > 0:
            method = re.search("^([A-Z]+)", lines[0]).group(1)
            for route in self._routes:
                if method != route["method"]:
                    continue
                path = re.search("^[A-Z]+\\s+(/[-a-zA-Z0-9_.]*)", lines[0]).group(1)
                if path == route["path"]:
                    print('1', method, path, route["path"])
                    return route
                else:
                    match = re.search("^" + route["path"] + "$", path)
                    if match:
                        print('2', method, path, route["path"])
                        return route
        return None
    
    async def not_found(self):
        """ Not found action """
        await self.send("404", status=404)

    def internal_error(self, error):
        """ Catch error action """
        output = io.StringIO()
        sys.print_exception(error, output)
        str_error = output.getvalue()
        output.close()
        if swriter.s.fileno() != -1:
            self.send("Error: " + str_error, status=500)

    def on_request(self, handler):
        """ Set request handler """
        self._on_request_handler = handler
