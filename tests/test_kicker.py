from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import AsyncMock, MagicMock, PropertyMock, call

from litterkicker.kicker import Kicker
from pylitterbot.enums import LitterBoxStatus
from pylitterbot.robot.litterrobot3 import LitterRobot3

class TestKicker(unittest.IsolatedAsyncioTestCase):

  async def test_cycle_after_idle(self):
    max_idle_duration_seconds = 60 * 60 * 3 # three hours
    kicker = Kicker(max_idle_duration_seconds, False)

    robot = AsyncMock(spec=LitterRobot3)
    # last cleaning was four hours ago
    four_hours = max_idle_duration_seconds + (60 * 60)
    last_clean_time = datetime.now(timezone.utc) - timedelta(seconds=four_hours)
    robot.get_activity_history.return_value = [
      MagicMock(action=LitterBoxStatus.CLEAN_CYCLE_COMPLETE, timestamp=last_clean_time)
    ]

    await kicker.kick(robot)

    robot.start_cleaning.assert_called_once()

  async def test_restart_on_pinch(self):
    max_idle_duration_seconds = 60 * 60 * 3 # three hours
    kicker = Kicker(max_idle_duration_seconds, True)

    robot = AsyncMock(spec=LitterRobot3)
    four_hours = max_idle_duration_seconds + (60 * 60)
    five_hours = four_hours + 3600
    now = datetime.now(timezone.utc)

    # last clean was 5 hours ago and 4 hours ago a pinch occured
    pinch_time = now - timedelta(seconds=four_hours) 
    last_clean_time = now - timedelta(seconds=five_hours)

    robot.get_activity_history.return_value = [
      MagicMock(action=LitterBoxStatus.PINCH_DETECT, timestamp=pinch_time),
      MagicMock(action=LitterBoxStatus.CLEAN_CYCLE_COMPLETE, timestamp=last_clean_time)
    ]
    robot.set_power_status.return_value = True
    robot.refresh.return_value = True
    type(robot).status = PropertyMock(side_effect=[
      LitterBoxStatus.OFF,
      LitterBoxStatus.CLEAN_CYCLE_COMPLETE
    ])

    await kicker.kick(robot)

    robot.set_power_status.assert_has_calls([call(False), call(True)], any_order=False)
