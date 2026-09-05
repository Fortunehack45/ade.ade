# Ade Language Specification (Version 0.1)

This document formally defines the syntax, lexical structure, type system, runtime semantics, and execution model of the Ade programming language (Milestone 0.1).

---

## 1. Lexical Structure

### 1.1 Character Set & Encoding
Ade source files (`.ade`) are UTF-8 encoded text files.

### 1.2 Comments
Single-line comments begin with `#` and continue until the end of the line.
```ade
# This is a comment in Ade
x = 10 # Inline comment
```

### 1.3 Whitespace & Newlines
- Whitespace (spaces, tabs, carriage returns) serves to separate tokens and is otherwise ignored outside string literals.
- Semicolons are optional and not required. Newlines delimit statements, except inside unclosed parentheses `(`, brackets `[`, or braces `{`.

### 1.4 Identifiers
An identifier begins with an ASCII letter or underscore (`_`), followed by any number of letters, digits, or underscores.
```ebnf
identifier ::= ( [a-z] | [A-Z] | "_" ) ( [a-z] | [A-Z] | [0-9] | "_" )*
```

### 1.5 Keywords
The following identifiers are reserved keywords in Ade 0.1:
```
function    return      if          else        while       for
in          break       continue    say         true        false
null        and         or          not
```

*(Reserved for future phases: `class`, `import`, `from`, `as`, `try`, `catch`, `async`, `await`, `yield`, `match`, `type`, `language`)*

### 1.6 Literals

#### 1.6.1 Number Literals
Ade supports numbers with decimal and integer notations. Numbers are represented without arbitrary precision loss for standard arithmetic.
```ebnf
digit          ::= [0-9]
integer_lit    ::= digit+
decimal_lit    ::= digit+ "." digit+
number_literal ::= decimal_lit | integer_lit
```
Examples: `42`, `0`, `3.14159`, `1000`

#### 1.6.2 String Literals
String literals are enclosed in double quotes `"` and support standard escape sequences:
- `\n`: Newline
- `\t`: Tab
- `\"`: Double quote
- `\\`: Backslash
```ebnf
string_literal ::= '"' ( [^"\\] | escape_seq )* '"'
escape_seq     ::= '\' ( 'n' | 't' | '"' | '\' )
```
Examples: `"Hello, World!"`, `"Line 1\nLine 2"`

#### 1.6.3 Boolean & Null Literals
- `true`: Boolean truth
- `false`: Boolean falsehood
- `null`: Absence of value

---

## 2. Grammar Specification (EBNF)

### 2.1 Program Structure
```ebnf
program ::= statement* EOF
```

### 2.2 Statements
```ebnf
statement ::= var_assignment
            | say_statement
            | if_statement
            | while_statement
            | for_statement
            | function_declaration
            | return_statement
            | break_statement
            | continue_statement
            | expression_statement
            | block_statement

block_statement ::= "{" statement* "}"

var_assignment ::= identifier "=" expression

say_statement ::= "say" expression

if_statement ::= "if" expression block_statement ( "else" ( if_statement | block_statement ) )?

while_statement ::= "while" expression block_statement

for_statement ::= "for" identifier "in" expression block_statement

function_declaration ::= "function" identifier "(" parameter_list? ")" block_statement

parameter_list ::= identifier ( "," identifier )*

return_statement ::= "return" expression?

break_statement ::= "break"

continue_statement ::= "continue"

expression_statement ::= expression
```

### 2.3 Expressions & Operator Precedence

Precedence levels (lowest to highest):
1. **Assignment**: `=` (right-associative)
2. **Logical OR**: `or` (left-associative)
3. **Logical AND**: `and` (left-associative)
4. **Equality**: `==`, `!=` (left-associative)
5. **Relational**: `<`, `<=`, `>`, `>=` (left-associative)
6. **Additive**: `+`, `-` (left-associative)
7. **Multiplicative**: `*`, `/`, `%` (left-associative)
8. **Unary**: `-`, `not` (prefix)
9. **Postfix / Call / Access**: `(args)`, `[index]`, `.member` (left-associative)
10. **Primary**: literals, identifiers, grouped expressions `(expr)`, anonymous functions `function(params) { ... }`, list literals `[...]`, map literals `{...}`

