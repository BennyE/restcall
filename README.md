restcall
========

RESTcall is a lightweight client backend/library to interact with the Alcatel-Lucent OpenTouch REST Web Services

**This is under development, expect changes ;)**

__Note for October:__
I'm currently changing some heavy things under the hood. Use the September 0.3 version if you need a working version. This text will be updated once all changes are done.

__Example:__

The user has the ability for "BASIC_TELEPHONY".

```

Benny$ python -i restcall.py 

RESTcall v0.3
A RESTful client backend/library for Alcatel-Lucent Enterprise OpenTouch

Developed in 2014 by:
Benjamin Eggerstedt
Christian Sailer

Attempting to login ...
Authentication successfull!
Attempting to register session!
Session successfully registered: OK - <Response [200]>
Session information:
{
    "services": [
        {
            "relativeUrl": "/logins", 
            "serviceVersion": "1.0", 
            "serviceName": "Logins"
        }, 
        {
            "relativeUrl": "/users", 
            "serviceVersion": "1.0", 
            "serviceName": "Users"
        }, 
        {
            "relativeUrl": "/telephony/basicCall", 
            "serviceVersion": "1.0", 
            "serviceName": "BasicTelephony"
        }
    ], 
    "publicBaseUrl": "https://{SERVER_URL}/api/rest/1.0", 
    "privateBaseUrl": "https://{INTERNAL_URL}/api/rest/1.0", 
    "timeToLive": 1800, 
    "capabilities": [
        "BASIC_TELEPHONY"
    ]
}
Get user details - <Response [200]>
User information:
{
    "instantMessagingId": "one-great-mail@maildomain12345.com", 
    "loginName": "firstname.lastname", 
    "firstName": "Firstname", 
    "lastName": "Lastname", 
    "voicemail": {
        "number": "<number>"
    }, 
    "companyPhone": "<number>", 
    "devices": [
        {
            "subType": "VHE8082", 
            "type": "DESKPHONE", 
            "id": "<number>"
        }, 
        {
            "subType": "ICM_MOBILE_IPHONE", 
            "type": "MOBILE", 
            "id": "MOBILE_123456789", 
            "associatedNumber": "+49<mobilenumber>"
        }, 
        {
            "subType": "MYICSIP", 
            "type": "SOFTPHONE", 
            "id": "<number>"
        }, 
        {
            "subType": "NOMADIC_OTHER", 
            "type": "NOMADIC", 
            "id": "NOMADIC_firstname.lastname"
        }
    ], 
    "companyEmail": "one-great-mail@maildomain12345.com", 
    "type": "MULTIMEDIA"
}
Get user preferences - <Response [200]>
User preferences:
{
    "guiLanguage": "de"
}
>>> 
>>> call = client.makebasiccall("<internal device nbr","<phone number>")
Call successfully made - <Response [201]>
>>> 
>>> drop = client.dropbasiccall()
Call ended - <Response [204]>
>>> client.keepalive()
Session successfully refreshed: OK - <Response [204]>
>>> prefs = client.userpreferences()
Get user preferences - <Response [200]>
User preferences:
{
    "guiLanguage": "de"
}
>>> client.preferences
{u'guiLanguage': u'de'}
>>> logout = client.logout()
Attempting to logout ...
Session successfully closed: OK - <Response [204]>

```
