def find_duplicates(items):
    seen = {}
    duplicates = []

    for x in items:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                duplicates.append(x)
            seen[x] += 1

    return duplicates


def flatten(t):
    return [item for sublist in t for item in sublist]
   

# todo try_int should have no concept of console!
def try_int(text, verbose=False, console=None):
    try:
        return int(text)
    except ValueError:
        if verbose:
            console.print(f'Failed to parse "{text}" to int in requirement ID!', highlight=False)

        return None