from secrets import *
import requests

# Steam Ladder Base URL
SL = 'https://steamladder.com/api/v1'

# Steam WEB API Base URL
SW = 'https://api.steampowered.com'

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

    print('Steam Store:', steam_store.capitalize())
    print('Sessions Logon:', session_logon.capitalize())
    print('Player Inventories:', player_inv.capitalize())
    print('CS:GO Match Making Scheduler:', match_scheduler.capitalize())

def getSteamID():
    print('Input Steam Custom URL')
    steamid = input()
    # Resolve Vanity URL
    rvurl = '{}/ISteamUser/ResolveVanityURL/v1/?key={}&vanityurl={}'.format(SW, SWK, steamid)
    rvurl_response = requests.get(rvurl)
    rvurl_data = rvurl_response.json()
    steamid = rvurl_data['response']['steamid']

    getSteamProfileData(steamid)

def getSteamProfileData(steamid):
    # GET PLAYER SUMMARIES
    profile_url = '{}/ISteamUser/GetPlayerSummaries/v2/?key={}&steamids={}'.format(SW, SWK, steamid)
    profile_response = requests.get(profile_url)
    profile_data = profile_response.json()
    
    name = profile_data['response']['players'][0]['personaname']
    avatar = profile_data['response']['players'][0]['avatarfull']
    country = profile_data['response']['players'][0]['loccountrycode']

    print('Name:', name, '\nAvatar:', avatar, '\nCountry:', country,'\n')
    getOwnedGames(steamid)

def getPlayerBans(steamid):
    # GET PLAYER BANS
    bans_url = '{}/ISteamUser/GetPlayerBans/v1/?key={}&steamids={}'.format(SW, SWK, steamid)
    bans_response = requests.get(bans_url)
    bans_data = bans_response.json()

    vac_ban = str(bans_data['players'][0]['VACBanned'])
    trade_ban = str(bans_data['players'][0]['EconomyBan'])
    community_ban = str(bans_data['players'][0]['CommunityBanned'])

    if vac_ban == 'false' or vac_ban == 'False':
        vac_ban = 'None'
    if vac_ban == 'true' or vac_ban == 'True':
      vac_ban = 'Banned'

    trade_ban = trade_ban.capitalize()

    if community_ban == 'false' or community_ban == 'False':
      community_ban = 'None'
    if community_ban == 'true' or community_ban == 'True':
        community_ban = 'Banned'

    print('--- BANS ---')
    print('VAC Ban:', vac_ban, '\nTrade Ban:', trade_ban, '\nCommunity Ban:', community_ban, '\n')

def getOwnedGames(steamid):
    # URL2 - GET PLAYER OWNED GAMES
    ownedgames_url = '{}/IPlayerService/GetOwnedGames/v1/?key={}&steamid={}&include_played_free_games=1'.format(SW, SWK, steamid)
    ownedgames_response = requests.get(ownedgames_url)
    owned_games = ownedgames_response.json()

    total_games = owned_games['response']['game_count']

    print('Total Games:', total_games, '\n')
    getPlayerBans(steamid)

def Menu():
  print('What do you want to do? \n 1 - Steam Status \n 2 - Player Data')
  option = input()
  if option == '1':
    getSteamStatus()
  if option == '2':
    getSteamID()

Menu()
