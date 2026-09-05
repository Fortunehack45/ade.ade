# Ade Standard Library Reference

Ade provides a suite of built-in modules designed for real-world programming, system automation, and data manipulation.

Standard library modules are imported directly without external dependencies:

```ade
import fs
import os
import io
import math
import json
import time
```

---

## 1. Filesystem (`fs`)

The `fs` module provides synchronous, safe filesystem operations.

### Functions

- `fs.read_text(path: text) -> text`: Reads the entire content of a UTF-8 text file.
- `fs.write_text(path: text, content: text) -> void`: Overwrites or creates a file with the given text.
- `fs.append_text(path: text, content: text) -> void`: Appends text to a file.
- `fs.exists(path: text) -> bool`: Checks whether a file or directory exists.
- `fs.is_file(path: text) -> bool`: Returns `true` if the path is a regular file.
- `fs.is_dir(path: text) -> bool`: Returns `true` if the path is a directory.
- `fs.list_dir(path: text = ".") -> list<text>`: Lists entry names in the directory.
- `fs.mkdir(path: text) -> bool`: Recursively creates directories.
- `fs.remove(path: text) -> bool`: Removes a file or directory.

### Example
```ade
import fs

fs.write_text("notes.txt", "Learning Ade!\n")
if fs.exists("notes.txt") {
    say fs.read_text("notes.txt")
}
```

---

## 2. Operating System (`os`)

The `os` module exposes platform details and environment control.

### Functions

- `os.platform() -> text`: Returns `"windows"`, `"linux"`, or `"macos"`.
- `os.cwd() -> text`: Returns the current working directory.
- `os.get_env(name: text, default: text = "") -> text`: Reads an environment variable.
- `os.set_env(name: text, value: text) -> void`: Sets an environment variable in the process.
- `os.args() -> list<text>`: Returns command-line arguments.
- `os.exit(code: number = 0) -> void`: Exits the program with the specified status code.

### Example
```ade
import os

say "Platform: {os.platform()}"
user = os.get_env("USER", "developer")
say "Current user: {user}"
```

---

## 3. Interactive I/O Streams (`io`)

The `io` module provides stream control and console input/output.

### Functions

- `io.read_line(prompt: text = "") -> text`: Reads a line of user input from stdin.
- `io.print(val: any) -> void`: Prints to stdout without appending a newline.
- `io.println(val: any) -> void`: Prints to stdout with a newline.
- `io.eprintln(val: any) -> void`: Prints an error line to stderr.

### Example
```ade
import io

name = io.read_line("Enter your name: ")
io.println("Welcome to Ade, {name}!")
```

---

## 4. Mathematics (`math`)

Constants:
- `math.pi`: `3.141592653589793`
- `math.e`: `2.718281828459045`

Functions:
- `math.sqrt(x)`: Square root
- `math.sin(x)`, `math.cos(x)`, `math.tan(x)`: Trigonometric functions
- `math.abs(x)`: Absolute value
- `math.floor(x)`, `math.ceil(x)`: Rounding
- `math.min(a, b)`, `math.max(a, b)`: Extrema
- `math.pow(base, exp)`: Exponentiation

---

## 5. JSON (`json`)

- `json.parse(text: text) -> any`: Parses a JSON string into Ade collections/values.
- `json.stringify(value: any) -> text`: Serializes an Ade value to JSON format.

---

## 6. Time (`time`)

- `time.now() -> text`: Current ISO timestamp string.
- `time.timestamp() -> number`: Unix epoch timestamp in seconds.
- `time.sleep(seconds: number) -> void`: Suspends execution for given seconds.
