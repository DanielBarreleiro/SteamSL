import discord
from discord.ext import tasks, commands
from secrets import *
import requests
import asyncio
from datetime import datetime
from datetime import timedelta
import pycountry as pc
import pycountry_convert as pcc

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(type=discord.ActivityType.watching, name="Low Levels"))

@client.event
async def on_message(message):
    channel = message.channel

    if message.author == client.user:
        return
    
    if message.content.startswith('.status'):

        status_url = '{}/ICSGOServers_730/GetGameServersStatus/v1/?key={}'.format(SW, SWK)
        try:
            status_response = requests.get(status_url)
        except Exception:
            await channel.send('Can\'t connect to Steam')
        
        def getSteamStatus(status_data):
            session_logon = status_data['result']['services']['SessionsLogon']
            community = status_data['result']['services']['SteamCommunity']
            match_scheduler = status_data['result']['matchmaking']['scheduler']
            store_latency = status_data['result']['perfectworld']['purchase']['latency']
            store_availability = status_data['result']['perfectworld']['purchase']['availability']

            if (store_latency == 'normal'):
                store_status = 'Normal ✅'
            elif (store_latency != 'normal'):
                store_status =  '{} ❌ | {}'.format(store_latency, store_availability)
                store_status = store_status.title()
            if (store_latency != 'normal' or session_logon != 'normal'):
                sidecolor = 0xff0000
            else:
                sidecolor = 0x000000
            
            embed = discord.Embed(title="Steam Status", color=sidecolor)
            embed.add_field(name="Steam Store", value=f"{store_status}", inline=True)
            embed.add_field(name="Session Logon", value=f"{session_logon.capitalize()}", inline=True)
            embed.add_field(name="Player Inventories", value=f"{community.capitalize()}", inline=True)
            embed.add_field(name="CS:GO Match Making Scheduler", value=f"{match_scheduler.capitalize()}", inline=False)
            embed.set_footer(text="Any problem, contact @UGH Dany")
            return embed
        
        statusMsg = status_response.reason
        statusCode = status_response.status_code
        
        if statusCode == 200:
            status_data = status_response.json()
            embed = getSteamStatus(status_data)
            await channel.send(embed=embed)
        else:
            await channel.send(f'Error: {statusMsg} | {statusCode}')
    
    # GET STEAM ID
    def getSteamID():
        # Resolve Vanity URL
        rvurl = '{}/ISteamUser/ResolveVanityURL/v1/?key={}&vanityurl={}'.format(SW, SWK, custom_url)
        rvurl_response = requests.get(rvurl)
        rvurl_data = rvurl_response.json()
        rv_success = rvurl_data['response']['success']
        steamid = rvurl_data['response']['steamid']
        return rv_success, steamid

    # Steam Ladder API - GET DATA
    def getSteamLadder():
        ladder_url = '{}/profile/{}/'.format(SL, steamid)
        ladder_response = requests.get(ladder_url, headers={
            'Authorization': 'Token {}'.format(SLK)
        })
        statusMsg = ladder_response.reason
        statusCode = ladder_response.status_code
        ladder_data = ladder_response.json()

        return statusCode, statusMsg, ladder_data, ladder_url

    # Steam Ladder API - UPDATE PROFILE DATA
    def updateSteamLadder(ladder_url):
        ladder_update_response = requests.post(ladder_url, headers={
            'Authorization': 'Token {}'.format(SLK)
        })
        statusMsg = ladder_update_response.reason
        statusCode = ladder_update_response.status_code
        if ladder_update_response.status_code == 200:
            update = 'Data Updated!'
        else:
            update = 'Can\'t Update Data Yet!'
        return statusCode, statusMsg, update

    # GET PLAYER BANS
    def getPlayerBans():
        bans_url = '{}/ISteamUser/GetPlayerBans/v1/?key={}&steamids={}'.format(SW, SWK, steamid)
        bans_response = requests.get(bans_url)
        statusMsg = bans_response.reason
        statusCode = bans_response.status_code
        bans_data = bans_response.json()

        vac_ban = str(bans_data['players'][0]['VACBanned'])
        trade_ban = str(bans_data['players'][0]['EconomyBan'])
        community_ban = str(bans_data['players'][0]['CommunityBanned'])

        if vac_ban == 'false' or vac_ban == 'False':
            vac_ban = 'None 🟢'
        if vac_ban == 'true' or vac_ban == 'True':
            vac_ban = 'Banned 🔴'

        if trade_ban == 'none' or trade_ban == 'None':
            trade_ban = 'None 🟢'
        else:
            trade_ban = 'Banned 🔴'

        if community_ban == 'false' or community_ban == 'False':
            community_ban = 'None 🟢'
        if community_ban == 'true' or community_ban == 'True':
            community_ban = 'Banned 🔴'
            
        return vac_ban, trade_ban, community_ban

    # GET PLAYER SUMMARIES
    def getPlayerSummaries():
        # GET PLAYER SUMMARIES
        profile_url = '{}/ISteamUser/GetPlayerSummaries/v2/?key={}&steamids={}'.format(SW, SWK, steamid)
        profile_response = requests.get(profile_url)
        statusMsg = profile_response.reason
        statusCode = profile_response.status_code
        profile_data = profile_response.json()
                
        name = profile_data['response']['players'][0]['personaname']
        avatar = profile_data['response']['players'][0]['avatarfull']
        country_code = profile_data['response']['players'][0]['loccountrycode']

        country = pc.countries.get(alpha_2=f'{country_code}')
        country = country.name
        region = pcc.country_alpha2_to_continent_code(country_code)
        region = pcc.convert_continent_code_to_continent_name(region)

        return name, avatar, country, region

    # SHOW PROFILE DATA EMBED
    def ShowProfile():
        embed1 = discord.Embed(title=f"{name}", url=f"https://steamcommunity.com/profiles/{steamid}", description=f"{country}, {region}", color=0x000000)
        embed1.set_author(name=name, url=f"https://steamcommunity.com/profiles/{steamid}", icon_url=avatar)
        embed1.set_thumbnail(url=avatar)

        embed1.add_field(name="Steam ID", value=f"{steamid}", inline=False)

        embed1.add_field(name="Steam Years", value=f"{joined_years}", inline=True)
        embed1.add_field(name="Level", value=f"{level}", inline=True)
        embed1.add_field(name="Badges", value=f"{badges}", inline=True)
        embed1.add_field(name="Games", value=f"{games}", inline=True)
        embed1.add_field(name="Playtime", value=f"{playtime}", inline=True)
        embed1.add_field(name="Friends", value=f"{friends}", inline=True)
        embed1.add_field(name="Most Played Game", value=f"{max_game} - {max_playtime}h", inline=False)
        embed1.set_footer(text="By: UGH Dany")
        return embed1

    # SHOW RANKS EMBED
    def ShowRanks():
        embed2 = discord.Embed(title=f"Steam Ladder Rank", url=steamladder_url, description=f"{country}, {region}", color=0x000000)
        embed2.set_author(name=f"{name} | SteamLadder Stats", url=f"https://steamcommunity.com/profiles/{steamid}", icon_url=avatar)

        embed2.add_field(name="W | R | C", value="World | Region | Country", inline=False)

        embed2.add_field(name="Level W", value=f"#{world_xp_rank}", inline=True)
        embed2.add_field(name="Playtime W", value=f"#{world_playtime_rank}", inline=True)
        embed2.add_field(name="Games W", value=f"#{world_games_rank}", inline=True)

        embed2.add_field(name="Level R", value=f"#{region_xp_rank}", inline=True)
        embed2.add_field(name="Playtime R", value=f"#{region_playtime_rank}", inline=True)
        embed2.add_field(name="Games R", value=f"#{region_games_rank}", inline=True)

        embed2.add_field(name="Level C", value=f"#{country_xp_rank}", inline=True)
        embed2.add_field(name="Playtime C", value=f"#{country_playtime_rank}", inline=True)
        embed2.add_field(name="Games C", value=f"#{country_games_rank}", inline=True)
                
        embed2.set_footer(text="By: UGH Dany")
        return embed2

    # SHOW BANS EMBED
    def ShowBans():
        embed3 = discord.Embed(title=f"{name}", url=f"https://steamcommunity.com/profiles/{steamid}", description=f"{country}, {region}", color=0x000000)
        embed3.set_author(name=f"{name} | Bans", url=f"https://steamcommunity.com/profiles/{steamid}", icon_url=avatar)
        embed3.set_thumbnail(url=avatar)

        embed3.add_field(name="VAC Ban", value=f"{vac_ban}", inline=True)
        embed3.add_field(name="Trade Ban", value=f"{trade_ban}", inline=True)
        embed3.add_field(name="Community Ban", value=f"{community_ban}", inline=True)
                    
        embed3.set_footer(text="By: UGH Dany")
        return embed3

    # SHOW ALL DATA
    if message.content.startswith('.steam'):
        custom_url = message.content.replace('.steam ', '')

        try:
            rv_success, steamid = getSteamID()
        except Exception:
            await channel.send('Can\'t connect to Steam')

        if (rv_success == 1):
            msg = await channel.send('Please wait a few seconds..')

            try:
                name, avatar, country, region = getPlayerSummaries()
            except Exception:
                await msg.edit(content = f'Error while trying to get Player Summaries \n||Error Message: {statusMsg} | {statusCode}||')
            
            try:
                vac_ban, trade_ban, community_ban = getPlayerBans()
            except Exception:
                await msg.edit(content = f'Error while trying to get Player Bans \n||Error Message: {statusMsg} | {statusCode}||')
            
            try:
                # Steam Ladder API - GET DATA
                ladder_url = '{}/profile/{}/'.format(SL, steamid)
                ladder_response = requests.get(ladder_url, headers={
                    'Authorization': 'Token {}'.format(SLK)
                })
                statusMsg = ladder_response.reason
                statusCode = ladder_response.status_code
                ladder_data = ladder_response.json()
            except Exception:
                await msg.edit(content = f'Error while trying to get Steam Ladder Player Data \n||Error Message: {statusMsg} | {statusCode}||')

            try:
                # Steam Ladder API - UPDATE PROFILE DATA
                ladder_update_response = requests.post(ladder_url, headers={'Authorization': 'Token {}'.format(SLK)})
                statusMsg = ladder_update_response.reason
                statusCode = ladder_update_response.status_code
                #ladder_update_data = ladder_update_response.json()
                if ladder_update_response.status_code == 200:
                    update = 'Data Updated!'
                else:
                    update = 'Can\'t Update Data Yet!'
            except Exception:
                await msg.edit(content = f'Error while trying to Update Steam Ladder Player Data \n||Error Message: {statusMsg} | {statusCode}||')
                
            if ladder_response.status_code == 200:
                steam_join = ladder_data['steam_user']['steam_join_date']
                steamladder_url = ladder_data['steam_user']['steamladder_url']
                last_update = ladder_data['steam_stats']['last_update']
                level = ladder_data['steam_stats']['level']
                xp = ladder_data['steam_stats']['xp']
                friends = ladder_data['steam_stats']['friends']
                badges = ladder_data['steam_stats']['badges']['total']
                games = ladder_data['steam_stats']['games']['total_games']
                playtime = ladder_data['steam_stats']['games']['total_playtime_min']
                max_game = ladder_data['steam_stats']['games']['most_played'][0]['name']
                max_playtime = ladder_data['steam_stats']['games']['most_played'][0]['playtime_min']

                # XP
                world_xp_rank = ladder_data['ladder_rank']['worldwide_xp']
                region_xp_rank = ladder_data['ladder_rank']['region']['region_xp']
                country_xp_rank = ladder_data['ladder_rank']['country']['country_xp']
                # PLAYTIME
                world_playtime_rank = ladder_data['ladder_rank']['worldwide_playtime']
                region_playtime_rank = ladder_data['ladder_rank']['region']['region_playtime']
                country_playtime_rank = ladder_data['ladder_rank']['country']['country_playtime']
                # GAMES
                world_games_rank = ladder_data['ladder_rank']['worldwide_games']
                region_games_rank = ladder_data['ladder_rank']['region']['region_games']
                country_games_rank = ladder_data['ladder_rank']['country']['country_games']

                # NEEDED
                last_update = datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S.%f')
                last_update = last_update.strftime('%d/%m/%Y - %H:%M')
                current_time = datetime.now().strftime('%Y-%m-%d')
                current_time = datetime.strptime(current_time, '%Y-%m-%d')
                steam_join = datetime.strptime(steam_join, '%Y-%m-%dT%H:%M:%S')
                joined_days = abs(current_time - steam_join).days
                joined_years = round(joined_days/366)

                playtime = round(playtime / 60)
                max_playtime = round(max_playtime / 60)
                
                await msg.edit(content = f'```{update}\nLast Data Update: {last_update}```')

                embed1 = ShowProfile()
                msg = await message.channel.send(embed=embed1)

                await msg.add_reaction('▶')
                user =  None
                reaction = None
                def check(reaction, user):
                    return user == message.author and str(reaction.emoji) == '▶'
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
                except asyncio.TimeoutError:
                    print()
                else:
                    embed2 = ShowRanks()
                    await msg.edit(embed=embed2)
                    await reaction.remove(user)
                    await reaction.remove(client.user)
                    await msg.add_reaction('▶')
                    user =  None
                    reaction = None
                    def check(reaction, user):
                        return user == message.author and str(reaction.emoji) == '▶'
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
                    except asyncio.TimeoutError:
                        print()
                    else:
                        embed3 = ShowBans()
                        await msg.edit(embed=embed3)
                    await reaction.remove(user)
                    await reaction.remove(client.user)
            else:
                statusMsg = ladder_response.reason
                statusCode = ladder_response.status_code
                await msg.edit(content = f'Error while trying to get Steam Ladder Player Data \n||Error Message: {statusMsg} | {statusCode}||')

        elif (rv_success == 42):
                await channel.send(f'No profile with Custom URL {custom_url} found')
        else:
            print("An error ocurred")

    # SHOW PROFILE DATA
    if message.content.startswith('.profile'):
        custom_url = message.content.replace('.profile ', '')

        try:
            rv_success, steamid = getSteamID()
        except Exception:
            await channel.send('Can\'t connect to Steam')

        if (rv_success == 1):
            msg = await channel.send('Please wait a few seconds..')

            try:
                name, avatar, country, region = getPlayerSummaries()
            except Exception:
                await msg.edit(content = f'Error while trying to get Player Summaries \n||Error Message: {statusMsg} | {statusCode}||')

            try:
                statusCode_get, statusMsg, ladder_data, ladder_url = getSteamLadder()
            except Exception:
                await msg.edit(content = f'Error while trying to Get Steam Ladder Player Data \n||Error Message: {statusCode} | {statusMsg}||')

            try:
                statusCode, statusMsg, update = updateSteamLadder(ladder_url)
            except Exception:
                await msg.edit(content = f'Error while trying to Update Steam Ladder Player Data \n||Error Message: {statusCode} | {statusMsg}||')

            if statusCode_get == 200:
                steam_join = ladder_data['steam_user']['steam_join_date']
                steamladder_url = ladder_data['steam_user']['steamladder_url']
                last_update = ladder_data['steam_stats']['last_update']
                level = ladder_data['steam_stats']['level']
                xp = ladder_data['steam_stats']['xp']
                friends = ladder_data['steam_stats']['friends']
                badges = ladder_data['steam_stats']['badges']['total']
                games = ladder_data['steam_stats']['games']['total_games']
                playtime = ladder_data['steam_stats']['games']['total_playtime_min']
                max_game = ladder_data['steam_stats']['games']['most_played'][0]['name']
                max_playtime = ladder_data['steam_stats']['games']['most_played'][0]['playtime_min']

                last_update = datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S.%f')
                last_update = last_update.strftime('%d/%m/%Y - %H:%M')
                current_time = datetime.now().strftime('%Y-%m-%d')
                current_time = datetime.strptime(current_time, '%Y-%m-%d')
                steam_join = datetime.strptime(steam_join, '%Y-%m-%dT%H:%M:%S')
                joined_days = abs(current_time - steam_join).days
                joined_years = round(joined_days/366)

                playtime = round(playtime / 60)
                max_playtime = round(max_playtime / 60)
                
                await msg.edit(content = f'```{update}\nLast Data Update: {last_update}```')
                embed1 = ShowProfile()
                await message.channel.send(embed=embed1)

    # SHOW STEAM LADDER RANK
    if message.content.startswith('.ranks'):
        custom_url = message.content.replace('.ranks ', '')

        try:
            rv_success, steamid = getSteamID()
        except Exception:
            await channel.send('Can\'t connect to Steam')

        if (rv_success == 1):
            msg = await channel.send('Please wait a few seconds..')

            try:
                name, avatar, country, region = getPlayerSummaries()
            except Exception:
                await msg.edit(content = f'Error while trying to get Player Summaries \n||Error Message: {statusMsg} | {statusCode}||')

            try:
                statusCode_get, statusMsg, ladder_data, ladder_url = getSteamLadder()
            except Exception:
                await msg.edit(content = f'Error while trying to Get Steam Ladder Player Data \n||Error Message: {statusCode} | {statusMsg}||')

            try:
                statusCode, statusMsg, update = updateSteamLadder(ladder_url)
            except Exception:
                await msg.edit(content = f'Error while trying to Update Steam Ladder Player Data \n||Error Message: {statusCode} | {statusMsg}||')
            
            if statusCode_get == 200:
                steamladder_url = ladder_data['steam_user']['steamladder_url']
                last_update = ladder_data['steam_stats']['last_update']
                last_update = datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S.%f')
                last_update = last_update.strftime('%d/%m/%Y - %H:%M')

                 # XP
                world_xp_rank = ladder_data['ladder_rank']['worldwide_xp']
                region_xp_rank = ladder_data['ladder_rank']['region']['region_xp']
                country_xp_rank = ladder_data['ladder_rank']['country']['country_xp']
                # PLAYTIME
                world_playtime_rank = ladder_data['ladder_rank']['worldwide_playtime']
                region_playtime_rank = ladder_data['ladder_rank']['region']['region_playtime']
                country_playtime_rank = ladder_data['ladder_rank']['country']['country_playtime']
                # GAMES
                world_games_rank = ladder_data['ladder_rank']['worldwide_games']
                region_games_rank = ladder_data['ladder_rank']['region']['region_games']
                country_games_rank = ladder_data['ladder_rank']['country']['country_games']

                await msg.edit(content = f'```{update}\nLast Data Update: {last_update}```')
                embed2 = ShowRanks()
                await channel.send(embed=embed2)

    # SHOW STEAM BANS
    if message.content.startswith('.bans'):
        custom_url = message.content.replace('.bans ', '')

        try:
            rv_success, steamid = getSteamID()
        except Exception:
            await channel.send('Can\'t connect to Steam')

        if (rv_success == 1):
            msg = await channel.send('Please wait a few seconds..')

            try:
                name, avatar, country, region = getPlayerSummaries()
            except Exception:
                await msg.edit(content = f'Error while trying to get Player Summaries \n||Error Message: {statusMsg} | {statusCode}||')
            
            try:
                vac_ban, trade_ban, community_ban = getPlayerBans()
            except Exception:
                await msg.edit(content = f'Error while trying to get Player Bans \n||Error Message: {statusMsg} | {statusCode}||')
            
            embed3 = ShowBans()
            await channel.send(embed=embed3)

client.run(token)