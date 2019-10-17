import nashpy as nashpy
import numpy as np
import scipy as sp

def get_next_game_value(game, attacker_health, defender_health, swing_damage, next_turn, turns_left, cache_table):
  if swing_damage < 0:
    if -swing_damage >= attacker_health:
      return 0
    else:
      attacker_health = attacker_health + swing_damage
  elif swing_damage > 0:
    if swing_damage >= defender_health:
      return 1
    else:
      defender_health = defender_health - swing_damage

  if next_turn == "defender":
    [defender_health, attacker_health] = [attacker_health, defender_health] 

  if game == "switch":
    value = get_switch_value(attacker_health, defender_health, turns_left - 1, cache_table)
  elif game == "step_in":
    value = get_step_in_value(attacker_health, defender_health, turns_left - 1, cache_table)
  elif game == "minor_advantage":
    value = get_minor_advantage_value(attacker_health, defender_health, turns_left - 1, cache_table)
  else:
    raise f"Unknown game {game}"

  if next_turn == "attacker":
    return value
  else:
    return 1 - value

def check_cache_table(game, attacker_health, defender_health, turns_left, cache_table):
  # If the direct entry exists, just use it
  existing_val = cache_table.get((game, attacker_health, defender_health, turns_left))
  if existing_val is not None:
    return existing_val["value"]

  # If it seems that the (attacker, defender) pair has converged in respect to turn_left,
  # just short cut and use that value
#  if turns_left >= 10:
#    val1 = cache_table.get((game, attacker_health, defender_health, turns_left - 1))
#    val2 = cache_table.get((game, attacker_health, defender_health, turns_left - 2))
#
#    if val1 is not None and val2 is not None \
#       and val1["value"] == val2["value"] \
#       and np.array_equal(val1["row_strategy"], val2["row_strategy"]) \
#       and np.array_equal(val1["col_strategy"], val2["col_strategy"]):
#      print(f"Using converged solution {val1} for {(game, attacker_health, defender_health, turns_left)}")
#      cache_table[(game,attacker_health, defender_health, turns_left)] = val1
#
#      return val1["value"]

  return None


def get_step_in_payoffs(attacker_health, defender_health, turns_left, cache_table):
  # col strats: stand, duck, jab
  step_in_2_payoffs =  [ get_next_game_value('minor_advantage', attacker_health, defender_health, -50, 'defender', turns_left, cache_table),
                         get_next_game_value('minor_advantage', attacker_health, defender_health, 70, 'attacker', turns_left, cache_table),
                         get_next_game_value('minor_advantage', attacker_health, defender_health, 70, 'attacker', turns_left, cache_table)]
  step_in_3_payoffs =  [ get_next_game_value('switch', attacker_health, defender_health, 25, 'attacker', turns_left, cache_table),
                         get_next_game_value('minor_advantage', attacker_health, defender_health, -55, 'defender', turns_left, cache_table),
                         get_next_game_value('minor_advantage', attacker_health, defender_health, -5, 'defender', turns_left, cache_table) ]
  step_in_4_payoffs =  [ get_next_game_value('switch', attacker_health, defender_health, 0, 'defender', turns_left, cache_table),
                         get_next_game_value('switch', attacker_health, defender_health, 15, 'attacker', turns_left, cache_table),
                         get_next_game_value('switch', attacker_health, defender_health, 15, 'attacker', turns_left, cache_table) ]
  step_in_12_payoffs =  [ get_next_game_value('minor_advantage', attacker_health, defender_health, 0, 'attacker', turns_left, cache_table),
                          get_next_game_value('minor_advantage', attacker_health, defender_health, 20, 'attacker', turns_left, cache_table),
                          get_next_game_value('minor_advantage', attacker_health, defender_health, -40, 'defender', turns_left, cache_table) ]

  payoffs = np.array([
    step_in_2_payoffs,
    step_in_3_payoffs,
    step_in_4_payoffs,
    step_in_12_payoffs
  ])

  return payoffs

