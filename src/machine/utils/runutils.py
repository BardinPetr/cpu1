import os
from typing import Optional, Dict, Type

from myhdl import intbv, modbv, _Signal, Signal
from myhdl._ShadowSignal import _TristateSignal
from myhdl._block import _Block
from vcd.gtkw import GTKWSave, spawn_gtkwave_interactive, GTKWColor

from src.machine.utils.enums import CtrlEnum
from src.machine.utils.gtkwave import gtkwave_generate_translation
from src.machine.utils.introspection import BlockIntrospection, TraceData


def _insert_signal_block_classic(gtkw: GTKWSave, root: _Block, base_name: str = None):
    if not isinstance(root, _Block):
        return

    self_name = root.name
    name = f"{base_name}.{self_name}"
    if base_name is None:
        name = self_name

    with gtkw.group(self_name):
        for sig_name, sig in root.sigdict.items():
            trace_name = f"{name}.{sig_name}"
            if isinstance(sig.val, intbv | modbv):
                trace_name += f"[{sig.val._nrbits - 1}:0]"
            gtkw.trace(trace_name)

        for sub in root.subs:
            _insert_signal_block_classic(gtkw, sub, base_name=name)


def gtkw_update_traces(gtkw: GTKWSave, base: str, example: Dict[str, _Signal]):
    for name, sig in example.items():
        val = sig.val
        sig_len = len(sig)
        is_bool = sig_len == 1

        trace_name = f"{base}.{name}"
        trace_fmt = 'hex'
        trace_color = GTKWColor.green
        trace_translate_path = None

        if isinstance(sig, _TristateSignal):
            pass
        elif isinstance(val, intbv | modbv):
            pass

        if is_bool:
            trace_color = GTKWColor.red
            trace_fmt = 'bin'
        else:
            trace_name += f"[{sig_len - 1}:0]"

        if 'ctrl' in trace_name:
            trace_color = GTKWColor.orange

        enc: Type[CtrlEnum] = getattr(sig, 'encoding', None)
        if enc is not None:
            trace_translate_path = gtkwave_generate_translation(enc)

        gtkw.trace(trace_name, color=trace_color, datafmt=trace_fmt, translate_filter_file=trace_translate_path)


def _insert_signal_block(gtkw: GTKWSave, root: _Block, base_name: str, is_root: bool = False):
    intro: BlockIntrospection = root.introspection

    presentation_name = intro.name if intro.name is not None else intro.type
    name = f"{base_name}.{root.name}"

    with gtkw.group(presentation_name):
        traces = dict(
            sorted(
                filter(
                    lambda i: i[0] != 'clk' or is_root,
                    intro.signals.items()
                ),
                key=lambda x: x[0]
            )
        )

        gtkw_update_traces(gtkw, name, traces)

        for v in intro.modules.values():
            _insert_signal_block(gtkw, v, base_name=name)


def display_trace_vcd(build_dir: str, name: str, data: TraceData):
    data.as_vcd(f'{build_dir}/{name}.vcd')

    def _update(gtkw: GTKWSave):
        base = 'main'
        with gtkw.group(base):
            gtkw_update_traces(
                gtkw, base,
                {k: Signal(v) for k, v in data.as_dict()[0].items()}
            )

    display_vcd(build_dir, name, _update)


def display_vcd(build_dir: str, name: str, update_func):
    filename = os.path.join(build_dir, name)
    gtkw_file = f"{filename}.gtkw"
    vcd_file = f"{filename}.vcd"

    gtkw = GTKWSave(open(gtkw_file, "w"))
    gtkw.dumpfile(vcd_file)
    gtkw.savefile(gtkw_file)
    gtkw.sst_expanded(True)
    gtkw.size(1920, 1080)
    gtkw.treeopen(name)

    update_func(gtkw)

    spawn_gtkwave_interactive(vcd_file, gtkw_file)


def display_sim_trace(build_dir: str, name: str, root_block: _Block):
    def _update(gtkw):
        for i in root_block.subs:
            if hasattr(i, "introspection"):
                _insert_signal_block(gtkw, i, root_block.name, is_root=True)
            else:
                _insert_signal_block_classic(gtkw, i, root_block.name)

    display_vcd(build_dir, name, _update)


def run_sim(root: _Block, duration: Optional[int], gtk_wave: bool = False, build_path: str = "dist"):
    name = root.name
    vcd_file = f"{name}.vcd"

    root.config_sim(trace=True, tracebackup=False, name=name)
    root.run_sim(duration, quiet=0)

    try:
        os.mkdir(build_path)
    except FileExistsError:
        pass

    # For some reason config_sim() ignores path argument, so move manually
    os.rename(vcd_file, os.path.join(build_path, vcd_file))

    if gtk_wave:
        display_sim_trace(build_path, name, root)
