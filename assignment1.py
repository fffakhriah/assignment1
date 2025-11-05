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
st.title("📺 TV Program Scheduling Optimizer")
st.write("This app uses a Genetic Algorithm to find the best TV schedule based on ratings.")

# Use local file path (same folder as main.py)
file_path = "program_ratings.csv"  # 👈 make sure this CSV is in the same directory

program_ratings_dict = read_csv_to_dict(file_path)

if not program_ratings_dict:
    st.warning("⚠️ No data found in the CSV file or file not found.")
    st.stop()

ratings = program_ratings_dict
GEN = st.slider("Generations", 10, 500, 100)
POP = st.slider("Population Size", 10, 200, 50)
CO_R = 0.8
MUT_R = 0.2
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
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2


def mutate(schedule):
    if len(schedule) == 0:
        return schedule
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule


def initialize_population(pop_size, programs, time_slots):
    population = []
    for _ in range(pop_size):
        schedule = random.choices(programs, k=len(time_slots))
        population.append(schedule)
    return population


def genetic_algorithm(generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
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

        population = new_population

    best_schedule = max(population, key=fitness_function)
    return best_schedule


if st.button("🚀 Run Genetic Algorithm"):
    best_schedule = genetic_algorithm()
    total_rating = fitness_function(best_schedule)

    st.success("✅ Optimal Schedule Found!")
    st.table({
        "Time Slot": [f"{t:02d}:00" for t in all_time_slots],
        "Program": best_schedule
    })
    st.write(f"**Total Ratings:** {total_rating:.2f}")
