from steem.transactionbuilder import TransactionBuilder
from steembase import operations
from steem import Steem
from steem.blockchain import Blockchain
from steem.account import Account
from steem.post import Post
import json
import datetime
import requests
import time
import requests
import hashlib
import string
import random
from random import randint

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

users = ("user")
keys = {"user":"key"}
addon_monsters = {"0":[],"1":[91],"2":[64],"3":[62],"4":[63],"5":[62,64],"6":[62,66],"7":[62,63],"8":[62,66,64],"9":[62,65],"10":[62,66,63],"11":[62,65,64],"12":[62,66,65],"13":[63,66,65]}
addon_brokenarrow = {"0":[],"1":[91],"2":[64],"3":[66],"4":[66,91],"5":[66,64],"6":[62,66],"7":[62,91,64],"8":[62,66,64],"9":[62,66,64],"10":[61,62,66],"11":[61,62,66],"12":[61,62,81],"13":[61,62,80]}
addon_upcloseandpersonal = {"0":[],"1":[91],"2":[64],"3":[62],"4":[61],"5":[62,64],"6":[61,64],"7":[61,62],"8":[61,62,91],"9":[61,62,64],"10":[81,62,64],"11":[80,62,64],"12":[81,61,62],"13":[80,61,62]}

def gettransactionid(username):
    time.sleep(20)
    # Ermittele  den letzten Block aus der Blockchain
    lastblock = steem.head_block_number
    #print (lastblock)
    print ("Letzter Block in der Blockchain:" +str(lastblock))
    startblock = lastblock -100

    #lade die API
    r = requests.get('https://steemmonsters.com/transactions/history?from_block=' +str(startblock))
    rawdata = r.json()
    for i in rawdata:
        type = i['type']
        player = i['player']
        trxid = i['id']
        if player == username and type == "sm_find_match":
            print (trxid)
            #check if this is a valid id
            r = requests.get('https://steemmonsters.com/battle/status?id=' +str(trxid))
            data = r.json()
            try:
                status = data['status']
                print ("ID Status:" +str(status))
                if int(status) == 1:
                    print ("Valid ID found")
                    return (trxid)
                if int(status) == 0:
                    print ("Valid ID found - waiting for match")
                    while int(status) == 0:
                        r = requests.get('https://steemmonsters.com/battle/status?id=' +str(trxid))
                        data = r.json()
                        status = data['status']
                        if int(status) == 1:
                            print ("Match found")
                            return (trxid)
            except:
                print ("unvalid ID")



def get_transactionid(username):
    time.sleep(6)
    found = False
    count = 0
    while found == False and count < 5:
        count = count +1
        print ("Attempt to get an ID number: " +str(count))
        b = Blockchain()
        end_block = steem.head_block_number
        start_block = end_block -100
        for block in b.stream_from(start_block=start_block, end_block=end_block, full_blocks=True):
            transactions =  block['transactions']
            for transaction in transactions:
                if (transaction['operations'][0][0] == "custom_json"):
                    if (transaction['operations'][0][1]['required_posting_auths'][0]) == user:
                        print (transaction)
                    if (transaction['operations'][0][1]['required_posting_auths'][0]) == user and (transaction['operations'][0][1]['id'])=="sm_find_match":
                        print (transaction['transaction_id'])
                        trxid = (transaction['transaction_id'])
                        #check if this is a valid id
                        r = requests.get('https://steemmonsters.com/battle/status?id=' +str(trxid))
                        data = r.json()
                        try:
                            status = data['status']
                            print ("ID Status:" +str(status))
                            if int(status) == 1:
                                found = True
                                return (trxid)
                        except:
                            found = False
    return

def check_if_buddy(name):
    buddy = False
    #get the list of other players
    r = requests.get("https://lightningdragon.bplaced.net/farmer-config.json")
    data = r.json()
    users = data[0]['users']
    for usr in users:
        if usr == name:
            buddy = True
    print ("buddy:")
    print (buddy)
    return (buddy)

def check_other_players():
    quest_ongoing = False
    #get the list of other players
    r = requests.get("https://lightningdragon.bplaced.net/farmer-config.json")
    data = r.json()
    users = data[0]['users']
    for usr in users:
        try:
            r = requests.get('https://steemmonsters.com/players/quests?username=' +str(usr))
            rawdata = r.json()
            data = rawdata[0]
            total_items = data['total_items']
            completed_items = data['completed_items']
            name = data['name']
            remaining = int(total_items) - int(completed_items)
            if remaining >0:
                if usr == user:
                    return(False)
                quest_ongoing = True
                print (usr)

        except:
            print ("Fehler")

    print (quest_ongoing)
    return (quest_ongoing)

