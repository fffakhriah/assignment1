import csv
import random
import os
import streamlit as st

# ==================== READ CSV ====================
def read_csv_to_dict(file_path):
    program_ratings = {}
    if not os.path.exists(file_path):
        st.error(f"❌ File not found at {file_path}")
        return program_ratings

    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                program = row[0]
                ratings = [float(x) for x in row[1:]]
                program_ratings[program] = ratings
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
    return program_ratings


# ==================== STREAMLIT UI ====================
st.set_page_config(page_title="TV Scheduling Optimizer", layout="wide")
st.title("📺 TV Program Scheduling Optimizer")
st.write("This app uses a Genetic Algorithm to find the best TV schedule based on ratings.")
st.divider()

# Load data
file_path = "program_ratings.csv"
program_ratings_dict = read_csv_to_dict(file_path)
if not program_ratings_dict:
    st.warning("⚠️ No data found in the CSV file or file not found.")
    st.stop()
ratings = program_ratings_dict

# Default constants
GEN = 100
POP = 50
EL_S = 2
all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))

# ==================== GA FUNCTIONS ====================
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot % len(ratings[program])]
    return total_rating

def crossover(schedule1, schedule2):
    if len(schedule1) < 3 or len(schedule2) < 3:
        return schedule1.copy(), schedule2.copy()
    cp = random.randint(1, len(schedule1)-2)
    child1 = schedule1[:cp] + schedule2[cp:]
    child2 = schedule2[:cp] + schedule1[cp:]
    return child1, child2

def mutate(schedule):
    if len(schedule) == 0:
        return schedule
    mp = random.randint(0, len(schedule)-1)
    schedule[mp] = random.choice(all_programs)
    return schedule

def initialize_population(pop_size, programs, time_slots):
    population = []
    for _ in range(pop_size):
        schedule = random.choices(programs, k=len(time_slots))
        population.append(schedule)
    return population

def genetic_algorithm(generations, population_size, crossover_rate, mutation_rate, elitism_size):
    population = initialize_population(population_size, all_programs, all_time_slots)
    for _ in range(generations):
        population.sort(key=lambda s: fitness_function(s), reverse=True)
        new_population = population[:elitism_size]
        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population[:10], k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)
            new_population.extend([child1, child2])
        population = new_population[:population_size]
    return max(population, key=fitness_function)


# ==================== THREE TRIALS SECTION ====================
st.header("🧪 Run 3 Trials")
st.write("Experiment with different Crossover and Mutation Rates to observe how they affect the results.")
st.divider()

for i in range(1, 4):
    st.subheader(f"🧩 Trial {i}")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        CO_R = st.slider(
            f"Trial {i} - Crossover Rate (CO_R)",
            min_value=0.0, max_value=0.95, value=0.8, step=0.05,
            key=f"co_{i}"
        )

    with col2:
        MUT_R = st.slider(
            f"Trial {i} - Mutation Rate (MUT_R)",
            min_value=0.01, max_value=0.05, value=0.02, step=0.01,
            key=f"mut_{i}"
        )

    with col3:
        run_trial = st.button(f"🚀 Run Trial {i}", key=f"run_{i}")

    if run_trial:
        with st.spinner(f"Running Genetic Algorithm for Trial {i}..."):
            best_schedule = genetic_algorithm(GEN, POP, CO_R, MUT_R, EL_S)
            total_rating = fitness_function(best_schedule)

        st.success(f"✅ Trial {i} Completed Successfully!")

        st.write(f"**Parameters Used:** CO_R = {CO_R}, MUT_R = {MUT_R}")
        st.table({
            "Time Slot": [f"{t:02d}:00" for t in all_time_slots],
            "Program": best_schedule
        })
        st.write(f"**Total Rating:** {total_rating:.2f}")
        st.divider()
