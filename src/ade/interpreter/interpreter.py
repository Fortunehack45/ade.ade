"""Tree-walking AST Interpreter for the Ade programming language."""

import sys
from typing import Any, List, Optional, TextIO
from ade.diagnostics.span import SourceSpan
from ade.ast.nodes import (
    Program,
    Statement,
    Expression,
    BlockStmt,
    ExpressionStmt,
    VarAssignmentStmt,
    SayStmt,
    IfStmt,
    WhileStmt,
    ForStmt,
    FunctionDeclStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    NumberLiteral,
    StringLiteral,
    BoolLiteral,
    NullLiteral,
    Identifier,
    BinaryExpr,
    UnaryExpr,
    CallExpr,
    NamedArgExpr,
    MemberAccessExpr,
    IndexAccessExpr,
    ListLiteral,
    MapLiteral,
    AnonymousFunctionExpr,
    StringInterpolationExpr,
    ImportStmt,
    FromImportStmt,
    ClassDeclStmt,
)
from ade.lexer.token import TokenType
from ade.runtime.value import (
    AdeValue,
    AdeNumber,
    AdeString,
    AdeBool,
    AdeNull,
    AdeList,
    AdeMap,
    AdeCallable,
    AdeFunction,
    AdeBuiltinFunction,
    AdeModule,
    AdeClass,
    AdeInstance,
    AdeBoundMethod,
)
from ade.runtime.environment import Environment
from ade.interpreter.signals import ReturnSignal, BreakSignal, ContinueSignal
from ade.interpreter.errors import AdeRuntimeError
from ade.modules.loader import ModuleLoader


