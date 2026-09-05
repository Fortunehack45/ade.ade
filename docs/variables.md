# Variables in Ade

Ade makes variable declaration straightforward and noise-free.

## Assignment
Variables do not require explicit declaration keywords like `var` or `let`:

```ade
name = "Fortune"
age = 19
height = 1.8
is_active = true
```

## Scoping
Variables are lexically scoped:
- Variables defined at the top-level reside in the global environment.
- Blocks `{ ... }` and functions introduce child lexical scopes.
- Reassigning a variable modifies the existing binding in the enclosing scope:
```ade
x = 10
if true {
    x = 20 # Updates x in outer scope
    y = 30 # Local to this block
}
say x # Prints: 20
```
