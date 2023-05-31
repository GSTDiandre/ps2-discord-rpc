# ps2-discord-rpc
A PS2 rich presence client for Discord, for use with Open PS2 Loader (OPL) over SMB.

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

Features:

- Implements rich presence status for both OPL and PS2 titles
- Includes a game title database, pulls game covers from [Xlenore's PS2 Covers](https://github.com/xlenore/ps2-covers)
- Clears presence when console goes offline


![Screenshot1](https://i.imgur.com/dODJ7Tc.png)

![Screenshot2](https://i.imgur.com/wpAvel8.png)

![Screenshot3](https://i.imgur.com/vBopTJh.png)


Requirements:

- Python 3.8+
- Tested with OPL 1.1.0. 
- Has to run before any game is launched on OPL.
- Only supports PS2 titles for now.

Usage: 

- Head to [Discord's developer portal](https://discord.com/developers/applications) to create a new application. Its name will be displayed in rich presence, recommended names are "PlayStation 2" or "PS2". Copy `Client ID` under `OAuth2`.
- Install [Python](https://www.python.org/downloads/), then run `pip install pypresence` and `pip install python-dotenv` in bash or command line prompt
- Download the latest release, open `.env` using a text editor and replace `CLIENT_ID` with the discord app's client ID, found under the OAuth2 tab. Specify the PS2 and host machine IPs as `PS2_IP` and `HOST_IP`, ensure the PS2 IP is set to STATIC in OPL.
- Run ps2rpc.py as administrator by opening an elevated command prompt and using `python ps2rpc.py`. 
- Boot the console into OPL, then launch a PS2 game.
