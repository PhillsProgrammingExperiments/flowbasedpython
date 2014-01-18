from fbpy.node_interface import Node

def gen():
    for i in range(100):
        yield i

inp_gen = gen()

class InputNode(Node):
    def pull(self):
        self.data = next(inp_gen)

    def body(self):
        try:
            self.data = int(self.data)
        except ValueError:
            self.skip()

    def push(self):
        self.output[0].put(self.data)