from datetime import datetime, timedelta, timezone
from litterkicker.kicker import Kicker
from pylitterbot import Account
from pylitterbot.enums import LitterBoxStatus
from pylitterbot.robot import Robot
from unittest.mock import MagicMock
import unittest

class TestKicker(unittest.TestCase):
    """Generated using ChatGPT"""

    def setUp(self):
        self.max_idle_duration_seconds = 60 * 60 * 3
        self.kicker = Kicker(None, None, self.max_idle_duration_seconds)
        self.robot = MagicMock()

    async def test_kick_no_previous_cycle(self):
        self.robot.get_activity_history.return_value = []
        await self.kicker.kick(robot)
        self.robot.start_cleaning.assert_not_called()

    async def test_kick_idle_duration_exceeded(self):
        last_clean = datetime.now(timezone.utc) - timedelta(hours=4)
        self.robot.get_activity_history.return_value = [
            MagicMock(action=LitterBoxStatus.CLEAN_CYCLE_COMPLETE, timestamp=last_clean)
        ]
        await self.kicker.kick(robot)
        self.robot.start_cleaning.assert_called_once()

    async def test_kick_idle_duration_not_exceeded(self):
        self.robot = MagicMock()
        last_clean = datetime.now(timezone.utc) - timedelta(hours=2)
        self.robot.get_activity_history.return_value = [
            MagicMock(action=LitterBoxStatus.CLEAN_CYCLE_COMPLETE, timestamp=last_clean)
        ]
        await self.kicker.kick(robot)
        self.robot.start_cleaning.assert_not_called()

    async def test_kick_multiple_activities(self):
        last_clean = datetime.now(timezone.utc) - timedelta(hours=4)
        self.robot.get_activity_history.return_value = [
            MagicMock(action=LitterBoxStatus.CLEAN_CYCLE_COMPLETE, timestamp=last_clean),
            MagicMock(action=LitterBoxStatus.CLEAN_CYCLE_COMPLETE, timestamp=last_clean - timedelta(hours=1)),
            MagicMock(action=LitterBoxStatus.CLEAN_CYCLE_COMPLETE, timestamp=last_clean - timedelta(hours=2))
        ]
        await self.kicker.kick(robot)
        self.robot.start_cleaning.assert_called_once()

    async def test_kick_no_clean_cycle_activity(self):
        last_clean = datetime.now(timezone.utc) - timedelta(hours=4)
        self.robot.get_activity_history.return_value = [
            MagicMock(action=LitterBoxStatus.SLEEP_MODE, timestamp=last_clean),
            MagicMock(action=LitterBoxStatus.CAT_DETECTED, timestamp=last_clean - timedelta(hours=1)),
            MagicMock(action=LitterBoxStatus.CLEAN_CYCLE_STARTED, timestamp=last_clean - timedelta(hours=2))
        ]
        await self.kicker.kick(robot)
        self.robot.start_cleaning.assert_not_called()
