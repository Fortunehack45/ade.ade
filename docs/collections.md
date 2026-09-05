# Collections in Ade

Ade provides two built-in collection primitives: **Lists** and **Maps**.

## Lists
Lists are ordered, dynamic sequences indexed from `0`:

```ade
numbers = [10, 20, 30]

# Access
say numbers[0] # 10

# Mutation
numbers[1] = 99

# Length
say len(numbers) # 3

# Iteration
for n in numbers {
    say n
}
```

## Maps (Objects)
Maps store key-value associations. Keys can be identifiers or strings:

```ade
user = {
    name: "Fortune",
    role: "Developer",
    score: 100
}

# Member access (dot notation)
say user.name

# Subscript access
say user["role"]

# Mutation
user.score = 120
user["location"] = "Lagos"
```
