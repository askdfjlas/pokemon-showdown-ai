# Convert a .tsv file into a 2D array
def get_list(filename):
    rows = []
    data = open(filename)

    for line in data:
        arr = line.rstrip().split('\t')
        rows.append([el for el in arr])

    data.close()
    return rows


# Convert a .tsv file (with 2 columns) into a dictionary
def get_dict(filename):
    d = {}
    data = open(filename)

    for line in data:
        arr = line.rstrip().split('\t')
        d[arr[0]] = arr[1]

    data.close()
    return d


# Write a row to a .tsv file
def write_row(row, file):
    for i in range(len(row)):
        file.write(str(row[i]) + ('\n' if i == len(row) - 1 else '\t'))


# Testing
if __name__ == "__main__":
    print(get_list("../data/pokemon/RAW_POKEMON.tsv"))
