import discord
import pickle
import os.path
import os
import dbl

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from random import randrange
from discord.ext import commands

# Author: Sanjana (¬sanj#2714) discord user
# Created: 26 MAY 2020
# Last updated: 29 MAY 2020
# About: Passel Bot is a solution to the number of limited number of pins in a discord server.
#        It manages pins in 2 modes, Mode 1 and Mode 2. Passel is run on Heroku and
#        uses google drive to store
#
#        More information can be found on https://passelbot.wixsite.com/home
#        Passel Support Server: https://discord.gg/wmSsKCX
#
#        Mode 1: In mode 1, the most recent pinned message gets sent to a pins archive
#        channel of your choice. This means that the most recent pin wont be viewable in
#        the pins tab, but will be visible in the pins archive channel that you chose during setup
#
#        Mode 2: In mode 2, the oldest pinned message gets sent to a pins archive channel of
#        your choice. This means that the most recent pin will be viewable in the pins tab, and
#        the oldest pin will be unpinned and put into the pins archive channel
#
#        Furthermore: the p.sendall feature described later in the code allows the user to set
#        Passel so that all pinned messages get sent to the pins archive channel.
client = commands.Bot(command_prefix='p.', status='Online')

globals()
driveFiles = {}
data = {}
SERVICE = ''

# discord embed colors
EMBED_COLORS = [
    discord.Colour.magenta(),
    discord.Colour.blurple(),
    discord.Colour.dark_teal(),
    discord.Colour.blue(),
    discord.Colour.dark_blue(),
    discord.Colour.dark_gold(),
    discord.Colour.dark_green(),
    discord.Colour.dark_grey(),
    discord.Colour.dark_magenta(),
    discord.Colour.dark_orange(),
    discord.Colour.dark_purple(),
    discord.Colour.dark_red(),
    discord.Colour.darker_grey(),
    discord.Colour.gold(),
    discord.Colour.green(),
    discord.Colour.greyple(),
    discord.Colour.orange(),
    discord.Colour.purple(),
    discord.Colour.magenta(),
]

# scopes for google drive
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.appdata',
          'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']


# following method below is modified from Google's api for google drive
def main():
    global SERVICE
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    SERVICE = build('drive', 'v3', credentials=creds)

    # modified versions below
    results = SERVICE.files().list(
        pageSize=20, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            driveFiles[item['name']] = item['id']


# used to autoupdate number of servers in https://top.gg/bot/714899096015732886
class TopGG(commands.Cog):

    def __init__(self, bot):
        bot = commands.Bot
        self.bot = bot
        self.token = 'TOKEN'
        self.dblpy = dbl.DBLClient(self.bot, self.token,
                                   autopost=True)  # Autopost will post your guild count every 30 minutes

    async def on_guild_post(self):
        print("Server count posted successfully")


# reads thhe data files from Google drive. Data file is a .txt file stored
# in the following format with a new line for each server which **sets up** Passel
# ServerID : mode number | pins channel ID | any blacklisted channels separated by ' | '
def fileReadIntoDict(fileName, dictionary, separator):
    global SERVICE
    file = SERVICE.files().get(fileId=driveFiles[fileName]).execute()
    dataread = str(SERVICE.files().get_media(fileId=driveFiles[fileName]).execute())
    length = len(dataread)
    dataStripped = dataread[2: length - 1]

    dataList = dataStripped.split('\\n')
    f = open('tempfile.txt', 'w')

    for elem in dataList:
        f.write(elem)
        f.write('\n')
    f.close()

    f = open('tempfile.txt', 'r')
    with f as reader:
        line = reader.readline()
        while line != '':
            try:
                lineTuple = line.partition(separator)
                listVal = lineTuple[2].split(' | ')
                dictionary[int(lineTuple[0])] = listVal
                counter = int(lineTuple[0])
                line = reader.readline()
            except:
                dictionary[counter] += line
                line = reader.readline()
    f.close()


# file writes the data file
def fileWrite(dictionary, fileName):
    file = open(fileName, "w")
    for val in dictionary:
        try:
            length = len(dictionary[val])
            if length == 1:
                file.write("")
                file.write("\n")
            if length > 1:
                file.write(str(val) + " : ")
                for num in dictionary[val]:
                    if num != '' and num != "\n":
                        file.write(str(num).rstrip() + " | ")
                file.write("\n")
        except:
            print('Invalid when writing file.')
    file.close()


# runs google drive files
if __name__ == '__main__':
    main()

# Reads the file into the data dictionary, data while the app is running
# is stored as a dictionary with the key as the server id, and all of the
# other data as the value of the key stored as a list
fileReadIntoDict(fileName="data.txt", dictionary=data, separator=" : ")


# When the bot is ready following sets the status of the bot
@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game(name='p.help | Visit https://passelbot.wixsite.com/home for help'))
    print('We have logged in as {0.user}'.format(client))