```ebnf
expression     ::= logical_or

logical_or     ::= logical_and ( "or" logical_and )*

logical_and    ::= equality ( "and" equality )*

equality       ::= relational ( ( "==" | "!=" ) relational )*

relational     ::= additive ( ( "<" | "<=" | ">" | ">=" ) additive )*

additive       ::= multiplicative ( ( "+" | "-" ) multiplicative )*

multiplicative ::= unary ( ( "*" | "/" | "%" ) unary )*

unary          ::= ( "-" | "not" ) unary | postfix

postfix        ::= primary ( call_suffix | index_suffix | member_suffix )*

call_suffix    ::= "(" argument_list? ")"
index_suffix   ::= "[" expression "]"
member_suffix  ::= "." identifier

argument_list  ::= expression ( "," expression )*

primary        ::= number_literal
                 | string_literal
                 | "true" | "false" | "null"
                 | identifier
                 | "(" expression ")"
                 | list_literal
                 | map_literal
                 | anon_function

list_literal   ::= "[" ( expression ( "," expression )* )? ","? "]"

map_literal    ::= "{" ( map_entry ( "," map_entry )* )? ","? "}"
map_entry      ::= ( identifier | string_literal ) ":" expression

anon_function  ::= "function" "(" parameter_list? ")" block_statement
```

---

## 3. Semantics and Type System

### 3.1 Data Types in Ade 0.1
1. **`number`**: Signed 64-bit integer or double-precision floating-point number. Arithmetic between integers produces integers where exact, and decimals on division (`/`).
2. **`text` / `string`**: Immutable sequence of UTF-8 characters. The `+` operator on strings performs concatenation.
3. **`bool`**: `true` or `false`. Truthiness evaluation: only `false` and `null` are falsy; all other values (including `0`, `""`, `[]`, `{}`) are truthy.
4. **`null`**: The singleton null value indicating uninitialized or absent data.
5. **`list`**: Dynamic, ordered, mutable collection of arbitrary Ade values. Indexed from `0` to `len - 1`. Negative indexing is not permitted in 0.1.
6. **`map`**: Unordered key-value dictionary with string or identifier keys. Supports dot access `user.name` and bracket access `user["name"]`.
7. **`function`**: First-class callable value with lexical scope encapsulation.

### 3.2 Scoping Rules
- Scoping is **lexical (static)**.
- Inner blocks `{ ... }` introduce a new lexical scope.
- Variables declared within an inner scope are accessible within nested scopes, but shadow bindings in outer scopes.
- Assignments to existing variables in outer scopes update those outer variables. If a variable has not been declared in any enclosing scope, the assignment binds it in the current local scope.
- Closures capture references to their lexical enclosing environment at definition time.

### 3.3 Control Flow Semantics
- **`if / else`**: Evaluates the condition expression. If truthy, the consequence block is executed; otherwise, the alternate block (if present) is executed.
- **`while`**: Evaluates condition repeatedly before each iteration; halts when condition evaluates to falsy.
- **`for item in collection`**: Evaluates collection (must be a list, string, or map). Iterates sequentially over the elements, binding `item` in a new loop scope for each step.
- **`break`**: Immediately terminates the innermost enclosing loop (`for` or `while`).
- **`continue`**: Immediately halts the current iteration of the innermost enclosing loop and proceeds to the next iteration.
- **`return`**: Halts execution of the current function and returns the provided expression (or `null` if omitted).

---

## 4. Diagnostics & Error Contracts

Ade compiler components preserve source positions (`file`, `line`, `column`, `offset`) across all tokens and AST nodes. When an error occurs (syntax error, parse error, or runtime error), the diagnostic system generates:
1. **Severity and message**: `Error: <brief description>`
2. **Source context**: 1-3 lines of surrounding code with line numbering.
3. **Caret pointer**: `^` precisely underneath the culprit token or span.
4. **Explanation**: Clear sentence explaining what the compiler expected vs. what was found.
5. **Actionable Fix**: Concrete `Try: ...` suggestion when a known correction exists.
