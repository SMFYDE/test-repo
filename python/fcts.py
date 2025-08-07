"""
"""


class T:

    def __init__(self, x):
        self.x = x
        self.y = x + 1


l = [T(1), T(2), T(3)]

for obj in l:
    print(obj.x, obj.y)
