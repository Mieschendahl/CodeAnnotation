import ast
from typing import Optional

class TypeAnnotationAndDocstringStripper(ast.NodeTransformer):
    def visit_Module(self, node: ast.Module) -> ast.Module:
        node.body = self.strip_docstring(node.body)
        node.body = [stmt for stmt in node.body if not isinstance(stmt, (ast.Import, ast.ImportFrom))]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        node.body = self.strip_docstring(node.body)
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node.returns = None
        self.generic_visit(node)
        node.body = self.strip_docstring(node.body)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        node.returns = None
        self.generic_visit(node)
        node.body = self.strip_docstring(node.body)
        return node

    def visit_Lambda(self, node: ast.Lambda) -> ast.Lambda:
        self.generic_visit(node)
        return node

    def visit_arguments(self, node: ast.arguments) -> ast.arguments:
        for arg in node.args + node.kwonlyargs:
            arg.annotation = None
        if node.vararg:
            node.vararg.annotation = None
        if node.kwarg:
            node.kwarg.annotation = None
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        node.annotation = None
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Optional[ast.Assign]:
        if node.value is not None:
            return ast.copy_location(ast.Assign(
                targets=[node.target],
                value=node.value
            ), node)
        return None

    def visit_Import(self, node: ast.Import) -> None:
        return None

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        return None

    def strip_docstring(self, body: list) -> list:
        if (
            body and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, (ast.Str, ast.Constant))
            and isinstance(getattr(body[0].value, "value", None), str)
        ):
            return body[1:]
        return body

def normalize_ast(code: str) -> ast.AST:
    tree = ast.parse(code)
    tree = TypeAnnotationAndDocstringStripper().visit(tree)
    ast.fix_missing_locations(tree)
    return tree

def is_safe(old_code: str, new_code: str) -> bool:
    try:
        tree1 = normalize_ast(old_code)
        tree2 = normalize_ast(new_code)
        return ast.dump(tree1, annotate_fields=True, include_attributes=False) == \
               ast.dump(tree2, annotate_fields=True, include_attributes=False)
    except SyntaxError:
        return False