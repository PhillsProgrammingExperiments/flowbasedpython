from collections import defaultdict
import importlib
import json
from multiprocessing import Queue
from whs.commons.patterns.flyweight import Flyweight

class Wrapper:
    def __call__(self):
        return self.dict

class JSONFile(Flyweight, Wrapper):
    def __init__(self, path):
        if not self._initialized:
            self.path = path
            with open(self.path) as f:
                self.dict = json.load(f)

    def __call__(self):
        return self.dict

class PureDict(Wrapper):
    def __call__(self, data):
        self.dict = data

class FlowBasedEnvironment:
    def __init__(self, config: Wrapper, net: Wrapper, runtime: Wrapper):
        self.config = config()
        self.net = net()
        self.runtime = runtime()

        self.load_configs()
        self.load_net()
        self.load_runtime()

    def load_configs(self):
        self.implementations = {}   #implementation name -> tuple(thread/process class, event class)
        for k, v in self.config["configs"].items():
            implementation = []
            for element in v:
                mod = importlib.import_module(element["module"])
                clz = getattr(mod, element["class"])
                implementation.append(clz)
            self.implementations[k] = tuple(implementation)

    def load_net(self):
        self.node_classes = {}  # type name -> class
        self.node_inputs = {}   # type name -> number of inputs
        self.node_outputs = {}  # type name -> number of outputs
        for k, v in self.net["types"].items():
            mod = importlib.import_module(v["module"])
            clz = getattr(mod, v["class"])
            self.node_classes[k] = clz
            self.node_inputs[k] = v["inputs"]
            self.node_outputs[k] = v["outputs"]

        self.node_types = {}    # var name -> type name
        self.node_instances = {}    # var name -> instance count
        for k, v in self.net["nodes"].items():
            self.node_types[k] = v["type"]
            self.node_instances[k] = v["instances"]

        self.edges = defaultdict(list)  # edge source (var name) -> list(edge dest (var name))
        for edge in self.net["edges"]:
            src = edge["src"]
            dest = edge["dest"]
            self.edges[src].append(dest)

    def load_runtime(self):
        self.node_implementations = {}  # var name -> implementation_name
        self.node_locals = {}           # var name -> locals dict
        for var, desc in self.runtime.items():
            self.node_implementations[var] = desc["implementation"]
            self.node_locals[var] = desc["locals"]

    def create_instances(self):
        self.instances = defaultdict(list)  # var name -> list of instances
        for var, type in self.node_types.items():
            instance_count = self.node_instances[var]
            clz = self.node_classes[type]
            for i in range(instance_count):
                instance = clz()
                self.instances[var].append(instance)
                #TODO: this will change, together with node interface
                instance.input_queues = list()
                instance.output_queues = list()

    def create_connections(self):
        self.queues = {} # tuple(source var name, dest var name) -> queue
        for src, dests in self.edges.items():
            for dest in dests:
                #TODO: it should depend on config field, together with things like process/thread and event
                self.queues[src, dest] = Queue()

    def connect(self):
        for src, dest in self.queues:
            for instance in self.instances[src]:
                instance.output_queues.append(self.queues[src, dest])
            for instance in self.instances[dest]:
                instance.input_queues.append(self.queues[src, dest])

    def set_up(self):
        self.create_instances()
        self.create_connections()
        self.connect()

    def up(self):
        for var in self.instances:
            imp = self.implementations[self.node_implementations[var]]
            for instance in self.instances[var]:
                instance.up(imp)

    def down(self):
        for var in self.instances:
            for instance in self.instances[var]:
                instance.down()