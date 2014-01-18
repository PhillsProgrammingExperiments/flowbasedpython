from collections import defaultdict
from multiprocessing import Process, Event
from threading import Thread


class Node:

    amounts = defaultdict(lambda *args: 0)    #subclass -> number of instances
    #TODO: probably doable with reference counting
    #also, I dont remember how many args should factory take

    def __init__(self):
        self.number = Node.amounts[type(self)]
        Node.amounts[type(self)] += 1

    #FRAMEWORK-PROVIDED

    @property
    def input(self):
        '''
        Should return object that when subscritped will return input queue for
        given index
        '''
        #TODO: this is naive and unsafe implementation, this should be view
        return self.input_queues

    @property
    def output(self):
        '''
        Should return object that when subscritped will return output queue for
        given index
        '''
        #TODO: this is naive and unsafe implementation, this should be view
        return self.output_queues

    @property
    def locals(self):
        '''
        Should returned dictionary defined in runtime.json
        '''
        #TODO: this is naive and unsafe implementation, this should be view
        return self.locals_dict

    def skip(self):
        '''
        Should skip to the next cycle.
        '''
        #TODO: how do we implement this?

    #HOOKS TO OVERRIDE

    def pull(self):
        '''
        In this method we should obtain data from inputs and save them for further
        processing
        '''

    def body(self):
        '''
        This method should have no communication with outside world, it should
        only manipulate data stored in self.
        '''

    def push(self):
        '''
        This method should send data into appropriate output queue, no processing
        should be performed here.
        '''

    #INTERNALS
    #TODO: move those to AbstractNode or something like that

    def _name(self):
        return "%s-%s" % (type(self).__name__, self.number)

    def _target(self, stop_event):
         while not stop_event.is_set():
             self.pull()
             self.body()
             self.push()

    def up(self, implementation: (Thread or Process, Event)):
        self.stop_event = implementation[1]()
        self.worker = implementation[0](name=self._name(), target=self._target, args=(self.stop_event, ))
        self.worker.start()

    def down(self):
        self.stop_event.set()