# Method below manages all messages related to the bot
@client.event
async def on_message(message):
    global SERVICE
    global data
    global EMBED_COLORS

    # does nothing if Passel is trigged
    if message.author == client.user:
        return

    # does nothing if another bot tries to trigger Passel
    if message.author.bot:
        return

    # help message
    # fixed w/ update
    if message.content.lower() == 'p.help':
        randomColor = randrange(len(EMBED_COLORS))
        # reads help data from data.txt file in google drive
        global SERVICE
        datahelp = str(SERVICE.files().get_media(fileId=driveFiles['help.txt']).execute())
        length = len(datahelp)
        dataStripped = datahelp[2: length - 1]
        msg = ''
        for elem in dataStripped.split('\\n'):
            msg += elem
            msg += '\n'
        embedHelp = discord.Embed(
            title="__**my prefix is: 'p.'**__",
            description=msg,
            colour=EMBED_COLORS[randomColor]
        )
        embedHelp.add_field(name="Help Website", value="https://passelbot.wixsite.com/home", inline=False)
        embedHelp.add_field(name="Support Server", value="https://discord.gg/wmSsKCX", inline=False)
        embedHelp.set_footer(
            text="Requested by:" + message.author.name + "\nFor help contact: ¬sanj#2714 or passelBot@gmail.com")
        await message.channel.send(embed=embedHelp)

    # info message
    # fixed w/ update
    if message.content.lower() == 'p.info':
        randomColor = randrange(len(EMBED_COLORS))
        # reads data from info.txt in google drive
        datainfo = str(SERVICE.files().get_media(fileId=driveFiles['info.txt']).execute())
        length = len(datainfo)
        dataStripped = datainfo[2: length - 1]
        msg = ''
        for elem in dataStripped.split('\\n'):
            msg += elem
            msg += '\n'
        embedInfo = discord.Embed(
            title="My Information",
            description=msg,
            colour=EMBED_COLORS[randomColor]
        )
        embedInfo.add_field(name="Help Website", value="https://passelbot.wixsite.com/home", inline=False)
        embedInfo.add_field(name="Support Server", value="https://discord.gg/wmSsKCX", inline=False)
        embedInfo.set_footer(
            text="Requested by:" + message.author.name + "\nFor help contact: ¬sanj#2714 or passelBot@gmail.com \nCreated on May 26th, 2020")
        await message.channel.send(embed=embedInfo)

    # invite message
    # fixed w/ update
    if message.content.lower() == 'p.invite':
        randomColor = randrange(len(EMBED_COLORS))
        embedinvite = discord.Embed(
            title="Click Here for Bot Invite Link",
            colour=EMBED_COLORS[randomColor],
            url='https://discord.com/api/oauth2/authorize?client_id=714899096015732886&permissions=388208&scope=bot'
        )
        embedinvite.add_field(name="Help Website", value="https://passelbot.wixsite.com/home", inline=False)
        embedinvite.add_field(name="Support Server", value="https://discord.gg/wmSsKCX", inline=False)
        embedinvite.set_footer(text="\nFor help contact: ¬sanj#2714 or passelBot@gmail.com")
        await message.channel.send(embed=embedinvite)

    # setup message requires admin perms, can only be used once upon setup

    if message.content.lower().startswith("p.setup ") and discord.abc.GuildChannel.permissions_for(
            member=message.author, self=message.author).administrator:

        # checks to see if set up has already been done in the server
        if message.author.guild.id in data:
            await message.channel.send(
                "You have already set up a channel to send messages: " + message.author.guild.get_channel(int(
                    data[message.author.guild.id][
                        2])).mention + "\nTo change channel or mode use p.changechannel <channel> or p.changemode "
                                       "<mode>" + "\nTo view use p.channel or p.mode")
            return

        try:
            dataVals = message.content[8:].split(" ")

            if len(dataVals) > 2:
                await message.channel.send("Invalid mode and channels try again")
                return
            if dataVals[0] != '1' and dataVals[0] != '2':
                await message.channel.send("Invalid mode try again")
                return

            mentionedChannels = message.channel_mentions

            if len(mentionedChannels) > 1:
                await message.channel.send("Invalid channel, only mention 1 channel")

            channelID = int(mentionedChannels[0].id)

            # checks to see if the channel is valid in the server
            isChannelValid = False
            for guild in client.guilds:
                if message.guild == guild:
                    channelList = message.guild.channels
                    for channel in channelList:
                        if channelID == channel.id:
                            isChannelValid = True

            # sends message if the channel is valid and puts it into the data, middle value is 0
            # because that is the value for sending all pins to the pins archive channel
            if isChannelValid:
                data[message.author.guild.id] = [str(dataVals[0]), str(0), str(channelID)]

                await message.channel.send("All archived pins will be sent to " + message.author.guild.get_channel(
                    channelID).mention + "\nSetup complete! You can use p.blacklist in a channel to blacklist that channel pins from being sent to " + message.author.guild.get_channel(
                    channelID).mention + "\n\nAlso make sure the bot has access to all channels that you want pins to be archived from and " + message.author.guild.get_channel(
                    channelID).mention + "so that the bot works properly \n\n The bot currently will only send pinned "
                                         "messages that **reach or exceed 50 pinned messages in a channel**, "
                                         "if you want to send all pinned messages to " +
                                           message.author.guild.get_channel(channelID).mention + " use p.sendall")

                # writes the data and re-sends to google drive, and deletes from the local storage
                fileWrite(dictionary=data, fileName="data.txt")
                file_metadata = {'name': 'data.txt'}

                media = MediaFileUpload('data.txt',
                                        mimetype='text/plain')

                file = SERVICE.files().create(body=file_metadata,
                                              media_body=media,
                                              fields='id').execute()

                SERVICE.files().delete(fileId=driveFiles['data.txt']).execute()

                driveFiles['data.txt'] = file.get('id')

                if os.path.exists("data.txt"):
                    os.remove("data.txt")
                else:
                    print("The file does not exist")

            # sends message if channel is valid and setup is not done
            if not isChannelValid:
                await message.channel.send("Invalid channel, try again")
        except:
            await message.channel.send(
                "That is an invalid channel for your server, try again. Contact ¬sanj#2714 or passelBot@gmail.com for help if you are having trouble.")

    # setup message information, requires admin perms, can only be used until bot is set up
    # fixed w/ update
    if message.content.lower() == 'p.setup' and discord.abc.GuildChannel.permissions_for(member=message.author,
                                                                                         self=message.author).administrator:

        if message.author.guild.id in data:
            await message.channel.send(
                "You have already set up a channel to send messages: " + message.author.guild.get_channel(int(
                    data[message.author.guild.id][
                        2])).mention + "\nTo change channel or mode use p.changechannel <channel> or p.changemode <mode>" + "\nTo view use p.channel or p.mode")
            return

        randomColor = randrange(len(EMBED_COLORS))
        datainfo = str(SERVICE.files().get_media(fileId=driveFiles['setup.txt']).execute())
        length = len(datainfo)
        dataStripped = datainfo[2: length - 1]
        msg = ''
        for elem in dataStripped.split('\\n'):
            msg += elem
            msg += '\n'
        embedSetup = discord.Embed(
            title="Setup Information",
            description=msg,
            colour=EMBED_COLORS[randomColor]
        )
        embedSetup.add_field(name="Help Website", value="https://passelbot.wixsite.com/home", inline=False)
        embedSetup.add_field(name="Setup Help Video", value="https://youtu.be/2uUKPoACkeE", inline=False)
        embedSetup.add_field(name="Support Server", value="https://discord.gg/wmSsKCX", inline=False)
        embedSetup.set_footer(text="\nFor help contact: ¬sanj#2714 or passelBot@gmail.com")
        await message.channel.send(embed=embedSetup)
        return

    # black-lists channels, command should be used in the channel that you want to blacklist
    # fixed w/ update
    if message.content.lower() == 'p.blacklist' and discord.abc.GuildChannel.permissions_for(
            member=message.author, self=message.author).administrator:

        # checks to see if bot is setup first
        if str(message.author.guild.id) not in str(data):
            await message.channel.send("You have not set up the bot, use p.setup")
            return

        try:
            channelBL = message.channel.id
            isChannelValid = False

            # checks channel validity, not needed in the way that blacklist is set up right now
            # but will be kept in here in case I want to change it so blacklist can be used as
            # p.blacklist <#channel> instead of how it is right now
            for guild in client.guilds:
                if message.guild == guild:
                    channelList = message.guild.channels
                    for channel in channelList:
                        if channelBL == channel.id:
                            isChannelValid = True

            if isChannelValid:
                # if true, un-blacklist, if false, need to blacklist
                isBlacklisted = False

                if str(message.author.guild.id) in str(data):
                    if str(channelBL) in data[message.author.guild.id]:
                        isBlacklisted = True

                if isBlacklisted:
                    channelIndex = data[message.author.guild.id].index(str(channelBL))
                    data[message.author.guild.id][channelIndex] = ''

                    await message.channel.send(
                        "Successfully removed " + message.author.guild.get_channel(
                            channelBL).mention + " from blacklist.")

                if not isBlacklisted:
                    data[message.author.guild.id].append(str(channelBL))
                    await message.channel.send(
                        "successfully blacklisted " + message.author.guild.get_channel(channelBL).mention)

                # rewrites data to the data.txt file
                fileWrite(dictionary=data, fileName="data.txt")
                file_metadata = {'name': 'data.txt'}

                media = MediaFileUpload('data.txt',
                                        mimetype='text/plain')

                file = SERVICE.files().create(body=file_metadata,
                                              media_body=media,
                                              fields='id').execute()

                SERVICE.files().delete(fileId=driveFiles['data.txt']).execute()

                driveFiles['data.txt'] = file.get('id')

                if os.path.exists("data.txt"):
                    os.remove("data.txt")
                else:
                    print("The file does not exist")

            if not isChannelValid:
                await message.channel.send("Invalid channel.")
        except:
            await message.channel.send("Invalid channel.")

    # changes the channel where pins are directed to
    # fixed w/ update
    if message.content.lower().startswith("p.changechannel ") and discord.abc.GuildChannel.permissions_for(
            member=message.author, self=message.author).administrator:

        # checks to see if bot is setup first
        if str(message.author.guild.id) not in str(data):
            await message.channel.send("You have not set up the bot, use p.setup")
            return

        try:
            channelID = int(message.content[18:len(message.content) - 1])
            isChannelValid = False

            # checks for channel validity
            for guild in client.guilds:
                if message.guild == guild:
                    channelList = message.guild.channels
                    for channel in channelList:
                        if channelID == channel.id:
                            isChannelValid = True

            if isChannelValid:
                data[message.author.guild.id][2] = channelID

                await message.channel.send("Changed channel to " + message.author.guild.get_channel(channelID).mention)

                # updates data file for google drive
                fileWrite(dictionary=data, fileName="data.txt")
                file_metadata = {'name': 'data.txt'}

                media = MediaFileUpload('data.txt',
                                        mimetype='text/plain')

                file = SERVICE.files().create(body=file_metadata,
                                              media_body=media,
                                              fields='id').execute()

                SERVICE.files().delete(fileId=driveFiles['data.txt']).execute()

                driveFiles['data.txt'] = file.get('id')

                if os.path.exists("data.txt"):
                    os.remove("data.txt")
                else:
                    print("The file does not exist")

            if not isChannelValid:
                await message.channel.send("Invalid channel, try again.")

        except:
            await message.channel.send("Invalid channel, try again.")

    # changes the mode in which the pins are setup in the server
    # fixed w/ update
    if message.content.lower().startswith("p.changemode ") and discord.abc.GuildChannel.permissions_for(
            member=message.author, self=message.author).administrator:

        # checks to see if bot is setup first
        if str(message.author.guild.id) not in str(data):
            await message.channel.send("You have not set up the bot, use p.setup")
            return

        try:
            mode = int(message.content[13:])
            isModeValid = False

            if mode == 1 or mode == 2:
                isModeValid = True

            if isModeValid:
                data[message.author.guild.id][0] = mode

                await message.channel.send("Changed mode to " + str(mode))

                # updates data file in google drive
                fileWrite(dictionary=data, fileName="data.txt")
                file_metadata = {'name': 'data.txt'}

                media = MediaFileUpload('data.txt',
                                        mimetype='text/plain')

                file = SERVICE.files().create(body=file_metadata,
                                              media_body=media,
                                              fields='id').execute()

                SERVICE.files().delete(fileId=driveFiles['data.txt']).execute()

                driveFiles['data.txt'] = file.get('id')

                if os.path.exists("data.txt"):
                    os.remove("data.txt")
                else:
                    print("The file does not exist")

            if not isModeValid:
                await message.channel.send("Invalid mode, try again.")

        except:
            await message.channel.send("Invalid mode, try again.")

    # shows which channel is currently set up
    # fixed w/ update
    if message.content.lower() == "p.channel" and discord.abc.GuildChannel.permissions_for(
            member=message.author, self=message.author).administrator:

        # checks to see if the bot is setup
        if str(message.author.guild.id) not in str(data):
            await message.channel.send("You have not set up the bot, use p.setup")
            return

        isChannelValid = False

        # checks to see if the set up channel still exists
        for guild in client.guilds:
            if message.guild == guild:
                channelList = message.guild.channels
                for channel in channelList:
                    if int(data[message.author.guild.id][2]) == int(channel.id):
                        isChannelValid = True

        if not isChannelValid:
            await channel.send("Seems that the channel you have setup is deleted, use p.changechannel <channel> to "
                               "set up a new channel")
            return

        await message.channel.send("The channel you have set up is: " + message.author.guild.get_channel(
            int(data[message.author.guild.id][2])).mention)

    # shows the mode the server is set up in
    # fixed w/ update
    if message.content.lower() == "p.mode" and discord.abc.GuildChannel.permissions_for(
            member=message.author, self=message.author).administrator:

        # checks to see if the bot is setup
        if str(message.author.guild.id) not in str(data):
            await message.channel.send("You have not set up the bot, use p.setup")
            return

        await message.channel.send("The mode you have setup is: " + str(data[message.author.guild.id][0]))

    # sends the number of pins in a channel in a server
    # fixed w/ update
    if message.content.lower() == 'p.pins':
        numPins = await message.channel.pins()
        await message.channel.send(message.channel.mention + " has " + str(len(numPins)) + " pins.")

    # toggles the option to send all pins to the pins archive channel on or off
    if message.content.lower() == 'p.sendall' and discord.abc.GuildChannel.permissions_for(
            member=message.author, self=message.author).administrator:

        # checks to see if the bot is setup
        if str(message.author.guild.id) not in str(data):
            await message.channel.send("You have not set up the bot, use p.setup")
            return

        isChannelValid = False

        # checks to see if the set up channel still exists
        for guild in client.guilds:
            if message.guild == guild:
                channelList = message.guild.channels
                for channel in channelList:
                    if int(data[message.author.guild.id][2]) == int(channel.id):
                        isChannelValid = True

        if not isChannelValid:
            await message.channel.send("Channel during setup has been deleted or the bot does not access to it. Use "
                                       "p.changechannel <#channel> to use a different channel")
            return

        # changes so that all pins can be sent
        if int(data[message.guild.id][1]) == 0 and isChannelValid:
            data[message.guild.id][1] = str(1)
            await message.channel.send(
                "Turned on all pinned messages forwarding to  " + message.author.guild.get_channel(
                    int(data[message.author.guild.id][2])).mention)

            # re-writes file data and uploads to google drive
            fileWrite(dictionary=data, fileName="data.txt")
            file_metadata = {'name': 'data.txt'}

            media = MediaFileUpload('data.txt',
                                    mimetype='text/plain')

            file = SERVICE.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute()

            SERVICE.files().delete(fileId=driveFiles['data.txt']).execute()

            driveFiles['data.txt'] = file.get('id')

            if os.path.exists("data.txt"):
                os.remove("data.txt")
            else:
                print("The file does not exist")

            return

        if int(data[message.guild.id][1]) == 1 and isChannelValid:
            data[message.guild.id][1] = str(0)
            await message.channel.send(
                "Turned off all pinned messages forwarding to " + message.author.guild.get_channel(
                    int(data[message.author.guild.id][2])).mention)

            # re-writes file data and uploads to google drive
            fileWrite(dictionary=data, fileName="data.txt")
            file_metadata = {'name': 'data.txt'}

            media = MediaFileUpload('data.txt',
                                    mimetype='text/plain')

            file = SERVICE.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute()

            SERVICE.files().delete(fileId=driveFiles['data.txt']).execute()

            driveFiles['data.txt'] = file.get('id')

            if os.path.exists("data.txt"):
                os.remove("data.txt")
            else:
                print("The file does not exist")

            return

    # can only be used by me in the passel support server to see the names and IDs of the joined servers, simply replace
    # author and guild id if you want the code to work for you as well.
    # fixed w/ update
    if message.content.lower() == 'p.servers' and message.guild.id == 715396068157947965 and message.author.id == 454342857239691306:
        guildsJoined = client.guilds
        guildsdesc = '\n'
        await message.channel.send('Joined Servers: ' + str(len(guildsJoined)))
        for guild in guildsJoined:
            await message.channel.send(str(guild.id) + " : " + guild.name)

    # can only be used my me to get the server photo if anyone wants their server on
    # https://passelbot.wixsite.com/home/featured-servers fixed w/ update
    if message.content.lower() == 'p.serverphoto' and message.author.id == 454342857239691306:
        await message.channel.send(str(message.guild.icon_url))

    # can only be used by me in the passel support server to send update messages to the servers the bot is in
    # change author and guild id if you want the code to work for you as well.
    if message.content.lower() == 'p.update' and message.guild.id == 715396068157947965 and message.author.id == 454342857239691306:
        print("reaches")
        randomColor = randrange(len(EMBED_COLORS))
        # reads data from info.txt in google drive
        dataUpdate = str(SERVICE.files().get_media(fileId=driveFiles['update.txt']).execute())
        length = len(dataUpdate)
        dataStripped = dataUpdate[2: length - 1]
        msg = ''
        for elem in dataStripped.split('\\n'):
            msg += elem
            msg += '\n'
        embedSend = discord.Embed(
            title="An Important Update Message",
            description=msg + "\n PS: This update may have caused deterioration in the functionality of Passel. "
                              "Please contact below if you are experiencing anything unusual with Passel.",
            colour=EMBED_COLORS[randomColor]
        )
        embedSend.add_field(name="Help Website", value="https://passelbot.wixsite.com/home", inline=False)
        embedSend.add_field(name="Support Server", value="https://discord.gg/wmSsKCX", inline=False)
        embedSend.set_footer(
            text="\nFor help contact: ¬sanj#2714 or passelBot@gmail.com \nCreated on May 26th, 2020")

        i = 0
        updateServerList = list(data.keys())
        for val in updateServerList:
            await client.get_guild(updateServerList[i]).get_channel(int(data[updateServerList[i]][2])).send(
                embed=embedSend)
            await client.get_guild(715396068157947965).get_channel(715402358913499136).send(
                "sent to " + str(updateServerList[i]))
            i += 1


