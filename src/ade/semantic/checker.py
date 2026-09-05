"""Static type checker and semantic analyzer for Ade."""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
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
    ImportStmt,
    FromImportStmt,
    ClassDeclStmt,
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
)
from ade.ast.visitor import ASTVisitor
from ade.diagnostics.diagnostic import Diagnostic, DiagnosticSeverity
from ade.diagnostics.span import SourceLocation, SourceSpan
from ade.semantic.symbols import Symbol, SymbolTable
from ade.types.model import (
    AdeType,
    PrimitiveType,
    ListType,
    MapType,
    NullableType,
    UnionType,
    FunctionType,
    ClassType,
    TYPE_NUMBER,
    TYPE_TEXT,
    TYPE_BOOL,
    TYPE_NULL,
    TYPE_ANY,
    TYPE_VOID,
    resolve_type_annotation,
)


class TypeChecker:
    """Performs static type checking and semantic analysis on an Ade AST."""

    def __init__(self, source_code: Optional[str] = None):
        self.source_code = source_code
        self.diagnostics: List[Diagnostic] = []
        self.global_scope = SymbolTable(name="global")
        self.current_scope = self.global_scope
        self.current_function: Optional[FunctionType] = None
        self.loop_depth = 0
        self._init_builtins()

    def visit(self, node: Optional[ASTNode]) -> Optional[AdeType]:
        """Dispatch visit to node-specific method visit_<NodeType>."""
        if node is None:
            return None
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> Optional[AdeType]:
        return None

    def _init_builtins(self) -> None:
        """Register built-in standard functions and modules in global scope."""
        dummy_span = SourceSpan.from_single(
            SourceLocation(file="<built-in>", line=1, column=1, offset=0)
        )

        # Built-in functions
        builtins = {
            "len": FunctionType(param_types=[("collection", TYPE_ANY)], return_type=TYPE_NUMBER),
            "range": FunctionType(param_types=[("limit", TYPE_NUMBER)], return_type=ListType(TYPE_NUMBER)),
            "type": FunctionType(param_types=[("value", TYPE_ANY)], return_type=TYPE_TEXT),
            "str": FunctionType(param_types=[("value", TYPE_ANY)], return_type=TYPE_TEXT),
            "num": FunctionType(param_types=[("value", TYPE_ANY)], return_type=TYPE_NUMBER),
            "push": FunctionType(param_types=[("list", ListType(TYPE_ANY)), ("item", TYPE_ANY)], return_type=TYPE_VOID),
            "pop": FunctionType(param_types=[("list", ListType(TYPE_ANY))], return_type=TYPE_ANY),
            "keys": FunctionType(param_types=[("map", MapType(TYPE_TEXT, TYPE_ANY))], return_type=ListType(TYPE_TEXT)),
            "values": FunctionType(param_types=[("map", MapType(TYPE_TEXT, TYPE_ANY))], return_type=ListType(TYPE_ANY)),
        }

        for name, func_type in builtins.items():
            self.global_scope.define(
                name,
                Symbol(name=name, type=func_type, span=dummy_span, is_function=True)
            )

        # Standard modules
        math_class = ClassType(
            name="math",
            fields={
                "pi": TYPE_NUMBER,
                "e": TYPE_NUMBER,
            },
            methods={
                "sqrt": FunctionType(param_types=[("x", TYPE_NUMBER)], return_type=TYPE_NUMBER),
                "sin": FunctionType(param_types=[("x", TYPE_NUMBER)], return_type=TYPE_NUMBER),
                "cos": FunctionType(param_types=[("x", TYPE_NUMBER)], return_type=TYPE_NUMBER),
                "tan": FunctionType(param_types=[("x", TYPE_NUMBER)], return_type=TYPE_NUMBER),
                "abs": FunctionType(param_types=[("x", TYPE_NUMBER)], return_type=TYPE_NUMBER),
                "floor": FunctionType(param_types=[("x", TYPE_NUMBER)], return_type=TYPE_NUMBER),
                "ceil": FunctionType(param_types=[("x", TYPE_NUMBER)], return_type=TYPE_NUMBER),
                "pow": FunctionType(param_types=[("base", TYPE_NUMBER), ("exp", TYPE_NUMBER)], return_type=TYPE_NUMBER),
            }
        )
        self.global_scope.define(
            "math",
            Symbol(name="math", type=math_class, span=dummy_span, is_class=True)
        )

        time_class = ClassType(
            name="time",
            methods={
                "now": FunctionType(param_types=[], return_type=TYPE_TEXT),
                "sleep": FunctionType(param_types=[("secs", TYPE_NUMBER)], return_type=TYPE_VOID),
                "timestamp": FunctionType(param_types=[], return_type=TYPE_NUMBER),
            }
        )
        self.global_scope.define(
            "time",
            Symbol(name="time", type=time_class, span=dummy_span, is_class=True)
        )

        json_class = ClassType(
            name="json",
            methods={
                "parse": FunctionType(param_types=[("text", TYPE_TEXT)], return_type=TYPE_ANY),
                "stringify": FunctionType(param_types=[("value", TYPE_ANY)], return_type=TYPE_TEXT),
            }
        )
        self.global_scope.define(
            "json",
            Symbol(name="json", type=json_class, span=dummy_span, is_class=True)
        )

        fs_class = ClassType(
            name="fs",
            methods={
                "read_text": FunctionType(param_types=[("path", TYPE_TEXT)], return_type=TYPE_TEXT),
                "write_text": FunctionType(param_types=[("path", TYPE_TEXT), ("content", TYPE_TEXT)], return_type=TYPE_VOID),
                "append_text": FunctionType(param_types=[("path", TYPE_TEXT), ("content", TYPE_TEXT)], return_type=TYPE_VOID),
                "exists": FunctionType(param_types=[("path", TYPE_TEXT)], return_type=TYPE_BOOL),
                "is_file": FunctionType(param_types=[("path", TYPE_TEXT)], return_type=TYPE_BOOL),
                "is_dir": FunctionType(param_types=[("path", TYPE_TEXT)], return_type=TYPE_BOOL),
                "list_dir": FunctionType(param_types=[("path", TYPE_TEXT)], return_type=ListType(TYPE_TEXT)),
                "remove": FunctionType(param_types=[("path", TYPE_TEXT)], return_type=TYPE_BOOL),
                "mkdir": FunctionType(param_types=[("path", TYPE_TEXT)], return_type=TYPE_BOOL),
            }
        )
        self.global_scope.define(
            "fs",
            Symbol(name="fs", type=fs_class, span=dummy_span, is_class=True)
        )

        os_class = ClassType(
            name="os",
            methods={
                "get_env": FunctionType(param_types=[("name", TYPE_TEXT), ("default", TYPE_TEXT)], return_type=TYPE_TEXT),
                "set_env": FunctionType(param_types=[("name", TYPE_TEXT), ("value", TYPE_TEXT)], return_type=TYPE_VOID),
                "platform": FunctionType(param_types=[], return_type=TYPE_TEXT),
                "cwd": FunctionType(param_types=[], return_type=TYPE_TEXT),
                "exit": FunctionType(param_types=[("code", TYPE_NUMBER)], return_type=TYPE_VOID),
                "args": FunctionType(param_types=[], return_type=ListType(TYPE_TEXT)),
            }
        )
        self.global_scope.define(
            "os",
            Symbol(name="os", type=os_class, span=dummy_span, is_class=True)
        )

        io_class = ClassType(
            name="io",
            methods={
                "read_line": FunctionType(param_types=[("prompt", TYPE_TEXT)], return_type=TYPE_TEXT),
                "print": FunctionType(param_types=[("value", TYPE_ANY)], return_type=TYPE_VOID),
                "println": FunctionType(param_types=[("value", TYPE_ANY)], return_type=TYPE_VOID),
                "eprintln": FunctionType(param_types=[("value", TYPE_ANY)], return_type=TYPE_VOID),
            }
        )
        self.global_scope.define(
            "io",
            Symbol(name="io", type=io_class, span=dummy_span, is_class=True)
        )

    def check(self, program: Program) -> List[Diagnostic]:
        """Perform type checking across the entire program AST and return all diagnostics."""
        self.visit(program)
        return self.diagnostics

    def _error(
        self,
        message: str,
        span: SourceSpan,
        title: str = "Type Error",
        hint: Optional[str] = None,
        suggested_fix: Optional[str] = None,
    ) -> None:
        self.diagnostics.append(
            Diagnostic(
                severity=DiagnosticSeverity.ERROR,
                title=title,
                message=message,
                span=span,
                source_code=self.source_code,
                hint=hint,
                suggested_fix=suggested_fix,
            )
        )

    def _warn(
        self,
        message: str,
        span: SourceSpan,
        title: str = "Type Warning",
        hint: Optional[str] = None,
        suggested_fix: Optional[str] = None,
    ) -> None:
        self.diagnostics.append(
            Diagnostic(
                severity=DiagnosticSeverity.WARNING,
                title=title,
                message=message,
                span=span,
                source_code=self.source_code,
                hint=hint,
                suggested_fix=suggested_fix,
            )
        )

    def _lookup_custom_type(self, name: str) -> Optional[AdeType]:
        sym = self.current_scope.resolve(name)
        if sym is not None:
            return sym.type
        return None

    # ========================================================================
    # Statements
    # ========================================================================

    def visit_Program(self, node: Program) -> Optional[AdeType]:
        for stmt in node.statements:
            self.visit(stmt)
        return None

    def visit_BlockStmt(self, node: BlockStmt) -> Optional[AdeType]:
        previous_scope = self.current_scope
        self.current_scope = SymbolTable(parent=previous_scope, name="block")
        for stmt in node.statements:
            self.visit(stmt)
        self.current_scope = previous_scope
        return None

    def visit_ExpressionStmt(self, node: ExpressionStmt) -> Optional[AdeType]:
        self.visit(node.expression)
        return None

    def visit_VarAssignmentStmt(self, node: VarAssignmentStmt) -> Optional[AdeType]:
        val_type = self.visit(node.value) or TYPE_ANY

        declared_type: Optional[AdeType] = None
        if node.type_annotation is not None:
            declared_type = resolve_type_annotation(
                node.type_annotation, self._lookup_custom_type
            )

        if isinstance(node.target, Identifier):
            var_name = node.target.name
            existing_sym = self.current_scope.resolve(var_name)

            if declared_type is not None:
                # Type annotation explicitly provided
                if not val_type.is_assignable_to(declared_type):
                    self._error(
                        message=f"Type mismatch: cannot assign value of type '{val_type}' to variable '{var_name}' with type '{declared_type}'.",
                        span=node.value.span,
                        hint=f"Expected an expression compatible with '{declared_type}', but found '{val_type}'.",
                        suggested_fix=f"Change the assigned value or adjust the type annotation to '{val_type}'."
                    )
                # Register in local scope
                self.current_scope.define(
                    var_name,
                    Symbol(name=var_name, type=declared_type, span=node.span)
                )
            else:
                # No type annotation
                if existing_sym is not None and existing_sym.type is not TYPE_ANY:
                    # Variable has an already established type
                    if not val_type.is_assignable_to(existing_sym.type):
                        self._error(
                            message=f"Type mismatch: cannot assign value of type '{val_type}' to variable '{var_name}' of type '{existing_sym.type}'.",
                            span=node.value.span,
                            hint=f"Variable '{var_name}' was previously defined with type '{existing_sym.type}'.",
                            suggested_fix=f"Assign a value compatible with '{existing_sym.type}' or create a new variable."
                        )
                else:
                    # Inferred type
                    inferred_type = val_type if val_type is not TYPE_NULL else TYPE_ANY
                    self.current_scope.define(
                        var_name,
                        Symbol(name=var_name, type=inferred_type, span=node.span)
                    )
        else:
            # Assignment to member or index: e.g. user.age = 20 or list[0] = 1
            target_type = self.visit(node.target) or TYPE_ANY
            if declared_type is not None and not val_type.is_assignable_to(declared_type):
                self._error(
                    message=f"Type mismatch: cannot assign '{val_type}' to declared type '{declared_type}'.",
                    span=node.value.span,
                )
            elif target_type is not TYPE_ANY and not val_type.is_assignable_to(target_type):
                self._error(
                    message=f"Type mismatch: cannot assign value of type '{val_type}' to target of type '{target_type}'.",
                    span=node.value.span,
                )

        return None

    def visit_SayStmt(self, node: SayStmt) -> Optional[AdeType]:
        self.visit(node.expression)
        return None

    def visit_IfStmt(self, node: IfStmt) -> Optional[AdeType]:
        cond_type = self.visit(node.condition)
        # Any type is truthy/falsy in Ade
        self.visit(node.then_branch)
        if node.else_branch is not None:
            self.visit(node.else_branch)
        return None

    def visit_WhileStmt(self, node: WhileStmt) -> Optional[AdeType]:
        self.visit(node.condition)
        self.loop_depth += 1
        self.visit(node.body)
        self.loop_depth -= 1
        return None

    def visit_ForStmt(self, node: ForStmt) -> Optional[AdeType]:
        iter_type = self.visit(node.iterable) or TYPE_ANY
        elem_type: AdeType = TYPE_ANY

        if isinstance(iter_type, ListType):
            elem_type = iter_type.element_type
        elif iter_type == TYPE_TEXT:
            elem_type = TYPE_TEXT
        elif isinstance(iter_type, MapType):
            elem_type = iter_type.key_type

        previous_scope = self.current_scope
        self.current_scope = SymbolTable(parent=previous_scope, name=f"for_{node.variable}")
        self.current_scope.define(
            node.variable,
            Symbol(name=node.variable, type=elem_type, span=node.span)
        )
        self.loop_depth += 1
        for s in node.body.statements:
            self.visit(s)
        self.loop_depth -= 1
        self.current_scope = previous_scope
        return None

    def visit_FunctionDeclStmt(self, node: FunctionDeclStmt) -> Optional[AdeType]:
        return_type = (
            resolve_type_annotation(node.return_type, self._lookup_custom_type)
            if node.return_type is not None
            else TYPE_ANY
        )

        param_types: List[Tuple[str, AdeType]] = []
        for p_name in node.params:
            ann = node.param_types.get(p_name) if node.param_types else None
            p_type = resolve_type_annotation(ann, self._lookup_custom_type)
            param_types.append((p_name, p_type))

        func_type = FunctionType(param_types=param_types, return_type=return_type)
        self.current_scope.define(
            node.name,
            Symbol(name=node.name, type=func_type, span=node.span, is_function=True)
        )

        # Enter function scope and analyze body
        previous_scope = self.current_scope
        previous_function = self.current_function
        self.current_scope = SymbolTable(parent=previous_scope, name=f"func_{node.name}")
        self.current_function = func_type

        for p_name, p_type in param_types:
            self.current_scope.define(
                p_name,
                Symbol(name=p_name, type=p_type, span=node.span)
            )

        for s in node.body.statements:
            self.visit(s)

        self.current_scope = previous_scope
        self.current_function = previous_function
        return None

    def visit_ReturnStmt(self, node: ReturnStmt) -> Optional[AdeType]:
        if self.current_function is None:
            self._error(
                message="Return statement outside of function.",
                span=node.span,
                hint="'return' can only be used inside a function body."
            )
            return None

        val_type = (
            self.visit(node.value) if node.value is not None else TYPE_NULL
        ) or TYPE_NULL

        expected_return = self.current_function.return_type
        if expected_return is not TYPE_ANY and expected_return is not TYPE_VOID:
            if not val_type.is_assignable_to(expected_return):
                self._error(
                    message=f"Return type mismatch: expected return type '{expected_return}', but returned '{val_type}'.",
                    span=node.value.span if node.value else node.span,
                    hint=f"Function signature declares return type '{expected_return}'.",
                    suggested_fix=f"Return a value compatible with '{expected_return}' or adjust the function signature."
                )

        return None

    def visit_BreakStmt(self, node: BreakStmt) -> Optional[AdeType]:
        if self.loop_depth <= 0:
            self._error(
                message="'break' outside of loop.",
                span=node.span,
                hint="'break' can only appear inside 'while' or 'for' loops."
            )
        return None

    def visit_ContinueStmt(self, node: ContinueStmt) -> Optional[AdeType]:
        if self.loop_depth <= 0:
            self._error(
                message="'continue' outside of loop.",
                span=node.span,
                hint="'continue' can only appear inside 'while' or 'for' loops."
            )
        return None

    def visit_ImportStmt(self, node: ImportStmt) -> Optional[AdeType]:
        # Bind module symbol as ClassType/Any
        mod_name = node.alias if node.alias else node.module_name
        existing = self.global_scope.resolve(node.module_name)
        mod_type = existing.type if existing else TYPE_ANY
        self.current_scope.define(
            mod_name,
            Symbol(name=mod_name, type=mod_type, span=node.span)
        )
        return None

    def visit_FromImportStmt(self, node: FromImportStmt) -> Optional[AdeType]:
        mod_sym = self.global_scope.resolve(node.module_name)
        for original, alias in node.symbols:
            bound_name = alias if alias else original
            sym_type = TYPE_ANY
            if mod_sym and isinstance(mod_sym.type, ClassType):
                if original in mod_sym.type.methods:
                    sym_type = mod_sym.type.methods[original]
                elif original in mod_sym.type.fields:
                    sym_type = mod_sym.type.fields[original]
            self.current_scope.define(
                bound_name,
                Symbol(name=bound_name, type=sym_type, span=node.span)
            )
        return None

    def visit_ClassDeclStmt(self, node: ClassDeclStmt) -> Optional[AdeType]:
        class_type = ClassType(name=node.name)
        self.current_scope.define(
            node.name,
            Symbol(name=node.name, type=class_type, span=node.span, is_class=True)
        )

        for f in node.fields:
            class_type.fields[f] = TYPE_ANY

        # Check methods
        previous_scope = self.current_scope
        self.current_scope = SymbolTable(parent=previous_scope, name=f"class_{node.name}")
        self.current_scope.define("self", Symbol(name="self", type=class_type, span=node.span))

        for method in node.methods:
            ret_type = (
                resolve_type_annotation(method.return_type, self._lookup_custom_type)
                if method.return_type
                else TYPE_ANY
            )
            p_types = [
                (p, resolve_type_annotation(method.param_types.get(p) if method.param_types else None, self._lookup_custom_type))
                for p in method.params
            ]
            m_type = FunctionType(param_types=p_types, return_type=ret_type)
            class_type.methods[method.name] = m_type

            # Visit method body
            self.visit_FunctionDeclStmt(method)

        self.current_scope = previous_scope
        return None

    # ========================================================================
    # Expressions
    # ========================================================================

    def visit_NumberLiteral(self, node: NumberLiteral) -> Optional[AdeType]:
        return TYPE_NUMBER

    def visit_StringLiteral(self, node: StringLiteral) -> Optional[AdeType]:
        return TYPE_TEXT

    def visit_BoolLiteral(self, node: BoolLiteral) -> Optional[AdeType]:
        return TYPE_BOOL

    def visit_NullLiteral(self, node: NullLiteral) -> Optional[AdeType]:
        return TYPE_NULL

    def visit_Identifier(self, node: Identifier) -> Optional[AdeType]:
        sym = self.current_scope.resolve(node.name)
        if sym is None:
            self._error(
                message=f"Undefined variable '{node.name}'.",
                span=node.span,
                hint=f"Variable '{node.name}' is referenced before being defined or imported.",
                suggested_fix=f"Define '{node.name}' before use, e.g. '{node.name} = ...'."
            )
            return TYPE_ANY
        return sym.type

    def visit_BinaryExpr(self, node: BinaryExpr) -> Optional[AdeType]:
        left = self.visit(node.left) or TYPE_ANY
        right = self.visit(node.right) or TYPE_ANY
        op = node.operator.lexeme

        if op == "+":
            if left == TYPE_NUMBER and right == TYPE_NUMBER:
                return TYPE_NUMBER
            if left == TYPE_TEXT or right == TYPE_TEXT:
                return TYPE_TEXT
            if left is TYPE_ANY or right is TYPE_ANY:
                return TYPE_ANY
            self._warn(
                message=f"Operator '+' applied to incompatible types '{left}' and '{right}'.",
                span=node.span,
                hint="In Ade, '+' performs numeric addition on numbers or string concatenation if either operand is text."
            )
            return TYPE_ANY

        if op in ("-", "*", "/", "%"):
            if left is not TYPE_ANY and left != TYPE_NUMBER:
                self._error(
                    message=f"Operator '{op}' requires numeric left operand, got '{left}'.",
                    span=node.left.span,
                )
            if right is not TYPE_ANY and right != TYPE_NUMBER:
                self._error(
                    message=f"Operator '{op}' requires numeric right operand, got '{right}'.",
                    span=node.right.span,
                )
            return TYPE_NUMBER

        if op in ("<", "<=", ">", ">="):
            if left is not TYPE_ANY and right is not TYPE_ANY and left != right:
                self._warn(
                    message=f"Comparison '{op}' between different types '{left}' and '{right}'.",
                    span=node.span,
                )
            return TYPE_BOOL

        if op in ("==", "!="):
            return TYPE_BOOL

        if op in ("and", "or"):
            return TYPE_BOOL

        return TYPE_ANY

    def visit_UnaryExpr(self, node: UnaryExpr) -> Optional[AdeType]:
        operand_type = self.visit(node.operand) or TYPE_ANY
        op = node.operator.lexeme

        if op == "-":
            if operand_type is not TYPE_ANY and operand_type != TYPE_NUMBER:
                self._error(
                    message=f"Unary '-' expects number operand, got '{operand_type}'.",
                    span=node.operand.span,
                )
            return TYPE_NUMBER

        if op == "not":
            return TYPE_BOOL

        return TYPE_ANY

    def visit_CallExpr(self, node: CallExpr) -> Optional[AdeType]:
        callee_type = self.visit(node.callee) or TYPE_ANY

        # Check if callee is a Class (instantiation)
        if isinstance(callee_type, ClassType):
            # Class instantiation returns the class instance
            return callee_type

        if isinstance(callee_type, FunctionType):
            expected_count = len(callee_type.param_types)
            actual_count = len(node.arguments)
            if actual_count != expected_count:
                self._error(
                    message=f"Function expected {expected_count} arguments, but got {actual_count}.",
                    span=node.span,
                    hint=f"Signature: {callee_type}"
                )
            else:
                for (p_name, p_type), arg in zip(callee_type.param_types, node.arguments):
                    arg_type = self.visit(arg) or TYPE_ANY
                    if p_type is not TYPE_ANY and not arg_type.is_assignable_to(p_type):
                        self._error(
                            message=f"Argument type mismatch for parameter '{p_name}': expected '{p_type}', found '{arg_type}'.",
                            span=arg.span,
                            hint=f"Parameter '{p_name}' requires a value of type '{p_type}'.",
                            suggested_fix=f"Pass a value compatible with '{p_type}'."
                        )
            return callee_type.return_type

        # For any untyped callable, analyze arguments and return ANY
        for arg in node.arguments:
            self.visit(arg)
        return TYPE_ANY

    def visit_NamedArgExpr(self, node: NamedArgExpr) -> Optional[AdeType]:
        return self.visit(node.value)

    def visit_MemberAccessExpr(self, node: MemberAccessExpr) -> Optional[AdeType]:
        obj_type = self.visit(node.object) or TYPE_ANY
        if isinstance(obj_type, ClassType):
            if node.member in obj_type.methods:
                return obj_type.methods[node.member]
            if node.member in obj_type.fields:
                return obj_type.fields[node.member]
            # Unknown member on typed class
            self._warn(
                message=f"Member '{node.member}' not declared on class '{obj_type.name}'.",
                span=node.span,
                hint=f"Class '{obj_type.name}' declares: {', '.join(list(obj_type.fields.keys()) + list(obj_type.methods.keys()))}"
            )
            return TYPE_ANY
        return TYPE_ANY

    def visit_IndexAccessExpr(self, node: IndexAccessExpr) -> Optional[AdeType]:
        obj_type = self.visit(node.object) or TYPE_ANY
        idx_type = self.visit(node.index) or TYPE_ANY

        if isinstance(obj_type, ListType):
            if idx_type is not TYPE_ANY and idx_type != TYPE_NUMBER:
                self._error(
                    message=f"List index must be a number, got '{idx_type}'.",
                    span=node.index.span,
                )
            return obj_type.element_type

        if isinstance(obj_type, MapType):
            if idx_type is not TYPE_ANY and not idx_type.is_assignable_to(obj_type.key_type):
                self._error(
                    message=f"Map key must be '{obj_type.key_type}', got '{idx_type}'.",
                    span=node.index.span,
                )
            return obj_type.value_type

        if obj_type == TYPE_TEXT:
            return TYPE_TEXT

        return TYPE_ANY

    def visit_ListLiteral(self, node: ListLiteral) -> Optional[AdeType]:
        if not node.elements:
            return ListType(element_type=TYPE_ANY)

        elem_types = [self.visit(elem) or TYPE_ANY for elem in node.elements]
        first_t = elem_types[0]
        if all(t == first_t for t in elem_types):
            return ListType(element_type=first_t)
        return ListType(element_type=TYPE_ANY)

    def visit_MapLiteral(self, node: MapLiteral) -> Optional[AdeType]:
        for entry in node.entries:
            self.visit(entry.key)
            self.visit(entry.value)
        return MapType(key_type=TYPE_TEXT, value_type=TYPE_ANY)

    def visit_AnonymousFunctionExpr(self, node: AnonymousFunctionExpr) -> Optional[AdeType]:
        return_type = (
            resolve_type_annotation(node.return_type, self._lookup_custom_type)
            if node.return_type
            else TYPE_ANY
        )
        param_types: List[Tuple[str, AdeType]] = []
        for p_name in node.params:
            ann = node.param_types.get(p_name) if node.param_types else None
            p_type = resolve_type_annotation(ann, self._lookup_custom_type)
            param_types.append((p_name, p_type))

        func_type = FunctionType(param_types=param_types, return_type=return_type)

        previous_scope = self.current_scope
        previous_function = self.current_function
        self.current_scope = SymbolTable(parent=previous_scope, name="anon_func")
        self.current_function = func_type

        for p_name, p_type in param_types:
            self.current_scope.define(
                p_name,
                Symbol(name=p_name, type=p_type, span=node.span)
            )

        for s in node.body.statements:
            self.visit(s)

        self.current_scope = previous_scope
        self.current_function = previous_function
        return func_type

    def visit_StringInterpolationExpr(self, node: StringInterpolationExpr) -> Optional[AdeType]:
        for part in node.parts:
            if isinstance(part, Expression):
                self.visit(part)
        return TYPE_TEXT
