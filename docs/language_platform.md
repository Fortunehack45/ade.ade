# Ade Language-Building Platform (`ade.language`)

Ade is designed from the ground up not only as a modern, expressive general-purpose language, but as an **extensible language platform** on which developers can build custom domain-specific languages (DSLs), query languages, and scripting engines.

---

## 1. Overview & Architecture

The language-building platform provides a unified compiler construction toolkit:

```
┌──────────────────────────────────────────────────────────────┐
│                    LanguageEngine                            │
├──────────────┬───────────────────┬──────────────┬────────────┤
│   DSLLexer   │     DSLParser     │   DSLNode    │DSLEvaluator│
│ (Token Rules)│(Pratt Precedence) │(Generic AST) │ (Visitor)  │
└──────────────┴───────────────────┴──────────────┴────────────┘
```

- **Dual-API Surface**:
  - **In Ade**: Write `import language` to build, parse, and execute DSLs inside Ade scripts.
  - **In Python**: Import `from ade.language import LanguageEngine` to embed customizable DSL engines in Python hosts.
- **Clang/Rust-Grade Diagnostics**: Custom DSLs automatically inherit Ade's visual diagnostic reporting with source snippets, line gutters, carets (`^`), and actionable guidance.

---

## 2. Building a DSL in Ade

### Example: Arithmetic Expression Calculator

```ade
import language

# 1. Create the engine
calc = language.create("Calculator")

# 2. Register token rules
calc.token("NUMBER", "\\d+", false)
calc.token("PLUS", "\\+", false)
calc.token("MINUS", "-", false)
calc.token("STAR", "\\*", false)
calc.token("SLASH", "/", false)
calc.token("LPAREN", "\\(", false)
calc.token("RPAREN", "\\)", false)
calc.ignore("\\s+")

# 3. Configure grammar & Pratt precedence
calc.literal("NUMBER")
calc.group("LPAREN", "RPAREN")

function do_add(a, b) { return a + b }
function do_sub(a, b) { return a - b }
function do_mul(a, b) { return a * b }
function do_div(a, b) { return a / b }

calc.binary_op("PLUS", 10, "add", do_add)
calc.binary_op("MINUS", 10, "sub", do_sub)
calc.binary_op("STAR", 20, "mul", do_mul)
calc.binary_op("SLASH", 20, "div", do_div)

# 4. Parse AST
ast = calc.parse("10 + 5 * 2")
say ast.pretty()

# 5. Execute
result = calc.execute("(10 + 5) * 2")
say "Result: {result}"  # Outputs: Result: 30
```

---

## 3. Building a Query / Filter DSL

Custom DSLs can accept dynamic execution contexts (variables / data maps) for each record evaluated:

```ade
import language

query = language.create("QueryDSL")

query.token("NUMBER", "\\d+", false)
query.token("AND", "AND|and", false)
query.token("GTE", ">=", false)
query.token("EQ", "==", false)
query.token("IDENT", "[a-zA-Z_]\\w*", false)
query.ignore("\\s+")

query.literal("NUMBER")
query.literal("IDENT", "identifier")

query.binary_op("GTE", 20, "gte", function(a, b) { return a >= b })
query.binary_op("EQ", 20, "eq", function(a, b) { return a == b })
query.binary_op("AND", 10, "and", function(a, b) { return a and b })

# Test record
user = {"age": 25, "active": 1}

matches = query.execute("age >= 18 AND active == 1", user)
say "Matches: {matches}"  # true
```

---

## 4. Building a DSL in Python

Python applications can directly use `LanguageEngine` to create and embed custom parsers and evaluators:

```python
from ade.language import LanguageEngine

engine = LanguageEngine("MathDSL")

# Define tokens
engine.token("NUMBER", r"\d+(\.\d+)?", converter=float)
engine.token("PLUS", r"\+")
engine.token("STAR", r"\*")
engine.ignore(r"\s+")

# Define grammar & precedence
engine.literal("NUMBER")
engine.binary_op("PLUS", 10, "add", lambda a, b: a + b)
engine.binary_op("STAR", 20, "mul", lambda a, b: a * b)

# Parse & Execute
res = engine.execute("2 + 3 * 4")
print(res)  # 14.0
```

---

## 5. CLI: Running Custom DSLs

You can run a DSL script directly using an Ade specification file:

```powershell
ade dsl <spec.ade> <file.dsl>
```

**`spec.ade`**:
```ade
import language

calc = language.create("Calc")
calc.token("NUMBER", "\\d+", false)
calc.token("PLUS", "\\+", false)
calc.token("STAR", "\\*", false)
calc.ignore("\\s+")

calc.literal("NUMBER")
calc.binary_op("PLUS", 10, "add", function(a, b) { return a + b })
calc.binary_op("STAR", 20, "mul", function(a, b) { return a * b })
```

**`input.dsl`**:
```
10 + 20 * 3
```

**Output**:
```
70
```

---

## 6. Diagnostic Error Reporting

Syntax errors, unexpected tokens, and runtime evaluation errors in custom DSLs are formatted with standard Ade diagnostics:

```text
Error: DSL Syntax Error

  1 | 2 + * 4
          ^

Unexpected token '*' at start of expression.

Note: No expression rule registered for token type 'STAR'.

Try:
  Check your expression or register this token in the language engine.
```
