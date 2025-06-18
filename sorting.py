# Create two empty lists to store groups
awards = []
trophies = []

print("Enter your lines (press Enter twice to finish):")

# Read input lines until a blank line is entered
while True:
    line = input()
    if line.strip() == "":
        break
    if "-" in line:
        # Split on the first occurrence of ' - '
        award, trophy = line.split(" - ", 1)
        awards.append(award.strip())
        trophies.append(trophy.strip())
    else:
        print("Warning: No '-' found in line, skipping.")

# Print the grouped data
print("\nAward Titles:")
for award in awards:
    print(award)

print("\nTrophy Names:")
for trophy in trophies:
    print(trophy)
