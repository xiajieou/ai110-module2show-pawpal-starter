import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)


def get_or_create_owner() -> Owner:
    """Return a persisted Owner object from session state."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(
            name="Jordan",
            daily_time_budget_minutes=90,
            preferences={"day_start_hour": "7"},
        )
    return st.session_state.owner


owner = get_or_create_owner()

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner Settings")
owner.name = st.text_input("Owner name", value=owner.name)
owner.daily_time_budget_minutes = st.number_input(
    "Daily time budget (minutes)", min_value=15, max_value=600, value=owner.daily_time_budget_minutes
)

st.divider()

st.subheader("Add Pet")
new_pet_name = st.text_input("Pet name")
new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="pet_species")
new_pet_age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    if not new_pet_name.strip():
        st.error("Please enter a pet name.")
    elif owner.get_pet(new_pet_name.strip()) is not None:
        st.error("A pet with that name already exists.")
    else:
        owner.add_pet(
            Pet(
                name=new_pet_name.strip(),
                species=new_pet_species,
                age_years=int(new_pet_age),
            )
        )
        st.success(f"Added pet: {new_pet_name.strip()}")

if owner.pets:
    st.markdown("### Your Pets")
    st.table(
        [
            {
                "name": pet.name,
                "species": pet.species,
                "age_years": pet.age_years,
                "task_count": len(pet.tasks),
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets added yet. Add one above.")

st.divider()

st.subheader("Add Task")
if not owner.pets:
    st.warning("Add a pet before creating tasks.")
else:
    pet_names = [pet.name for pet in owner.pets]
    task_pet_name = st.selectbox("Assign to pet", pet_names)
    task_title = st.text_input("Task title", value="Morning walk")
    task_type = st.text_input("Task type", value="walk")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        selected_pet = owner.get_pet(task_pet_name)
        if selected_pet is None:
            st.error("Selected pet was not found.")
        elif not task_title.strip():
            st.error("Please enter a task title.")
        else:
            priority = {
                "low": Priority.LOW,
                "medium": Priority.MEDIUM,
                "high": Priority.HIGH,
            }[priority_label]
            selected_pet.add_task(
                Task(
                    title=task_title.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    pet_name=selected_pet.name,
                    task_type=task_type.strip() or "general",
                )
            )
            st.success(f"Added task '{task_title.strip()}' to {selected_pet.name}")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.markdown("### Current Tasks")
    st.table(
        [
            {
                "pet": task.pet_name,
                "title": task.title,
                "type": task.task_type,
                "duration": task.duration_minutes,
                "priority": task.priority.value,
                "completed": task.completed,
            }
            for task in all_tasks
        ]
    )

st.divider()

st.subheader("Build Schedule")
st.caption("Generate today's schedule from your persisted pets and tasks.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    schedule = scheduler.build_daily_plan(target_date=date.today())

    if not schedule:
        st.info("No tasks were scheduled for today.")
    else:
        st.success("Today's schedule generated.")
        st.table(
            [
                {
                    "start": item.start_time.strftime("%H:%M"),
                    "pet": item.task.pet_name,
                    "task": item.task.title,
                    "duration": item.task.duration_minutes,
                    "priority": item.task.priority.value,
                }
                for item in schedule
            ]
        )
        st.text(scheduler.explain_plan(schedule))
