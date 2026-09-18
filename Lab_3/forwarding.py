locations = {
    "A": "B",
    "B": "C",
    "C": "D",
    "D": "192.168.1.50:5000"
}


def resolve(location):

    hops = 0

    while location in locations:

        print(
            "Following:",
            location,
            "->",
            locations[location]
        )

        location = locations[location]

        hops += 1

    return location, hops


address, hops = resolve("A")

locations["A"] = "B"
del locations["C"]

print("\nFinal location:")

address3, hops3 = resolve("A")

print("\nFinal value reached:", address3)
print("Number of Hops:", hops3)


