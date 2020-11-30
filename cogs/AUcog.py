from asyncio.tasks import current_task
import os
# import random
import time
import datetime as dt
from attr import dataclass
import pandas as pd
import json
from numpy import arange

import discord
from discord.ext import commands, tasks
import asyncio

# Settings
# Maps:                 Skeld, Polus, MiraHQ
# Confirm ejects:       on/off
# Emergency meetings:   1-9
# Emergency cooldown:   0-60 by 5
# Discussion time:      0-120 by 15
# Voting time:          0-300 by 15
# Anonymous votes:      on/off
# Player speed:         0.5-3.0x by 0.25
# Crewmate vision:      0.25-5.0x by 0.25
# Imposter vision:      0.25-5.0x by 0.25
# Kill cooldown:        10-60s by 2.5
# Kill distance:        short/medium/long
# Visual tasks:         on/off
# Task bar updates:     always/meetings/never
# Common tasks:         0-2
# Long tasks:           0-3
# Short tasks:          0.5

# Settings

default_settings = {
    "the_map":"skeld", "confirm_eject":True, "meetings_num":1, "meetings_cd":15,
    "discussion_t":15, "voting_t":120, "anon_votes":False, "speed_player":1,
    "vision_cm":1, "vision_imp":1.5, "kill_cd":45, "kill_dist":"normal",
    "tasks_visual":True, "task_bar":"never", "tasks_common":1, "tasks_long":1,
    "tasks_short":2
}

valid_setting_names = ', '.join(['`' + x + '`' for x in default_settings.keys()])
valid_settings = {
    "the_map":["skeld", "polus", "mira"],
    "confirm_eject":[True, False], 
    "meetings_num":range(1, 10), 
    "meetings_cd":range(0, 60 + 5, 5),
    "discussion_t":range(0, 120 + 15, 15), 
    "voting_t":range(0, 300 + 15, 15), 
    "anon_votes":[True, False], 
    "speed_player":arange(0.5, 3.0 + 0.25, 0.25),
    "vision_cm":arange(0.25, 5 + 0.25, 0.25),
    "vision_imp":arange(0.25, 5 + 0.25, 0.25), 
    "kill_cd":arange(10, 60 + 2.5, 2.5), 
    "kill_dist":["short", "medium", "long"],
    "tasks_visual":[True, False], 
    "task_bar":["always", "meetings", "never"], 
    "tasks_common":range(2 + 1), 
    "tasks_long":range(3 + 1),
    "tasks_short":range(5 + 1)
}

# Win types
win_types = ["imp_kill", "imp_vote", "imp_sabotage",
                "cm_vote", "cm_task"]

# Settings
settings_vals = [
    ["the_map", 'Map'],
    ["confirm_eject", 'Confrim Ejects'],
    ["meetings_num", '# Meetings'],
    ["meetings_cd" , 'Meeting Cooldown'],
    ["discussion_t", 'Discussion Time'],
    ["voting_t" , 'Voting Time'],
    ["anon_votes", 'Anonymous Votes'],
    ["speed_player", 'Player Speed'],
    ["vision_cm" , 'Crew Vision'],
    ["vision_imp" , 'Imposter Vision'],
    ["kill_cd", 'Kill Cooldown'],
    ["kill_dist", 'Kill Distance'],
    ["tasks_visual", 'Visual Tasks'],
    ["task_bar", 'Task Bar'],
    ["tasks_common", '# Common Tasks'],
    ["tasks_long", '# Long Tasks'],
    ["tasks_short", '# Short Tasks'],
]

