from dotenv import load_dotenv
from pathlib import Path
from .botmaster import TwitchBotMaster

if __name__ == '__main__':
    dot_path = Path('/home/bam/bambot/.env')
    load_dotenv(verbose=True, dotenv_path=dot_path)
    twitch_master = TwitchBotMaster()
    twitch_master.run()
