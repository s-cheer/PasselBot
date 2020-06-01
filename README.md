# About
Passel is a discord bot that manages the number of pins in a server. Discord has a pin limit of 50 pins per channel. However with passel, that limit can be bypassed. The following readme will explain how the bot works and how to add and setup the bot in a server.

![Passel Logo Color](https://github.com/sanjana0109/PasselBot/blob/master/PasselColorSmall.png)

# Invite
The bot can be invited by following this link: https://discord.com/oauth2/authorize?client_id=714899096015732886&permissions=388208&scope=bot 

The support server is: https://discord.gg/wmSsKCX 

The bot website is: https://passelbot.wixsite.com/home

# How it works / setup
The bot works by unpinning one message and sending it to a different channel during setup. There are 2 modes the bot can be setup in. 

Inorder for the bot to work properly, I reccomend giving the bot a role with administrator permission so the bot has access to view every channel. If you do not give the bot administrator permissions, Make sure that the bot has access to read and be able to type in the channels that you set up the bot in.

Also, any channel that has 50 pins should have one message unpinned, and then repin that 1 message after the bot is setup.

***Please keep in mind that the bot only pins messages that REACH and EXCEED the limit of 50 pins per channel in discord.***

**The prerequisites for the bot to work properly are:**
1. make sure the bot has access to view and type in the channels of the server
2. unpin one message from channels with 50 pins, and repin that after setup (you can use p.pins to check how many pins are in a chhannel)

# Setup
To set up you need to have administrator permissions and meet the pre-requisites above.

1. First create a channel that you want the extra pinned messages in, this channel can be named anything (I will call it pins for the purpose of the readme.md file)

2. Select a mode you want the mode to be setup in. The modes are as follows:

	> 1. In mode 1, the most recent pinned message is sent into the pins channel, and not pinned into the original channel where the message was pinned in. For example, if "Hello" is the most recent pinned message in a channel, it gets sent into the pins channel and NOT pinned into the orignal channel.

	> 2. In mode 2, the oldest pinned message in a channel is sent into the pins channel and un-pinned, and then the most recently pinned message stays in that channel. For example, if "Hello" is the most recent pinned message, and "Hello World is the oldest pinned message in that same channel. "Hello World" is unpiined and sent into the pins channel, and "Hello" is under the pinned messages in the channel.

3. After you select a mode, simply type this to set up the bot. 

```p.setup <mode> #channel```

here is an example:

```p.setup 1 #pins```


4. **[Optional] ** you can use the p.blacklist command in a specific channel to blacklist that channel from having extra pinned messages sent into the pins channel
example:
```p.blacklist``` type that in #mod-general if you do not want extra pinned messages from that channel being sent to #pins

That concludes setup! If you have any issues please visit the website mentioned above, the website has videos that are easy to follow and set up the bot.

**The channel and mode can be changed at any time after setup use:**

```p.changemode <mode>```

```p.changechannel <#channel>```


# All Commands
**Commands:**

```p.info: To see information about modes and more information about me.```

```p.invite: To invite me to your server```

```p.pins: To see the number of pins in thatt specific channel```


**Commands below require administrator permissions**

```p.setup: To set up the bot in your server```

```p.channel: To see your setup channel```

```p.mode: To see your set up mode```

```p.changechannel <channel>: To change channel of archived pins```

```p.changemode <mode>: To change the mode```

```p.blacklist: Type p.blacklist in a specific channel to blacklist that channel```

# Images
The following will show how the bot embeds the pinned messages in a server!

**When the message is pinned:**
![Hello World Pin](https://github.com/sanjana0109/PasselBot/blob/master/HelloWorldPin.png)

![Image Pin](https://github.com/sanjana0109/PasselBot/blob/master/ImagePin.png)

**How the pinned embed looks:**
![Hello World Embed](https://github.com/sanjana0109/PasselBot/blob/master/HelloWorldEmbed.png)

![Image Embed](https://github.com/sanjana0109/PasselBot/blob/master/ImageEmbed.png)

# Contact
Contact information can be found on the website https://passelbot.wixsite.com/home
- Email: passelBot@gmail.com
- Discord User ID: ¬sanj#2714

![Passel Logo Black and White](https://github.com/sanjana0109/PasselBot/blob/master/PasselBandWSmall.png)

### End
