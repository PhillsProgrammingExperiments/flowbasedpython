from fbpy.node_interface import Node


class ProcessingNode(Node):
    def pull(self):
        self.data = self.input[0].get()

    def body(self):
        self.data = self.data*2

    def push(self):
        self.output[0].put(self.data)
