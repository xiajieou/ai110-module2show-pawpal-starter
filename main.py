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

    scheduler = Scheduler(owner)
    schedule = scheduler.build_daily_plan(today)
    format_schedule(scheduler, schedule)


if __name__ == "__main__":
    main()
