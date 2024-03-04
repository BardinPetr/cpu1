# from random import randrange

from myhdl import *
from myhdl import _Signal

# from src.base import Clock
# from utils.runutils import run_sim
#
#
#
# @block
# def bench():
#     d, q, clk = [Signal(bool(0)) for _ in range(3)]
#
#     clock = Clock(clk, 10)
#
#     @always(clk.negedge)
#     def stimulus():
#         d.next = randrange(2)
#
#     return instances()
#
#
# if __name__ == "__main__":
#     inst = bench()
#     run_sim(inst, 1000, gtk_wave=True)


memory = [intbv(0) for _ in range(4)]

memory[0]= intbv(1)
print(memory)
memory[3]= intbv(2)
print(memory)
memory[2]= intbv(3)
print(memory)
memory[1]= intbv(4)
print(memory)

