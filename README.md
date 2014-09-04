restcall
========

RESTcall is a lightweight client backend/library to interact with the Alcatel-Lucent OpenTouch REST Web Services

**This is under development, expect changes ;)**

__Example:__

```

Benny$ python -i restcall.py 

RESTcall v0.2
A RESTful client backend/library for Alcatel-Lucent Enterprise OpenTouch

Developed in 2014 by:
Benjamin Eggerstedt
Christian Sailer

Attempting to login ...
Authentication successfull!
Attempting to register session!
Session successfully registered: OK - <Response [200]>
Session information:
... removed ...

Get user details - <Response [200]>
User information:
... removed ...

>>> call = client.makebasiccall("<internal device nbr","<phone number>")
Call successfully made - <Response [201]>
>>> 
>>> drop = client.dropbasiccall()
Call ended - <Response [204]>

```
