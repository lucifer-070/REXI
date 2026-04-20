"""
environment.py — Scoped symbol table (variable / function store) for REXI.

Each Environment has an optional parent, forming a chain of scopes.
Variable lookup walks up the chain — inner scopes shadow outer ones.
"""


class Environment:
    """
    A single scope in the interpreter's symbol table.

    Usage:
        global_env = Environment()
        local_env  = Environment(parent=global_env)
        local_env.set('x', 42)
        local_env.get('x')   # 42
    """

    def __init__(self, parent=None):
        self._vars  = {}          # name → value store for this scope
        self.parent = parent      # enclosing scope (None for the global scope)

    # ── Write ─────────────────────────────────────────────────────────────────

    def set(self, name: str, value):
        """
        Define or update a variable in THIS scope.
        Always writes here — does not walk up to the parent.
        """
        self._vars[name] = value

    def assign(self, name: str, value):
        """
        Update an EXISTING variable by walking up the scope chain.
        If not found anywhere, defines it in the current scope.
        """
        if name in self._vars:
            self._vars[name] = value
        elif self.parent is not None:
            self.parent.assign(name, value)
        else:
            # Variable doesn't exist anywhere — create it at global scope
            self._vars[name] = value

    # ── Read ──────────────────────────────────────────────────────────────────

    def get(self, name: str):
        """
        Look up a variable, walking up the scope chain.
        Raises NameError if not found anywhere.
        """
        if name in self._vars:
            return self._vars[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameError(name)

    def has(self, name: str) -> bool:
        """Return True if the name exists anywhere in the scope chain."""
        if name in self._vars:
            return True
        if self.parent is not None:
            return self.parent.has(name)
        return False

    # ── Debug ─────────────────────────────────────────────────────────────────

    def __repr__(self):
        return f"Environment({list(self._vars.keys())}, parent={'yes' if self.parent else 'none'})"

    def dump(self, indent: int = 0) -> str:
        """
        Return a formatted string showing all variables defined in this scope
        and all parent scopes. Used by the REPL's :env command.

        Example output:
            [local scope]
              n = 5
              result = 120
            [global scope]
              fact = <function fact>
        """
        lines = []
        label = "global scope" if self.parent is None else "local scope"
        lines.append(" " * indent + f"[{label}]")

        for name, value in sorted(self._vars.items()):
            # FuncDefNode objects have a 'params' attribute — show them nicely
            if hasattr(value, 'params'):
                display = f"<function {name}>"
            else:
                display = repr(value)
            lines.append(" " * indent + f"  {name} = {display}")

        if self.parent is not None:
            lines.append(self.parent.dump(indent))

        return "\n".join(lines)
