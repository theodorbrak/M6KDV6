# -*- coding: utf-8 -*-
"""
@author: fleaue


Chain calculator prototype
--------------------------
Nodes = things (a, b, c ...). Edges = "how much of SRC is needed for DST"
Each edge holds an equation in x (any math expression), usable in BOTH directions:

  need(t)    : amount of SRC needed to make t of DST        (backward)
  produce(s) : amount of DST you get from s of SRC          (forward)

If you only give `need`, `produce` is found by numerically inverting it
(assumes the equation is increasing, e.g. x*2, x**2, sqrt(x)*3)

Example: 1a + 2b = 3c
    g.add_edge("a", "c", "x/3*1")
    g.add_edge("b", "c", "x/3*2")
"""

import math

# safe-ish equation evaluation

_ALLOWED = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
_ALLOWED.update({"abs": abs, "min": min, "max": max, "round": round})


def evaluate(expr, x):
    """Evaluate a math expression string with variable x."""
    return eval(expr, {"__builtins__": {}}, {**_ALLOWED, "x": x})


def invert(func, y):
    """Find x >= 0 with func(x) = y, by bisection (func must be increasing)."""
    if y <= func(0):
        return 0.0
    lo, hi = 0.0, 1.0
    while func(hi) < y and hi < 1e12:
        hi *= 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if func(mid) < y:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------- data model ----------

class Edge:
    def __init__(self, source, dst, need_expr, produce_expr=None):
        self.source = source
        self.dst = dst
        self.need_expr = need_expr
        self.produce_expr = produce_expr

    def need(self, target_amount):
        return evaluate(self.need_expr, target_amount)

    def produce(self, source_amount):
        if self.produce_expr is not None:
            return evaluate(self.produce_expr, source_amount)
        return invert(self.need, source_amount)


class Graph:
    def __init__(self):
        self.nodes = {}   # name -> dict of extra info (free-form, for customization)
        self.edges = []

    def add_node(self, name, **info):
        self.nodes[name] = info

    def add_edge(self, source, dst, need_expr, produce_expr=None):
        for n in (source, dst):
            self.nodes.setdefault(n, {})
        self.edges.append(Edge(source, dst, need_expr, produce_expr))

    def inputs(self, name):
        return [e for e in self.edges if e.dst == name]

    def outputs(self, name):
        return [e for e in self.edges if e.source == name]

    def raw_nodes(self):
        return [n for n in self.nodes if not self.inputs(n)]


# ---------- core computations ----------

def requirements(graph, item, amount):
    """Backward: how much of every node is needed to make `amount` of `item`.
    Returns dict name -> amount. Shared ingredients are summed."""
    totals = {}

    def walk(name, amt, path):
        if name in path:
            raise ValueError("Cycle: " + " -> ".join(path + [name]))
        totals[name] = totals.get(name, 0) + amt
        for e in graph.inputs(name):
            walk(e.source, e.need(amt), path + [name])

    walk(item, amount, [])
    return totals


def raw_requirements(graph, item, amount):
    totals = requirements(graph, item, amount)
    return {n: a for n, a in totals.items() if n in graph.raw_nodes()}


def producible(graph, item, raw_amounts):
    """Forward: how much of `item` can be made from the given raw amounts.
    The scarcest input limits the result (min)."""
    def go(name, path):
        if name in path:
            raise ValueError("Cycle: " + " -> ".join(path + [name]))
        ins = graph.inputs(name)
        if not ins:
            return raw_amounts.get(name, 0)
        return min(e.produce(go(e.source, path + [name])) for e in ins)

    return go(item, [])


# ---------- text output ----------

def print_tree(graph, item, amount, indent=0):
    print("  " * indent + f"{amount:.2f} x {item}")
    for e in graph.inputs(item):
        print_tree(graph, e.source, e.need(amount), indent + 1)


# ---------- minimal visual (tkinter, work in progress) ----------

def levels(graph):
    lvl = {}

    def level(n):
        if n not in lvl:
            ins = graph.inputs(n)
            lvl[n] = 0 if not ins else 1 + max(level(e.source) for e in ins)
        return lvl[n]

    for n in graph.nodes:
        level(n)
    return lvl


def draw(graph, amounts=None):
    import tkinter as tk
    lvl = levels(graph)
    cols = {}
    for n, l in lvl.items():
        cols.setdefault(l, []).append(n)

    root = tk.Tk()
    root.title("Chain")
    canvas = tk.Canvas(root, width=700, height=450, bg="white")
    canvas.pack()
    pos, r = {}, 28
    for l, names in cols.items():
        for i, n in enumerate(names):
            pos[n] = (80 + l * 180, 60 + i * 100)

    for e in graph.edges:
        (x1, y1), (x2, y2) = pos[e.source], pos[e.dst]
        canvas.create_line(x1 + r, y1, x2 - r, y2, arrow=tk.LAST)
        canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 10, text=e.need_expr, fill="gray")
    for n, (x, y) in pos.items():
        canvas.create_oval(x - r, y - r, x + r, y + r, fill="lightblue")
        label = n if not amounts or n not in amounts else f"{n}\n{amounts[n]:.1f}"
        canvas.create_text(x, y, text=label)
    root.mainloop()


# ---------- demo ----------

if __name__ == "__main__":
    g = Graph()
    # 1a + 2b = 3c
    g.add_edge("a", "c", "x/3*1")
    g.add_edge("b", "c", "x/3*2")
    # d needs 2 c per d, plus a nonlinear use of b
    g.add_edge("c", "d", "x*2")
    g.add_edge("b", "d", "sqrt(x)*3")

    target = 12
    print(f"To make {target} d:")
    print_tree(g, "d", target)

    print("\nRaw totals:", {k: round(v, 2) for k, v in raw_requirements(g, "d", target).items()})
    print("Everything:", {k: round(v, 2) for k, v in requirements(g, "d", target).items()})

    have = {"a": 40, "b": 100}
    print(f"\nWith {have} you can make {producible(g, 'd', have):.2f} d")

    #draw(g, requirements(g, "d", target))   # uncomment to activate the visual (NOT FULLY FUNCTIONAL)