def get_step_in_value(attacker_health, defender_health, turns_left, cache_table):
  if turns_left == 0:
    if attacker_health < defender_health:
      return 0
    elif attacker_health > defender_health:
      return 1
    else:
      return 0.5

  existing_val = check_cache_table("step_in", attacker_health, defender_health, turns_left, cache_table)
  if existing_val is not None:
    return existing_val

  payoffs = get_step_in_payoffs(attacker_health, defender_health, turns_left, cache_table)
  print(f"Solve step in for {(attacker_health, defender_health, turns_left)}")
  print(payoffs)
  solution = solve_zero_sum_game(payoffs)
  print(f"Value is {solution['value']}")
  cache_table[("step_in", attacker_health, defender_health, turns_left)] = solution

  return solution["value"]

def get_switch_payoffs(attacker_health, defender_health, turns_left, cache_table):
  # col strats: stand, duck, jab, launch
  switch_1_payoffs = [get_next_game_value('switch', attacker_health, defender_health, 0, 'defender', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, -65, 'defender', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, 70, 'attacker', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, 70, 'attacker', turns_left, cache_table)]
  switch_2_payoffs = [get_next_game_value('switch', attacker_health, defender_health, 0, 'defender', turns_left, cache_table),
                      get_next_game_value('switch', attacker_health, defender_health, 15, 'attacker', turns_left, cache_table),
                      get_next_game_value('switch', attacker_health, defender_health, -5, 'defender', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, 70, 'attacker', turns_left, cache_table)]
  switch_3_payoffs = [get_next_game_value('minor_advantage', attacker_health, defender_health, 15, 'defender', turns_left, cache_table), # minus frames on hit
                      get_next_game_value('minor_advantage', attacker_health, defender_health, -50, 'defender', turns_left, cache_table),
                      get_next_game_value('switch', attacker_health, defender_health, -5, 'defender', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, 70, 'attacker', turns_left, cache_table)]
  switch_4_payoffs = [get_next_game_value('switch', attacker_health, defender_health, 0, 'defender', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, 20, 'attacker', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, -40, 'defender', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, 20, 'attacker', turns_left, cache_table)]
  step_in_payoffs  = [get_next_game_value('step_in', attacker_health, defender_health, 0, 'attacker', turns_left, cache_table),
                      get_next_game_value('step_in', attacker_health, defender_health, 0, 'attacker', turns_left, cache_table),
                      get_next_game_value('step_in', attacker_health, defender_health, 0, 'attacker', turns_left, cache_table),
                      get_next_game_value('minor_advantage', attacker_health, defender_health, -60, 'defender', turns_left, cache_table)]

  payoffs = np.array([
    switch_1_payoffs,
    switch_2_payoffs,
    switch_3_payoffs,
    switch_4_payoffs,
    step_in_payoffs
  ])

  return payoffs

def get_switch_value(attacker_health, defender_health, turns_left, cache_table):
  if turns_left == 0:
    if attacker_health < defender_health:
      return 0
    elif attacker_health > defender_health:
      return 1
    else:
      return 0.5

  existing_val = check_cache_table("switch", attacker_health, defender_health, turns_left, cache_table)
  if existing_val is not None:
    return existing_val

  payoffs = get_switch_payoffs(attacker_health, defender_health, turns_left, cache_table)
  print(f"Solve switch for {(attacker_health, defender_health, turns_left)}")
  print(payoffs)
  solution = solve_zero_sum_game(payoffs)
  print(f"Value is {solution['value']}")
  cache_table[("switch", attacker_health, defender_health, turns_left)] = solution

  return solution["value"]

def get_minor_advantage_payoffs(attacker_health, defender_health, turns_left, cache_table):
  # col strats: stand, jab, duck jab
  jab_payoffs = [get_next_game_value('minor_advantage', attacker_health, defender_health, 0, 'attacker', turns_left, cache_table),
                 get_next_game_value('switch', attacker_health, defender_health, 5, 'attacker', turns_left, cache_table),
                 get_next_game_value('switch', attacker_health, defender_health, -5, 'defender', turns_left, cache_table)]
  duck_payoffs = [get_next_game_value('minor_advantage', attacker_health, defender_health, 0, 'defender', turns_left, cache_table),
                  get_next_game_value('minor_advantage', attacker_health, defender_health, 0, 'attacker', turns_left, cache_table),
                  get_next_game_value('minor_advantage', attacker_health, defender_health, 50, 'attacker', turns_left, cache_table)]
  switch_payoffs = [get_next_game_value('switch', attacker_health, defender_health, 0, 'attacker', turns_left, cache_table),
                    get_next_game_value('switch', attacker_health, defender_health, -5, 'defender', turns_left, cache_table),
                    get_next_game_value('switch', attacker_health, defender_health, -5, 'defender', turns_left, cache_table)]

  payoffs = np.array([
    jab_payoffs,
    duck_payoffs,
    switch_payoffs
  ])

  return payoffs

