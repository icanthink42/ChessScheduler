p = int(input("Amount of players: "))

o = 0

for i in range(p):
    o += p - (i + 1)

print(f"{o} matches")
