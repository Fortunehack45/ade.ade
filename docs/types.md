# Gradual & Static Type System in Ade

Ade features a **gradual, progressive type system**. 
You can write rapid, dynamic scripts without any type annotations, or add explicit types where readability, documentation, and compiler-verified safety are needed.

---

## 1. Type Annotations

### 1.1 Variable Annotations
Variables can be declared dynamically or with explicit types:

```ade
# Dynamic (unannotated)
name = "Fortune"

# Explicitly typed
name: text = "Fortune"
age: number = 19
is_active: bool = true
empty_field: null = null
```

### 1.2 Primitive Types
- `number`: 64-bit integers and double-precision floating-point numbers.
- `text` (or `string`): UTF-8 character strings.
- `bool`: `true` or `false`.
- `null`: Represents absence of value.
- `any`: Universal escape hatch compatible with all types.
- `void`: Used for functions that return no value.

---

## 2. Collections & Generics Foundations

Ade supports parameterized collection types:

```ade
# Generic lists
scores: list<number> = [100, 95, 88]
names: list<text> = ["Alice", "Bob", "Charlie"]

# Generic maps
user_scores: map<text, number> = { "Alice": 100, "Bob": 95 }
```

---

## 3. Nullable & Union Types

### 3.1 Nullable Types (`T?`)
Nullable types permit either the underlying type or `null`:

```ade
bio: text? = null
bio = "Language Designer"
```

### 3.2 Union Types (`T1 | T2`)
Union types allow a variable to hold values of multiple designated types:

```ade
id: number | text = 42
id = "ADE-42"
```

---

## 4. Function Signatures

Functions declare typed parameters and return types using the `->` arrow:

```ade
function add(a: number, b: number) -> number {
    return a + b
}

function greet(user: text) -> text {
    return "Hello, {user}!"
}

function log_message(msg: text) -> void {
    say msg
}
```

---

## 5. Static Verification with `ade check`

Ade provides a static type checker command that analyzes your source code without running it:

```bash
ade check <file.ade>
```

When type violations occur, Ade generates rich diagnostic messages pointing directly to the offending token with carets (`^`) and actionable fix suggestions:

```
Error: Type Error

  2 | age: number = "nineteen"
    |               ^^^^^^^^^^

Type mismatch: cannot assign value of type 'text' to variable 'age' with type 'number'.

Note: Expected an expression compatible with 'number', but found 'text'.

Try:
  Change the assigned value or adjust the type annotation to 'text'.
```
