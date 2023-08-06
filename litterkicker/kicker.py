from asyncio import run
from datetime import datetime, timedelta, timezone
from pylitterbot import Account
from pylitterbot.enums import LitterBoxStatus
from pylitterbot.robot import Robot
from time import sleep
import logging

log = logging.getLogger(__name__)

class Kicker:
    def __init__(self,
        username: str,
        password: str,
        max_idle_duration_seconds: int = (60 * 60 * 3)
    ) -> None:
        self.account = Account()
        self.connect = self.account.connect(username=username, password=password, load_robots=True)
        self.max_idle_duration_seconds = max_idle_duration_seconds

    async def kick(self, robot: Robot) -> None:
        """Checks when the last cycle was.
        If last cycle happened more than max_idle_duration_seconds ago, cycle.
        Otherwise, no-op. Notify on issues.
        """
        history = await robot.get_activity_history()
        last_clean = None
        for activity in history:
            if activity.action == LitterBoxStatus.CLEAN_CYCLE_COMPLETE:
                last_clean = activity.timestamp
                break

        if not last_clean:
            log.warn("No previous cycle found")
            return
            
        now = datetime.now(timezone.utc)
        seconds_since_last_cycle = (now - last_clean).total_seconds()
        if seconds_since_last_cycle > self.max_idle_duration_seconds:
            log.info(f"Last cycle was {seconds_since_last_cycle / 3600:.2f} hours ago, cycling")
            await robot.start_cleaning()
        else:
            log.info(f"Last cycle was {seconds_since_last_cycle / 3600:.2f} hours ago, waiting")

    async def fetch_robot(self) -> Robot:
        await self.connect
        return self.account.robots[0]
