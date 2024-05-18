from asyncio import run, sleep
import logging
import os

from litterkicker.kicker import Kicker

log = logging.getLogger(__name__)

async def main():
  logging.basicConfig(level=logging.INFO)
  username = os.environ.get("WHISKER_USERNAME")
  password = os.environ.get("WHISKER_PASSWORD")

  if not username:
    raise Exception("missing username")
  if not password:
    raise Exception("missing password")

  three_hours = 60 * 60 * 3
  kicker = Kicker(three_hours, restart_on_pinch=True)
  robot = await kicker.fetch_robot(username, password)

  while True:
    await kicker.kick(robot)
    await sleep(60 * 15)  # 15 minutes

if __name__ == "__main__":
  run(main())
