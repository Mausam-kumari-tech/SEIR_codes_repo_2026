import sys
import socket
import ssl
import re

if len(sys.argv) < 2:
    print("url not found")
    sys.exit()
url = sys.argv[1]
print(url)

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
        sys.exit()
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
except socket.timeout:
    print("Error : DNS lookput failed")
    sys.exit()
except socket.gaierror:
    print("DNS lookup failed")
    sys.exit()
except Exception as e:
    print(f"connection error : {e}")
    sys.exit()

html = response.decode(errors = "ignore")
# print(html[:500])

if "\r\n\r\n" in html:
    header , content = html.split("\r\n\r\n",1)
else:
    header = html
    content = ""

status_match = re.search(r"HTTP/\d\.\d\s+(\d{3})",header)
if status_match:
    status_code = status_match.group(1)
    if status_code.startswith(('4','5')):
        print(f"------warning : Server returned HTTP error {status_code}------")


print("\n------------------title------------------")
title_search = re.findall(r'<title>(.*?)</title>', content,re.IGNORECASE | re.DOTALL)
if title_search:
    for t in title_search:
        clean_title = t.strip().replace('\n',' ').replace('\r','')
        print(clean_title)
else:
    print("no title found")

print("\n------------------body------------------")
clean_html = re.sub(r'<(script|style).*?>.*?</\1>', "" , content , flags = re.IGNORECASE | re.DOTALL)
clean_text = re.sub(r'<[^>]+>' , '', clean_html)
body_lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
print("\n".join(body_lines))

print("\n------------------links------------------")
links = re.findall(r'href=["\'](.*?)["\']' ,content , re.IGNORECASE)
if links:
    for link in links:
        print(link)
else:
    print("no link found")





