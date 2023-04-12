from pyparsing import Literal, CaselessLiteral, Word, Combine, Group, Optional, ZeroOrMore, Forward, nums, alphas, oneOf
import numpy as np
import operator
import functools


class NumericStringParser:
    def __init__(self, vars={}):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = Literal(".")
        var_literals = {}
        for var in vars:
            var_literals[var] = CaselessLiteral(var)
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        lt = Literal("<")
        le = Literal("<=")
        gt = Literal(">")
        ge = Literal(">=")
        eq = Literal("==")
        ne = Literal("!=")
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        compop = le | ge | eq | lt | gt | ne
        expr = Forward()
        to_parse = [ident + lpar + expr + rpar] + [var_literals[var]
                                                   for var in vars] + [fnumber]
        to_parse_or = functools.reduce(lambda x, y: x | y, to_parse)
        atom = ((Optional(oneOf("- +")) +
                 to_parse_or.setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        equation = expr + \
            ZeroOrMore((compop + expr).setParseAction(self.pushFirst))

        self.bnf = equation
        # map operator symbols to corresponding arithmetic operations
        self.vars = vars
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow}
        self.comp_eq = {"<=": operator.le,
                        ">=": operator.ge,
                        "==": operator.eq}
        self.comp_neq = {"<": operator.lt,
                         ">": operator.gt,
                         "!=": operator.ne}
        self.fn = {"sinh": np.sinh,
                   "cosh": np.cosh,
                   "tanh": np.tanh,
                   "sin": np.sin,
                   "cos": np.cos,
                   "tan": np.tan,
                   "exp": np.exp,
                   "ln": np.log,
                   "log": np.log,
                   "abs": np.abs,
                   "floor": np.floor,
                   "ceil": np.ceil,
                   "sign": np.sign,
                   "maximum": np.maximum,
                   "minimum": np.minimum,
                   "H": np.heaviside}

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')

    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        elif op in self.comp_eq:
            rhs = self.evaluateStack(s)
            lhs = self.evaluateStack(s)
            return self.comp_eq[op](lhs, rhs)
        elif op in self.comp_neq:
            rhs = self.evaluateStack(s)
            lhs = self.evaluateStack(s)
            return self.comp_neq[op](lhs, rhs)
        elif op in self.opn:
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op in self.vars:
            return self.vars[op]
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val


def parse_formula(vars, formula):
    nsp = NumericStringParser(vars)
    new_series = nsp.eval(formula)
    return new_series