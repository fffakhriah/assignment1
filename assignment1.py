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
st.write("This app uses a Genetic Algorithm to find the best TV schedule based on program ratings.")

# Use your modified CSV file
file_path = "program_ratings_modified.csv"
program_ratings_dict = read_csv_to_dict(file_path)

if not program_ratings_dict:
    st.warning("⚠️ No data found in the CSV file or file not found.")
    st.stop()

ratings = program_ratings_dict

# ========================================
# LAYOUT: KIRI untuk input, KANAN untuk result
# ========================================
col_left, col_right = st.columns([1, 2])

# --------------------
# Kiri: parameter input
# --------------------
with col_left:
    st.header("⚙️ Parameters")
    GEN = st.selectbox(
        "Generations",
        options=[10, 50, 100, 200, 300, 400, 500],
        index=2
    )
    POP = st.selectbox(
        "Population Size",
        options=[10, 20, 50, 100, 150, 200],
        index=2
    )

    # Add sliders for Crossover & Mutation Rate
    CO_R = st.slider(
        "Crossover Rate (CO_R)",
        min_value=0.0,
        max_value=0.95,
        value=0.8,
        step=0.05
    )

    MUT_R = st.slider(
        "Mutation Rate (MUT_R)",
        min_value=0.01,
        max_value=0.05,
        value=0.02,
        step=0.01
    )

    EL_S = 2
    run_button = st.button("🚀 Run Genetic Algorithm")

# --------------------
# Kanan: hasil (kotak biasa)
# --------------------
with col_right:
    st.header("🎯 Best Schedule Result")
    if run_button:
        with st.spinner("Running Genetic Algorithm..."):
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
                    population = new_population[:population_size]
                return max(population, key=fitness_function)

            best_schedule = genetic_algorithm(crossover_rate=CO_R, mutation_rate=MUT_R)
            total_rating = fitness_function(best_schedule)

        st.success("✅ Optimal Schedule Found!")

        # ==================== Display result ====================
        st.subheader("📅 Schedule Table")
        st.table({
            "Time Slot": [f"{t:02d}:00" for t in all_time_slots],
            "Program": best_schedule
        })

        st.subheader("🏆 Total Rating")
        st.write(f"**Total Ratings:** {total_rating:.2f}")

        st.info(f"Parameters used → Generations: {GEN}, Population: {POP}, CO_R: {CO_R}, MUT_R: {MUT_R}")
