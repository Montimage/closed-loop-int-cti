import urllib.request
import json, sys

CACHES = {}
# local CTI
CTI_ADDRESS="127.0.0.1:4000"

# MI server
CTI_ADDRESS="51.178.36.152:4000"

def _get(url):
    print( " - connecting to CTI: {0}".format( url ) )
    body = urllib.request.urlopen( url ).read()
    print( " - CTI answer: {0}".format(body ))
    data = json.loads( body.decode() )
    return data

def is_ipv_in_blacklist( ip ):
    # return value in cache if it is available
    if ip in CACHES:
        print("Is {0} in black list: {1}".format( ip, CACHES[ip] ))
        return CACHES[ip]
    
    print( "Checking reputation of IP: {0}".format( ip ))
    result = False
    try:
        data = _get("http://{0}/ip/{1}".format(CTI_ADDRESS, ip))
        size = len(data) # number of black list
        # max 10 black list
        if size > 10:
            size = 10
        # reputation: invers number of appearence in blacklist
        reput = ((10-size)/10) * 100
        print(" - reputation: {0}%".format( reput ))
        result = (reput <    100.0)
    except Exception as ex:
        print("Error: {0}".format(ex))

    print( " - is in black list: {0}".format( result ))
    # cache the result to increase performance
    CACHES[ip] = result
    return result


# to run a test
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage: python3 {0} <ip>".format( sys.argv[0]))
        print("""   Ex: python3 {0} '91.92.253.23'\n""".format( sys.argv[0]))
        sys.exit(1)
    print( is_ipv_in_blacklist( sys.argv[1]) )