class AUCog(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    def init_settings(self, ctx):
        # Write default settings to file
        json_obj = json.dumps(default_settings, indent=4)
        guild_json = str(ctx.message.guild.id) + "_config.json"
        with open(guild_json, "w") as f:
            f.write(json_obj)

    @commands.command(name="create", help="Create new league")    
    async def create_league(self, ctx):

        league = pd.DataFrame({
            'guild':        pd.Series([], dtype='str'),
            'timestamp':    pd.Series([], dtype='datetime64[ns]'),
            'win_type':     pd.Series([], dtype='str'),
                # imp_kill, imp_sabotage, imp_vote, crew_task, crew_vote
            'imposters':    pd.Series([], dtype='object'),
            'crewmates':    pd.Series([], dtype='object'),
            # Settings
            "the_map":       pd.Series([], dtype='str'), 
            "confirm_eject": pd.Series([], dtype='bool'), 
            "meetings_num":  pd.Series([], dtype='int'), 
            "meetings_cd":   pd.Series([], dtype='int'), 
            "discussion_t":  pd.Series([], dtype='int'), 
            "voting_t":      pd.Series([], dtype='int'), 
            "anon_votes":    pd.Series([], dtype='bool'), 
            "speed_player":  pd.Series([], dtype='float'), 
            "vision_cm":     pd.Series([], dtype='float'), 
            "vision_imp":    pd.Series([], dtype='float'), 
            "kill_cd":       pd.Series([], dtype='int'), 
            "kill_dist":     pd.Series([], dtype='str'), 
            "tasks_visual":  pd.Series([], dtype='bool'), 
            "task_bar":      pd.Series([], dtype='str'), 
            "tasks_common":  pd.Series([], dtype='int'), 
            "tasks_long":    pd.Series([], dtype='int'), 
            "tasks_short":   pd.Series([], dtype='int'), 
        })

        league_csv = str(ctx.message.guild.id) + "_results.csv"

        # if not os.path.isfile(league_csv):
        league.to_csv(league_csv)

        self.init_settings(ctx)

    @commands.command(name="setting", help="Update settings")
    async def update_setting(self, ctx):

        msgs = []
        msgs.append(ctx.message)
       
        guild_json = str(ctx.message.guild.id) + "_config.json"
        with open(guild_json) as f:
            current_settings = json.load(f)    

        # Split content into commands, and drop first (.setting)
        contents = ctx.message.content.split()[1:]
        print(contents)

        # If both a setting and value are given
        if len(contents) == 2:

            # The name of the setting
            setting = contents[0]

            if setting in default_settings.keys():
                value = contents[1]
                valid = ', '.join(['`' + str(x) + '`' for x in valid_settings[setting]])

                if value in valid:
                    current_settings[setting] = value
                    json_obj = json.dumps(current_settings, indent=4)
                    with open(guild_json, "w") as f:
                        f.write(json_obj)

                    msgs.append(await ctx.send("👍 Setting updated!"))
                else:
                    msgs.append(await ctx.send("❌ Error: Invalid value `%s` for setting `%s`" % (value, setting)))
                    msgs.append(await ctx.send("💁 Valid settings: %s" % valid))


            else:
                msgs.append(await ctx.send("❌ Error: Invalid setting `%s`!" % setting))
                msgs.append(await ctx.send("💁 Valid settings: %s" % valid_setting_names))

        elif len(contents) == 1 and (contents[0] == "show") or contents[0] == "valid":

            if contents[0] == "show":
                #create embed
                formatted_settings = discord.Embed(
                    title = f'Settings for current {} league',
                    color = discord.Color.blue()
                )

                for item in settings_vals:
                    formatted_settings.add_field(name=item[1], value=str(current_settings[item[0]]))

                #show embed
                #msgs.append(await ctx.send(current_settings))
                msgs.append(await ctx.send(formatted_settings))
                
            elif contents[0] == "valid":
                msgs.append(await ctx.send("💁 Valid settings: %s" % valid_setting_names))

        else:
            msgs.append(await ctx.send("❌ Error: Supply setting and value!"))
            msgs.append(await ctx.send("💁 Valid settings: %s" % valid_setting_names))


    @commands.command(name='add', help='Show current league table')
    async def add_game(self, ctx):

        msgs = []
        msgs.append(ctx.message)

        # Get current table
        league_csv = str(ctx.message.guild.id) + "_results.csv"
        league = pd.read_csv(league_csv)

        # Get current settings
        guild_json = str(ctx.message.guild.id) + "_config.json"
        with open(guild_json) as f:
            current_settings = json.load(f)

        ## HACKY WAY OF GETTING THINGS
        
        contents = ctx.message.content.split()[1:]
        msgs.append(await ctx.send(contents))

        I = [i for i, x in enumerate(contents) if x == "I:"][0]
        C = [i for i, x in enumerate(contents) if x == "C:"][0]
        V = [i for i, x in enumerate(contents) if x == "V:"][0]

        imposters = [contents[i] for i in range(I + 1, C)]
        crewmates = [contents[i] for i in range(C + 1, V)]
        victory = contents[V + 1]

        ##

        added_game = discord.Embed(
            title = f'Results from current game',
            color = discord.Color.green()
        )

        
        added_game.add_field(name='👹 Imposters:', value=imposters)
        added_game.add_field(name='🧉 Crewmates:', value=crewmates)
        added_game.add_field(name='🎮 Victory:', value=victory)

        #show embed
        msgs.append(await ctx.send(added_game))
        
        '''
        msgs.append(await ctx.send("👹 Imposters: %s" % imposters))
        msgs.append(await ctx.send("🧉 Crewmates: %s" % crewmates))
        msgs.append(await ctx.send("🎮 Victory: %s" % victory))
        '''

        if victory not in win_types:
            msgs.append(await ctx.send("❌ Error: Invalid win condition `%s`!" % victory))

        else:
            
            game = current_settings
            game["guild"] = ctx.message.guild.id
            game["timestamp"] = dt.datetime.now()
            game["win_type"] = victory
            game["imposters"] = imposters
            game["crewmates"] = crewmates

            l = league.append(game, ignore_index=True)
            l.to_csv(league_csv)

    @commands.command(name='show', help='Show current league table')
    async def show_league_table(self, ctx):

        msgs = []
        msgs.append(ctx.message)

        # Get current table
        league_csv = str(ctx.message.guild.id) + "_results.csv"
        league = pd.read_csv(league_csv)

        msgs.append(await ctx.send(league))

def setup(bot):
    cog = AUCog(bot)
    bot.add_cog(cog)