from random import randrange

from myhdl import *
from myhdl import _Signal

from utils.runutils import run_sim


@block
def Trig(d, q, clk):
    @always(clk.posedge)
    def run():
        q.next = d

    return run


@block
def Clock(clk: _Signal, period: int):
    @always(delay(period))
    def run():
        clk.next = not clk

    return run


@block
def Counter(clk: _Signal, num: _Signal):
    @always(clk.posedge)
    def run():
        if num >= 10:
            num.next = 0
        else:
            num.next = num + 1

    return run


@block
def bench():
    d, q, clk = [Signal(bool(0)) for _ in range(3)]

    num = Signal(intbv(0, 0, 1000))
    clock = Clock(clk, 10)
    trig = Trig(d, q, clk)
    cntr = Counter(clk, num)

    @always(clk.negedge)
    def stimulus():
        d.next = randrange(2)

    return trig, clock, stimulus, cntr


if __name__ == "__main__":
    inst = bench()
    run_sim(inst, 1000, gtk_wave=True)
