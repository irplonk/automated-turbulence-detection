import csv
from .. import definitions


def airport_statistics():
    """Returns a tuple containing airport IATA codes, a dictionary containing their
    probabilities of being the origin of a flight, and their conditional probabilities
    for being the destination of a flight given the origin."""

    file = open(definitions.FLIGHTS_DIR, 'r')
    reader = csv.reader(file, delimiter=',')

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

    file.close()

    prob = {origin: count[origin] / total for origin in codes}

    conditional_prob = {origin: {dest: conditional_count[(origin, dest)] / conditional_total[origin]
                        if (origin, dest) in conditional_count else 0 for dest in codes} for origin in codes}

    return codes, prob, conditional_prob


def airport_info():
    """Returns a dictionary from an airport to its latitude, longitude, and altitude in meters."""
    file = open(definitions.AIRPORTS_DIR, 'r')
    reader = csv.reader(file, delimiter=',')
    airports = {row[0]: (float(row[1]), float(row[2]), float(row[3])) for row in reader}
    file.close()
    return airports
