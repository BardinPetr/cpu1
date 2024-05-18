from typing import List

from myhdl import *
from myhdl import _Signal, _ShadowSignal

from src.machine.utils.hdl import hdl_block
from src.machine.utils.introspection import introspect


@hdl_block
def Mux(inputs: List[_Signal], output: _Signal, ctrl: _Signal):
    """
    Asynchronous multiplexer with any number of ports.
    Sets output to 0 if ctrl value is out of inputs array range.
    TODO: signal arrays are incompatible with Verilog translation
    :param ctrl:   number of signal in input array
    :param output: output of selected input signal
    :param inputs: input signal array
    """
    if len(inputs) > ctrl.val.max:
        raise ValueError(f"{ctrl.val._nrbits}bit Mux got {len(inputs)} inputs")

    @always(ctrl, *inputs)
    def run():
        n = int(ctrl.val)
        if n >= len(inputs):
            output.next = 0
        else:
            output.next = inputs[n]

    return introspect()


@hdl_block
def DeMux(input: _Signal, outputs: List[_Signal], ctrl: _Signal):
    """
    Asynchronous demultiplexer with any number of ports.
    Sets to 0 all unused outputs. Ignores invalid ctrl.
    :param input:   input signal
    :param outputs: array of output signals to redirect input to
    :param ctrl:    id of output signal
    """
    if len(outputs) > ctrl.val.max:
        raise ValueError(f"{ctrl.val._nrbits}bit Demux got {len(outputs)} outputs")

    @always(ctrl, input)
    def run():
        n = int(ctrl.val)
        for i in range(len(outputs)):
            if isinstance(outputs[i], _ShadowSignal._TristateDriver):
                outputs[i].next = input if i == n else None
            else:
                outputs[i].next = input if i == n else 0

    return introspect()
