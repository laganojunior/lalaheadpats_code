counts_by_sample_length = {}
total = 0

for line in open("samples.txt"):
  parts = line.strip().split("\t")
  sample = parts[1:]
  sample_length = int(parts[0])
  total += 1

  unique_so_far = set()
  last_unique_draw_time = None

  for i, s in enumerate(sample):
    if s not in unique_so_far:
      last_unique_draw_time = i + 1
      unique_so_far.add(s)

  if sample_length not in counts_by_sample_length:
    counts_by_sample_length[sample_length] = {
      "exact": [0] * (sample_length + 1),
      "loose": []
    }

    for i in range(sample_length + 1):
      counts_by_sample_length[sample_length]["loose"].append([0] * (sample_length + 1))

  if last_unique_draw_time == sample_length:
    counts_by_sample_length[sample_length]["exact"][len(unique_so_far)] += 1
  else:
    counts_by_sample_length[sample_length]["loose"][len(unique_so_far)][last_unique_draw_time] += 1
  

sample_counts_array = counts_by_sample_length.items()
sample_counts_array.sort(key = lambda l: l[0])

for sample_length, counts in sample_counts_array:
  for num_unique, count in enumerate(counts["exact"]):
    if count > 0:
      print "exact_{}_{}\t{}\t{}".format(sample_length, num_unique, count, float(count)/total)
  for num_unique, draw_time_counts in enumerate(counts["loose"]):
    for draw_time, count in enumerate(draw_time_counts):
      if count > 0:
        print "loose_{}_{}_{}\t{}\t{}".format(sample_length, num_unique, draw_time, count, float(count)/total)