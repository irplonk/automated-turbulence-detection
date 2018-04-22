import csv

flights = open('Flights.csv', 'r')
reader = csv.reader(flights, delimiter=',')

total = 0
count = {}
conditional_total = {}
conditional_count = {}
codes = set()

for row in reader:
    origin = row[0]
    dest = row[1]
    codes.add(origin)
    codes.add(dest)

    total += 1

    if origin not in count:
        count[origin] = 1
    else:
        count[origin] += 1

    if origin not in conditional_total:
        conditional_total[origin] = 1
    else:
        conditional_total[origin] += 1

    if (origin, dest) not in conditional_count:
        conditional_count[(origin, dest)] = 1
    else:
        conditional_count[(origin, dest)] += 1

flights.close()

codes_sorted = sorted(list(codes))


counts = open('Origin_Counts.csv', 'w', newline='')
writer = csv.writer(counts, delimiter=',')

writer.writerow(['Origin', 'Count'])

for origin in codes_sorted:
    writer.writerow([origin, count[origin]])

counts.close()


probabilities = open('Origin_Probabilities.csv', 'w', newline='')
writer = csv.writer(probabilities, delimiter=',')

writer.writerow(['Origin', 'Probability'])

for origin in codes_sorted:
    writer.writerow([origin, count[origin] / total])

probabilities.close()


conditional_counts = open('Conditional_Counts.csv', 'w', newline='')
writer = csv.writer(conditional_counts, delimiter=',')

writer.writerow(['Origin/Destination'] + codes_sorted)

for origin in codes_sorted:
    writer.writerow([origin] + [conditional_count[(origin, dest)] if (origin, dest) in conditional_count else 0
                                for dest in codes_sorted])

conditional_counts.close()


conditional_probabilities = open(
    'Conditional_Probabilities.csv', 'w', newline='')
writer = csv.writer(conditional_probabilities, delimiter=',')

writer.writerow(['Origin/Destination'] + codes_sorted)

for origin in codes_sorted:
    writer.writerow([origin] + [conditional_count[(origin, dest)] / conditional_total[origin]
                                if (origin, dest) in conditional_count else 0 for dest in codes_sorted])

conditional_probabilities.close()
