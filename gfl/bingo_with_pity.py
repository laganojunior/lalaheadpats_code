import random
import math

sample_file = open("samples.txt", "w")

def num_combinations(n, r):
  numer = 1
  denom = 1
  for i in range(1, r+1):
    numer *= n - i + 1
    denom *= i

  return numer/denom

def fill_time_sample(num_buckets, pity_threshold):
  still_unchosen = set(range(num_buckets))
  sample_path = []

  num_samples = 0
  pity_points = 0
  while len(still_unchosen) * pity_threshold > pity_points:
    chosen = random.randrange(num_buckets)
    if chosen in still_unchosen:
      still_unchosen.remove(chosen)
    else:
      pity_points += 1

    num_samples += 1
    sample_path.append(chosen)

  sample_file.write("{}\t{}\n".format(str(num_samples), "\t".join([str(i) for i in sample_path])))

  return num_samples

def get_predicted_prob(t, k, n, cache):
  if k < 0:
    return 0

  if k == 0:
    if t == 0:
      return 1
    else:
      return 0

  if t < k :
    return 0

  if k == 2:
    return ((1.0 / t) ** (n - 2)) * ((t-1) * 1.0) / t

  if (t, k, n) in cache:
    return cache[(t, k, n)]

  s = 0
  for m in range(2, n):
    s += get_predicted_prob(t, k-1, m, cache) * (((k - 1) * 1.0 / t) ** (n - m - 1)) * (t - k + 1) / t

  cache[(t, k, n)] = s

  return s


def get_predicted_prob_with_pity_last_repeat_number(t, k, n, pity_threshold, cache):
  if k == n or (n - t) % 9 != 0:
    return 0

  pity_pulls_used = (n - k) / 9
  natural_drawn = k - pity_pulls_used

  prob_sum = 0
  for exact_pull_time in range(natural_drawn, n):
    contrib = get_predicted_prob(t, natural_drawn, exact_pull_time, cache) * ((natural_drawn * 1.0 / t) ** (n - exact_pull_time))
#    print("last repeat prob sum contrib", n, k, natural_drawn, exact_pull_time, contrib)
    prob_sum += contrib

#  print("last repeat number sum", n, k, prob_sum)

  return prob_sum

def get_predicted_prob_with_pity_last_new_number(t, k, n, pity_threshold, cache):
  prob_sum = 0
  min_natural_drawn = int(math.ceil((pity_threshold * k - n) * 1.0 / (pity_threshold - 1)))
  max_natural_drawn_plus_one = min(int(math.ceil((pity_threshold * (k + 1) - n) * 1.0 / (pity_threshold - 1))), k + 1)
  for natural_drawn in range(min_natural_drawn, max_natural_drawn_plus_one):
    contrib = get_predicted_prob(t, natural_drawn, n, cache)
#    print("last new number prob sum contrib", n, k, natural_drawn, contrib)
    prob_sum += contrib

#  print("last new number sum", n, k, prob_sum)

  return prob_sum

def get_predicted_prob_with_pity(t, k, n, pity_threshold, cache):
  return get_predicted_prob_with_pity_last_new_number(t, k, n, pity_threshold, cache) + \
         get_predicted_prob_with_pity_last_repeat_number(t, k, n, pity_threshold, cache)

num_samples = 10000
num_buckets = 36
natural_draw_time_limit = 189
pity_threshold = 10

samples = {}

for _ in range(num_samples):
  sample_time = fill_time_sample(num_buckets, pity_threshold)

  if sample_time in samples:
    samples[sample_time] += 1
  else:
    samples[sample_time] = 1

sample_pairs = samples.items()
sample_pairs.sort(key = lambda e: e[0])

cache = {}

time_sum = 0
natural_draws = 0
predicted_avg = 0
for num_time, num_time_samples in sample_pairs:
  actual = num_time_samples * 1.0 / num_samples
  predicted = get_predicted_prob_with_pity(num_buckets, num_buckets, num_time, pity_threshold, cache)
  predicted_avg += predicted * num_time
  print(num_time, num_time_samples, actual, predicted)

  time_sum += num_time * num_time_samples

  if num_time <= natural_draw_time_limit:
    natural_draws += num_time_samples

print("Average:", time_sum * 1.0 / num_samples)
print("Predicted Average:", predicted_avg)

prob_sum = 0
for i in range(num_buckets, natural_draw_time_limit + 1):
  prob_sum += get_predicted_prob_with_pity(num_buckets, num_buckets, i, pity_threshold, cache)

print("Actual natural draw chance:", natural_draws * 1.0 / num_samples)
print("Predicted natural draw chance:", prob_sum)