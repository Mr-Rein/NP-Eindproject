### Modules inladen
import urllib
import requests
import time
import json
from prettytable import PrettyTable

### Variabelen maken

# WEBEX (key eventueel veranderen als hij ongeldig is)
webex_key = "Bearer Nzc0NTMwZDUtMDM2Yi00YzI2LWI0ZmMtMWE5YTY1ZjJlMzk5Y2E2NjRiNDAtZDAw_PF84_fecd1450-832a-4c45-a6ec-5e060cd52046"

r = requests.get(   "https://webexapis.com/v1/rooms",
                    headers = {"Authorization": webex_key}
                )

# SPORTSDB
sportsdb_url = "https://www.thesportsdb.com/api/v1/json/"
sportsdb_key = "1" # Test-key

main_url = sportsdb_url + urllib.parse.urlencode({
    "key": sportsdb_key, })

### Welkoms bericht, korte intro

print("\nWelkom op mijn network programming project:")
print("   Voetbal data via thesportsdb.com open API.")
print(  "   _____________________________\n"
        "   |             |             |\n"
        "   |___          |          ___|\n"
        "   |_  |         |         |  _|\n"
        "   | | |.       ,|.       .| | |\n"
        "   | | | )     ( | )     ( | | |\n"
        "   |_| |'       `|'       `| |_|\n"
        "   |___|         |         |___|\n"
        "   |             |             |\n"
        "   |_____________|_____________|\n"
)

print("Ryan Balfoort, SNWB 2020 Howest Brugge.\n")
input("Press any key to continue...")

### Lijst al mijn rooms op webex

print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print (room["title"])

### Vragen welke room er moet gemonitord worden

while True:

    # Geef de naam van de room die u wilt
    roomNaam = input("\nGelieve de room te selecteren die u wilt monitoren: ")

    # Defines a variable that will hold the roomId 
    roomIdToMonitor = None

    for room in rooms:
        # Zoek de room die overeenkomt 
        if(room["title"].find(roomNaam) != -1):

            # Toon gevonden rooms
            print ("Gevonden rooms met het woord " + roomNaam)
            print(room["title"])

            # Stores room id and room title into variables
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room : " + roomTitleToGetMessages)
            break

    if(roomIdToGetMessages == None):
        print("Sorry, I didn't find any room with " + roomNaam + " in it.")
        print("Please try again...")
    else:
        break

