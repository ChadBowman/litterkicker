from asyncio import sleep
from datetime import datetime, timezone
import logging

from pylitterbot import Account
from pylitterbot.activity import Activity
from pylitterbot.enums import LitterBoxStatus
from pylitterbot.robot import Robot

log = logging.getLogger(__name__)

class Kicker:
  def __init__(self, max_idle_duration_seconds: int, restart_on_pinch: bool) -> None:
    self.max_idle_duration_seconds = max_idle_duration_seconds
    self.restart_on_pinch = restart_on_pinch

  async def kick(self, robot: Robot) -> None:
    """Checks when the last cycle was.
    If last cycle happened more than max_idle_duration_seconds ago, cycle.
    Otherwise, no-op. Notify on issues.
    """
    history = await robot.get_activity_history()
    if self.restart_on_pinch and self.should_restart(history):
      log.info("pinch detected, restarting")
      await self.restart_robot(robot)
    elif self.should_clean(history):
      log.info("cleaning")
      await robot.start_cleaning()

  def should_clean(self, history: list[Activity]) -> bool:
    last_clean = None
    # find the most recent clean cycle
    for activity in history:
      if activity.action == LitterBoxStatus.CLEAN_CYCLE_COMPLETE:
        last_clean = activity.timestamp
        break

    if not last_clean:
      log.info("No previous cycle found")
      return False
        
    now = datetime.now(timezone.utc)
    seconds_since_last_cycle = (now - last_clean).total_seconds()
    log.info(f"Last cycle was {seconds_since_last_cycle / 3600:.2f} hours ago")
    return seconds_since_last_cycle > self.max_idle_duration_seconds

  def should_restart(self, history: list[Activity]) -> bool:
    if not history:
      return False
    last_action = history[0].action
    return last_action == LitterBoxStatus.PINCH_DETECT

  async def fetch_robot(self, username: str, password: str) -> Robot:
    account = Account()
    await account.connect(username, password, load_robots=True)
    return account.robots[0]

  async def restart_robot(self, robot):
    async def try_power_change(on_off: bool) -> bool:
      target_statuses = set()
      if on_off:
        target_statuses = {
          LitterBoxStatus.CLEAN_CYCLE,
          LitterBoxStatus.CLEAN_CYCLE_COMPLETE,
          LitterBoxStatus.READY
        }
      else:
        target_statuses = {LitterBoxStatus.OFF}

      try:
        await robot.set_power_status(on_off)
        for sleep_s in [10, 30, 60, 120, 240, 600]:
          await robot.refresh()
          if robot.status in target_statuses:
            return True
          await sleep(sleep_s)
      except Exception as e:
        log.warn(e)
      log.error("Unable to change Robot's power setting")
      return False

    log.info("Restarting robot")
    turned_off = await try_power_change(False)
    if turned_off:
      log.info("Robot turned off")
      turned_on = await try_power_change(True)
      if turned_on:
        log.info("Robot turned on")
