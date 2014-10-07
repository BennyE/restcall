#!/usr/bin/python

# The MIT License (MIT)
#
# Copyright (c) 2014 Benjamin Eggerstedt
# Copyright (c) 2014 Christian Sailer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# Description:
# RESTcall is the back-end library used to interact with the
# RESTful API web service of the Alcatel-Lucent Enterprise
# OpenTouch.

# Imports
import json
import sys
try:
    import requests
except ImportError:
    sys.exit("Dependency missing: python-requests")


class Client(object):
    """
    Client is a RESTful API client class that leverages python-requests
    and interacts with the Alcatel-Lucent Enterprise
    OpenTouch RESTful API web service
    """

    def __init__(self, ot_external, ot_internal, username, password, sn,
                 verify_ssl=True, dbg=False):
        """
        Constructor of class "Client"

        The class requires the following parameters to be set:
        - ot_external = Public BaseURL of OpenTouch server (the external interface)
        - ot_internal = Private BaseURL of OpenTouch server (the internal interface)
        - username    = Valid username for OpenTouch service
        - password    = Valid password for OpenTouch service
        - sn          = Software name / version
         Optional:
        - verify_ssl  = Override with False if OpenTouch service
                        doesn't have a valid SSL certificate
        - dbg         = Debug flag

        """
        self.ot_external = ot_external
        self.ot_internal = ot_internal
        self.rest = requests.Session()
        self.rest.verify = verify_ssl
        # Set our own User-Agent
        self.rest.headers["User-Agent"] = sn
        self.username = username
        self.password = password
        self.sn = sn
        # Set our username/password for authentication
        self.rest.auth = (self.username, self.password)
        self.dbg = dbg
        self.debugprint("""Debug:
    Server:\t%s
    Username:\t%s
    Password:\t%s
    Verify_SSL:\t%s
    Debug:\t%s\n """ % (self.ot_url, self.username,
                        self.password, self.rest.verify,
                        self.dbg))

    def login(self):
        """
        This function performs a login to the OpenTouch
        RESTful service.
        """
        # TODO
        # We should probably split this in
        #   - authenticate()
        #   - Session()
        # This is the way RESTful API is doing it.
        # Or login() becomes a helper function to do both in order

        print("Attempting to login ...")

        authurl = "/api/rest/authenticate?version=1.0"
        authresponse = self.rest.get(self.ot_url + authurl)
        self.debugprint("Request Headers:\n%s" %
                        authresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % authresponse.headers)
        self.debugprint(authresponse)
        self.debugprint("Response Content:\n%s" % authresponse.content)

        rqheader = {"Content-Type": "application/json"}
        payload = {"ApplicationName": self.sn}

        if authresponse.status_code == 200:
            print("Authentication successfull!")
            print("Attempting to register session!")
            self.authentication = authresponse.json()

            try:
                authpostresponse = self.rest.post(
                    self.authentication["publicUrl"],
                    headers=rqheader,
                    data=json.dumps(payload)
                )
            except requests.exceptions.ConnectionError:
                print("publicUrl failed, trying internal!")
                authpostresponse = self.rest.post(
                    self.authentication["internalUrl"],
                    headers=rqheader,
                    data=json.dumps(payload)
                )

            self.debugprint("Request POST Headers:\n%s" %
                            authpostresponse.request.headers)
            self.debugprint("Response POST Headers:\n%s" %
                            authpostresponse.headers)
            self.debugprint(authpostresponse)
            self.debugprint("Response POST Content:\n%s" %
                            authpostresponse.content)
            if authpostresponse.status_code == 200:
                print("Session successfully registered: OK - %s" %
                      authpostresponse)
                self.login_successfull = True
                self.session = authpostresponse.json()
                print("Session information:\n%s" %
                      json.dumps(self.session, indent=4))
            elif authpostresponse.status_code == 400:
                print("Bad Request - %s" % authpostresponse)
                self.login_successfull = False
            elif authpostresponse.status_code == 403:
                print("Forbidden - %s" % authpostresponse)
                self.login_successfull = False
            elif authpostresponse.status_code == 500:
                print("Internal Server Error - %s" % authpostresponse)
                self.login_successfull = False
            elif authpostresponse.status_code == 503:
                print("Service Unavailable - %s" % authpostresponse)
                self.login_successfull = False
            return authpostresponse

        elif authresponse.status_code == 401:
            print("ERROR: Username or password incorrect/missing!")
            self.login_successfull = False
        # NOTES
        # This goes beyond API documentation, seen when OT was unavailable
        elif authresponse.status_code == 502:
            print("Bad Gateway - %s" % authresponse)
            self.login_successfull = False
        return authresponse

    def keepalive(self):
        """
        This function performs a session keepalive with the OpenTouch
        RESTful service.
        """

        rqheader = {"Content-Type": "application/json"}
        payload = {"ApplicationName": self.sn}

        try:
            karesponse = self.rest.post(
                self.authentication["publicUrl"] + "/keepalive",
                headers=rqheader,
                data=json.dumps(payload)
            )
        except requests.exceptions.ConnectionError:
            print("publicUrl failed, trying internal!")
            karesponse = self.rest.post(
                self.authentication["internalUrl"] + "/keepalive",
                headers=rqheader,
                data=json.dumps(payload)
            )

        self.debugprint("Request POST Headers:\n%s" %
                        karesponse.request.headers)
        self.debugprint("Response POST Headers:\n%s" %
                        karesponse.headers)
        self.debugprint(karesponse)
        self.debugprint("Response POST Content:\n%s" %
                        karesponse.content)
        if karesponse.status_code == 204:
            print("Session successfully refreshed: OK - %s" % karesponse)
        elif karesponse.status_code == 400:
            print("Bad Request - %s" % karesponse)
        elif karesponse.status_code == 403:
            print("Forbidden - %s" % karesponse)
            print("(The session doesn't exist!)")
        elif karesponse.status_code == 500:
            print("Internal Server Error - %s" % karesponse)
        elif karesponse.status_code == 503:
            print("Service Unavailable - %s" % karesponse)
        return karesponse

    def logout(self):
        """
        This function performs a logout from the OpenTouch
        RESTful service.
        """

        print("Attempting to logout ...")

        rqheader = {"Content-Type": "application/json"}
        payload = {"ApplicationName": self.sn}

        try:
            delresponse = self.rest.delete(
                self.authentication["publicUrl"],
                headers=rqheader,
                data=json.dumps(payload)
            )
        except requests.exceptions.ConnectionError:
            print("publicUrl failed, trying internal!")
            delresponse = self.rest.delete(
                self.authentication["internalUrl"],
                headers=rqheader,
                data=json.dumps(payload)
            )

        self.debugprint("Request POST Headers:\n%s" %
                        delresponse.request.headers)
        self.debugprint("Response POST Headers:\n%s" %
                        delresponse.headers)
        self.debugprint(delresponse)
        self.debugprint("Response POST Content:\n%s" %
                        delresponse.content)
        if delresponse.status_code == 204:
            print("Session successfully closed: OK - %s" %
                  delresponse)
        elif delresponse.status_code == 400:
            print("Bad Request - %s" % delresponse)
        elif delresponse.status_code == 403:
            print("Forbidden - %s" % delresponse)
            print("(The session was already closed!)")
        elif delresponse.status_code == 500:
            print("Internal Server Error - %s" % delresponse)
            print("(The session doesn't exist!)")
        elif delresponse.status_code == 503:
            print("Service Unavailable - %s" % delresponse)
        return delresponse

    def debugprint(self, content):
        """
        Takes content as an argument and prints it if
        debugging is enabled.
        """
        if self.dbg:
            print(content)

    def getlogins(self):
        """
        This function returns the currently logged in user.
        For an administrator all logged in users will be returned.
        """
        rqheader = {"Content-Type": "application/json"}
        userurl = "/api/rest/1.0/logins"
        userresponse = self.rest.get(self.ot_url + userurl,
                                     headers=rqheader)

        self.debugprint("Request Headers:\n%s" %
                        userresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % userresponse.headers)
        self.debugprint(userresponse)
        self.debugprint("Response Content:\n%s" % userresponse.content)

        if userresponse.status_code == 200:
            return userresponse
        elif userresponse.status_code == 400:
            print("Bad Request - %s" % userreponse)
        elif userresponse.status_code == 403:
            print("Forbidden - %s" % userresponse)
        elif userresponse.status_code == 500:
            print("Internal Server Error - %s" % userresponse)
        elif userresponse.status_code == 503:
            print("Service Unavailable - %s" % userresponse)
        return userresponse

    def userdetails(self):
        """
        This function returns the details of the currently
        logged in user.
        """
        rqheader = {"Content-Type": "application/json"}
        userurl = "/api/rest/1.0/users/" + self.username
        userresponse = self.rest.get(self.ot_url + userurl,
                                     headers=rqheader)

        self.debugprint("Request Headers:\n%s" %
                        userresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % userresponse.headers)
        self.debugprint(userresponse)
        self.debugprint("Response Content:\n%s" % userresponse.content)

        if userresponse.status_code == 200:
            print("Get user details - %s" % userresponse)
            self.devices = userresponse.json()
            print("User information:\n%s" %
                  json.dumps(self.devices, indent=4))
        elif userresponse.status_code == 400:
            print("Bad Request - %s" % userreponse)
        elif userresponse.status_code == 403:
            print("Forbidden - %s" % userresponse)
        elif userresponse.status_code == 500:
            print("Internal Server Error - %s" % userresponse)
        elif userresponse.status_code == 503:
            print("Service Unavailable - %s" % userresponse)
        return userresponse

    def userpreferences(self):
        """
        This function returns the preferences of the currently
        logged in user.
        """

        # NOTES
        # - This is currently undocumented in API guide
        # - I assume the same response codes as for "user details" apply
        # - We can read the language preference from here (guiLanguage)
        # - guiLanguage will hold: de, en, fr (and so on)
        # - Would likely also hold the following attributes
        #   - personalMobile
        #   - personalPhone

        rqheader = {"Content-Type": "application/json"}
        userurl = "/api/rest/1.0/users/" + self.username + "/preferences"
        userresponse = self.rest.get(self.ot_url + userurl,
                                     headers=rqheader)

        self.debugprint("Request Headers:\n%s" %
                        userresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % userresponse.headers)
        self.debugprint(userresponse)
        self.debugprint("Response Content:\n%s" % userresponse.content)

        if userresponse.status_code == 200:
            print("Get user preferences - %s" % userresponse)
            self.preferences = userresponse.json()
            print("User preferences:\n%s" %
                  json.dumps(self.preferences, indent=4))
        elif userresponse.status_code == 400:
            print("Bad Request - %s" % userreponse)
        elif userresponse.status_code == 403:
            print("Forbidden - %s" % userresponse)
        elif userresponse.status_code == 500:
            print("Internal Server Error - %s" % userresponse)
        elif userresponse.status_code == 503:
            print("Service Unavailable - %s" % userresponse)
        return userresponse

    def makebasiccall(self, device, callee, anonymous=False,
                      autoanswer=False):
        """
        This function places a basic call.

        Requires:
            - deviceId (the device of the caller)
            - callee (the number to be called)
            - anonymous (if the number should be suppressed)
            - autoAnswer (if the callback is automatically accepted)
        """

        rqheader = {"Content-Type": "application/json"}
        call = {
            "deviceId": device,
            "callee": callee,
            "anonymous": anonymous,
            "autoAnswer": autoanswer
        }
        bcurl = "/api/rest/1.0/telephony/basicCall"
        bcresponse = self.rest.post(self.ot_url + bcurl,
                                    headers=rqheader,
                                    data=json.dumps(call))

        self.debugprint("Request Headers:\n%s" %
                        bcresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % bcresponse.headers)
        self.debugprint(bcresponse)
        self.debugprint("Response Content:\n%s" % bcresponse.content)

        if bcresponse.status_code == 201:
            print("Call successfully made - %s" % bcresponse)
        elif bcresponse.status_code == 400:
            print("Bad Request - %s" % bcresponse)
        elif bcresponse.status_code == 401:
            print("Unauthorized - %s" % bcresponse)
        elif bcresponse.status_code == 403:
            print("Forbidden - %s" % bcresponse)
        elif bcresponse.status_code == 500:
            print("Internal Server Error - %s" % bcresponse)
        elif bcresponse.status_code == 503:
            print("Service Unavailable - %s" % bcresponse)
        return bcresponse

    def answerbasiccall(self, device):
        """
        This function answers a basic call.
        Takes deviceId as an argument.
        """

        # NOTES
        # You can accept an incoming call, but not the callback coming
        # from the OT if you set autoAnswer to False
        #
        # TELEPHONY_BASIC doesn't allow a RESTful notification towards
        # the user. We can simply only accept the call if you see it
        # on your handset.

        rqheader = {"Content-Type": "application/json"}
        bcurl = "/api/rest/1.0/telephony/basicCall/answer"
        bcresponse = self.rest.post(self.ot_url + bcurl,
                                    headers=rqheader,
                                    data=json.dumps({"deviceId": device}))

        self.debugprint("Request Headers:\n%s" %
                        bcresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % bcresponse.headers)
        self.debugprint(bcresponse)
        self.debugprint("Response Content:\n%s" % bcresponse.content)

        if bcresponse.status_code == 204:
            print("Call successfully answered - %s" % bcresponse)
        elif bcresponse.status_code == 400:
            print("Bad Request - %s" % bcresponse)
        elif bcresponse.status_code == 401:
            print("Unauthorized - %s" % bcresponse)
        elif bcresponse.status_code == 403:
            print("Forbidden - %s" % bcresponse)
        elif bcresponse.status_code == 500:
            print("Internal Server Error - %s" % bcresponse)
        elif bcresponse.status_code == 503:
            print("Service Unavailable - %s" % bcresponse)
        return bcresponse

    def dropbasiccall(self):
        """
        This function drops a basic call.
        """

        # NOTES
        # Changes in OT2.0 Iteration 9 Hotfixes 2014.02.21
        #   - Exit from the call:
        #       - if the call is a single call, it is released
        #       - if it is conference, the call carries on without
        #         the user

        rqheader = {"Content-Type": "application/json"}
        bcurl = "/api/rest/1.0/telephony/basicCall/dropme"
        bcresponse = self.rest.post(self.ot_url + bcurl, headers=rqheader)

        self.debugprint("Request Headers:\n%s" % bcresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % bcresponse.headers)
        self.debugprint(bcresponse)
        self.debugprint("Response Content:\n%s" % bcresponse.content)

        if bcresponse.status_code == 204:
            print("Call ended - %s" % bcresponse)
        elif bcresponse.status_code == 400:
            print("Bad Request - %s" % bcresponse)
        elif bcresponse.status_code == 403:
            print("Forbidden - %s" % bcresponse)
        elif bcresponse.status_code == 500:
            print("Internal Server Error - %s" % bcresponse)
        elif bcresponse.status_code == 503:
            print("Service Unavailable - %s" % bcresponse)
        return bcresponse

    def devget(self, devurl):
        """
        This function sends a GET request.
            - Requires request URL (server/host is set)

        Example for devurl:
        devurl = /api/rest/1.0/users/{login.name}/preferences

        Meant for development.
        """

        # TODO
        # Potentially remove function after development phase

        rqheader = {"Content-Type": "application/json"}
        devresponse = self.rest.get(self.ot_url + devurl,
                                    headers=rqheader)

        self.debugprint("Request Headers:\n%s" %
                        devresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % devresponse.headers)
        self.debugprint(devresponse)
        self.debugprint("Response Content:\n%s" % devresponse.content)
        return devresponse

    def devpost(self, devurl, payload):
        """
        This function sends a POST request with payload.
            - Requires request URL (server/host is set)
            - Requires payload as dict

        Example for devurl:
        devurl = "/api/rest/1.0/telephony/basicCall/answer"

        Meant for development.
        """

        # TODO
        # Potentially remove function after development phase

        rqheader = {"Content-Type": "application/json"}
        devresponse = self.rest.post(self.ot_url + devurl,
                                     headers=rqheader,
                                     data=json.dumps(payload))

        self.debugprint("Request Headers:\n%s" %
                        devresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % devresponse.headers)
        self.debugprint(devresponse)
        self.debugprint("Response Content:\n%s" % devresponse.content)
        return devresponse


if __name__ == "__main__":
    """
    This is called if running as a script and not being imported by
    another script!
    """
    sn = "RESTcall v0.3"

    print("""
%s
A RESTful client backend/library for Alcatel-Lucent Enterprise OpenTouch

Developed in 2014 by:
Benjamin Eggerstedt
Christian Sailer\n""" % sn)

    # Load the login credentials from external file that is in .gitignore
    # Never commit your login credentials to a public respository
    try:
        with open("login.json", "r") as json_data:
            login = json.load(json_data)
            ot_url = login["server"]
            username = login["username"]
            password = login["password"]
    except IOError:
        print("ERROR: Couldn't find \'login.json\' file!")
        sys.exit("You may want to rename / edit the template!")
    except TypeError:
        sys.exit("ERROR: Couldn't read json format!")

    if ot_url == "https://yourserver":
        sys.exit("This won't work with default template values!")

    # Use the class, set variables
    #                                               vSSL, Debug
    client = Client(ot_url, username, password, sn, False, False)
    client.login()

    if client.login_successfull is True:
        devices = client.userdetails()
        preferences = client.userpreferences()

    # TODO:
    #   - Need to write logout() function
    #   - Need a way to keep our session active
    #       - POST api/session/keepalive (TBD)
    # client.logout()