# controleer op messages zolang er geen fout voorkomt
while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is is ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    GetParameters = {
                            "roomId": roomIdToGetMessages,
                            "max": 1
                         }
    # run the call against the messages endpoint of the Webex Teams API using the HTTP GET method
    r = requests.get("https://api.ciscospark.com/v1/messages", 
                         params = GetParameters, 
                         headers = {"Authorization": webex_key}
                    )
    # verify if the returned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception( "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
    
    # get the JSON formatted returned data
    json_data = r.json()
    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")
    
    # store the array of messages
    messages = json_data["items"]
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)
    
    #########################################################
    ### OPTIE 1: INFORMATIE OVER EEN BEPAALD TEAM KRIJGEN ###
    #########################################################

    if message.find("!") == 0:
        # "!" + team -> om informatie te geven over een team
        #  e.g.  "!Club Brugge"
        team = message[1:]
        
        #  "t" is the the team to lookup
        #  "key" is 1 (testkey)
        sportsdb_GetAPI = { 
                                "t": team, 
                                "key": "1"
                               }

        # Get team information using the sportsdb API service using the HTTP GET method
        r = requests.get("https://www.thesportsdb.com/api/v1/json/1/searchteams.php", 
                             params = sportsdb_GetAPI
                        )

        # JSON formatted data krijgen
        json_data = r.json()
        
        # Enkel data eruit halen die ik wil
        teamName = json_data['teams'][0]['strTeam']
        teamNameAlt = json_data['teams'][0]['strAlternate']
        teamFormedYear = json_data['teams'][0]['intFormedYear']
        teamStadium = json_data['teams'][0]['strStadium']
        teamLeague = json_data['teams'][0]['strLeague']

        responseMessage = "Naam: " + teamName + " ( " + teamNameAlt + " )\n" + "Opgericht: " + teamFormedYear + "\n" + "Stadium: " + teamStadium + "\n" + "Competitie: " + teamLeague
        print(responseMessage)

        # the Webex Teams HTTP headers, including the Content-Type header for the POST JSON data
        HTTPHeaders = { 
                             "Authorization": webex_key,
                             "Content-Type": "application/json"
                           }

        # the Webex Teams POST JSON data
        #  "roomId" is is ID of the selected room
        #  "text": is the responseMessage assembled above
        PostData = {
                            "roomId": roomIdToGetMessages,
                            "text": responseMessage
                        }

        # run the call against the messages endpoint of the Webex Teams API using the HTTP POST method
        r = requests.post( "https://webexapis.com/v1/messages", 
                              data = json.dumps(PostData), 
                              headers = HTTPHeaders
                         )

    ###############################################################################################
    ### OPTIE 2: INFORMATIE OVER DE LAATSTE 10 WEDSTRIJDEN IN DE HOOGSTE COMPETITIE IN EEN LAND ###
    ###############################################################################################

    elif message.find("?") == 0:
        #  "?" + land -> om de laatste 10 wedstrijden te geven
        #  e.g.  "?belgium"
        league = message[1:]

        if league == "Spain" or league == "spain" or league == "Spanje" or league == "spanje":
            league = '4335'
        
        elif league == "England" or league == "england" or league == "Engeland" or league == "engeland":
            league = '4328'
        
        elif league == "Netherlands" or league == "netherlands" or league == "Nederland" or league == "nederland":
            league = '4337'

        elif league == "Belgium" or league == "belgium" or league == "Beglië" or league == "belgië":
            league = '4338'

        elif league == "France" or league == "france" or league == "Frankrijk" or league == "frankrijk":
            league = '4484'
        
        #  "id" is de competitie om te zoeken
        #  "key" is 1 (testkey)
        sportsdb_GetAPI = { 
                                "id": league, 
                                "key": "1"
                               }

        # Get league information using the sportsdb API service using the HTTP GET method
        r = requests.get("https://www.thesportsdb.com/api/v1/json/1/eventspastleague.php", 
                             params = sportsdb_GetAPI
                        )

        # JSON formatted data krijgen
        json_data = r.json()

        # Toon resultaten van de laatste 10 wedstrijden in een competitie
        for x in range (10):

            # Enkel data eruit halen die ik wil
            teamHome = str(json_data['events'][x]['strHomeTeam'])
            teamAway = str(json_data['events'][x]['strAwayTeam'])
            scoreHome = str(json_data['events'][x]['intHomeScore'])
            scoreAway = str(json_data['events'][x]['intAwayScore'])

            responseMessage = teamHome + " " + scoreHome + " - " + scoreAway + " " + teamAway
            print(responseMessage)

            # the Webex Teams HTTP headers, including the Content-Type header for the POST JSON data
            HTTPHeaders = { 
                                "Authorization": webex_key,
                                "Content-Type": "application/json"
                            }

            # the Webex Teams POST JSON data
            #  "roomId" is is ID of the selected room
            #  "text": is the responseMessage assembled above
            PostData = {
                                "roomId": roomIdToGetMessages,
                                "text": responseMessage
                            }

            # run the call against the messages endpoint of the Webex Teams API using the HTTP POST method
            r = requests.post( "https://webexapis.com/v1/messages", 
                                data = json.dumps(PostData), 
                                headers = HTTPHeaders
                            )

    ################################################################################################
    ### OPTIE 3: INFORMATIE OVER DE VOLGENDE 10 WEDSTRIJDEN IN DE HOOGSTE COMPETITIE IN EEN LAND ###
    ################################################################################################

    elif message.find("-") == 0:
        #  "-" + land -> om de volgende 10 wedstrijden te geven
        #  e.g.  "-belgium"
        league = message[1:]

        if league == "Spain" or league == "spain" or league == "Spanje" or league == "spanje":
            league = '4335'
        
        elif league == "England" or league == "england" or league == "Engeland" or league == "engeland":
            league = '4328'
        
        elif league == "Netherlands" or league == "netherlands" or league == "Nederland" or league == "nederland":
            league = '4337'

        elif league == "Belgium" or league == "belgium" or league == "Beglië" or league == "belgië":
            league = '4338'

        elif league == "France" or league == "france" or league == "Frankrijk" or league == "frankrijk":
            league = '4484'
        
        #  "id" is de competitie om te zoeken
        #  "key" is 1 (testkey)
        sportsdb_GetAPI = { 
                                "id": league, 
                                "key": "1"
                               }

        # Get league information using the sportsdb API service using the HTTP GET method
        r = requests.get("https://www.thesportsdb.com/api/v1/json/1/eventsnextleague.php", 
                             params = sportsdb_GetAPI
                        )

        # JSON formatted data krijgen
        json_data = r.json()

        # Toon de volgende 10 wedstrijden in een competitie
        for x in range (10):

            # Enkel data eruit halen die ik wil
            teamHome = str(json_data['events'][x]['strHomeTeam'])
            teamAway = str(json_data['events'][x]['strAwayTeam'])
            dateGame = str(json_data['events'][x]['dateEvent'])

            responseMessage = teamHome + " vs. " + teamAway + " (" + dateGame + ")"
            print(responseMessage)

            # the Webex Teams HTTP headers, including the Content-Type header for the POST JSON data
            HTTPHeaders = { 
                                "Authorization": webex_key,
                                "Content-Type": "application/json"
                            }

            # the Webex Teams POST JSON data
            #  "roomId" is is ID of the selected room
            #  "text": is the responseMessage assembled above
            PostData = {
                                "roomId": roomIdToGetMessages,
                                "text": responseMessage
                            }

            # run the call against the messages endpoint of the Webex Teams API using the HTTP POST method
            r = requests.post( "https://webexapis.com/v1/messages", 
                                data = json.dumps(PostData), 
                                headers = HTTPHeaders
                            )

    #####################################################################
    ### OPTIE 4: INFORMATIE OVER HET VOORLOPIG KLASSEMENT IN EEN LAND ###
    #####################################################################

    elif message.find("/") == 0:
        #  "/" + land -> om het klassement te tonen
        #  e.g.  "/belgium"
        league = message[1:]
        season = "2020-2021"

        print("Voorlopig klassement: ")

        if league == "Spain" or league == "spain" or league == "Spanje" or league == "spanje":
            league = '4335'
        
        elif league == "England" or league == "england" or league == "Engeland" or league == "engeland":
            league = '4328'
        
        elif league == "Netherlands" or league == "netherlands" or league == "Nederland" or league == "nederland":
            league = '4337'

        elif league == "Belgium" or league == "belgium" or league == "Beglië" or league == "belgië":
            league = '4338'

        elif league == "France" or league == "france" or league == "Frankrijk" or league == "frankrijk":
            league = '4484'
        
        #  "l" is de competitie om te zoeken
        #  "key" is 1 (testkey)
        sportsdb_GetAPI = { 
                                "l": league,
                                "s": season,
                                "key": "1"
                               }

        # Get league information using the sportsdb API service using the HTTP GET method
        r = requests.get("https://www.thesportsdb.com/api/v1/json/1/lookuptable.php", 
                             params = sportsdb_GetAPI
                        )

        # JSON formatted data krijgen
        json_data = r.json()

        # Mooie tabel maken
        tableComp = PrettyTable(['Team','Points'])

        # Toon de top 10 in de competitie
        for x in range (10):

            # Enkel data eruit halen die ik wil
            team = str(json_data['table'][x]['name'])
            teamPoints = str(json_data['table'][x]['total'])

            # Proberen mooie tabel te maken
            tableComp.add_row([team,teamPoints])

            # Bericht opstellen om te verzenden
            responseMessage = str(x+1) + ". " + team + " :  " + teamPoints + " (Punten)"
            responseMessageTableForm = tableComp

            # Mooie tabel (enkel te zien in programma zelf)
            print(responseMessageTableForm)

            # the Webex Teams HTTP headers, including the Content-Type header for the POST JSON data
            HTTPHeaders = { 
                                "Authorization": webex_key,
                                "Content-Type": "application/json"
                            }

            # the Webex Teams POST JSON data
            #  "roomId" is is ID of the selected room
            #  "text": is the responseMessage assembled above
            PostData = {
                                "roomId": roomIdToGetMessages,
                                "text": responseMessage
                            }

            # run the call against the messages endpoint of the Webex Teams API using the HTTP POST method
            r = requests.post( "https://webexapis.com/v1/messages", 
                                data = json.dumps(PostData), 
                                headers = HTTPHeaders
                            )

### GEBRUIK ###

#   !x  = info over team
#   ?x = laatste 10 wedstrijden in hoogste competitie
#   -x = volgende 10 wedstrijden in hoogste competitie
#   /x = huidig klassement in hoogste competitie