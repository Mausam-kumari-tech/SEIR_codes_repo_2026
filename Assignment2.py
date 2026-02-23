import sys
import socket
import ssl
import re

def fetch_content(url):

    use_https = False
    if url.startswith("https://"):
        use_https = True
        url = url.replace("https://", "")
    elif url.startswith("http://"):
        url = url.replace("http://", "")

    parts = url.split("/",1)
    host = parts[0]
    path = "/" 

    if len(parts) > 1:
        path = "/"+ parts[1]

    print(host)
    print(path)
    print("HTTPS:",use_https)

    socket_client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    socket_client.settimeout(10)
    if use_https:
        try:
            context = ssl.create_default_context()
            socket_client = context.wrap_socket(socket_client , server_hostname = host)
            port = 443
        except Exception as e:
            print(f"SSL context error:{e}")
            return ""
    else:
        port = 80

    try:
        socket_client.connect((host,port))

        request = (f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
                "Accept: text/html\r\n"
                "Connection: close\r\n\r\n"
                )
        socket_client.send(request.encode())

        response = b""
        while True:
            data = socket_client.recv(4096)
            if not data:
                break
            response += data
        socket_client.close()

        html = response.decode(errors = "ignore")
        # print(html[:500])

        if "\r\n\r\n" in html:
             content = html.split("\r\n\r\n",1)[1]
        else:
            content = ""
        clean_html = re.sub(r'<(script|style).*?>.*?</\1>', "" , content , flags = re.IGNORECASE | re.DOTALL)
        clean_text = re.sub(r'<[^>]+>' , '', clean_html)
        final_body_text = " ".join(clean_text.split())
        return final_body_text
    
    except socket.timeout:
        print("Error : DNS lookput failed")
        return ""
    except socket.gaierror:
        print("DNS lookup failed")
        return ""
    except Exception as e:
        print(f"connection error : {e}")
        return ""
    
def word_freq(text):
    words = re.findall(r'[a-z0-9]+',text.lower())
    freq = {}
    for word in words:
        freq[word] = freq.get(word,0)+1
    return freq

def polynomial_rolling_hash(word):
    p = 53
    m = 2**64
    h = 0
    for i , char in enumerate(word):
        h += ord(char)*(p**i)
    return h%m

def simhash(word_freq):
    v = [0] *64
    for word, weight in word_freq.items():
        word_hash = polynomial_rolling_hash(word)
        for i in range(64):
            if(word_hash >> i) & 1:
                v[i] += weight
            else:
                v[i] -= weight
    fingerprint = 0
    for i in range(64):
        if v[i] > 0:
            fingerprint |= (1<<i)
    return fingerprint


def no_of_common_bits(hash1 , hash2):
    common_bits = ~(hash1 ^ hash2) & ((1 << 64)-1)
    return bin(common_bits).count('1')


if len(sys.argv) < 3:
    sys.exit()
url1 , url2 = sys.argv[1] , sys.argv[2]

print("processing first url")
text1  = fetch_content(url1)
freq1 = word_freq(text1)
sim1 = simhash(freq1)


print("processing second url")
text2  = fetch_content(url2)
freq2 = word_freq(text2)
sim2 = simhash(freq2)


common = no_of_common_bits(sim1,sim2)
print("\n" + "-----------------------------------------------------")
print(f"simhash 1 : { hex(sim1)}")
print(f"simhash 2 : { hex(sim2)}")
print(f" common bits : {common} out of 64")






