def get_next_player():
    #get the deck data
    r = requests.get("https://lightningdragon.bplaced.net/farmer-config.json")
    data = r.json()
    users = data[0]['users']
    oldest_quest_age = 0
    nextuser = user
    for usr in users:
        #try:
            #get the age of the quest
            # get some data regarding the old quest from the API
            r = requests.get('https://steemmonsters.com/players/quests?username=' +str(usr))
            rawdata = r.json()
            data = rawdata[0]
            created_date = data['created_date']
            # get the age of the quest
            create_time = datetime.datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            current_time = datetime.datetime.now()
            time_since_last_quest = (current_time - create_time).days *24*3600 + (current_time - create_time).seconds
            #print (time_since_last_quest)
            if time_since_last_quest > oldest_quest_age:
                oldest_quest_age = time_since_last_quest
                nextuser = usr
        #except:
                #continue
    print (nextuser)
    return (nextuser)


def start_quest():
    json = '{"type":"daily"}'
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_start_quest",
            "json": json,
            "required_auths": [],
            "required_posting_auths": [user],
        }),
    ]
    tb = TransactionBuilder()
    tb.appendOps(ops)
    tb.appendSigner(user, "posting")
    tb.sign()
    tb.broadcast()


def claimreward():
    #get the claim id
    # get the current quest data
    r = requests.get('https://steemmonsters.com/players/quests?username=' +str(user))
    rawdata = r.json()
    data = rawdata[0]
    claimid = data['id']

    json = '{"type":"quest","quest_id":"' + claimid +'"}'
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_claim_reward",
            "json": json,
            "required_auths": [],
            "required_posting_auths": [user],
        }),
    ]
    tb = TransactionBuilder()
    tb.appendOps(ops)
    tb.appendSigner(user, "posting")
    tb.sign()
    tb.broadcast()



def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()

def smfindmatch():
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_find_match",
            "json": '{"match_type":"Ranked"}',
            "required_auths": [],
           "required_posting_auths": [user],
        }),
    ]
    tb = TransactionBuilder()
    tb.appendOps(ops)
    tb.appendSigner(user, "posting")
    tb.sign()
    tb.broadcast()


def cancel_match():
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_cancel_match",
            "json": '{"app":"steemmonsters/0.4.4.1"}',
            "required_auths": [],
            "required_posting_auths": [user],
        }),
    ]
    tb = TransactionBuilder()
    tb.appendOps(ops)
    tb.appendSigner(user, "posting")
    tb.sign()


def sm_submit_team(json):
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_submit_team",
            "json": json,
            "required_auths": [],
            "required_posting_auths": [user],
        }),
    ]
    tb = TransactionBuilder()
    tb.appendOps(ops)
    tb.appendSigner(user, "posting")
    tb.sign()
    tb.broadcast()

def smshowteam(show_json):
    ops = [
        operations.CustomJson(**{
            "from": user,
            "id": "sm_team_reveal",
            "json": show_json,
            "required_auths": [],
            "required_posting_auths": [user],
        }),
    ]
    tb = TransactionBuilder()
    tb.appendOps(ops)
    tb.appendSigner(user, "posting")
    tb.sign()
    tb.broadcast()


