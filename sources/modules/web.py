## systemdump.py
## create and load a system dump for B&R PLC from the command line
##
## https://github.com/hilch/systemdump.py
##

# pip install requests

import sys
import re
import requests

accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
response_timeout = 20


def create( host, datafiles=True ):
    headers = {   
        'Accept': accept,
    }

    params = (
        ('type', 'systemdump'),
        ('action', 'start'),
        ('datafile', '1' if datafiles else '0' ),
        ('size', 'function getSIZE() /{ return 1;/}'),
    )

    try:
        response = requests.get(f'http://{host}/sdm/svg.cgi', headers=headers, params=params, verify=False, timeout=response_timeout)
    except( requests.ConnectionError) :
        return {'result': 'ConnectionError'} 
    except( requests.exceptions.InvalidURL ):
        return {'result': 'Invalid URL'}
    except( requests.HTTPError ):
        return { 'result': 'HttpError' }
    except( requests.Timeout ):
        return { 'result' :  f'Timeout ({response_timeout}s)' }
    except:
        exception = sys.exc_info()[0]
        return { 'result' : f'Unexpected error: {exception}' }

    if response.status_code == 200:
        return {'result':'Ok'}
    else:
        return f'status:{response.status_code}'


def uploadFromTarget( host ):
    timeout = response_timeout

    headers = {      
        'Accept': accept,
    }

    params = (
        ('type', '256'),
        ('module', 'Sysdump'),
    )


    while True: 
        try:
            response = requests.get(f'http://{host}/sdm/cgiFileLoop.cgi', headers=headers, params=params, verify=False, timeout=timeout)
        except( requests.ConnectionError) :
            return {'result': 'ConnectionError'} 
        except( requests.exceptions.InvalidURL ):
            return {'result': 'Invalid URL'}            
        except( requests.HTTPError ):
            return { 'result': 'HttpError' }
        except( requests.Timeout ):
            return { 'result' :  f'Timeout ({response_timeout}s)' }
        except:
            exception = sys.exc_info()[0]
            return { 'result' : f'Unexpected error: {exception}' }

        if response.status_code == 200:
            timeout -= response.elapsed.microseconds / 1e6
            if timeout < 0:
                return { 'result' :  f'Timeout ({response_timeout}s)' }
            content_disposition = response.headers.get('Content-Disposition')
            content_type = response.headers.get('Content-Type')
            if content_disposition and content_type == 'application/octet-stream':
                x = re.search(r'(attachment;\sfilename=\")([a-zA-Z0-9_-]*.tar.gz)\"', content_disposition )
                if x == None:
                    continue
                return { 'filename': x.group(2), 
                         'data': response.content, 
                         'result': 'Ok' }
            else:
                continue
        else:
            return { 'result' : f'Http-result {response.status_code}' }



def deleteFromTarget(host):
    headers = {    
        'Accept': accept,
    }

    params = (
        ('type', 'systemdump'),
        ('action', 'delete'),
        ('param', 'Sysdump'),
        ('size', '1'),
    )


    try:
        response = requests.get(f'http://{host}/sdm/svg.cgi', headers=headers, params=params, verify=False, timeout=response_timeout)
    except( requests.ConnectionError) :
        return {'result': 'ConnectionError'} 
    except( requests.exceptions.InvalidURL ):
        return {'result': 'Invalid URL'}    
    except( requests.HTTPError ):
        return { 'result': 'HttpError' }
    except( requests.Timeout ):
        return { 'result' :  f'Timeout ({response_timeout}s)' }
    except:
        exception = sys.exc_info()[0]
        return { 'result' : f'Unexpected error: {exception}' }

    if response.status_code == 200:
        return { 'result' : 'Ok' }
    else:
        return { 'result' : f'Http-result {response.status_code}' }



if __name__ == '__main__':
    pass