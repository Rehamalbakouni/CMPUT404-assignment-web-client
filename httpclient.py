#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Modifications from original version:
# Copyright 2023 Reham Albakouni
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        parsed_url = urllib.parse.urlparse(url)
        # get port
        if not parsed_url.port:
            self.port = 80
        else:
            self.port = parsed_url.port
        # get path 
        if not parsed_url.path:
            self.path = "/"
        else:
            self.path = parsed_url.path
        
        # get host
        self.host = parsed_url.hostname

        # get query
        if parsed_url.query:
            self.query = "?" + parsed_url.query

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        
        return None

    def get_code(self, data):
        if not data:
            return None
        lines = data.splitlines()[0]
        code =  int(lines.split()[1])
        return code

    def get_headers(self,data):
        headers = {}
        if not data:
            return headers
        for header in data.splitlines():
            # store the value of the header in the dictionary headers[index] = value
            headers[header.split(": ")[0]] = header.split(": ")[1] 
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')



    def GET(self, url, args=None):
        #code = 500
        #body = ""

        self.get_host_port(url)

        try:
            self.connect(self.host, self.port)
        except:
            print("Connection failed")
            return HTTPResponse(404,"")
        
        request = "GET " + self.path + " HTTP/1.1\r\nHost: " + self.host + "\r\nAccept: */*\r\nConnection: close\r\n\r\n"
        self.sendall(request)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #code = 500
        #body = ""

        self.get_host_port(url)
   
        try:
            self.connect(self.host, self.port)
        except:
            print("Connection failed")
            return HTTPResponse(404,"") 
        
        request = "POST " + self.path + " HTTP/1.1\r\nHost: " + self.host + "\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded\r\n"
        if args:
            request += "Content-Length: " + str(len(urllib.parse.urlencode(args))) + "\r\n"
            request += "Connection: close\r\n\r\n"
            request += urllib.parse.urlencode(args)
        else:
            request += "Content-Length: 0\r\n"
            request += "Connection: close\r\n\r\n"
        
        self.sendall(request)
        response = self.recvall(self.socket)
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
