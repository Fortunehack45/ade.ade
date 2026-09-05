# Object-Oriented Programming (Classes) in Ade

Ade supports object-oriented programming with classes, methods, fields, and instances, while keeping the language fully usable without OOP.

## Defining a Class
```ade
class User {
    name
    age

    function greet() {
        say "Hello, my name is {self.name} and I am {self.age} years old."
    }
}
```

## Instantiation
Instances can be created using positional arguments or named parameters:
```ade
# Named arguments
user1 = User(
    name: "Fortune",
    age: 19
)

# Positional arguments
user2 = User("Ade", 20)
```

## Methods and `self`
Methods access the instance through the implicit `self` binding:
```ade
class Counter {
    value

    function increment() {
        self.value = self.value + 1
    }
}

c = Counter(0)
c.increment()
say c.value # 1
```

## Attribute Mutation
Instance properties can be read and mutated dynamically:
```ade
user1.age = 20
say user1.age # 20
```
