class CircularBuffer:
    def __init__(self, size):
        self.buffer = [0] * size
        self.size = size
        self.head = 0
        self.tail = 0
        self.count = 0

    def enqueue(self, item):
        if self.count == self.size:
            # Optionally handle full buffer
            return
        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.size
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            # Optionally handle empty buffer
            return None
        item = self.buffer[self.head]
        self.head = (self.head + 1) % self.size
        self.count -= 1
        return item

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self.size




