import socket
import time
import subprocess
import logging
import datetime
import os
import sys
from pypresence import Presence

#TODO Kill RPC after disconnect in OPL
#TODO log to .log file, signal new sessions
#TODO read IDs and IPs from config file

CLIENT_ID = "1112585966562070639"  # Fake ID, put your real one here
HOST_IP = "192.168.1.110"
PS2_IP = "192.168.1.114"
PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
DVD_FILTER = bytes([0x5C, 0x00, 0x44, 0x00, 0x56, 0x00, 0x44, 0x00, 0x5C])
GAMES_BIN_FILTER = bytes(
    [
        0x5C,
        0x00,
        0x44,
        0x00,
        0x56,
        0x00,
        0x44,
        0x00,
        0x5C,
        0x00,
        0x67,
        0x00,
        0x61,
        0x00,
        0x6D,
        0x00,
        0x65,
        0x00,
        0x73,
        0x00,
        0x2E,
        0x00,
        0x62,
        0x00,
        0x69,
        0x00,
        0x6E,
    ]
)
GAMEDB_PATH = PATH + '\\GameDB.txt'
CONFIG_PATH = PATH + '\\config.ini'
PING_GRACE = 3

LARGE_IMAGE_MAP = {#unused maps
    "SLUS_210.05" : "https://i.imgur.com/GXSok6D.jpg",
    "SLES_535.40" : "https://i.imgur.com/jjRCj7e.jpg",
}

SMALL_IMAGE_MAP = {#unused maps
    "SLUS_210.05" : "https://i.imgur.com/9eC9WOP.png",
    "SLES_535.40" : "https://i.imgur.com/z4iSnFj.png",
}

# poor man's python
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text  # or whatever

def get_fixed_gamename(filename, search_string):
    found_line = "Unknown game"
    with open(filename, 'r') as file:
        lines = file.readlines()
        for index, line in enumerate(lines):
            if line.startswith(search_string):
                if index + 1 < len(lines):
                    found_line = lines[index + 1].strip()[1:-1]
                break
    return found_line

def ping_ps2(ip=PS2_IP):
    # Define the ping command based on the operating system
    # ping_cmd = ["ping", "-c", "1", ip]  # For Linux/macOS
    ping_cmd = ["ping", "-n", "1", ip, "-w", "5000"]  # For Windows
    try:
        # Execute the ping command and capture the output
        result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout.lower()
        # Check the output for successful ping
        if "ttl=" in output:
            logging.debug("PS2 is alive")
            return True
        else:
            return False
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        return False


def main():
    logger.info(f"PS2 IP is set as {PS2_IP}")
    logger.info(f"PS2 IP is set as {HOST_IP}")
    RPC = Presence(CLIENT_ID)  # Initialize the client class
    RPC.connect()  # Start the handshake loop
    # create a raw socket and bind it to the public interface
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    s.bind((HOST_IP, 0))
    # Include IP headers
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # receive all packets
    s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    PS2Online = False
    while True:
        message, address = s.recvfrom(65565)
        ip, port = address
        if ip == PS2_IP:
            if not PS2Online:
                RPC.update(state="Idle",
                details="running OPL", 
                large_image="https://i.imgur.com/MXzehWn.png", 
                large_text="Open PS2 Loader", 
                start=time.time())
                logger.info("PS2 has come online")
                PS2Online = True
            # drop last byte
            slice = message[128:-1]
            if slice.startswith(GAMES_BIN_FILTER):
                continue
            elif slice.startswith(DVD_FILTER):
                gamepath = bytes([c for c in slice if c != 0x00]).decode()
                gamecode, gamename, _ = remove_prefix(gamepath, "\\DVD\\").rsplit(
                    ".", 2
                )
                fixed_gamecode = gamecode.replace('_','-').replace('.','')
                fixed_gamename = get_fixed_gamename(GAMEDB_PATH, fixed_gamecode)
                RPC.update(
                    state=fixed_gamecode,#middle text
                    details=fixed_gamename,#top text
                    #large_image=LARGE_IMAGE_MAP.get(gamecode, "https://i.imgur.com/HjuVXhR.png"), #default PS2 Logo
                    large_image=f"https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/{fixed_gamecode}.jpg",
                    large_text=fixed_gamename,#large image hover text
                    small_image=SMALL_IMAGE_MAP.get(gamecode,"https://i.imgur.com/91Nj3w0.png"),
                    small_text="PlayStation 2",#small image hover text
                    start=time.time(),#timer
                )
                logger.info("RPC started: " + gamecode + " - " + gamename)
                time.sleep(10)#necessary wait to avoid dropped pings on game startup
                ping_count=1
                ping_lost=False
                while ping_count<=PING_GRACE:
                    if ping_ps2(PS2_IP):
                        ping_count=1
                        if ping_lost:
                            logging.info("PS2 has resumed pings")
                            ping_lost=False
                	    #wait before pinging again
                        time.sleep(3)
                    else:
                        logging.warning(f"No response from PS2,. ({ping_count}/{PING_GRACE} attempts)")
                        ping_lost=True
                        ping_count+=1
                PS2Online = False                
                RPC.clear()
                logging.info("PS2 has gone offline, RPC terminated")
                #we don't talk about bruno
                s.recvfrom(65565)
                s.recvfrom(65565)
                s.recvfrom(65565)
                s.recvfrom(65565)
                s.recvfrom(65565)
                time.sleep(3)
    # receive a packet
    # disabled promiscuous mode
    s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
    )
    logger = logging.getLogger()
    try:
        main()
    except Exception as e:
        logger.exception(e)
        time.sleep(4000)