# ps2-discord-rpc
A PS2 rich presence client for Discord, for use with Open PS2 Loader (OPL) over SMB.

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

Detects game at launch, maintains rich presence until the console is turned off. Has to run before any game is launched on OPL.

Game covers pulled from [Xlenore's PS2 Covers](https://github.com/xlenore/ps2-covers).

Requires Python 3.8+. Tested with OPL 1.1.0. Only supports PS2 titles for now.

Usage: 

- Head to https://discord.com/developers/applications to create a new application. Its name will be displayed in rich presence, recommended names are "PlayStation 2" or "PS2".

- Install Python and run `pip install pypresence` in bash or command line

- Download the project as ZIP, open conf.ini and replace CLIENT_ID with the discord app's client ID, found under the OAuth2 tab. Specify the PS2 and host machine IPs, ensure the PS2 IP is set to STATIC in OPL.

- Run ps2rpc.py as administrator. Boot the console into OPL, then launch a PS2 game.
