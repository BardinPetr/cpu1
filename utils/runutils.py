import os
from typing import Optional

from myhdl import intbv, modbv
from myhdl._block import _Block, block
from vcd.gtkw import GTKWSave, spawn_gtkwave_interactive


def _insert_signal_block(gtkw: GTKWSave, root: _Block, base_name: str = None):
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
            _insert_signal_block(gtkw, sub, base_name=name)


def display(build_dir: str, name: str, root_block: _Block):
    filename = os.path.join(build_dir, name)
    gtkw_file = f"{filename}.gtkw"
    vcd_file = f"{filename}.vcd"

    gtkw = GTKWSave(open(gtkw_file, "w"))
    gtkw.dumpfile(vcd_file)
    gtkw.savefile(gtkw_file)
    gtkw.sst_expanded(True)
    gtkw.size(1920, 1080)
    gtkw.treeopen(name)

    _insert_signal_block(gtkw, root_block)

    spawn_gtkwave_interactive(vcd_file, gtkw_file)


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
        display(build_path, name, root)

