"""PawPal+ backend system skeleton.

Phase 1 provides class structure and method stubs only.
Scheduling algorithms and full validation are implemented in later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


class Priority(str, Enum):
    """Relative urgency used by the scheduler."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """A single pet-care task such as feeding, walking, or medication."""

    title: str
    duration_minutes: int
    priority: Priority
    pet_name: str
    task_type: str
    due_date: Optional[date] = None
    preferred_start: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_days: int = 0
    notes: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_due_date(self) -> Optional[date]:
        """Return the next due date for recurring tasks."""
        if not self.is_recurring or self.due_date is None or self.recurrence_days <= 0:
            return None
        return self.due_date + timedelta(days=self.recurrence_days)


@dataclass
class Pet:
    """Represents one pet profile and its task list."""

    name: str
    species: str
    age_years: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> bool:
        """Remove a task by title, returning True when removed."""
        for index, task in enumerate(self.tasks):
            if task.title == task_title:
                del self.tasks[index]
                return True
        return False


@dataclass
class Owner:
    """Represents the owner and configuration used by the scheduler."""

    name: str
    daily_time_budget_minutes: int
    preferences: Dict[str, str] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet profile to this owner."""
        self.pets.append(pet)

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return a pet by name if found."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None


@dataclass
class ScheduledItem:
    """A task placed on the plan with a concrete start time."""

    task: Task
    start_time: datetime


class Scheduler:
    """Builds a daily plan from owner, pets, and pending tasks."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def collect_pending_tasks(self) -> List[Task]:
        """Collect all incomplete tasks across all pets."""
        pending_tasks: List[Task] = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                if not task.completed:
                    pending_tasks.append(task)
        return pending_tasks

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority and due date for scheduling."""
        raise NotImplementedError

    def detect_conflicts(self, scheduled_items: List[ScheduledItem]) -> List[str]:
        """Detect overlaps or incompatible tasks in a proposed schedule."""
        raise NotImplementedError

    def build_daily_plan(self, target_date: date) -> List[ScheduledItem]:
        """Select and order tasks for a specific day."""
        raise NotImplementedError

    def explain_plan(self, scheduled_items: List[ScheduledItem]) -> str:
        """Produce human-readable reasoning for schedule decisions."""
        raise NotImplementedError