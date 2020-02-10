with open("./questions-formatted.csv", "r") as f:
    lines = f.readlines()
    print(lines)

with open("./output.csv", "w") as out:
    for line in lines:
        if line.startswith("\"") and line[1].islower():
            out.write(line[0] + line[1].upper() + line[2:])
        elif line[0].islower():
            out.write(line[0].upper() + line[1:])
        else:
            out.write(line)