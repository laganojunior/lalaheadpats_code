import random

def fill_time_sample(num_buckets, num_to_pick):
  still_unchosen = set(range(num_buckets))

  num_samples = 0
  while len(still_unchosen) > num_buckets - num_to_pick:
    chosen = random.randrange(num_buckets)
    if chosen in still_unchosen:
      still_unchosen.remove(chosen)

    num_samples += 1

  return num_samples

def get_predicted_prob(t, k, n, cache):
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


num_samples = 10000
num_buckets = 36
num_to_pick = 36
natural_draw_time_limit = 189

samples = {}

for _ in range(num_samples):
  sample_time = fill_time_sample(num_buckets, num_to_pick)

  if sample_time in samples:
    samples[sample_time] += 1
  else:
    samples[sample_time] = 1

sample_pairs = samples.items()
sample_pairs.sort(key = lambda e: e[0])

cache = {}

time_sum = 0
natural_draws = 0
for num_time, num_time_samples in sample_pairs:
  actual = num_time_samples * 1.0 / num_samples
  predicted = get_predicted_prob(num_buckets, num_to_pick, num_time, cache)
  print(num_time, num_time_samples, actual, predicted)

  time_sum += num_time * num_time_samples

  if num_time <= natural_draw_time_limit:
    natural_draws += num_time_samples

print("Average:", time_sum * 1.0 / num_samples)
print("Predicted Average:", sum([36.0/i for i in range(1, num_buckets+1)]))

prob_sum = 0
for i in range(num_buckets, natural_draw_time_limit + 1):
  prob_sum += get_predicted_prob(num_buckets, num_to_pick, i, cache)

print("Actual natural draw chance:", natural_draws * 1.0 / num_samples)
print("Predicted natural draw chance:", prob_sum)
