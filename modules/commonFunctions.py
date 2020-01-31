import requests
import json

def channelIDToName(channelID, clientID):
    headers = {
        'Client-ID': clientID
    }
    r = requests.get(f"https://api.twitch.tv/helix/users?id={channelID}", headers=headers)
    jsonObj = r.json()
    return jsonObj["data"][0]["login"]

def isUserVerified(mongoDBObj, user):
    if mongoDBObj.find({'discord': str(user.id)}).count() > 0:
        return True
    return False
