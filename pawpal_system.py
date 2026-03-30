"""PawPal+ backend system skeleton.

Phase 1 provides class structure and method stubs only.
Scheduling algorithms and full validation are implemented in later phases.
"""

from __future__ import annotations

from dataclasses import asdict
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
    frequency: str = "once"
    notes: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_due_date(self) -> Optional[date]:
        """Return the next due date for recurring tasks."""
        if not self.is_recurring or self.due_date is None:
            return None
        interval_days = self._recurrence_interval_days()
        if interval_days <= 0:
            return None
        return self.due_date + timedelta(days=interval_days)

    def _recurrence_interval_days(self) -> int:
        """Return the recurrence interval in days from frequency or explicit value."""
        if self.recurrence_days > 0:
            return self.recurrence_days

        normalized = self.frequency.strip().lower()
        if normalized == "daily":
            return 1
        if normalized == "weekly":
            return 7
        return 0

    def build_next_instance(self) -> Optional[Task]:
        """Create the next recurring task instance when this one is complete."""
        next_due = self.next_due_date()
        if next_due is None:
            return None

        data = asdict(self)
        data["due_date"] = next_due
        data["completed"] = False
        if self.preferred_start is not None:
            data["preferred_start"] = self.preferred_start + timedelta(
                days=self._recurrence_interval_days()
            )
        return Task(**data)

    def is_due_on(self, target_date: date) -> bool:
        """Return whether this task should be considered on a specific date."""
        if self.due_date is None:
            return True

        if not self.is_recurring:
            return self.due_date <= target_date

        interval_days = self._recurrence_interval_days()
        if interval_days <= 0:
            return self.due_date <= target_date

        if target_date < self.due_date:
            return False

        delta_days = (target_date - self.due_date).days
        return delta_days % interval_days == 0


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

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across every pet owned by this owner."""
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


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
        return [task for task in self.owner.get_all_tasks() if not task.completed]

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority and due date for scheduling."""
        priority_order = {
            Priority.HIGH: 0,
            Priority.MEDIUM: 1,
            Priority.LOW: 2,
        }

        def sort_key(task: Task) -> tuple[int, date, datetime, int]:
            due_value = task.due_date if task.due_date is not None else date.max
            preferred_value = (
                task.preferred_start
                if task.preferred_start is not None
                else datetime.max.replace(tzinfo=None)
            )
            return (
                priority_order.get(task.priority, 3),
                due_value,
                preferred_value,
                task.duration_minutes,
            )

        return sorted(tasks, key=sort_key)

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by preferred start time (HH:MM), placing unscheduled tasks last."""
        return sorted(
            tasks,
            key=lambda task: (
                task.preferred_start is None,
                task.preferred_start.strftime("%H:%M") if task.preferred_start else "99:99",
                task.title.lower(),
            ),
        )

    def filter_tasks(
        self,
        tasks: Optional[List[Task]] = None,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Filter tasks by pet name and/or completion status."""
        selected_tasks = tasks if tasks is not None else self.owner.get_all_tasks()
        filtered_tasks: List[Task] = []

        for task in selected_tasks:
            if pet_name is not None and task.pet_name.lower() != pet_name.lower():
                continue
            if completed is not None and task.completed != completed:
                continue
            filtered_tasks.append(task)

        return filtered_tasks

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and auto-create the next instance when recurring."""
        task.mark_complete()
        next_task = task.build_next_instance()
        if next_task is None:
            return None

        pet = self.owner.get_pet(task.pet_name)
        if pet is None:
            return None

        pet.add_task(next_task)
        return next_task

    def detect_time_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return warnings for tasks that share the exact same preferred start time."""
        warnings: List[str] = []
        sorted_tasks = sorted(
            [task for task in tasks if task.preferred_start is not None],
            key=lambda task: task.preferred_start,
        )

        for index in range(len(sorted_tasks) - 1):
            current_task = sorted_tasks[index]
            next_task = sorted_tasks[index + 1]

            if current_task.preferred_start == next_task.preferred_start:
                warnings.append(
                    "Warning: "
                    f"'{current_task.title}' ({current_task.pet_name}) and "
                    f"'{next_task.title}' ({next_task.pet_name}) both start at "
                    f"{current_task.preferred_start.strftime('%H:%M')}."
                )

        return warnings

    def detect_conflicts(self, scheduled_items: List[ScheduledItem]) -> List[str]:
        """Detect overlaps or incompatible tasks in a proposed schedule."""
        conflicts: List[str] = []
        ordered_items = sorted(scheduled_items, key=lambda item: item.start_time)

        for index in range(len(ordered_items) - 1):
            current_item = ordered_items[index]
            next_item = ordered_items[index + 1]
            current_end = current_item.start_time + timedelta(
                minutes=current_item.task.duration_minutes
            )

            if current_end > next_item.start_time:
                conflicts.append(
                    "Conflict: "
                    f"'{current_item.task.title}' for {current_item.task.pet_name} overlaps with "
                    f"'{next_item.task.title}' for {next_item.task.pet_name}."
                )

        return conflicts

    def _day_start(self, target_date: date) -> datetime:
        """Return the default start time for plan generation."""
        start_hour = int(self.owner.preferences.get("day_start_hour", "8"))
        start_hour = max(0, min(start_hour, 23))
        return datetime.combine(target_date, datetime.min.time()).replace(hour=start_hour)

    def build_daily_plan(self, target_date: date) -> List[ScheduledItem]:
        """Select and order tasks for a specific day."""
        pending_tasks = self.collect_pending_tasks()
        due_tasks = [task for task in pending_tasks if task.is_due_on(target_date)]
        sorted_tasks = self.sort_tasks(due_tasks)

        scheduled_items: List[ScheduledItem] = []
        minutes_used = 0
        current_time = self._day_start(target_date)

        for task in sorted_tasks:
            if minutes_used + task.duration_minutes > self.owner.daily_time_budget_minutes:
                continue

            start_time = current_time
            if (
                task.preferred_start is not None
                and task.preferred_start.date() == target_date
                and task.preferred_start > current_time
            ):
                start_time = task.preferred_start

            scheduled_items.append(ScheduledItem(task=task, start_time=start_time))
            minutes_used += task.duration_minutes
            current_time = start_time + timedelta(minutes=task.duration_minutes)

        return scheduled_items

    def explain_plan(self, scheduled_items: List[ScheduledItem]) -> str:
        """Produce human-readable reasoning for schedule decisions."""
        if not scheduled_items:
            return "No tasks scheduled today."

        lines: List[str] = ["Today's Schedule Rationale:"]
        for item in scheduled_items:
            lines.append(
                f"- {item.start_time.strftime('%H:%M')} | {item.task.pet_name}: {item.task.title} "
                f"({item.task.duration_minutes} min, {item.task.priority.value} priority)"
            )

        return "\n".join(lines)