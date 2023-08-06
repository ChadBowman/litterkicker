from litterkicker.kicker import Kicker
from asyncio import run, sleep
import logging
import sys
import os

async def main():
    logging.basicConfig(level=logging.INFO)
    username = os.environ.get("WHISKER_USERNAME")
    password = os.environ.get("WHISKER_PASSWORD")
    kicker = Kicker(username, password)
    robot = await kicker.fetch_robot()
    while True:
        await kicker.kick(robot)
        await sleep(60 * 15)  # 15 minutes

if __name__ == "__main__":
    run(main())
