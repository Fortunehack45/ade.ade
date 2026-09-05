# Functions in Ade

Functions in Ade are first-class values that support parameters, return values, recursion, and lexical closures.

## Declaration
```ade
function greet(name) {
    say "Hello, " + name
}

greet("Fortune")
```

## Return Values
Use `return` to pass values back to the caller:
```ade
function add(a, b) {
    return a + b
}

sum = add(10, 20)
say sum
```

## First-Class & Anonymous Functions
Functions can be stored in variables or passed as parameters:
```ade
double = function(x) {
    return x * 2
}

say double(21)
```

## Closures
Functions retain access to variables in the scope where they were declared:
```ade
function make_adder(x) {
    return function(y) {
        return x + y
    }
}

add_five = make_adder(5)
say add_five(10) # 15
```
