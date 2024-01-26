class Filter:
    def __init__(self, b, a):
        self.b = b
        self.a = a
        self.order = len(b) - 1
        self.x = [0] * (self.order + 1)  # Input history
        self.y = [0] * (self.order + 1)  # Output history

    def filter(self, new_sample):
        # Update input history
        self.x = [new_sample] + self.x[:-1]

        # Apply the filter
        new_y = sum(bi * xi for bi, xi in zip(self.b, self.x)) - sum(ai * yi for ai, yi in zip(self.a[1:], self.y[:-1]))

        # Update output history
        self.y = [new_y] + self.y[:-1]

        return new_y





