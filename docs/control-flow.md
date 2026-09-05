# Control Flow in Ade

Ade provides familiar, explicit block-based control flow constructs.

## Conditionals: `if` / `else if` / `else`
```ade
score = 88

if score >= 90 {
    say "A"
} else if score >= 80 {
    say "B"
} else {
    say "C"
}
```

## `while` Loops
```ade
count = 0
while count < 5 {
    say count
    count = count + 1
}
```

## `for ... in ...` Loops
Iterate over lists, strings, or map keys:
```ade
# Over list
for item in [1, 2, 3] {
    say item
}

# Over string characters
for ch in "ade" {
    say ch
}
```

## `break` and `continue`
- `break`: terminates the innermost loop.
- `continue`: proceeds to the next iteration of the loop.
```ade
for x in [1, 2, 3, 4, 5] {
    if x == 2 {
        continue
    }
    if x == 4 {
        break
    }
    say x
}
```
