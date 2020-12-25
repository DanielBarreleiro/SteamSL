from secrets import *
import requests

# Steam Ladder Base URL
SL = 'https://steamladder.com/api/v1'

# Steam WEB API Base URL
SW = 'https://api.steampowered.com'


def getSteamID():
    print('Input Steam Custom URL')
    steamid = input()
    # Resolve Vanity URL
    rvurl = '{}/ISteamUser/ResolveVanityURL/v1/?key={}&vanityurl={}'.format(SW, SWK, steamid)
    rvurl_response = requests.get(rvurl)
    rvurl_data = rvurl_response.json()
    steamid = rvurl_data['response']['steamid']
    return steamid

def getSteamStatus():
    status_url = '{}/ICSGOServers_730/GetGameServersStatus/v1/?key={}'.format(SW, SWK)
    status_response = requests.get(status_url)
    status_data = status_response.json()

    session_logon = status_data['result']['services']['SessionsLogon']
    player_inv = status_data['result']['services']['SteamCommunity']
    match_scheduler = status_data['result']['matchmaking']['scheduler']
    steam_store = status_data['result']['perfectworld']['purchase']['latency']
    steam_store_b = status_data['result']['perfectworld']['purchase']['availability']
    if (steam_store != 'normal'):
        steam_store =  '{} | {}'.format(steam_store, steam_store_b)

    print('Steam Store:', steam_store)
    print('Sessions Logon:', session_logon)
    print('Player Inventories:', player_inv)
    print('CS:GO Match Making Scheduler:', match_scheduler)

def getSteamProfileData():
    steamid = getSteamID()
    # URL0 - GET PLAYER SUMMARIES
    url0 = '{}/ISteamUser/GetPlayerSummaries/v2/?key={}&steamids={}'.format(SW, SWK, steamid)
    url0_response = requests.get(url0)
    data0 = url0_response.json()

    # URL1 - GET PLAYER BANS
    url1 = '{}/ISteamUser/GetPlayerBans/v1/?key={}&steamids={}'.format(SW, SWK, steamid)
    url1_response = requests.get(url1)
    data1 = url1_response.json()

    name = data0['response']['players'][0]['personaname']
    avatar = data0['response']['players'][0]['avatarfull']
    country = data0['response']['players'][0]['loccountrycode']

    vac_ban = str(data1['players'][0]['VACBanned'])
    trade_ban = str(data1['players'][0]['EconomyBan'])
    community_ban = str(data1['players'][0]['CommunityBanned'])

    if vac_ban == 'false' or vac_ban == 'False':
        vac_ban = 'None'
    if vac_ban == 'true' or vac_ban == 'True':
      vac_ban = 'Banned'

    if trade_ban == 'none' or trade_ban == 'None':
      trade_ban = 'None'
    if trade_ban == 'banned' or trade_ban == 'Banned':
      trade_ban = 'Banned'

    if community_ban == 'false' or community_ban == 'False':
      community_ban = 'None'
    if community_ban == 'true' or community_ban == 'True':
        community_ban = 'Banned'

    print('Name:', name)
    print('Avatar:', avatar)
    print('Country', country)
    print('VAC Ban:', vac_ban)
    print('Trade Ban:', trade_ban)
    print('Community Ban:', community_ban)

getSteamProfileData()