# a = {
#     'file_a': {
#         'a': 1,
#         'b': 2
#     }
# }

# b = {
#     'file_b': {
#         'c': 3,
#         'd': 4
#     }
# }

# f = {}
# f.update(**a, **b)

# print(f)

import re


def test(test):
    return test


a = "error: 1,2,3,4,5,6,7,8,9,10"

if len(a) > 0:
    print(f"Error report: {a}")


def extract_floats(value):
    return [
        float(x.replace(',', '.'))
        for x in re.findall(r'-?\d+(?:,\d+)?', value)
    ]


# print(extract_floats("The values are."))  # Example usage