def get_minor_advantage_value(attacker_health, defender_health, turns_left, cache_table):
  if turns_left == 0:
    if attacker_health < defender_health:
      return 0
    elif attacker_health > defender_health:
      return 1
    else:
      return 0.5

  existing_val = check_cache_table("minor_advantage", attacker_health, defender_health, turns_left, cache_table)
  if existing_val is not None:
    return existing_val

  payoffs = get_minor_advantage_payoffs(attacker_health, defender_health, turns_left, cache_table)
  print(f"Solve minor_advantage for {(attacker_health, defender_health, turns_left)}")
  print(payoffs)
  solution = solve_zero_sum_game(payoffs)
  print(f"Value is {solution['value']}")
  cache_table[("minor_advantage", attacker_health, defender_health, turns_left)] = solution

  return solution["value"]

def col_maximize(payoffs):
  # Solves a zero sum game for a column player given that the column player
  # is trying to maximize the payoff matrix.
  #
  # Taken from wikipedia article:
  # https://en.wikipedia.org/wiki/Zero-sum_game#Solving

  [num_rows, num_cols] = payoffs.shape

  # Make sure that the payoffs are positive
  # This doesn't affect the equilibrium since the payoffs are all
  # moving up by a constant. But the overall value of the game needs to
  # be adjusted back later
  adjustment = np.amin(payoffs) - 1
  payoffs = payoffs - adjustment * np.ones(payoffs.shape)

  # Choose vector u that minimizes sum(u) s.t:
  #   u_i >= 0 (equivalently -u_i <= 0)
  #   payoffs * u >= 1 (equivalently -payoffs * u <= -1)
  coeff = np.ones(num_cols)
  upper_bounds_zeros_coeffs = -np.eye(num_cols)
  upper_bounds_zeros_bounds = np.zeros(num_cols)
  upper_bounds_ones_coeffs  = -payoffs
  upper_bounds_ones_bounds = -np.ones(num_rows)

  upper_bounds_coeffs = np.concatenate((upper_bounds_zeros_coeffs, upper_bounds_ones_coeffs))
  upper_bounds_bounds = np.concatenate((upper_bounds_zeros_bounds, upper_bounds_ones_bounds))

  result = sp.optimize.linprog(coeff, A_ub = upper_bounds_coeffs, b_ub = upper_bounds_bounds)

  if result.success == False:
    raise f"No solution found for payoff matrix {col_maximize}"

  total_result_weights = np.sum(result.x)
  value = 1/total_result_weights + adjustment
  strategy = result.x / total_result_weights

  return {
    "value": value,
    "strategy": strategy
  }

def solve_zero_sum_game(payoffs):
  # My convention is that the row player is trying to maximize payoffs
  # Since the col_maximize function assumes the col player is trying to maximize payoffs instead:
  #  - negate the payoff matrix to get col player solution that minimizes original solution
  #  - transpose matrix to get row player solution so that the row player becomes the col player

  col_solution = col_maximize(-payoffs)
  row_solution = col_maximize(np.transpose(payoffs))

  return {
    "row_strategy": np.round(row_solution["strategy"], 3),
    "col_strategy": np.round(col_solution["strategy"], 3),
    "value": np.round(row_solution["value"], 3)
  }

cache_table = {}
get_minor_advantage_value(170, 170, 100, cache_table)

with open("results.txt", "w") as f:
  for ((game, attacker_health, defender_health, turns_left), solution) in cache_table.items():
    print("\t".join(np.concatenate((np.array([game, attacker_health, defender_health, turns_left, solution["value"]]), solution["row_strategy"], solution["col_strategy"])).tolist()), file=f)