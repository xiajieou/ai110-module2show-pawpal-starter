from datetime import date, datetime, timedelta

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def test_task_mark_complete_changes_status() -> None:
    task = Task(
        title="Give medication",
        duration_minutes=5,
        priority=Priority.HIGH,
        pet_name="Mochi",
        task_type="medication",
    )

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Luna", species="cat", age_years=2)
    before_count = len(pet.tasks)

    pet.add_task(
        Task(
            title="Feeding",
            duration_minutes=10,
            priority=Priority.MEDIUM,
            pet_name="Luna",
            task_type="feeding",
        )
    )

    assert len(pet.tasks) == before_count + 1


def test_sort_and_filter_tasks() -> None:
    owner = Owner(name="Jordan", daily_time_budget_minutes=120)
    mochi = Pet(name="Mochi", species="dog", age_years=4)
    luna = Pet(name="Luna", species="cat", age_years=2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    today = date.today()
    mochi.add_task(
        Task(
            title="Late Walk",
            duration_minutes=20,
            priority=Priority.HIGH,
            pet_name="Mochi",
            task_type="walk",
            preferred_start=datetime.combine(today, datetime.min.time()).replace(hour=18),
        )
    )
    mochi.add_task(
        Task(
            title="Early Walk",
            duration_minutes=20,
            priority=Priority.HIGH,
            pet_name="Mochi",
            task_type="walk",
            preferred_start=datetime.combine(today, datetime.min.time()).replace(hour=7),
        )
    )
    luna.add_task(
        Task(
            title="Feeding",
            duration_minutes=10,
            priority=Priority.MEDIUM,
            pet_name="Luna",
            task_type="feeding",
        )
    )

    scheduler = Scheduler(owner)

    sorted_titles = [task.title for task in scheduler.sort_by_time(owner.get_all_tasks())]
    assert sorted_titles[:2] == ["Early Walk", "Late Walk"]

    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi", completed=False)
    assert len(mochi_tasks) == 2


def test_mark_task_complete_creates_next_recurring_instance() -> None:
    owner = Owner(name="Jordan", daily_time_budget_minutes=120)
    pet = Pet(name="Mochi", species="dog", age_years=4)
    owner.add_pet(pet)
    today = date.today()

    recurring_task = Task(
        title="Daily Medication",
        duration_minutes=5,
        priority=Priority.HIGH,
        pet_name="Mochi",
        task_type="medication",
        due_date=today,
        is_recurring=True,
        frequency="daily",
    )
    pet.add_task(recurring_task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(recurring_task)

    assert recurring_task.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)


def test_detect_time_conflicts_warns_on_exact_time_match() -> None:
    owner = Owner(name="Jordan", daily_time_budget_minutes=120)
    pet = Pet(name="Mochi", species="dog", age_years=4)
    owner.add_pet(pet)
    today = date.today()

    task_one = Task(
        title="Walk",
        duration_minutes=20,
        priority=Priority.MEDIUM,
        pet_name="Mochi",
        task_type="walk",
        preferred_start=datetime.combine(today, datetime.min.time()).replace(hour=9),
    )
    task_two = Task(
        title="Feeding",
        duration_minutes=10,
        priority=Priority.MEDIUM,
        pet_name="Mochi",
        task_type="feeding",
        preferred_start=datetime.combine(today, datetime.min.time()).replace(hour=9),
    )

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_time_conflicts([task_one, task_two])

    assert warnings


def test_build_daily_plan_returns_empty_for_pet_with_no_tasks() -> None:
    owner = Owner(name="Jordan", daily_time_budget_minutes=120)
    owner.add_pet(Pet(name="Mochi", species="dog", age_years=4))
    scheduler = Scheduler(owner)

    assert scheduler.build_daily_plan(date.today()) == []


def test_weekly_recurrence_due_only_on_matching_day() -> None:
    task = Task(
        title="Weekly Grooming",
        duration_minutes=30,
        priority=Priority.MEDIUM,
        pet_name="Mochi",
        task_type="grooming",
        due_date=date(2026, 3, 23),
        is_recurring=True,
        frequency="weekly",
    )

    assert task.is_due_on(date(2026, 3, 30)) is True
    assert task.is_due_on(date(2026, 3, 31)) is False
