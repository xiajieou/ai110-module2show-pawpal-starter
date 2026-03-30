from datetime import date, datetime, timedelta
from typing import List

from pawpal_system import Owner, Pet, Priority, ScheduledItem, Scheduler, Task


def format_schedule(scheduler: Scheduler, schedule: List[ScheduledItem]) -> None:
    print("\n=== Today's Schedule ===")
    if not schedule:
        print("No tasks fit within today's constraints.")
        return

    for index, item in enumerate(schedule, start=1):
        # End time is derived from start + duration for clearer CLI output.
        end_time = item.start_time + timedelta(minutes=item.task.duration_minutes)
        print(
            f"{index}. {item.start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} | "
            f"{item.task.pet_name} | {item.task.title} | "
            f"{item.task.duration_minutes} min | {item.task.priority.value}"
        )

    print("\n" + scheduler.explain_plan(schedule))


def print_task_list(header: str, tasks: List[Task]) -> None:
    """Print a simple, readable task list for CLI verification."""
    print(f"\n=== {header} ===")
    if not tasks:
        print("No tasks found.")
        return

    for index, task in enumerate(tasks, start=1):
        time_text = task.preferred_start.strftime("%H:%M") if task.preferred_start else "--:--"
        print(
            f"{index}. {time_text} | {task.pet_name} | {task.title} | "
            f"completed={task.completed}"
        )


def print_warnings(warnings: List[str]) -> None:
    """Print warning lines returned by conflict detection."""
    if not warnings:
        print("\nNo time conflicts detected.")
        return

    print("\n=== Conflict Warnings ===")
    for warning in warnings:
        print(warning)


def main() -> None:
    owner = Owner(
        name="Jordan",
        daily_time_budget_minutes=90,
        preferences={"day_start_hour": "7"},
    )

    mochi = Pet(name="Mochi", species="dog", age_years=4)
    luna = Pet(name="Luna", species="cat", age_years=2)

    owner.add_pet(mochi)
    owner.add_pet(luna)

    today = date.today()

    # Added out of chronological order on purpose to validate sort_by_time.
    mochi.add_task(
        Task(
            title="Evening Medication",
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_name="Mochi",
            task_type="medication",
            due_date=today,
            preferred_start=datetime.combine(today, datetime.min.time()).replace(hour=18),
        )
    )
    mochi.add_task(
        Task(
            title="Morning Walk",
            duration_minutes=25,
            priority=Priority.HIGH,
            pet_name="Mochi",
            task_type="walk",
            due_date=today,
            preferred_start=datetime.combine(today, datetime.min.time()).replace(hour=7),
        )
    )
    luna.add_task(
        Task(
            title="Litter Box Cleanup",
            duration_minutes=15,
            priority=Priority.MEDIUM,
            pet_name="Luna",
            task_type="hygiene",
            due_date=today,
            preferred_start=datetime.combine(today, datetime.min.time()).replace(hour=8),
        )
    )
    luna.add_task(
        Task(
            title="Breakfast Feeding",
            duration_minutes=10,
            priority=Priority.MEDIUM,
            pet_name="Luna",
            task_type="feeding",
            due_date=today,
            preferred_start=datetime.combine(today, datetime.min.time()).replace(hour=7),
            is_recurring=True,
            frequency="daily",
        )
    )

    scheduler = Scheduler(owner)

    print_task_list("All Tasks (Unsorted)", owner.get_all_tasks())

    sorted_by_time = scheduler.sort_by_time(owner.get_all_tasks())
    print_task_list("Tasks Sorted by Time", sorted_by_time)

    mochi_pending = scheduler.filter_tasks(pet_name="Mochi", completed=False)
    print_task_list("Filtered: Mochi Pending Tasks", mochi_pending)

    recurring_task = next(
        task for task in owner.get_all_tasks() if task.title == "Breakfast Feeding"
    )
    next_instance = scheduler.mark_task_complete(recurring_task)
    if next_instance is not None:
        print(
            "\nRecurring task rollover created: "
            f"{next_instance.title} due {next_instance.due_date.isoformat()}"
        )

    exact_time_warnings = scheduler.detect_time_conflicts(owner.get_all_tasks())
    print_warnings(exact_time_warnings)

    schedule = scheduler.build_daily_plan(today)
    format_schedule(scheduler, schedule)

    overlap_warnings = scheduler.detect_conflicts(schedule)
    print_warnings(overlap_warnings)


if __name__ == "__main__":
    main()
