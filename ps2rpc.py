import socket
import time
import logging
import pathlib
import os
import ping3
from dotenv import load_dotenv
from pypresence import Presence
from multiprocessing import Process, Value

#TODO prevent counter from overflowing grace
#TODO proper buffer flush aka bruno
#TODO use pyinstaller for setup

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
HOST_IP = os.getenv('HOST_IP')
PS2_IP = os.getenv('PS2_IP')

GAMEDB_FILE = 'GameDB.txt'

DVD_FILTER = bytes.fromhex('5c004400560044005c')
STAR_FILTER = bytes.fromhex('5c004400560044005c002a')
GAMES_BIN_FILTER = bytes.fromhex('5c004400560044005c00670061006d00650073002e00620069006e')

PING_GRACE = 3 # number of dropped pings before terminating RPC
PING_WAIT = 3 # time to wait before next ping
PING_TIMEOUT = 1 # timeout in ms

GameDB = {}
last_ping = Value('i', 1)  # ping value will be stored here
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('logs.log')
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    handlers=[stream_handler, file_handler]
)
logger = logging.getLogger()

def ping_func(n):
    ping_count = 1
    ping_lost = False
    n.value = True
    while True:
        ping_response = ping_ps2()
        if ping_response:  # successful ping
            ping_count = 1
            if ping_lost:
                logging.info("PS2 has resumed pings")
                ping_lost = False
        else:  # dropped ping
            logging.warning(f"No response from PS2, retrying.. ({ping_count}/{PING_GRACE})")
            ping_lost = True
            ping_count += 1
        if ping_count > PING_GRACE:
            n.value = False
        # wait before pinging again
        time.sleep(PING_WAIT)

# poor man's python
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

def load_gamename_map(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            code, name = line.rstrip().split(":", 1)  # this splits the line into 2 parts on the first colon
            GameDB[code] = name  # this adds a new key/value to the dictionary

# Ping once w/ a timeout of 1000ms
def ping_ps2(ip=PS2_IP):
    try:
        result = ping3.ping(ip, timeout=PING_TIMEOUT)
        # Check the return code for successful ping
        if result >= 0:
            logging.debug(f"PS2 is alive, responded in {result:.3f}s")
            return True
        else:
            return False
    except TypeError:
        return False
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        return False

def main():
    logger.info(f"---------------------------------")
    logger.info(f"PS2 IP is set as {PS2_IP}")
    logger.info(f"Host IP is set as {HOST_IP}")
    load_gamename_map(GAMEDB_FILE)
    logger.info(f"GameDB: loaded {len(GameDB)} game(s)")
    RPC = Presence(CLIENT_ID)  # initialize the client class
    RPC.connect()  # start the handshake loop
    p = Process(target=ping_func, args=(last_ping,)) # Initialize subprocess
    # create a raw socket and bind it to the public interface
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    s.bind((HOST_IP, 0))
    # include IP headers
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # receive all packets
    s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    PS2Online = False
    while True:
        message, address = s.recvfrom(65565)
        ip, port = address
        # check if the last ping was successful, clear rich presence otherwise
        if not last_ping.value:
            PS2Online = False
            RPC.clear()
            if p.is_alive():
                last_ping.value = 1
                logging.info("PS2 has gone offline, RPC terminated")
                logger.debug("Killing ping subprocess")
                p.kill()
        if ip == PS2_IP:
            #logger.debug(f"PACKET from {ip} at {port}, : {message}") 
            if not p.is_alive():
                last_ping.value = 1
                p = Process(target=ping_func, args=(last_ping,))
                p.start()
            if not PS2Online:
                RPC.update(state="Idle",
                           details="running OPL",
                           large_image="https://i.imgur.com/HjuVXhR.png",
                           # https://i.imgur.com/MXzehWn.png for OPL logo
                           large_text="Open PS2 Loader",
                           start=time.time())
                logger.info("PS2 has come online")
                PS2Online = True
            # drop last byte
            #msg_slice = message[128:-1] #never using this again
            testposition1 = message.find(GAMES_BIN_FILTER)
            testposition2 = message.find(STAR_FILTER)
            testposition3 = message.find(DVD_FILTER)
            if testposition1!=-1:
                logger.debug(f"gamebinfilter found at {testposition1}, message is {message}")
                continue
            elif testposition2!=-1:
                logger.debug(f"starfilter found at {testposition2}, message is {message}")
                continue
            elif testposition3!=-1:
                logger.debug(f"dvdfilter found at {testposition3}, message is {message}")
                msg_slice = message[testposition3:-1]
                gamepath = bytes([c for c in msg_slice if c != 0x00]).decode()
                gamecode, gamename, _ = remove_prefix(gamepath, "\\DVD\\").rsplit(
                    ".", 2
                )
                fixed_gamecode = gamecode.replace('_', '-').replace('.', '')
                fixed_gamename = GameDB[fixed_gamecode]
                RPC.update(
                    state=fixed_gamecode,  # middle text
                    details=fixed_gamename,  # top text
                    large_image=f"https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/{fixed_gamecode}.jpg",
                    large_text=fixed_gamename,  # large image hover text
                    small_image="https://i.imgur.com/91Nj3w0.png",
                    small_text="PlayStation 2",  # small image hover text
                    start=time.time(),  # timer
                )
                logger.info("RPC started: " + gamecode + " - " + fixed_gamename)
                time.sleep(10)  # necessary wait to avoid dropped pings on game startup
                while last_ping.value:
                    time.sleep(2.8)
                PS2Online = False
                RPC.clear()
                logging.info("PS2 has gone offline, RPC terminated")
                if p.is_alive():
                    last_ping.value = 1
                    logger.debug("Killing ping subprocess")
                    p.kill()
                # we don't talk about bruno
                time.sleep(3)
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
    try:
        main()
    except Exception as e:
        logger.exception(e)
        input()
