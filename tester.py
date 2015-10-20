from bcc import BPF
import time
import sys
import argparse

parser = argparse.ArgumentParser(description = "Notifier usage\nex) sudo python tester.py --event task.create --condition \"count > 1\" --time 10")
parser.add_argument("--event", type=str, default=None, help = "the kind of event that you want notify")
parser.add_argument("--condition", type=str, default=None, help = "the condition expression you want to notify that moment")
parser.add_argument("--time", type=int, default=5, help = "timeout second")
args = parser.parse_args()

if args.event:
    event = args.event
    print ("event: %s" % (event))
if args.condition:
    expr = args.condition
    print ("condition expression: %s" % (expr))
if args.time:
    interval = args.time
    print ("timeout: %u" % (interval))

def print_map():
    map_name = EVENT_LIST[event][3] + "_map"
    for k,v in b[map_name].items():
        print ("total count : %u" % (v.count))
        #print ("total size : %u" % (v.size))
    exit()


def call_back (pid, call_chain):
    print "The event happened"
    print_map()

if len(sys.argv) == 1:
    print " "
    exit()

EVENT_LIST = {
        "task.create" : ["task/task_create.c", "_do_fork", "task_create_begin", "task_create"],
        "task.exit" : ["task/task_exit.c", "do_exit", "task_exit_begin", "task_exit"],
        "task.switch" : ["task/task_switch.c", "finish_task_switch", "task_switch_begin", "task_switch"],
        "memory.alloc" : ["memory/memory_alloc.c", "__kmalloc", "memory_alloc_begin", "memory_alloc"],
        "memory.free" : ["memory/memory_free.c", "kfree", "memory_free_begin", "memory_free"],
        "memory.alloc_page" : ["memory/memory_alloc_page.c", "__alloc_pages_nodemask", "memory_alloc_page_begin", "memory_alloc_page"],
        "memory.free_page" : ["memory/memory_free_page.c", "__free_pages_ok", "memory_free_page_begin", "memory_free_page", "free_hot_cold_page", "memory_free_page_order_zero_begin"]
        }

with open(EVENT_LIST[event][0], 'r') as f:
    cfile = f.read()

rep = "EXPRESSION"
bpf_code = cfile.replace(rep, expr)

b = BPF(text = bpf_code, cb = call_back, debug=0)
b.attach_kprobe(event = EVENT_LIST[event][1], fn_name = EVENT_LIST[event][2])
#if event == "memory.free_page":
#    b.attach_kprobe(event = EVENT_LIST[event][4], fn_name = EVENT_LIST[event][5])

interval = interval * 1000
b.kprobe_poll(timeout = interval)

print_map()

exit()
