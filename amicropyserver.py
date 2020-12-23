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
        
        self._counter = 0  # Remove it in the production release.

    async def start(self):
        """ Start server """
        print('Awaiting client connection on {}:{}'.format(self._host, self._port))
        self.server = await asyncio.start_server(self.run_client, self._host, self._port, self.backlog)
        while True:
            await asyncio.sleep(1)

    async def run_client(self, sreader, swriter):
        self.start_time = utime.ticks_ms()
        #print('Got connection from client', self, sreader, sreader.s.fileno(), sreader.e['peername'])
        try:
            request = b''
            res = b''
            while True:
                try:
                    '''
                    # 450-550 ms
                    res = await asyncio.wait_for(sreader.readline(), self.timeout)
                    request += res
                    if res == b'\r\n':  # end of HTTP request
                        break
                    '''
                    
                    # 150-250 ms
                    res = await asyncio.wait_for(sreader.read(1024), self.timeout)
                    print(res)
                    request += res
                    if request[-4:] == b'\r\n\r\n':  # end of HTTP request
                        break
                    '''
                    # 150-250 ms
                    request = await asyncio.wait_for(sreader.readline(), self.timeout)
                    res = await asyncio.wait_for(sreader.read(1024), self.timeout)
                    if res[-4:] == b'\r\n\r\n':  # end of HTTP request
                        break
                    '''
                except asyncio.TimeoutError as e:
                    print(1, e, "asyncio.TimeoutError", self.timeout)
                    res = b''
                if res == b'':  # socket connection broken
                    print('raise OSError')
                    raise OSError
            
            if request:
                request = str(request, "utf8")
                #print('request >>>{}<<<'.format(request))
                
                try:
                    route = self.find_route(request)
                    if route:
                        await route["handler"](swriter, request)
                    else:
                        await self.not_found(swriter)
                    #1/0  # test internal_error
                except Exception as e:
                    print(2, e)
                    self.internal_error(swriter, e)
                    raise
                        
        except OSError as e:
            print(3, e)
            pass
        swriter_s_fileno = swriter.s.fileno()
        await swriter.wait_closed()
        #print('Client socket closed.', self, swriter, swriter_s_fileno, swriter.s.fileno(), swriter.e['peername'])
        
        print('Render time: %i ms' % utime.ticks_diff(utime.ticks_ms(), self.start_time))
        gc.collect()
        #print('---------------------------------------------------------------')

    async def close(self):
        print('Closing server...')
        self.server.close()
        await self.server.wait_closed()
        print('Server is closed.')

    def add_route(self, path, handler, method="GET"):
        """ Add new route  """
        self._routes.append({"path": path, "handler": handler, "method": method})

    async def send(self, swriter, response, status=200, content_type="Content-Type: text/plain", extra_headers=[]):
        """ Send response to client """

        if swriter is None:
            raise Exception("Can't send response, no connection instance")

        status_message = {200: "OK", 400: "Bad Request", 403: "Forbidden", 404: "Not Found",
                          500: "Internal Server Error"}
        swriter.write("HTTP/1.0 " + str(status) + " " + status_message[status] + "\r\n" + \
                      content_type + "\r\n")
        await swriter.drain()
        for header in extra_headers:
            swriter.write(header + "\r\n")
        ### await swriter.write("X-Powered-By: MicroPyServer\r\n")  # not required, vainglory
        swriter.write("Cache-Control: no-store\r\n")  # The response may not be stored in any cache.
                                                      # This is necessary to execute the code on the server:
                                                      # switch PIN ON and switch PIN OFF.
                                                      # This prevents showing the cashed text
                                                      # when a user presses the "Backward/Forward" button in a browser.
        swriter.write("\r\n")  # end of HTTP header
        await swriter.drain()

        self._counter += 1
        swriter.write(str(self._counter) + '\r\n')
        swriter.write(response)
        
        #print("swriter.out_buf >>>{}<<<".format(swriter.out_buf))
        await swriter.drain()
        #print("Finished processing request.")

    def find_route(self, request):
        """ Find route """
        method = re.search("^([A-Z]+)", request).group(1)
        for route in self._routes:
            if method != route["method"]:
                continue
            path = re.search("^[A-Z]+\\s+(/[-a-zA-Z0-9_.]*)", request).group(1)
            if path == route["path"]:
                return route
            else:
                match = re.search("^" + route["path"] + "$", path)
                if match:
                    return route
        return None

    '''    
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
                    return route
                else:
                    match = re.search("^" + route["path"] + "$", path)
                    if match:
                        return route
        return None
    '''    
    async def not_found(self, swriter):
        """ Not found action """
        await self.send(swriter, "404 Not found", status=404)

    async def internal_error(self, swriter, error):
        """ Catch error action """
        output = io.StringIO()
        sys.print_exception(error, output)
        str_error = output.getvalue()
        output.close()
        if swriter.s.fileno() != -1:
            await self.send(swriter, "Error: " + str_error, status=500)

    def on_request(self, handler):
        """ Set request handler """
        self._on_request_handler = handler
