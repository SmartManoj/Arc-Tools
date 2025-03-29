import numpy as np

def keep_border_values(data, background_color):
    # Create a new matrix with zeros
    result = [[background_color for _ in range(len(data[0]))] for _ in range(len(data))]

    # keep border values
    for i in range(len(data)):
        result[i][0] = data[i][0]
        result[i][-1] = data[i][-1]
        result[0][i] = data[0][i]
        result[-1][i] = data[-1][i]

    return result

def remove_duplicate_values(data, background_color):
    result = [[background_color for _ in range(len(data[0]))] for _ in range(len(data))]
    # Keep track of seen values
    # add corners to seen values
    seen_values = set()
    seen_values.add(data[0][0])
    seen_values.add(data[0][-1])
    seen_values.add(data[-1][0])
    seen_values.add(data[-1][-1])
    result[0][0] = data[0][0]
    result[0][-1] = data[0][-1]
    result[-1][0] = data[-1][0]
    result[-1][-1] = data[-1][-1]

    # Copy values, replacing second and subsequent occurrences with 0
    for i in range(len(data)):
        for j in range(len(data[0])):
            current_value = data[i][j]
            if current_value not in seen_values:
                result[i][j] = current_value
                seen_values.add(current_value)

    return result

def squash_grid(data, background_color):
    data= keep_border_values(data, background_color)
    data = remove_duplicate_values(data, background_color)
    # pprint(data)
    data = np.array(data)
    top_border = [i for i in data[0] if i != background_color]
    bottom_border = [i for i in data[-1] if i != background_color]
    left_border = [i for i in data[:,0][1:-1] if i != background_color]
    right_border = [i for i in data[:, -1][1:-1] if i != background_color]
    from itertools import chain
    return [*top_border, *chain.from_iterable(zip(left_border, right_border)), *bottom_border]


