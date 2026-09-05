# Modules in Ade

Ade features an independent module resolution system that does not rely on host environment import machinery.

## Importing Modules

### Standard Library Modules
Ade provides built-in modules including `math`, `time`, and `json`:
```ade
import math

say math.sqrt(144) # 12
say math.pi
```

### Specific Imports (`from ... import`)
```ade
from math import sqrt, pi

say sqrt(25) # 5
```

### Module Aliases
```ade
import math as m

say m.pow(2, 3) # 8
```

## Project-Local Modules
When importing a local module, Ade searches relative to the importing file:
```
project/
  main.ade
  utils.ade
```
In `utils.ade`:
```ade
function greet(name) {
    return "Hello, " + name
}
```
In `main.ade`:
```ade
import utils

say utils.greet("Fortune")
```
Modules are evaluated once in an isolated lexical environment and cached globally.
