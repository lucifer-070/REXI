"""
errors.py — Unified error display for REXI.

Provides format_error(source, exc) which turns any REXI error into a
human-readable string with:
  - Error type and message
  - The offending source line
  - A caret pointer to the exact column

Usage:
    from src.errors import format_error
    try:
        ...
    except LexerError as e:
        print(format_error(source, e))
"""


def format_error(source: str, exc: Exception) -> str:
    """
    Format a LexerError, ParseError, or REXIRuntimeError into a
    human-readable error string with a source line and caret pointer.

    Args:
        source — the full original source string that was being parsed/run
        exc    — the exception (should have .line and .col integer attributes)

    Returns:
        A multi-line string ready to print to the terminal.
    """
    lines    = source.splitlines()
    line_no  = getattr(exc, 'line', 0)
    col_no   = getattr(exc, 'col',  0)
    err_type = type(exc).__name__

    # ── Header line ───────────────────────────────────────────────────────────
    if line_no and col_no:
        header = f"[{err_type}] Line {line_no}, Col {col_no}: {_plain_message(exc)}"
    else:
        header = f"[{err_type}]: {_plain_message(exc)}"

    parts = ["", header]

    # ── Source snippet + caret ────────────────────────────────────────────────
    if line_no and 1 <= line_no <= len(lines):
        src_line = lines[line_no - 1]
        parts.append(f"  {src_line}")
        if col_no:
            parts.append("  " + " " * max(col_no - 1, 0) + "^")

    parts.append("")
    return "\n".join(parts)


def _plain_message(exc: Exception) -> str:
    """
    Strip the auto-generated '[TypeName] Line X, Col Y: ' prefix from the
    exception message, since format_error builds its own header.
    """
    msg = str(exc)
    # Exceptions in this project self-format as:
    #   "[LexerError] Line 1, Col 5: Unexpected character '@'"
    # We only want the part after the last ': '
    if '] ' in msg:
        after_bracket = msg[msg.index('] ') + 2:]
        colon = after_bracket.find(': ')
        if colon != -1 and after_bracket[:colon].startswith('Line '):
            return after_bracket[colon + 2:]
        return after_bracket
    return msg
