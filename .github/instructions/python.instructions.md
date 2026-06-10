---
name: "Python Standards"
description: "Coding conventions for Python files"
applyTo: "**/*.py"
---

# Python coding standards

- Follow the PEP 8 style guide.
- Use 4 spaces for indentation.
- Write docstrings for public functions in Google style, using quartodoc interlinks when applicable.
- If a function has any `return` statement, there should be only one `return` statement as the last line of the function.
- Do not use `continue` or `break` in loops.
- Do not use bare `except` clauses; always specify the expected exception type.
