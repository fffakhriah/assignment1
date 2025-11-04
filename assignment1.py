# save as ga_tv_scheduler.py and run with: python ga_tv_scheduler.py
import csv
import random
import pandas as pd
from pprint import pprint

# ---------- SETTINGS ----------
CSV_PATH = "C:/Users/User/Desktop/COMPUTER EOLUTION"  # change to your file path
HOUR_COLUMNS = [f"Hour {h}" for h in range(6, 24)]  # Hour 6..Hour 23 inclusive
GENERATIONS = 200
POPULATION_SIZE = 100
ELITISM_SIZE = 4
TOURNAMENT_SIZE = 2
# -------------------------------

def read_ratings(csv_path):
    df = pd.read_csv(csv_path)
    # ensure columns match hours
    missing = [c for c in HOUR_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing hour columns: {missing}")
    programs = list(df.iloc[:,0])  # first column assumed program name
    ratings = {}
    for idx, prog in enumerate(programs):
        row = df.loc[idx, HOUR_COLUMNS].astype(float).tolist()
        ratings[str(prog)] = row
    return ratings, programs

# fitness: sum of ratings per hour for schedule (schedule length = num_slots)
def fitness_function(schedule, ratings):
    total = 0.0
    for slot_idx, program in enumerate(schedule):
        total += ratings[program][slot_idx]
    return total

# initialize population: random schedules (program chosen for each hour, repeats allowed)
def init_population(programs, num_slots, pop_size):
    population = []
    for _ in range(pop_size):
        schedule = [random.choice(programs) for _ in range(num_slots)]
        population.append(schedule)
    return population

# tournament selection
def tournament_selection(population, ratings, k=TOURNAMENT_SIZE):
    candidates = random.sample(population, k)
    candidates.sort(key=lambda s: fitness_function(s, ratings), reverse=True)
    return candidates[0]

# single point crossover
def crossover(parent1, parent2):
    if len(parent1) <= 1:
        return parent1.copy(), parent2.copy()
    point = random.randint(1, len(parent1)-1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

# mutation: with certain probability per gene replace program with random program
def mutate(schedule, programs, mutation_rate):
    new = schedule.copy()
    for i in range(len(new)):
        if random.random() < mutation_rate:
            new[i] = random.choice(programs)
    return new

def evolve(ratings, programs, num_slots,
           generations=GENERATIONS,
           pop_size=POPULATION_SIZE,
           crossover_rate=0.8,
           mutation_rate=0.02,
           elitism_size=ELITISM_SIZE):
    # init
    population = init_population(programs, num_slots, pop_size)
    for gen in range(generations):
        # evaluate & sort
        population.sort(key=lambda s: fitness_function(s, ratings), reverse=True)
        new_pop = population[:elitism_size]  # elitism
        # generate offspring
        while len(new_pop) < pop_size:
            parent1 = tournament_selection(population, ratings)
            parent2 = tournament_selection(population, ratings)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            child1 = mutate(child1, programs, mutation_rate)
            child2 = mutate(child2, programs, mutation_rate)
            new_pop.append(child1)
            if len(new_pop) < pop_size:
                new_pop.append(child2)
        population = new_pop
    # final sort and return best
    population.sort(key=lambda s: fitness_function(s, ratings), reverse=True)
    best = population[0]
    best_score = fitness_function(best, ratings)
    return best, best_score

def schedule_to_table(schedule, all_hours):
    rows = []
    for i, prog in enumerate(schedule):
        hour = all_hours[i]
        rows.append({"Hour": hour, "Program": prog})
    return pd.DataFrame(rows)

def run_three_trials(csv_path, param_sets, generations=GENERATIONS, pop_size=POPULATION_SIZE):
    ratings, programs = read_ratings(csv_path)
    num_slots = len(HOUR_COLUMNS)
    all_hours = [f"{h}:00" for h in range(6, 24)]
    results = []
    for idx, (co_r, mut_r) in enumerate(param_sets, start=1):
        print(f"\n=== Trial {idx} (CO_R={co_r}, MUT_R={mut_r}) ===")
        best_sched, best_score = evolve(ratings, programs, num_slots,
                                        generations=generations,
                                        pop_size=pop_size,
                                        crossover_rate=co_r,
                                        mutation_rate=mut_r,
                                        elitism_size=ELITISM_SIZE)
        df_table = schedule_to_table(best_sched, all_hours)
        print(df_table.to_string(index=False))
        print("Total Score (fitness):", round(best_score, 4))
        # Save CSV of schedule for that trial
        df_table.to_csv(f"best_schedule_trial_{idx}.csv", index=False)
        results.append({"trial": idx, "co_r": co_r, "mut_r": mut_r, "score": best_score, "schedule_df": df_table})
    return results

if __name__ == "__main__":
    # Example parameter sets for 3 trials (you can change)
    param_sets = [
        (0.8, 0.02),
        (0.9, 0.04),
        (0.7, 0.01)
    ]
    results = run_three_trials(CSV_PATH, param_sets,
                               generations=GENERATIONS,
                               pop_size=POPULATION_SIZE)
    # Print summary
    print("\nSummary of 3 trials:")
    for r in results:
        print(f"Trial {r['trial']}: CO_R={r['co_r']}, MUT_R={r['mut_r']}, Score={round(r['score'],4)}")
