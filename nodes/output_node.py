from fbpy.node_interface import Node


class OutputNode(Node):
    def pull(self):
        self.data = self.input[0].get()

    def body(self):
        pass

    def push(self):
        print("I got number", self.data)