# The method that takes care of pin updates in a server
@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    global data
    try:
        randomColor = randrange(len(EMBED_COLORS))
        numPins = await channel.pins()
        guildpinnedID = channel.guild.id
        guildMode = int(data[guildpinnedID][0])
        sendall = int(data[guildpinnedID][1])
        guildChannel = data[guildpinnedID][2]

        # checks to see if message is in the blacklist
        # message is only sent if there is a blacklisted server with 50 messages pinned, informs them
        # that passel is in the server and they can un-blacklist the channel to have passel work
        if len(data[guildpinnedID]) > 3:
            pinnedChannelList = data[guildpinnedID][3:]
            if str(channel.id) in pinnedChannelList:
                # await channel.send("Reached limit, un-blacklist this channel and remove 50th pin and repin 50th pin "
                #                   "to archive extra pins. p.help for more information")
                return

        isChannelThere = False

        # checks to see if pins channel exists in the server
        for guild in client.guilds:
            if channel.guild == guild:
                channnelList = channel.guild.channels
                for channel in channnelList:
                    if int(guildChannel) == int(channel.id):
                        isChannelThere = True

        # checks to see if pins channel exists or has been deleted
        if not isChannelThere:
            await channel.send("Check to see if the pins archive channel during setup has been deleted. (with the "
                               "channel ID " + str(guildChannel) + "use p.changechannel <#channel> to setup a new "
                                                                   "channel")
            return

        # only happens if send all is toggled on
        if len(numPins) < 50 and sendall == 1:
            last_pinned = numPins[0]
            pinEmbed = discord.Embed(
                title="Sent by " + last_pinned.author.name,
                description="\"" + last_pinned.content + "\"",
                colour=EMBED_COLORS[randomColor]
            )
            # checks to see if pinned message has attachments
            attachments = last_pinned.attachments
            if len(attachments) >= 1:
                pinEmbed.set_image(url=attachments[0].url)
            pinEmbed.add_field(name="Jump", value=last_pinned.jump_url, inline=False)
            pinEmbed.set_footer(
                text="sent in: " + last_pinned.channel.name + " - at: " + str(last_pinned.created_at))
            pinEmbed.set_author(name=last_pinned.author.name, url=last_pinned.author.avatar_url,
                                icon_url=last_pinned.author.avatar_url)
            await channel.guild.get_channel(int(guildChannel)).send(embed=pinEmbed)
            await last_pinned.channel.send(
                "See pinned message in " + channel.guild.get_channel(int(guildChannel)).mention)

            # if guild mode is one does the process following mode 1
        if guildMode == 1:
            last_pinned = numPins[len(numPins) - 1]
            # sends extra messages
            if len(numPins) == 50:
                last_pinned = numPins[0]
                pinEmbed = discord.Embed(
                    title="Sent by " + last_pinned.author.name,
                    description="\"" + last_pinned.content + "\"",
                    colour=EMBED_COLORS[randomColor]
                )
                # checks to see if pinned message has attachments
                attachments = last_pinned.attachments
                if len(attachments) >= 1:
                    pinEmbed.set_image(url=attachments[0].url)
                pinEmbed.add_field(name="Jump", value=last_pinned.jump_url, inline=False)
                pinEmbed.set_footer(
                    text="sent in: " + last_pinned.channel.name + " - at: " + str(last_pinned.created_at))
                pinEmbed.set_author(name=last_pinned.author.name, url=last_pinned.author.avatar_url,
                                    icon_url=last_pinned.author.avatar_url)
                await channel.guild.get_channel(int(guildChannel)).send(embed=pinEmbed)
                await last_pinned.channel.send(
                    "See pinned message in " + channel.guild.get_channel(int(guildChannel)).mention)
                await last_pinned.unpin()

        # if guild mode is two follows the process for mode 2
        if guildMode == 2:
            last_pinned = numPins[0]
            if len(numPins) == 50:
                last_pinned = numPins[len(numPins) - 1]
                pinEmbed = discord.Embed(
                    title="Sent by " + last_pinned.author.name,
                    description="\"" + last_pinned.content + "\"",
                    colour=EMBED_COLORS[randomColor]
                )
                # checks to see if pinned message has attachments
                attachments = last_pinned.attachments
                if len(attachments) >= 1:
                    pinEmbed.set_image(url=attachments[0].url)
                pinEmbed.add_field(name="Jump", value=last_pinned.jump_url, inline=False)
                pinEmbed.set_footer(
                    text="sent in: " + last_pinned.channel.name + " - at: " + str(last_pinned.created_at))
                pinEmbed.set_author(name=last_pinned.author.name, url=last_pinned.author.avatar_url,
                                    icon_url=last_pinned.author.avatar_url)
                await last_pinned.guild.get_channel(int(guildChannel)).send(embed=pinEmbed)
                await last_pinned.channel.send(
                    "See oldest pinned message in " + channel.guild.get_channel(int(guildChannel)).mention)
                await last_pinned.unpin()
    except:
        print("unpinned a message, not useful for bot so does nothing")


