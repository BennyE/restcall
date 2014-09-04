#!/usr/bin/python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#
# Some license stuff
# benjamin eggerstedt
# christian sailer (alphabetical order - sorry ;)

# Imports
import json
import sys
try:
    import requests
except ImportError:
    sys.exit("Dependency missing: python-requests")

# TODO & NOTES:
# - Deutsch?
# - SSL Zertifikat ist doch "nie" ungueltig beim Kunden oder?
# - Error Handler
# - Version Handler (RESTful v1.0, v1.1, v1.x)
# - Proxy Handler
# - Mehr Try & Except zur Fehlerbehandlung
# - Auslesen welche Faehigkeiten ein User hat (BASIC, ADVANCED)
#   - Anzeige in GUI o.ae. nach Faehigkeiten
# - Parameter an makecall() uebergeben um Geraet eines Nutzers zu waehlen usw.


class Client(object):
    """
    Client is a RESTful API client class that leverages python-requests
    and interacts with the Alcatel-Lucent Enterprise
    OpenTouch RESTful service

    The class requires the following parameters to be set:
        - ot_url     = BaseURL of OpenTouch server
        - username   = Valid username for OpenTouch service
        - password   = Valid password for OpenTouch service
        - sn         = Software name / version
    Optional:
        - verify_ssl = Override with False if OpenTouch service
                       doesn't have a valid SSL certificate
        - dbg        = Debug flag
    """

    def __init__(self, ot_url, username, password, sn,
                 verify_ssl=True, dbg=False):
        """
        Constructor of class "Client"
        """
        self.ot_url = ot_url
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
        self.debugprint("""
Debug:
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
        print("Attempting to login ...")

        authurl = "/api/rest/authenticate?version=1.0"
        authresponse = self.rest.get(self.ot_url + authurl)
        self.debugprint("Request Headers:\n%s" % authresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % authresponse.headers)
        self.debugprint(authresponse)
        self.debugprint("Response Content:\n%s" % authresponse.content)

        rqheader = {"Content-Type": "application/json"}
        payload = {"ApplicationName": self.sn}

        if authresponse.status_code == 200:
            print("Authentication successfull!")
            print("Attempting to register session!")
            authpostresponse = self.rest.post(
                                authresponse.json()["publicUrl"],
                                headers = rqheader,
                                data = json.dumps(payload)
                                )
            self.debugprint("Request POST Headers:\n%s" % authpostresponse.request.headers)
            self.debugprint("Response POST Headers:\n%s" % authpostresponse.headers)
            self.debugprint(authpostresponse)
            self.debugprint("Response POST Content:\n%s" % authpostresponse.content)
            if authpostresponse.status_code == 200:
                print("Session successfully registered!")
                print(authpostresponse.json())
                self.login_successfull = True
            else:
                print("Something went wrong ...")
                self.login_successfull = False

        elif authresponse.status_code == 401:
            print("Username or password wrong/missing!")
            self.login_successfull = False 
        else:
            # Some more error handling here
            pass 
        #print(authresponse)
        #self.debugprint(authresponse.json())
        #if self.dbg:
        #    print(authresponse.json())
        #print(response.content)

    def debugprint(self, content):
        """
        Takes content as an argument and prints it if
        debugging is enabled.
        """
        if self.dbg:
            print(content)

    
    def userdetails(self):
        """
        This function returns the details of the currently
        logged in user.
        """
        rqheader = {"Content-Type" : "application/json"}
        userurl = "/api/rest/1.0/users/" + self.username
        userresponse = self.rest.get(self.ot_url + userurl, headers = rqheader)
                
        self.debugprint("Request Headers:\n%s" % userresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % userresponse.headers)
        self.debugprint(userresponse)
        self.debugprint("Response Content:\n%s" % userresponse.content)

        if userresponse.status_code == 200:
            print(userresponse.json())
            userdict = userresponse.json()   
            return userdict
        else:
            return "Error"


    def makebasiccall(self, device, callee, anonymous=False, autoanswer=False):
        """
        This function places a basic call.
        
        """

        # TODO
        # - Device Id, welche nehmen wir da per default?
        # - Ich wuerd vorschlagen wir laden die Faehigkeiten des Teilnehmers und dann das DeskPhone per default

        rqheader = {"Content-Type" : "application/json"}
        call = {
            "deviceId" : device,
            "callee" : callee,
            "anonymous" : anonymous,
            "autoAnswer" : autoanswer
        }
        bcurl = "/api/rest/1.0/telephony/basicCall"
        bcresponse = self.rest.post(self.ot_url + bcurl, headers = rqheader, data=json.dumps(call))
                
        self.debugprint("Request Headers:\n%s" % bcresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % bcresponse.headers)
        self.debugprint(bcresponse)
        self.debugprint("Response Content:\n%s" % bcresponse.content)

        # TODO: Pruefen was hier zurueckkommt!
        # Welche Notifications gibt es (besetzt?)?

        if bcresponse.status_code == 201:
            print(bcresponse.json())
            bcdict = userresponse.json()   
            return bcdict
        else:
            return "Error"

    

    def endbasiccall(self, device):
        """
        This function ends a basic call.
        
        """

        # TODO

        rqheader = {"Content-Type" : "application/json"}
        bcurl = "/api/rest/1.0/telephony/basicCall/dropme"
        bcresponse = self.rest.post(self.ot_url + bcurl, headers = rqheader)
                
        self.debugprint("Request Headers:\n%s" % bcresponse.request.headers)
        self.debugprint("Response Headers:\n%s" % bcresponse.headers)
        self.debugprint(bcresponse)
        self.debugprint("Response Content:\n%s" % bcresponse.content)

        # TODO: Pruefen was hier zurueckkommt!
        # Welche Notifications gibt es (besetzt?)?

        if bcresponse.status_code == 201:
            print(bcresponse.json())
            bcdict = userresponse.json()   
            return bcdict
        else:
            return "Error"


if __name__ == "__main__":
    """
    This is called if running as a script and not being imported by
    another script!
    """
    ot_url = "https://remote.alu4u.com"
    sn = "RESTcall v0.2"
    
    print("""
%s - RESTful client backend/library for Alcatel-Lucent Enterprise OpenTouch

Developed in 2014 by:
Benjamin Eggerstedt
Christian Sailer""" % sn)

    # Load the login credentials from external file that is in .gitignore
    # Never commit your login credentials to a public respository
    try:
        with open("login.json", "r") as json_data:
            login = json.load(json_data)
            username = login["username"]
            password = login["password"]
    except IOError:
        sys.exit("Couldn't find \'login.json\' file!") 
    except TypeError:
        sys.exit("Couldn't read json format!")

    #                                               vSSL, Debug
    client = Client(ot_url, username, password, sn, False, True)   
    client.login()
    #if client.login_successfull is True:
    #    userdict = client.userdetails()
        # Damit kann man halt nett im Programm sehen ob gewisse Dinge
        # gesetzt wurden bzw. verfuegbar sind.
    #    if userdict != "Error":
    #        print("Mail: %s" % userdict["companyEmail"])
       # caller = client.makecall()
    # Mueeedeeee ;)
    #client.logout()
