import re
import discord
from discord.ext import commands
import socket
from rHLDS import Console
client = commands.Bot(command_prefix = "!")

srv = Console(host='192.223.26.130', password='rational')
#srv = Console(host='localhost', password='rational')
srv.connect()

@client.event
async def on_ready():
    print("Bot is Ready")


'''@client.event
async def on_message(message):
    if(message.content.startswith('!log')):
        await message.channel.send("Channel will start logging..")'''

UDP_IP_ADDRESS = "0.0.0.0"
UDP_PORT_NO = 6789
channel = client.get_channel(775427997351542795)
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
sayList = []
redTeam = []
blueTeam = []
playerStats = {}
sayString = ""
blueScore = ""
redScore = ""
channel = client.get_channel(773619903054872596)
#DICTIONARY FORMAT NAME: KILLS, DEATHS, SUICIDES,  SGs KILLED, FLAG TOUCHES, FLAG CAPTURES, FLAG TIME, SG KILLS, DISPENSER KILLS, TKs, Grenade Kills
@client.command(pass_context=True)
async def start(ctx):
    global blueTeam
    global redTeam
    global blueScore
    global redScore
    global playerStats
    matchStart = 0
    await ctx.send('starting..')    
    while True:
        try:
            data, addr = serverSock.recvfrom(1024)
            print(str(data))
            
            if("say" in str(data)):
                name = re.search(r': "([^<]+)', str(data)).group(1)
                print(name)
            if('"Match_Begins_Now"' in str(data)):
                matchStart = 1

            if("joined team" in str(data)):
                name = re.search(r': "([^<]+)', str(data)).group(1)
                team = re.search(r'team "([^"]+)', str(data)).group(1)
                if(team == "Red"):
                    redTeam.append(name)
                    if(name in blueTeam):
                        blueTeam.remove(name)
                if(team == "Blue"):
                    blueTeam.append(name)
                    if(name in redTeam):
                        redTeam.remove(name)
                if(team == "SPECTATOR"):
                    if(name in blueTeam):
                        blueTeam.remove(name)
                    if(name in redTeam):
                        redTeam.remove(name)
                playerStats[name] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

            if(('say' not in str(data)) and ("say_team" not in str(data)) and (matchStart == 1)):
                
                if(("Team 1 dropoff" in str(data)) or ("Blue Capture Point" in str(data))):
                    name = re.search(r': "([^<]+)', str(data)).group(1)
                    print(name)
                    playerStats[name][5] += 1
                    print(playerStats)

                '''if("disconnected" in str(data)):
                    if(name in blueTeam):
                        blueTeam.remove(name)
                    if(name in redTeam):
                        redTeam.remove(name)'''

                if(("Team 2 dropoff" in str(data)) or ("Red Capture Point" in str(data))):
                    name = re.search(r': "([^<]+)', str(data)).group(1)
                    print(name)
                    playerStats[name][5] += 1
                    print(playerStats)

                if(("Red Flag" in str(data)) or ("Red_Flag" in str(data))):
                    if("Red Flag Plus" not in str(data)):
                        name = re.search(r': "([^<]+)', str(data)).group(1)
                        print(name)
                        playerStats[name][4] += 1
                        print(playerStats)
                
                if("suicide" in str(data)):
                    name = re.search(r': "([^<]+)', str(data)).group(1)
                    playerStats[name][2] += 1

                if("Blue Flag" in str(data)):
                    if("Blue Flag Plus" not in str(data)):   
                        name = re.search(r': "([^<]+)', str(data)).group(1)
                        print(name)
                        playerStats[name][4] += 1
                        print(playerStats)

                if("killed" in str(data)):
                    name = re.search(r': "([^<]+)', str(data)).group(1)
                    nme = re.search(r'd "([^<]+)', str(data)).group(1)
                    
                    if ((name in blueTeam) and (nme in blueTeam)):
                        playerStats[name][8] += 1
                    elif ((name in redTeam) and (nme in redTeam)):
                        playerStats[name][8] += 1
                    else:   
                        print(name + " killed " + nme)
                        if("sentrygun" in str(data)):
                            playerStats[name][6] += 1
                        elif("building_dispenser" in str(data)):
                            playerStats[name][7] += 1
                        else:
                            playerStats[name][0] += 1
                        playerStats[nme][1] += 1

                        print(playerStats)
                    if("grenade" in str(data)):
                        playerStats[name][9] += 1

                if("Sentry_Destroyed" in str(data)):
                    print("SG DESTOYRED)")
                    name = re.search(r': "([^<]+)', str(data)).group(1)
                    playerStats[name][3] += 1
                    print(playerStats)

                if ("changed name" in str(data)):
                    name = re.search(r': "([^<]+)', str(data)).group(1)
                    newname = re.search(r'o "([^"]+)', str(data)).group(1)
                    playerStats[newname] = playerStats[name]
                    del playerStats[name]
                    if(name in blueTeam):
                        blueTeam.remove(name)
                        blueTeam.append(newname)
                    if(name in redTeam):
                        redTeam.remove(name)
                        redTeam.append(newname)


                if ("Loading map" in str(data)):
                    print("resetting lists")
                    playerStats = {}
                    blueTeam = []
                    redTeam = []
                    matchStart = 0

                if ('Team "Blue" scored' in str(data)):
                    blueScore = re.search(r'scored "([^" with]+)', str(data)).group(1)
                    print(blueScore)
                if ('Team "Red" scored' in str(data)):
                    blueIndexStart = 3
                    redIndexStart = 3
                    pVar = srv.execute("pickupactive")
                    pVarSplit = pVar.split()
                    pickupActive = pVarSplit[2]
                    mapcomm = srv.execute("currentmap")
                    mapSplit = mapcomm.split()
                    mapname = mapSplit[2][1:-1]
                    redScore = re.search(r'scored "([^" with]+)', str(data)).group(1)
                    print(redScore)
                    
                    
                    bMsgList = ["**BLUE TEAM**",
                                "\n     PlayerName     │ Kills │ Deaths │ Suicides │ SGs Killed │ FTs │ FCs | SG Kills │  Disp Kills │ TKs |",
                                "\n====================╪=======╪========╪==========╪============╪=====╪=====╪==========╪=============╪=====╪"]
                    rMsgList = ["**RED TEAM**",
                                "\n     PlayerName     │ Kills │ Deaths │ Suicides │ SGs Killed │ FTs │ FCs | SG Kills │  Disp Kills │ TKs |",
                                "\n====================╪=======╪========╪==========╪============╪=====╪=====╪==========╪=============╪=====╪"]


                    for i in blueTeam:
                        if(len(i) >= 18):
                            string = "\n" + i[0:19] +  " |   " \
                            + str(playerStats[i][0]) + " " * (3 - len(str(playerStats[i][0]))) + " |   " \
                            + str(playerStats[i][1]) + " " * (4 - len(str(playerStats[i][1]))) + " |    "\
                            + str(playerStats[i][2]) + " " * (5 - len(str(playerStats[i][2]))) + " |     "\
                            + str(playerStats[i][3]) + " " * (6 - len(str(playerStats[i][3]))) + " |  "\
                            + str(playerStats[i][4]) + " " * (2 - len(str(playerStats[i][4]))) + " |  "\
                            + str(playerStats[i][5]) + " " * (2 - len(str(playerStats[i][5]))) + " |     "\
                            + str(playerStats[i][6]) + " " * (4 - len(str(playerStats[i][6]))) + " |      "\
                            + str(playerStats[i][7]) + " " * (6 - len(str(playerStats[i][7]))) + " |  "\
                            + str(playerStats[i][8]) + " " * (2 - len(str(playerStats[i][8]))) + " | "
                        else:
                            string = "\n" + i[0:19] + " " * (19 - len(i[0:19])) + " |   " \
                        + str(playerStats[i][0]) + " " * (3 - len(str(playerStats[i][0]))) + " |   " \
                        + str(playerStats[i][1]) + " " * (4 - len(str(playerStats[i][1]))) + " |    "\
                        + str(playerStats[i][2]) + " " * (5 - len(str(playerStats[i][2]))) + " |     "\
                        + str(playerStats[i][3]) + " " * (6 - len(str(playerStats[i][3]))) + " |  "\
                        + str(playerStats[i][4]) + " " * (2 - len(str(playerStats[i][4]))) + " |  "\
                        + str(playerStats[i][5]) + " " * (2 - len(str(playerStats[i][5]))) + " |     "\
                        + str(playerStats[i][6]) + " " * (4 - len(str(playerStats[i][6]))) + " |      "\
                        + str(playerStats[i][7]) + " " * (6 - len(str(playerStats[i][7]))) + " |  "\
                        + str(playerStats[i][8]) + " " * (2 - len(str(playerStats[i][8]))) + " |"
                        
                        bMsgList.insert(blueIndexStart, string)
                    bMsg = ''.join(bMsgList)
                    for i in redTeam:
                        if(len(i) >= 19):
                            string = "\n" + i[0:19] +  " |   " \
                            + str(playerStats[i][0]) + " " * (3 - len(str(playerStats[i][0]))) + " |   " \
                            + str(playerStats[i][1]) + " " * (4 - len(str(playerStats[i][1]))) + " |    "\
                            + str(playerStats[i][2]) + " " * (5 - len(str(playerStats[i][2]))) + " |     "\
                            + str(playerStats[i][3]) + " " * (6 - len(str(playerStats[i][3]))) + " |  "\
                            + str(playerStats[i][4]) + " " * (2 - len(str(playerStats[i][4]))) + " |  "\
                            + str(playerStats[i][5]) + " " * (2 - len(str(playerStats[i][5]))) + " |     "\
                            + str(playerStats[i][6]) + " " * (4 - len(str(playerStats[i][6]))) + " |      "\
                            + str(playerStats[i][7]) + " " * (6 - len(str(playerStats[i][7]))) + " |  "\
                            + str(playerStats[i][8]) + " " * (2 - len(str(playerStats[i][8]))) + " |  "
                        else:
                            string = "\n" + i[0:19] + " " * (19 - len(i[0:19])) + " |   " \
                        + str(playerStats[i][0]) + " " * (3 - len(str(playerStats[i][0]))) + " |   " \
                        + str(playerStats[i][1]) + " " * (4 - len(str(playerStats[i][1]))) + " |    "\
                        + str(playerStats[i][2]) + " " * (5 - len(str(playerStats[i][2]))) + " |     "\
                        + str(playerStats[i][3]) + " " * (6 - len(str(playerStats[i][3]))) + " |  "\
                        + str(playerStats[i][4]) + " " * (2 - len(str(playerStats[i][4]))) + " |  "\
                        + str(playerStats[i][5]) + " " * (2 - len(str(playerStats[i][5]))) + " |     "\
                        + str(playerStats[i][6]) + " " * (4 - len(str(playerStats[i][6]))) + " |      "\
                        + str(playerStats[i][7]) + " " * (6 - len(str(playerStats[i][7]))) + " |  "\
                        + str(playerStats[i][8]) + " " * (2 - len(str(playerStats[i][8]))) + " |"
                        
                        rMsgList.insert(redIndexStart, string)
                        redIndexStart += 1

                    rMsg = ''.join(rMsgList)
                    #print(pickupActive)
                    #KILLS SORTER
                    kills = {}
                    harmless = {}
                    grenWhore = {}
                    imposter = {}
                    deaths = {}
                    for i in list(playerStats):
                        kills[i] = playerStats[i][0]
                    killOrder = sorted(kills, key=kills.get, reverse=True)
                    killOrder = list(killOrder)
                    for i in list(playerStats):
                        harmless[i] = playerStats[i][0]
                    harmlessOrder = sorted(harmless, key=harmless.get, reverse=False)
                    harmlessOrder = list(harmlessOrder)
                    for i in list(playerStats):
                        grenWhore[i] = playerStats[i][9]
                    grenWhoreOrder = sorted(grenWhore, key=grenWhore.get, reverse=True)
                    grenWhoreOrder = list(grenWhoreOrder)
                    for i in list(playerStats):
                        deaths[i] = playerStats[i][1]
                    deathsOrder = sorted(deaths, key=deaths.get, reverse=True)
                    deathsOrder = list(deathsOrder)
                    for i in list(playerStats):
                        imposter[i] = playerStats[i][8]
                    imposterOrder = sorted(imposter, key=imposter.get, reverse=True)
                    imposterOrder = list(imposterOrder)
                    #if(pickupActive == '"1"'):
                    print(kills)
                    print(deaths)
                    print(imposterOrder)
                    print(harmlessOrder)
                    print(grenWhoreOrder)
                    await ctx.send("```Blue: " + blueScore + "   " + "Red: " + redScore + "\nMap: " + mapname + "```")
                    await ctx.send("```" + bMsg + "```")
                    await ctx.send("```" + rMsg + "```")
                    await ctx.send("```\nTerminator: " + killOrder[0] + " had the most kills with " + str(playerStats[killOrder[0]][0]) + " kills"
                                    + "\n\nMostly Harmless: " + harmlessOrder[0] + " had the least kills with " + str(playerStats[harmlessOrder[0]][0]) + " kills" 
                                    + "\n\nCrash Test Dummy: " + deathsOrder[0] + " had the most deaths with " + str(playerStats[deathsOrder[0]][1]) + " deaths"
                                    + "\n\nGrenade Whore: " + grenWhoreOrder[0] + " had " + str(playerStats[grenWhoreOrder[0]][9]) + " kills with grenades" 
                                    + "\n\nImposter: " + imposterOrder[0] + " had the most team kills with " + str(playerStats[imposterOrder[0]][0]) + " team kills```" )
                    print(len(bMsg))
                

        
        except:
            continue

        '''if("STEAM_" in str(dataSplit[5])):
            steamID = "STEAM_" + re.search('STEAM_(.+?)>', str(dataSplit[5])).group(1)
            name = re.search('"(.+?)<', str(dataSplit[5])).group(1)
            print (steamID)
            print(name)
            print(dataSplit)
            if("b'say'" in str(dataSplit[9])):
                sMessage = re.search('"(.+?)"', str(dataSplit[7])).group(1)
                print(name + " ( " + steamID + " ) said: " + sMessage)
                await message.channel.send(name + " ( " + steamID + " ) said: " + sMessage)
            if('say_team' in str(dataSplit) and len(str(dataSplit[6])) > 7):
                sMessage = re.search('"(.+?)"', str(dataSplit[7])).group(1)
                print(name + " ( " + steamID + " ) said to team: " + sMessage)
                await message.channel.send(name + " ( " + steamID + " ) said to team: " + sMessage)
            if (('Red' in str(dataSplit[7])) and ('Flag' in str(dataSplit))):
                print(name + " ( " + steamID + " ) has touched the Red Flag!")
                await message.channel.send(name + " ( " + steamID + " ) has touched the Red Flag!")
            if (('Blue' in str(dataSplit[7])) and ('Flag' in str(dataSplit))):
                print(name + " ( " + steamID + " ) has touched the Blue Flag!")
                await message.channel.send(name + " ( " + steamID + " ) has touched the Blue Flag!")
            if (('2' in str(dataSplit[8])) and ('dropoff' in str(dataSplit))):
                print(name + " ( " + steamID + " ) has captured the Blue Flag!")
                await message.channel.send(name + " ( " + steamID + " ) has captured the Blue Flag!")
            if (('1' in str(dataSplit[8])) and ('dropoff' in str(dataSplit))):
                print(name + " ( " + steamID + " ) has captured the Red Flag!")
                await message.channel.send(name + " ( " + steamID + " ) has captured the Red Flag!")'''

