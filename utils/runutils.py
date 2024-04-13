import os
from typing import Optional, Iterable

from myhdl import intbv, modbv
from myhdl._block import _Block
from vcd.gtkw import GTKWSave, spawn_gtkwave_interactive

from utils.introspection import BlockIntrospection


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


def _insert_signal_block(gtkw: GTKWSave, root: _Block, base_name: str):
    intro: BlockIntrospection = root.introspection

    presentation_name = intro.name if intro.name is not None else intro.type
    name = f"{base_name}.{root.name}"

    with gtkw.group(presentation_name):
        for sig_name, sig in sorted(intro.signals.items(), key=lambda x: x[0]):
            trace_name = f"{name}.{sig_name}"
            if isinstance(sig.val, intbv | modbv):
                trace_name += f"[{sig.val._nrbits - 1}:0]"
            gtkw.trace(trace_name)

        for v in intro.modules.values():
            _insert_signal_block(gtkw, v, base_name=name)


def display_vcd_update_traces_list(gtkw: GTKWSave, base: str, traces: Iterable[str]):
    with gtkw.group(base):
        for i in traces:
            gtkw.trace(f"{base}.{i}")


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
                _insert_signal_block(gtkw, i, root_block.name)
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
