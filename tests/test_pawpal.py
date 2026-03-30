from pawpal_system import Pet, Priority, Task


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
