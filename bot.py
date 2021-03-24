import discord
from discord.ext import tasks, commands
from secrets import *
import requests
import asyncio
from datetime import datetime
from datetime import timedelta
import pycountry as pc
import pycountry_convert as pcc

# Steam Ladder Base URL
SL = 'https://steamladder.com/api/v1'

# Steam WEB API Base URL
SW = 'https://api.steampowered.com'


client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(type=discord.ActivityType.watching, name="Low Levels"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('.status'):
        channel = message.channel

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
        if (steam_store != 'normal' or session_logon != 'normal'):
            sidecolor = 0xff0000
        else:
            sidecolor = 0x000000

        embed = discord.Embed(title="Steam Status", color=sidecolor)
        embed.add_field(name="Steam Store", value=f"{steam_store.capitalize()}", inline=True)
        embed.add_field(name="Session Logon", value=f"{session_logon.capitalize()}", inline=True)
        embed.add_field(name="Player Inventories", value=f"{player_inv.capitalize()}", inline=True)
        embed.add_field(name="CS:GO Match Making Scheduler", value=f"{match_scheduler.capitalize()}", inline=False)
        embed.set_footer(text="By: UGH Dany")
        await message.channel.send(embed=embed)

    if message.content.startswith('.steam'):
        steamid = message.content.replace('.steam ', '')
        channel = message.channel

        #STEAM WEB API
        # Resolve Vanity URL
        rvurl = '{}/ISteamUser/ResolveVanityURL/v1/?key={}&vanityurl={}'.format(SW, SWK, steamid)
        rvurl_response = requests.get(rvurl)
        rvurl_data = rvurl_response.json()

        if rvurl_data['response']['success'] == 1:
            steamid = rvurl_data['response']['steamid']

            # GET PLAYER SUMMARIES
            profile_url = '{}/ISteamUser/GetPlayerSummaries/v2/?key={}&steamids={}'.format(SW, SWK, steamid)
            profile_response = requests.get(profile_url)
            profile_data = profile_response.json()
            
            name = profile_data['response']['players'][0]['personaname']
            avatar = profile_data['response']['players'][0]['avatarfull']
            country_code = profile_data['response']['players'][0]['loccountrycode']

            country = pc.countries.get(alpha_2=f'{country_code}')
            country = country.name
            region = pcc.country_alpha2_to_continent_code(country_code)
            region = pcc.convert_continent_code_to_continent_name(region)

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

            # Steam Ladder API - GET
            ladder_url = '{}/profile/{}/'.format(SL, steamid)
            ladder_response = requests.get(ladder_url, headers={
                'Authorization': 'Token {}'.format(SLK)
            })
            ladder_data = ladder_response.json()

            # Steam Ladder API - POST
            ladder_update_response = requests.post(ladder_url, headers={'Authorization': 'Token {}'.format(SLK)})
            ladder_update_data = ladder_update_response.json()
            if ladder_update_response.status_code == 200:
                update = 'Data Updated!'
            else:
                update = 'Can\'t Update Data Yet!'

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
                
            elif ladder_response.status_code == 429:
                print("Request rate limited: {}".format(ladder_response.text))
            elif ladder_response.status_code == 401:
                print("Not authorized: {}".format(ladder_response.text))
            elif ladder_response.status_code == 404:
                print("Not found: {}".format(ladder_response.text))
                error = ladder_data['error']
                await message.channel.send(f"An error ocurred: {error}")
            else:
                try:
                    error = ladder_data['error']
                except:
                    await message.channel.send("A weird error happened, F")
                await message.channel.send(f"An error ocurred: {error}")

            # WRITE DATA
            await message.channel.send(f'```{update}\nLast Data Update: {last_update}```')

            embed = discord.Embed(title=f"{name}", url=f"https://steamcommunity.com/profiles/{steamid}", description=f"{country}, {region}", color=0x000000)
            embed.set_author(name=name, url=f"https://steamcommunity.com/profiles/{steamid}", icon_url=avatar)
            embed.set_thumbnail(url=avatar)

            embed.add_field(name="Steam ID", value=f"{steamid}", inline=False)

            embed.add_field(name="Steam Years", value=f"{joined_years}", inline=True)
            embed.add_field(name="Level", value=f"{level}", inline=True)
            embed.add_field(name="Badges", value=f"{badges}", inline=True)
            embed.add_field(name="Games", value=f"{games}", inline=True)
            embed.add_field(name="Playtime", value=f"{playtime}", inline=True)
            embed.add_field(name="Friends", value=f"{friends}", inline=True)
            embed.add_field(name="Most Played Game", value=f"{max_game} - {max_playtime}h", inline=False)
            embed.set_footer(text="By: UGH Dany")
            msg = await message.channel.send(embed=embed)

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
                embed2 = discord.Embed(color=0x000000, description=f"{country}, {region}")
                embed2.set_author(name=f"{name} | SteamLadder Stats", url=steamladder_url, icon_url=avatar)

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
                    embed3 = discord.Embed(color=0x000000, description=f"{country}, {region}")
                    embed3.set_author(name=f"{name} | Bans", url=steamladder_url, icon_url=avatar)

                    embed3.add_field(name="VAC Ban", value=f"{vac_ban}", inline=True)
                    embed3.add_field(name="Trade Ban", value=f"{trade_ban}", inline=True)
                    embed3.add_field(name="Community Ban", value=f"{community_ban}", inline=True)
                    
                    embed3.set_footer(text="By: UGH Dany")
                    await msg.edit(embed=embed3)
                await reaction.remove(user)
                await reaction.remove(client.user)
        else:
            await message.channel.send('Steam Custom URL Not Found!\n||(If you\'re sure this is an error, DM @UGH Dany)||')

client.run(token)