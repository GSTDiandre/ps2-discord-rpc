# ps2-discord-rpc
A PS2 rich presence client for Discord, for use with Open PS2 Loader (OPL) over SMB.

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

Detects game at launch, maintains rich presence until the console is turned off. Has to run before any game is launched on OPL.

Game covers pulled from [Xlenore's PS2 Covers](https://github.com/xlenore/ps2-covers).

Requires Python 3.8+. Tested with OPL 1.1.0.

Usage: 

- Head to https://discord.com/developers/applications to create a new application. Its name will be displayed in rich presence, recommended names are "PlayStation 2" or "PS2".

- Download the project as ZIP, open conf.ini and replace CLIENT_ID with new app's client ID, found under the OAuth2 tab. Specify the PS2's IP as well as the host machine's IP in PS2_IP and HOST_IP.

- Run ps2rpc.py as administrator.
