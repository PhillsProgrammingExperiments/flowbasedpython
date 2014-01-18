#whole framework should be scirptable as well as runnable with start_fby script
#or something like that
import os
import time
import datetime
from fbpy.environment import JSONFile, FlowBasedEnvironment

THIS_DIR = os.path.realpath(os.path.dirname(__file__))

if __name__=="__main__":
    config = JSONFile(os.path.join(THIS_DIR, "config.json"))
    net = JSONFile(os.path.join(THIS_DIR, "net.json"))
    runtime = JSONFile(os.path.join(THIS_DIR, "runtime.json"))

    env = FlowBasedEnvironment(config, net, runtime)
    env.set_up()
    env.up()
    print("started at", datetime.datetime.utcnow())
    time.sleep(60)
    print("sleep finished at", datetime.datetime.utcnow())
    env.down()