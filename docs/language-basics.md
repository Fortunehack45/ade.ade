# Ade Language Basics

This document provides a concise overview of Ade's fundamental syntax, values, and operators.

## Comments
Single-line comments begin with `#`:
```ade
# Calculate total user points
points = 100 # Inline comment
```

## Values & Primitive Types
- **Numbers**: `42`, `3.14`, `-10`
- **Text**: `"Hello"`, `"Line 1\nLine 2"`
- **Booleans**: `true`, `false`
- **Null**: `null`

## Printing with `say`
Use `say` to output any expression to standard output:
```ade
say "Welcome to Ade!"
say 10 + 20
```

## Operators
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Comparisons**: `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Logical**: `and`, `or`, `not`
- **Concatenation**: `+` on strings or lists