@client.command(pass_context=True)
async def test(ctx):
    blueIndexStart = 3
    redIndexStart = 3
    pVar = srv.execute("pickupactive")
    pVarSplit = pVar.split()
    pickupActive = pVarSplit[2]
    mapcomm = srv.execute("currentmap")
    mapSplit = mapcomm.split()
    mapname = mapSplit[2][1:-1]
    #redScore = re.search(r'scored "([^" with]+)', str(data)).group(1)
    print(redScore)
    playerStats = { "test1": [2, 6, 0, 0, 0, 0, 0, 0, 6, 0],
                    "test2": [66, 56, 0, 0, 0, 0, 0, 0, 0, 15],
                    "test3": [25, 9, 0, 0, 0, 0, 0, 0, 4, 0],
                    "test4": [12, 4, 0, 0, 0, 0, 0, 0, 0, 22],
                    "test5": [3, 27, 0, 0, 0, 0, 0, 0, 9, 0],
                    "test6": [89, 2, 0, 0, 0, 0, 0, 0, 0, 0],
                    "test7": [12, 90, 0, 0, 0, 0, 0, 0, 12, 0],
                    "test8": [1, 12, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    blueTeam = ["test1", "test2", "test3", "test4"]
    redTeam = ["test5", "test6", "test7", "test8"]
    
    bMsgList = ["**BLUE TEAM**",
                "\n     PlayerName     │ Kills │ Deaths │ Suicides │ SGs Killed │ FTs │ FCs | SG Kills │  Disp Kills │ TKs |",
                "\n====================╪=======╪========╪==========╪============╪=====╪=====╪==========╪=============╪=====╪"]
    rMsgList = ["**RED TEAM**",
                "\n     PlayerName     │ Kills │ Deaths │ Suicides │ SGs Killed │ FTs │ FCs | SG Kills │  Disp Kills │ TKs |",
                "\n====================╪=======╪========╪==========╪============╪=====╪=====╪==========╪=============╪=====╪"]


    for i in blueTeam:
        if(len(i) >= 18):
            string = "\n" + i[0:19] +  " |   " \
            + str(playerStats[i][0]) + " " * (3 - len(str(playerStats[i][0]))) + " |   " \
            + str(playerStats[i][1]) + " " * (4 - len(str(playerStats[i][1]))) + " |    "\
            + str(playerStats[i][2]) + " " * (5 - len(str(playerStats[i][2]))) + " |     "\
            + str(playerStats[i][3]) + " " * (6 - len(str(playerStats[i][3]))) + " |  "\
            + str(playerStats[i][4]) + " " * (2 - len(str(playerStats[i][4]))) + " |  "\
            + str(playerStats[i][5]) + " " * (2 - len(str(playerStats[i][5]))) + " |     "\
            + str(playerStats[i][6]) + " " * (4 - len(str(playerStats[i][6]))) + " |      "\
            + str(playerStats[i][7]) + " " * (6 - len(str(playerStats[i][7]))) + " |  "\
            + str(playerStats[i][8]) + " " * (2 - len(str(playerStats[i][8]))) + " | "
        else:
            string = "\n" + i[0:19] + " " * (19 - len(i[0:19])) + " |   " \
        + str(playerStats[i][0]) + " " * (3 - len(str(playerStats[i][0]))) + " |   " \
        + str(playerStats[i][1]) + " " * (4 - len(str(playerStats[i][1]))) + " |    "\
        + str(playerStats[i][2]) + " " * (5 - len(str(playerStats[i][2]))) + " |     "\
        + str(playerStats[i][3]) + " " * (6 - len(str(playerStats[i][3]))) + " |  "\
        + str(playerStats[i][4]) + " " * (2 - len(str(playerStats[i][4]))) + " |  "\
        + str(playerStats[i][5]) + " " * (2 - len(str(playerStats[i][5]))) + " |     "\
        + str(playerStats[i][6]) + " " * (4 - len(str(playerStats[i][6]))) + " |      "\
        + str(playerStats[i][7]) + " " * (6 - len(str(playerStats[i][7]))) + " |  "\
        + str(playerStats[i][8]) + " " * (2 - len(str(playerStats[i][8]))) + " |"
        
        bMsgList.insert(blueIndexStart, string)
    bMsg = ''.join(bMsgList)
    for i in redTeam:
        if(len(i) >= 19):
            string = "\n" + i[0:19] +  " |   " \
            + str(playerStats[i][0]) + " " * (3 - len(str(playerStats[i][0]))) + " |   " \
            + str(playerStats[i][1]) + " " * (4 - len(str(playerStats[i][1]))) + " |    "\
            + str(playerStats[i][2]) + " " * (5 - len(str(playerStats[i][2]))) + " |     "\
            + str(playerStats[i][3]) + " " * (6 - len(str(playerStats[i][3]))) + " |  "\
            + str(playerStats[i][4]) + " " * (2 - len(str(playerStats[i][4]))) + " |  "\
            + str(playerStats[i][5]) + " " * (2 - len(str(playerStats[i][5]))) + " |     "\
            + str(playerStats[i][6]) + " " * (4 - len(str(playerStats[i][6]))) + " |      "\
            + str(playerStats[i][7]) + " " * (6 - len(str(playerStats[i][7]))) + " |  "\
            + str(playerStats[i][8]) + " " * (2 - len(str(playerStats[i][8]))) + " |  "
        else:
            string = "\n" + i[0:19] + " " * (19 - len(i[0:19])) + " |   " \
        + str(playerStats[i][0]) + " " * (3 - len(str(playerStats[i][0]))) + " |   " \
        + str(playerStats[i][1]) + " " * (4 - len(str(playerStats[i][1]))) + " |    "\
        + str(playerStats[i][2]) + " " * (5 - len(str(playerStats[i][2]))) + " |     "\
        + str(playerStats[i][3]) + " " * (6 - len(str(playerStats[i][3]))) + " |  "\
        + str(playerStats[i][4]) + " " * (2 - len(str(playerStats[i][4]))) + " |  "\
        + str(playerStats[i][5]) + " " * (2 - len(str(playerStats[i][5]))) + " |     "\
        + str(playerStats[i][6]) + " " * (4 - len(str(playerStats[i][6]))) + " |      "\
        + str(playerStats[i][7]) + " " * (6 - len(str(playerStats[i][7]))) + " |  "\
        + str(playerStats[i][8]) + " " * (2 - len(str(playerStats[i][8]))) + " |"
        
        rMsgList.insert(redIndexStart, string)
        redIndexStart += 1

    rMsg = ''.join(rMsgList)
    #print(pickupActive)
    #if(pickupActive == '"1"'):
    kills = {}
    harmless = {}
    grenWhore = {}
    imposter = {}
    deaths = {}
    for i in list(playerStats):
        kills[i] = playerStats[i][0]
    killOrder = sorted(kills, key=kills.get, reverse=True)
    killOrder = list(killOrder)
    for i in list(playerStats):
        harmless[i] = playerStats[i][0]
    harmlessOrder = sorted(harmless, key=harmless.get, reverse=False)
    harmlessOrder = list(harmlessOrder)
    for i in list(playerStats):
        grenWhore[i] = playerStats[i][9]
    grenWhoreOrder = sorted(grenWhore, key=grenWhore.get, reverse=True)
    grenWhoreOrder = list(grenWhoreOrder)
    for i in list(playerStats):
        deaths[i] = playerStats[i][1]
    deathsOrder = sorted(deaths, key=deaths.get, reverse=True)
    deathsOrder = list(deathsOrder)
    for i in list(playerStats):
        imposter[i] = playerStats[i][8]
    imposterOrder = sorted(imposter, key=imposter.get, reverse=True)
    imposterOrder = list(imposterOrder)
    #if(pickupActive == '"1"'):
    print(kills)
    print(deaths)
    print(imposterOrder)
    print(harmlessOrder)
    print(grenWhoreOrder)
    await ctx.send("```Blue: " + blueScore + "   " + "Red: " + redScore + "\nMap: " + mapname + "```")
    await ctx.send("```" + bMsg + "```")
    await ctx.send("```" + rMsg + "```")
    await ctx.send("```\nTerminator: " + killOrder[0] + " had the most kills with " + str(playerStats[killOrder[0]][0]) + " kills"
                    + "\n\nMostly Harmless: " + harmlessOrder[0] + " had the least kills with " + str(playerStats[harmlessOrder[0]][0]) + " kills" 
                    + "\n\nCrash Test Dummy: " + deathsOrder[0] + " had the most deaths with " + str(playerStats[deathsOrder[0]][1]) + " deaths"
                    + "\n\nGrenade Whore: " + grenWhoreOrder[0] + " had " + str(playerStats[grenWhoreOrder[0]][9]) + " kills with grenades" 
                    + "\n\nImposter: " + imposterOrder[0] + " had the most team kills with " + str(playerStats[imposterOrder[0]][0]) + " team kills```" )
client.run('NzU3MDgzNTkyNzM1MDY0MTY2.X2bPCg.QOndInrTzUQQMwNJF1BpSsnUarI')


#L 07/18/2020 - 16:37:17: "Woozle Wozzle?<3><STEAM_0:1:31257069><Red>" killed "CoachSouz<1><STEAM_0:1:2278493><Blue>" with "supershotgun"