def match(deckid):
    addons = []
    # transmit the request to fight
    smfindmatch()
    print ("Request to fight has been sent")
    print ("Waiting for TRX ID")

    # get the block id for the request to fight
    try:
        trx_id = gettransactionid(user)
    except:
        time.sleep(3)
        trx_id = get_transactionid(user)

    # check if an opponnent has been found
    status = 0
    count = 0
    timeout = False
    while (status < 1) and (status > 1) and (timeout == False):
        time.sleep(1)
        count = count +1
        r = requests.get('https://steemmonsters.com/battle/status?id=' +str(trx_id))
        data = r.json()
        status = data['status']
        print ("Waiting for opponent")
        if count > 180:
            timeout = True
            break
    if timeout == False:
        print ("Match found")
        r = requests.get('https://steemmonsters.com/battle/status?id=' +str(trx_id))
        data = r.json()
        status = data['status']
        mana_cap = data['mana_cap']
        ruleset = data['ruleset']
        opponent = data['opponent_player']
        inactive = data['inactive']
        additional_mana = int(mana_cap)-15
        if int(additional_mana) > 13:
            additional_mana = 13
        #buddy = check_if_buddy(opponent)

        print (status)
        print (opponent)
        print (mana_cap)
        print (ruleset)
        print (additional_mana)
        print (inactive)
        (decknumber,remaining) = getquest()
        if remaining <1:
            if ("White" in inactive) or ("white" in inactive):
                deckid = [5,8,1,4]
            elif (("Red" in inactive) or ("red" in inactive)) and (("White" in inactive) or ("white" in inactive)):
                deckid = [49,50,48,52]

            else:
                deckid = [38,40,34,39]

            if ruleset == "Broken Arrows":
                if ("White" in inactive) or ("white" in inactive):
                    deckid = [5,8,2,1]
                elif (("Red" in inactive) or ("red" in inactive)) and (("White" in inactive) or ("white" in inactive)):
                    deckid = [49,50,48,52]
                else:
                    deckid = [38,40,37,35]


            if ruleset == "Up Close & Personal":
                if ("White" in inactive) or ("white" in inactive):
                    deckid = [5,8,2,1]
                elif (("Red" in inactive) or ("red" in inactive)) and (("White" in inactive) or ("white" in inactive)):
                    deckid = [49,45,48,47]
                else:
                    deckid = [38,40,37,35]


        #construct the team according to the given deckid:
        summoner = getcardid(deckid[0])
        monsters = []
        for i in range(1,len(deckid)):
            uid = getcardid(deckid[i])
            monsters.append(uid)

        # check if the rules allow neutralmosters
        neutral_allowed = True
        if ruleset == "Taking Sides":
            neutral_allowed = False


        #get additional monsters
        addons = addon_monsters
        if ruleset == "Broken Arrows":
            addons = addon_brokenarrow
        if ruleset == "Up Close & Personal":
            addons = addon_upcloseandpersonal

        addon_deck = addons[str(additional_mana)]
        print ("Adding additional monsters")
        print (addon_deck)
        if neutral_allowed == True:
            for i in range(0,len(addon_deck)):
                uid = getcardid(addon_deck[i])
                monsters.append(uid)

        deck = {'summoner': summoner, 'monsters' : monsters}

        secret = id_generator()
        strg_to_hash = (summoner + ',' + ",".join(monsters) + ',' + secret)
        hashvalue = hashlib.md5(strg_to_hash.encode('utf-8')).hexdigest()
        json = '{"trx_id":"' + trx_id +'","team_hash":"' +hashvalue +'"}'
        show_json = '{"trx_id":"' + trx_id +'","summoner":"' + summoner + '","monsters":["' +'","'.join(monsters) + '"],"secret":"' +secret +'"}'
        print (json)
        time.sleep(4)
        # submit the team
        sm_submit_team(json)
        time.sleep(4)
        print ("Team was submitted")
        smshowteam(show_json)
        print ("Team was revealed")
        time.sleep(4)
        # check if the fight is over
#        print ("Waiting for the battle to be over")
#        battle_over = False
#        while battle_over == False:
#            try:
#                r = requests.get('https://steemmonsters.com/battle/status?id=' +str(trx_id))
#                data = r.json()
#                status = data['status']
#                if int(status) >1:
#                    print ("Battle is over.")
#                    battle_over = True
#            except:
#                continue

def getcardid(cardnumber):
    # get the cards of the player from the API
    max_xp = -1
    r = requests.get('https://steemmonsters.com/cards/collection/' +str(user))
    data = r.json()
    cards = data['cards']
    for card in cards:
        card_detail_id = card['card_detail_id']
        if card_detail_id == cardnumber:
            xp = card['xp']
            if int(xp) > max_xp:
                max_xp = xp
                uid = card['uid']
    return(uid)

def getquest():
    print ("Checking quest details")
    # get the current quest data
    r = requests.get('https://steemmonsters.com/players/quests?username=' +str(user))
    rawdata = r.json()
    data = rawdata[0]
    total_items = data['total_items']
    completed_items = data['completed_items']
    name = data['name']
    remaining = int(total_items) - int(completed_items)
    print (name)
    print (remaining)
    #get the deck data
    r = requests.get("https://lightningdragon.bplaced.net/farmer-config.json")
    data = r.json()
    decks = data[1]['decks']
    decknumber = decks[name]
    #print (decknumber)
    return (decknumber,remaining)

def quest():
    (decknumber,remaining) = getquest()
    match(decknumber)
    (decknumber,remaining) = getquest()

    r = requests.get('https://steemmonsters.com/players/quests?username=' +str(user))
    rawdata = r.json()
    data = rawdata[0]
    claim_date = data['claim_date']
    created_date = data['created_date']
    if claim_date == None:
        claimreward()
        time.sleep(3)
    # check if a new quest can be started
    create_time = datetime.datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    current_time = datetime.datetime.now()
    time_since_last_quest = (current_time - create_time).days *24*3600 + (current_time - create_time).seconds
    if time_since_last_quest > 86401: #check if the last quest creation is more than 1 day old
        start_quest()
        time.sleep(3)
    (decknumber,remaining) = getquest()


if __name__ == '__main__':
    while True:
        try:
            for user in users:
                key = keys[user]
                steem = Steem(nodes=["https://steemd.privex.io"],
                    keys=[key])
                print ("_____________________________________")
                print ("Next player: " +user)
                quest()
            time.sleep(4)
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows args to be printed directly,
                                 # but may be overridden in exception subclasse$
            print ("Fehler")
