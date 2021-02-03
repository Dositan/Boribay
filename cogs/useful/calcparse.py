import decimal
import math

from sly import Parser

from .calclex import CalcLexer
from utils.Exceptions import (
    CalcError,
    KeywordAlreadyTaken,
    Overflow,
    UndefinedVariable
)


class CalcParser(Parser):
    tokens = CalcLexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        ('left', '^'),
        ('left', '!'),
        ('right', UMINUS)
    )
    funcs = {
        'round': round,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'sqrt': lambda x: x.sqrt(),
        'abs': lambda x: x.copy_abs()
    }
    constants = {
        "pi": decimal.Decimal(math.pi),
        "e": decimal.Decimal(math.e),
        "tau": decimal.Decimal(math.tau),
        "inf": decimal.Decimal(math.inf),
        "nan": decimal.Decimal(math.nan)
    }

    @_('statement')
    @_('statements NEWLINE_CHAR statement')
    def statements(self, p):
        self.result.append(p.statement)

    @_('NAME "=" expression')
    def statement(self, p):
        if p.NAME in self.funcs or p.NAME in self.constants:
            raise KeywordAlreadyTaken()
        self.variables[p.NAME] = p.expression
        return f'{p.NAME} = {p.expression}'

    @_('expression')
    def statement(self, p):
        return p.expression

    @_('expression "+" expression')
    def expression(self, p):
        return p.expression0 + p.expression1

    @_('expression "-" expression')
    def expression(self, p):
        return p.expression0 - p.expression1

    @_('expression "*" expression')
    def expression(self, p):
        return p.expression0 * p.expression1

    @_('expression "/" expression')
    def expression(self, p):
        return p.expression0 / p.expression1

    @_('expression "%" expression')
    def expression(self, p):
        return p.expression0 % p.expression1

    @_('expression "^" expression')
    def expression(self, p):
        if p.expression0 > 200 or p.expression1 > 200:
            raise Overflow()
        return p.expression0 ** p.expression1

    @_('expression "!"')
    def expression(self, p):
        if p.expression > 50:
            raise Overflow()
        return decimal.Decimal(math.gamma(p.expression + decimal.Decimal("1.0")))

    @_('"-" expression %prec UMINUS')
    def expression(self, p):
        return -p.expression

    @_('"(" expression ")"')
    def expression(self, p):
        return p.expression

    @_('NAME "(" expression ")"')
    def expression(self, p):
        try:
            return decimal.Decimal(self.funcs[p.NAME](p.expression))
        except KeyError:
            raise UndefinedVariable(p.NAME)

    @_("NUMBER")
    def expression(self, p):
        return p.NUMBER

    @_("NAME")
    def expression(self, p):
        try:
            try:
                return self.constants[p.NAME]
            except KeyError:
                return self.variables[p.NAME]
        except KeyError:
            raise UndefinedVariable(p.NAME)

    def error(self, p):
        raise CalcError(getattr(p, "value", "EOF"))

    def __init__(self):
        self.variables = {}
        self.result = []
        super().__init__()

    @staticmethod
    def match(expression):
        o = tuple("({[")
        c = tuple(")}]")
        mapping = dict(zip(o, c))
        lis = []

        for letter in expression:
            if letter in o:
                lis.append(mapping[letter])
            elif letter in c:
                if not lis or letter != lis.pop():
                    return False
        return not lis

    def parse(self, expression):
        super().parse(expression)
        return self.result