# when the bot joins a new guild a message is embedded into the support server
@client.event
async def on_guild_join(guild):
    global EMBED_COLORS
    randomColor = randrange(len(EMBED_COLORS))
    guildsJoined = client.guilds
    embedjoin = discord.Embed(
        title="Joined " + guild.name,
        description="ID: " + str(guild.id),
        colour=EMBED_COLORS[randomColor]
    )
    embedjoin.set_footer(text="Total Number of Servers: " + str(len(guildsJoined)))
    await client.get_guild(715396068157947965).get_channel(715627621303582750).send(embed=embedjoin)


# when the bot joins a new guild a message is embedded into the support server
# and data is removed from the data file and local dictionary
@client.event
async def on_guild_remove(guild):
    global SERVICE
    global data
    global EMBED_COLORS
    guildsJoined = client.guilds
    randomColor = randrange(len(EMBED_COLORS))
    embedleave = discord.Embed(
        title="Left " + guild.name,
        description="ID: " + str(guild.id),
        colour=EMBED_COLORS[randomColor]
    )

    # removes server from dictionary if it exists, else sends an embed
    # to the support server saying it has left without setting up
    try:
        data.pop(int(guild.id))
        print("reaches")
    except:
        print("no setting up reaches")
        embedleave.set_footer(text="Left without setting up.\nTotal Number of Servers: " + str(len(guildsJoined)))
        await client.get_guild(715396068157947965).get_channel(715627621303582750).send(embed=embedleave)
        return

    embedleave.set_footer(text="Total Number of Servers: " + str(len(guildsJoined)))
    await client.get_guild(715396068157947965).get_channel(715627621303582750).send(embed=embedleave)

    # re-writes file data and uploads to google drive
    fileWrite(dictionary=data, fileName="data.txt")
    file_metadata = {'name': 'data.txt'}

    media = MediaFileUpload('data.txt',
                            mimetype='text/plain')

    file = SERVICE.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()

    SERVICE.files().delete(fileId=driveFiles['data.txt']).execute()

    driveFiles['data.txt'] = file.get('id')

    if os.path.exists("data.txt"):
        os.remove("data.txt")
    else:
        print("The file does not exist")

client.add_cog(TopGG(client))
#generates error AttributeError: type object 'Bot' has no attribute 'loop' from line 109
client.run('TOKEN')
