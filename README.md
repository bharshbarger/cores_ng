# C.O.R.E.S ![Supported Python versions](https://img.shields.io/badge/python-3.6-blue.svg)
    Description:Cross-Origin Resource Exploitation Server.
    Created by: Nick Sanzotta/@Beamr
    
    This tool 'cores_ng.py' will launch a Python http.server configured with 
    HTML & JavaScript code to execute a CORS Proof of Concept (PoC) vulnerability.
    At a minimum the user will need to supply a URL vulnerable to excessive CORS along 
    with the correct HTTP (-m)ethod.
    
    Optionally, the user has the ability to (-a) Autolaunch their default browser and execute the payload.
	
# Overview:
    The CORS spec denies the header Access-Control-Allow-Origin (ACAO) to be configured with 
    '*' while allowing Access-Control-Allow-Credential (ACAC) set to 'true'.
    Example: (NOT Allowed!)
	Access-Control-Allow-Origin: *
	Access-Control-Allow-Credentials: true
	
    A commonly found misconfiguration or work around for this restriction is the following.
    Example: (Insecure Work Around, Shares with any domain with credentials!)
	<? php 
	header("Access-Control-Allow-Origin: ".$_SERVER["HTTP_ORIGIN"]);
	header("Access-Control-Allow-Credentials: true");

	
# Usage:
	usage: cores_ng.py [-h] [-a] [-l PAYLOAD] -m get, post, etc. [-p 8080]
			   [-r RQHDR] -u http://foo.com [-v]

	optional arguments:
	  -h, --help            show this help message and exit
	  -a, --autolaunch_browser
				Auto launches a browser
	  -l PAYLOAD, --payload PAYLOAD
				payload to POST
	  -m get, post, etc., --method get, post, etc.
				Define HTTP request method ex: -m post
	  -p 8080, --port 8080  Port to start local HTTP server on. Default is 8080
	  -r RQHDR, --rqhdr RQHDR
				Specify optional header(s) for authentication, JWT,
				i.e. Authorization: Bearer eyJhbGciOiJSUz... yadda
				yadda
	  -u http://foo.com, --url http://foo.com
				Define vulnerable CORS targert URL ex:
				https://site.com/
	  -v, --verbose         Enable verbosity
