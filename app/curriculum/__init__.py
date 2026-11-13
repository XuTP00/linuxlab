"""Реестр учебного курса LinuxLab."""
from __future__ import annotations

from .helpers import (ccontains, cfail, cok, cmatch, cnot, ceq, cron, dc, de,
                      fa, fc, fe, fm, fl, fcount, fmode, fne, fowner, fsize,
                      ge, hist, inpath, no_proc, out, outnot, port, proc, slink,
                      ue, uig)

from .m00_help import MODULE as M0
from .m01_terminal import MODULE as M1
from .m02_files import MODULE as M2
from .m03_redirects import MODULE as M3
from .m04_text import MODULE as M4
from .m05_find import MODULE as M5
from .m06_processes import MODULE as M6
from .m07_users import MODULE as M7
from .m08_network import MODULE as M8
from .m09_bash import MODULE as M9
from .m10_system import MODULE as M10
from .m11_advanced import MODULE as M11
from .m12_angie import MODULE as M12
from .m13_apache import MODULE as M13

from .theory_1 import THEORY_1
from .theory_2 import THEORY_2
from .theory_3 import THEORY_3
from .theory_4 import THEORY_4
from .theory_5 import THEORY_5

THEORY = {**THEORY_1, **THEORY_2, **THEORY_3, **THEORY_4, **THEORY_5}

MODULES = [M0, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, M13]

TASKS: dict[str, dict] = {}
for _m in MODULES:
    for _t in _m["tasks"]:
        _t = dict(_t)
        _t["module"] = _m["id"]
        _t["module_title"] = _m["title"]
        _t["theory"] = THEORY.get(_t["id"], "")
        TASKS[_t["id"]] = _t

TASK_IDS = list(TASKS.keys())