class Interpreter:
    """Executes an Ade AST program."""

    def __init__(
        self,
        output_stream: Optional[TextIO] = None,
        source_code: Optional[str] = None,
        environment: Optional[Environment] = None,
        current_file_path: str = "<stdin>",
        module_loader: Optional[ModuleLoader] = None,
    ):
        self.output_stream = output_stream or sys.stdout
        self.source_code = source_code
        self.globals = environment or Environment()
        self.environment = self.globals
        self.current_file_path = current_file_path
        self.module_loader = module_loader or ModuleLoader()
        self._init_builtins()

    def _init_builtins(self) -> None:
        """Register built-in standard functions."""

        def _builtin_len(
            interpreter: Interpreter, args: List[AdeValue], span: SourceSpan
        ) -> AdeValue:
            val = args[0]
            if isinstance(val, AdeList):
                return AdeNumber(len(val.elements))
            if isinstance(val, AdeString):
                return AdeNumber(len(val.value))
            if isinstance(val, AdeMap):
                return AdeNumber(len(val.entries))
            raise AdeRuntimeError(
                f"Object of type '{val.type_name()}' has no length.",
                span=span,
                source_code=self.source_code,
                hint="Function 'len()' accepts lists, text strings, or maps."
            )

        def _builtin_type(
            interpreter: Interpreter, args: List[AdeValue], span: SourceSpan
        ) -> AdeValue:
            return AdeString(args[0].type_name())

        def _builtin_str(
            interpreter: Interpreter, args: List[AdeValue], span: SourceSpan
        ) -> AdeValue:
            return AdeString(args[0].to_string())

        def _builtin_range(
            interpreter: Interpreter, args: List[AdeValue], span: SourceSpan
        ) -> AdeValue:
            start_val = args[0]
            end_val = args[1]
            if not isinstance(start_val, AdeNumber) or not isinstance(end_val, AdeNumber):
                raise AdeRuntimeError(
                    "Arguments to 'range()' must be numbers.",
                    span=span,
                    source_code=self.source_code,
                )
            items = [
                AdeNumber(i)
                for i in range(int(start_val.value), int(end_val.value))
            ]
            return AdeList(items)

        self.globals.define("len", AdeBuiltinFunction("len", 1, _builtin_len))
        self.globals.define("type", AdeBuiltinFunction("type", 1, _builtin_type))
        self.globals.define("str", AdeBuiltinFunction("str", 1, _builtin_str))
        self.globals.define("range", AdeBuiltinFunction("range", 2, _builtin_range))

    def interpret(self, program: Program) -> AdeValue:
        """Execute the given program and return the result of the last expression."""
        last_value: AdeValue = AdeNull.INSTANCE
        for stmt in program.statements:
            last_value = self.execute(stmt)
        return last_value

    def execute(self, stmt: Statement) -> AdeValue:
        """Execute a single statement."""
        if isinstance(stmt, ExpressionStmt):
            return self.evaluate(stmt.expression)

        if isinstance(stmt, SayStmt):
            val = self.evaluate(stmt.expression)
            self.output_stream.write(val.to_string() + "\n")
            self.output_stream.flush()
            return val

        if isinstance(stmt, VarAssignmentStmt):
            return self._execute_assignment(stmt)

        if isinstance(stmt, BlockStmt):
            return self.execute_block(stmt, Environment(parent=self.environment))

        if isinstance(stmt, IfStmt):
            cond_val = self.evaluate(stmt.condition)
            if cond_val.is_truthy():
                return self.execute(stmt.then_branch)
            elif stmt.else_branch is not None:
                return self.execute(stmt.else_branch)
            return AdeNull.INSTANCE

        if isinstance(stmt, WhileStmt):
            last_val: AdeValue = AdeNull.INSTANCE
            while self.evaluate(stmt.condition).is_truthy():
                try:
                    last_val = self.execute_block(
                        stmt.body, Environment(parent=self.environment)
                    )
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return last_val

        if isinstance(stmt, ForStmt):
            return self._execute_for(stmt)

        if isinstance(stmt, FunctionDeclStmt):
            func = AdeFunction(
                name=stmt.name,
                params=stmt.params,
                body=stmt.body,
                closure=self.environment,
            )
            self.environment.define(stmt.name, func)
            return func

        if isinstance(stmt, ReturnStmt):
            ret_val = (
                self.evaluate(stmt.value) if stmt.value is not None else AdeNull.INSTANCE
            )
            raise ReturnSignal(ret_val)

        if isinstance(stmt, ImportStmt):
            mod = self.module_loader.load_module(
                stmt.module_name, self.current_file_path, stmt.span, self
            )
            name = stmt.alias or stmt.module_name
            self.environment.define(name, mod)
            return mod

        if isinstance(stmt, FromImportStmt):
            mod = self.module_loader.load_module(
                stmt.module_name, self.current_file_path, stmt.span, self
            )
            for orig_name, alias in stmt.symbols:
                val = mod.get_export(orig_name)
                if val is None:
                    raise AdeRuntimeError(
                        f"Module '{stmt.module_name}' has no export named '{orig_name}'.",
                        span=stmt.span,
                        source_code=self.source_code,
                    )
                self.environment.define(alias or orig_name, val)
            return mod

        if isinstance(stmt, ClassDeclStmt):
            super_klass = None
            if stmt.superclass:
                super_val = self.environment.get(stmt.superclass)
                if not isinstance(super_val, AdeClass):
                    raise AdeRuntimeError(
                        f"Superclass '{stmt.superclass}' is not a class.",
                        span=stmt.span,
                        source_code=self.source_code,
                    )
                super_klass = super_val

            methods: dict[str, AdeFunction] = {}
            for m in stmt.methods:
                methods[m.name] = AdeFunction(
                    name=m.name,
                    params=m.params,
                    body=m.body,
                    closure=self.environment,
                )
            klass = AdeClass(
                name=stmt.name,
                superclass=super_klass,
                fields=stmt.fields,
                methods=methods,
            )
            self.environment.define(stmt.name, klass)
            return klass

        if isinstance(stmt, BreakStmt):
            raise BreakSignal()

        if isinstance(stmt, ContinueStmt):
            raise ContinueSignal()

        raise AdeRuntimeError(
            f"Unknown statement node '{type(stmt).__name__}'.",
            span=stmt.span,
            source_code=self.source_code,
        )

    def execute_block(self, block: BlockStmt, environment: Environment) -> AdeValue:
        """Execute a block of statements within a new lexical scope."""
        previous_env = self.environment
        self.environment = environment
        last_val: AdeValue = AdeNull.INSTANCE
        try:
            for stmt in block.statements:
                last_val = self.execute(stmt)
        finally:
            self.environment = previous_env
        return last_val

    def _execute_assignment(self, stmt: VarAssignmentStmt) -> AdeValue:
        val = self.evaluate(stmt.value)

        if isinstance(stmt.target, Identifier):
            self.environment.assign(stmt.target.name, val)
            return val

        if isinstance(stmt.target, MemberAccessExpr):
            obj = self.evaluate(stmt.target.object)
            if isinstance(obj, AdeInstance):
                obj.set_member(stmt.target.member, val)
                return val
            if isinstance(obj, AdeMap):
                obj.entries[stmt.target.member] = val
                return val
            raise AdeRuntimeError(
                f"Cannot set property '{stmt.target.member}' on type '{obj.type_name()}'.",
                span=stmt.target.span,
                source_code=self.source_code,
                hint="Member assignment is supported on class instances and maps."
            )

        if isinstance(stmt.target, IndexAccessExpr):
            obj = self.evaluate(stmt.target.object)
            idx_val = self.evaluate(stmt.target.index)

            if isinstance(obj, AdeList):
                if not isinstance(idx_val, AdeNumber) or not isinstance(idx_val.value, int):
                    raise AdeRuntimeError(
                        "List index must be an integer.",
                        span=stmt.target.index.span,
                        source_code=self.source_code,
                    )
                idx = idx_val.value
                if idx < 0 or idx >= len(obj.elements):
                    raise AdeRuntimeError(
                        f"List index out of range (index {idx}, length {len(obj.elements)}).",
                        span=stmt.target.index.span,
                        source_code=self.source_code,
                    )
                obj.elements[idx] = val
                return val

            if isinstance(obj, AdeMap):
                key = idx_val.to_string()
                obj.entries[key] = val
                return val

            raise AdeRuntimeError(
                f"Cannot index into type '{obj.type_name()}'.",
                span=stmt.target.span,
                source_code=self.source_code,
            )

        raise AdeRuntimeError(
            "Invalid assignment target.",
            span=stmt.span,
            source_code=self.source_code,
        )

    def _execute_for(self, stmt: ForStmt) -> AdeValue:
        iterable = self.evaluate(stmt.iterable)
        last_val: AdeValue = AdeNull.INSTANCE

        items_to_iterate: List[AdeValue] = []
        if isinstance(iterable, AdeList):
            items_to_iterate = iterable.elements
        elif isinstance(iterable, AdeString):
            items_to_iterate = [AdeString(ch) for ch in iterable.value]
        elif isinstance(iterable, AdeMap):
            items_to_iterate = [AdeString(k) for k in iterable.entries.keys()]
        else:
            raise AdeRuntimeError(
                f"Type '{iterable.type_name()}' is not iterable.",
                span=stmt.iterable.span,
                source_code=self.source_code,
                hint="For loops can iterate over lists, strings, and maps."
            )

        for item in items_to_iterate:
            loop_env = Environment(parent=self.environment)
            loop_env.define(stmt.variable, item)
            try:
                last_val = self.execute_block(stmt.body, loop_env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

        return last_val

    # ========================================================================
    # Expression Evaluation
    # ========================================================================

    def evaluate(self, expr: Expression) -> AdeValue:
        """Evaluate an expression node and produce an AdeValue."""
        if isinstance(expr, NumberLiteral):
            return AdeNumber(expr.value)

        if isinstance(expr, StringLiteral):
            return AdeString(expr.value)

        if isinstance(expr, BoolLiteral):
            return AdeBool.TRUE if expr.value else AdeBool.FALSE

        if isinstance(expr, NullLiteral):
            return AdeNull.INSTANCE

        if isinstance(expr, Identifier):
            val = self.environment.get(expr.name)
            if val is None:
                raise AdeRuntimeError(
                    f"Undefined variable '{expr.name}'.",
                    span=expr.span,
                    source_code=self.source_code,
                    hint=f"Variable '{expr.name}' has not been assigned in this scope.",
                    suggested_fix=f"{expr.name} = ..."
                )
            return val

        if isinstance(expr, BinaryExpr):
            return self._evaluate_binary(expr)

        if isinstance(expr, UnaryExpr):
            return self._evaluate_unary(expr)

        if isinstance(expr, CallExpr):
            return self._evaluate_call(expr)

        if isinstance(expr, MemberAccessExpr):
            return self._evaluate_member_access(expr)

        if isinstance(expr, IndexAccessExpr):
            return self._evaluate_index_access(expr)

        if isinstance(expr, ListLiteral):
            elements = [self.evaluate(elem) for elem in expr.elements]
            return AdeList(elements)

        if isinstance(expr, MapLiteral):
            entries = {}
            for entry in expr.entries:
                k_val = self.evaluate(entry.key)
                v_val = self.evaluate(entry.value)
                entries[k_val.to_string()] = v_val
            return AdeMap(entries)

        if isinstance(expr, AnonymousFunctionExpr):
            return AdeFunction(
                name=None,
                params=expr.params,
                body=expr.body,
                closure=self.environment,
            )

        if isinstance(expr, StringInterpolationExpr):
            parts: List[str] = []
            for part in expr.parts:
                if isinstance(part, str):
                    parts.append(part)
                else:
                    val = self.evaluate(part)
                    parts.append(val.to_string())
            return AdeString("".join(parts))

        raise AdeRuntimeError(
            f"Unknown expression node '{type(expr).__name__}'.",
            span=expr.span,
            source_code=self.source_code,
        )

    def _evaluate_binary(self, expr: BinaryExpr) -> AdeValue:
        # Short-circuit logical operators
        if expr.operator.type == TokenType.OR:
            left = self.evaluate(expr.left)
            if left.is_truthy():
                return left
            return self.evaluate(expr.right)

        if expr.operator.type == TokenType.AND:
            left = self.evaluate(expr.left)
            if not left.is_truthy():
                return left
            return self.evaluate(expr.right)

        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        op_type = expr.operator.type

        # Equality
        if op_type == TokenType.EQUAL_EQUAL:
            return AdeBool.TRUE if left == right else AdeBool.FALSE
        if op_type == TokenType.BANG_EQUAL:
            return AdeBool.TRUE if left != right else AdeBool.FALSE

        # Addition / Concatenation
        if op_type == TokenType.PLUS:
            if isinstance(left, AdeNumber) and isinstance(right, AdeNumber):
                res = left.value + right.value
                return AdeNumber(res)
            if isinstance(left, AdeString) or isinstance(right, AdeString):
                return AdeString(left.to_string() + right.to_string())
            if isinstance(left, AdeList) and isinstance(right, AdeList):
                return AdeList(left.elements + right.elements)
            raise AdeRuntimeError(
                f"Cannot add types '{left.type_name()}' and '{right.type_name()}'.",
                span=expr.span,
                source_code=self.source_code,
                hint="'+' is supported between two numbers, two lists, or where at least one operand is text."
            )

        # Arithmetic operations (- , * , / , %)
        if op_type in (TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            if not isinstance(left, AdeNumber) or not isinstance(right, AdeNumber):
                raise AdeRuntimeError(
                    f"Operator '{expr.operator.lexeme}' requires number operands, got '{left.type_name()}' and '{right.type_name()}'.",
                    span=expr.span,
                    source_code=self.source_code,
                )
            if op_type == TokenType.MINUS:
                return AdeNumber(left.value - right.value)
            if op_type == TokenType.STAR:
                return AdeNumber(left.value * right.value)
            if op_type == TokenType.SLASH:
                if right.value == 0:
                    raise AdeRuntimeError(
                        "Division by zero.",
                        span=expr.span,
                        source_code=self.source_code,
                        hint="Check that the divisor expression does not evaluate to 0."
                    )
                val = left.value / right.value
                # If exact integer division, promote to int
                if isinstance(val, float) and val.is_integer():
                    val = int(val)
                return AdeNumber(val)
            if op_type == TokenType.PERCENT:
                if right.value == 0:
                    raise AdeRuntimeError(
                        "Modulo by zero.",
                        span=expr.span,
                        source_code=self.source_code,
                    )
                return AdeNumber(left.value % right.value)

        # Relational comparisons (<, <=, >, >=)
        if op_type in (
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            if isinstance(left, AdeNumber) and isinstance(right, AdeNumber):
                if op_type == TokenType.LESS:
                    return AdeBool.TRUE if left.value < right.value else AdeBool.FALSE
                if op_type == TokenType.LESS_EQUAL:
                    return AdeBool.TRUE if left.value <= right.value else AdeBool.FALSE
                if op_type == TokenType.GREATER:
                    return AdeBool.TRUE if left.value > right.value else AdeBool.FALSE
                if op_type == TokenType.GREATER_EQUAL:
                    return AdeBool.TRUE if left.value >= right.value else AdeBool.FALSE

            if isinstance(left, AdeString) and isinstance(right, AdeString):
                if op_type == TokenType.LESS:
                    return AdeBool.TRUE if left.value < right.value else AdeBool.FALSE
                if op_type == TokenType.LESS_EQUAL:
                    return AdeBool.TRUE if left.value <= right.value else AdeBool.FALSE
                if op_type == TokenType.GREATER:
                    return AdeBool.TRUE if left.value > right.value else AdeBool.FALSE
                if op_type == TokenType.GREATER_EQUAL:
                    return AdeBool.TRUE if left.value >= right.value else AdeBool.FALSE

            raise AdeRuntimeError(
                f"Cannot compare '{left.type_name()}' with '{right.type_name()}'.",
                span=expr.span,
                source_code=self.source_code,
            )

        raise AdeRuntimeError(
            f"Unsupported binary operator '{expr.operator.lexeme}'.",
            span=expr.span,
            source_code=self.source_code,
        )

    def _evaluate_unary(self, expr: UnaryExpr) -> AdeValue:
        operand = self.evaluate(expr.operand)
        if expr.operator.type == TokenType.MINUS:
            if not isinstance(operand, AdeNumber):
                raise AdeRuntimeError(
                    f"Unary '-' expects number operand, got '{operand.type_name()}'.",
                    span=expr.span,
                    source_code=self.source_code,
                )
            return AdeNumber(-operand.value)

        if expr.operator.type == TokenType.NOT:
            return AdeBool.FALSE if operand.is_truthy() else AdeBool.TRUE

        raise AdeRuntimeError(
            f"Unsupported unary operator '{expr.operator.lexeme}'.",
            span=expr.span,
            source_code=self.source_code,
        )

    def _evaluate_call(self, expr: CallExpr) -> AdeValue:
        callee = self.evaluate(expr.callee)

        pos_args: List[AdeValue] = []
        named_args: dict[str, AdeValue] = {}
        for arg in expr.arguments:
            if isinstance(arg, NamedArgExpr):
                named_args[arg.name] = self.evaluate(arg.value)
            else:
                pos_args.append(self.evaluate(arg))

        if not isinstance(callee, AdeCallable):
            raise AdeRuntimeError(
                f"Type '{callee.type_name()}' is not callable.",
                span=expr.callee.span,
                source_code=self.source_code,
                hint="Only functions, classes, and builtins can be called with '()'."
            )

        if isinstance(callee, AdeClass):
            return callee.call_with_args(self, pos_args, named_args, expr.span)

        if named_args and isinstance(callee, AdeFunction):
            ordered_args = []
            for i, param_name in enumerate(callee.params):
                if param_name in named_args:
                    ordered_args.append(named_args[param_name])
                elif i < len(pos_args):
                    ordered_args.append(pos_args[i])
                else:
                    raise AdeRuntimeError(
                        f"Missing required parameter '{param_name}'.",
                        span=expr.span,
                        source_code=self.source_code,
                    )
            return callee.call(self, ordered_args, expr.span)

        args = pos_args
        if callee.arity() != len(args):
            raise AdeRuntimeError(
                f"Expected {callee.arity()} argument(s), but got {len(args)}.",
                span=expr.span,
                source_code=self.source_code,
                hint=f"Function '{getattr(callee, 'name', '<callable>')}' requires exactly {callee.arity()} parameters."
            )

        return callee.call(self, args, expr.span)

    def _evaluate_member_access(self, expr: MemberAccessExpr) -> AdeValue:
        obj = self.evaluate(expr.object)

        if isinstance(obj, AdeMap):
            if expr.member in obj.entries:
                return obj.entries[expr.member]
            return AdeNull.INSTANCE

        if isinstance(obj, AdeModule):
            val = obj.get_export(expr.member)
            if val is not None:
                return val
            raise AdeRuntimeError(
                f"Module '{obj.name}' has no export named '{expr.member}'.",
                span=expr.span,
                source_code=self.source_code,
                hint=f"Available exports in '{obj.name}': {', '.join(obj.exports.keys())}"
            )

        if isinstance(obj, AdeInstance):
            val = obj.get_member(expr.member)
            if val is not None:
                return val
            raise AdeRuntimeError(
                f"Instance of '{obj.klass.name}' has no property or method '{expr.member}'.",
                span=expr.span,
                source_code=self.source_code,
            )

        if isinstance(obj, AdeClass):
            method = obj.find_method(expr.member)
            if method is not None:
                return method
            raise AdeRuntimeError(
                f"Class '{obj.name}' has no static method '{expr.member}'.",
                span=expr.span,
                source_code=self.source_code,
            )

        raise AdeRuntimeError(
            f"Cannot access member '.{expr.member}' on type '{obj.type_name()}'.",
            span=expr.span,
            source_code=self.source_code,
            hint="Member access is supported on maps, module exports, and class instances."
        )

    def _evaluate_index_access(self, expr: IndexAccessExpr) -> AdeValue:
        obj = self.evaluate(expr.object)
        idx_val = self.evaluate(expr.index)

        if isinstance(obj, AdeList):
            if not isinstance(idx_val, AdeNumber) or not isinstance(idx_val.value, int):
                raise AdeRuntimeError(
                    f"List index must be an integer, got '{idx_val.type_name()}'.",
                    span=expr.index.span,
                    source_code=self.source_code,
                )
            idx = idx_val.value
            if idx < 0 or idx >= len(obj.elements):
                raise AdeRuntimeError(
                    f"List index out of range (index {idx}, length {len(obj.elements)}).",
                    span=expr.span,
                    source_code=self.source_code,
                    hint="Indices in Ade lists are 0-indexed."
                )
            return obj.elements[idx]

        if isinstance(obj, AdeMap):
            key = idx_val.to_string()
            return obj.entries.get(key, AdeNull.INSTANCE)

        if isinstance(obj, AdeString):
            if not isinstance(idx_val, AdeNumber) or not isinstance(idx_val.value, int):
                raise AdeRuntimeError(
                    "String index must be an integer.",
                    span=expr.index.span,
                    source_code=self.source_code,
                )
            idx = idx_val.value
            if idx < 0 or idx >= len(obj.value):
                raise AdeRuntimeError(
                    f"String index out of range (index {idx}, length {len(obj.value)}).",
                    span=expr.span,
                    source_code=self.source_code,
                )
            return AdeString(obj.value[idx])

        raise AdeRuntimeError(
            f"Cannot index into type '{obj.type_name()}'.",
            span=expr.span,
            source_code=self.source_code,
            hint="Indexing is supported on lists, maps, and text strings."
        )
