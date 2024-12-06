from abc import ABC, abstractmethod


class AbstractNode(ABC):
    @abstractmethod
    def emit(self, emitter):
        pass


class ProgramNode(AbstractNode):
    def __init__(self):
        self.statements = []

    def add_statement(self, stmt):
        self.statements.append(stmt)

    def emit(self, emitter):
        emitter.emit_line("/* Begin Program */")
        for stmt in self.statements:
            stmt.emit(emitter)
        emitter.emit_line("/* End Program */")


class ClassNode(AbstractNode):
    def __init__(self, name):
        self.name = name
        self.members = []

    def add_member(self, member):
        self.members.append(member)

    def emit(self, emitter):
        emitter.emit_line(f"class {self.name} {{")
        for member in self.members:
            member.emit(emitter)
        emitter.emit_line("};")


class FunctionNode(AbstractNode):
    def __init__(self, name, params, return_type):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.statements = []

    def add_statement(self, stmt):
        self.statements.append(stmt)

    def emit(self, emitter):
        params_str = ", ".join(self.params)
        emitter.emit_line(f"{self.return_type} {self.name}({params_str}) {{")
        for stmt in self.statements:
            stmt.emit(emitter)
        emitter.emit_line("}")


# Define other nodes like StructNode, IfNode, LoopNode, etc. in the same manner
