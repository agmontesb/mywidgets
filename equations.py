# -*- coding: utf-8 -*-
import typing
import collections
import re
import tkinter as tk
import functools

SCANNER = re.compile(r'''
(?P<FUNCTION>(?:
    eq |   # equal
    ne |   # not equal
    le |   # less equal
    lt |   # less than
    ge |   # greater equal
    gt     # greater than
)) |                                
(?P<OPERATOR>(?:
    \+ |            # OR
    \* |            # AND
    \!              # NOT
 )) |           
(?P<PUNCTUATION>(?:
    \,      # comma
)) |
(?P<OPEN_TAG>(?:
    \(      # parenthesis
)) | 
(?P<CLOSE_TAG>(?:
    \)      # parenthesis
)) | 
(?P<CONSTANT>(?:
    (?:(?P<quote>["'])(.+?)(?P=quote)) |   # string
    (?:\b(?:true | false)\b)  |                 # bool
    (?:[0-9]+(?:\.[0-9]+)*))                    # float, int
) |                                
(?P<NAME>\b[_a-zA-Z][_a-zA-Z0-9]*\b) |           # string
(?P<WHITESPACE>\s+) |           # string
(?P<ERROR>.)            # an error
''', re.DOTALL | re.VERBOSE)


class EqTokenizer(typing.Iterable):

    Token = collections.namedtuple('Token', 'tag value')

    def __init__(self, scanner, skipTokens=('WHITESPACE',)):
        super(EqTokenizer, self).__init__()
        self.scanner = scanner
        self.skipTokens = skipTokens

    def tokenize(self, strin):
        self.strIn = strin
        self.pos = None
        self._nxtToken = (-1, self.Token('', '\0'))
        self._actToken = (-1, self.Token('', '\0'))
        self._prevToken = (-1, self.Token('', '\0'))
        return self

    def __iter__(self):
        self.pos = 0
        return self

    def _getNextToken(self):
        aStr = self.strIn
        p = self.pos
        while True:
            bFlag = 0 <= p < len(aStr)
            if not bFlag:
                m = None
                break
            m = self.scanner.match(aStr, p)
            case = m.lastgroup
            bFlag = not self.skipTokens or case not in self.skipTokens
            if bFlag: break
            p = m.end(case)
        try:
            case = m.lastgroup
            val = m.group(case)
            pos = m.end(case)
        except:
            return -1, self.Token('', '\0')
        return pos, self.Token(case, val)

    def __next__(self):
        self._prevToken = self._actToken
        pos, token = self._nxtToken \
            if self._nxtToken[0] > self.pos else \
            self._getNextToken()
        if token.value == '\0':
            raise StopIteration
        self.pos = pos
        self._actToken = (pos, token)
        return token

    def peek(self):
        if self._nxtToken[0] <= self.pos:
            self._nxtToken = self._getNextToken()
        return self._nxtToken[1]

    def currentLine(self):
        beg = self.strIn[:self.pos].rfind(';') + 1
        end = self.strIn[self.pos:].find(';')
        if end == -1:
            end = len(self.strIn)
        else:
            end += self.pos
        end += 1
        return self.strIn[beg:end].strip()

    def getContext(self):
        return self.strIn[self.pos:]

    def getNextChar(self):
        nxtToken = self.peek()
        return nxtToken.value[0] if nxtToken else '\0'

    def getPrevChar(self):
        prvToken = self._prevToken[1]
        strToken = '\0' if prvToken is None \
            else (
            prvToken.value[-1] if not prvToken.tag.endswith('_TAG')
            else prvToken.value[0]
        )
        return strToken


class Equations:
    '''
    Clase que maneja el estado de un widget determinado en por lo menos dos variables:
    enabled: El widget esta disponible para recibir información del usuario.
    visible: El widget es visible en la pantalla de la aplicación dado que se cumplen las
    condiciones para ello.
    Estas variables son booleans que se calculan con base en ecuaciones lógicas en que se
    establece de que variables externas depende el estado propio del widget.
    Las ecuaciones son expresiones que utilizan operadores relacionales como igual (eq),
    menor que (lt), mayor que (gt) y conectores lógicos OR (+) y AND (*). Ejemplos:
    visible = eq(ui_panel, 0) <=> ui_panel == 0.
    enabled = gt(quantity, 25) + eq(class, 2) <=> quantity > 25 OR class == 2
    Las Variables:
    Estas pueden apuntar a dos tipos de objetos: Variables tkinter (IntVar(), DoubleVar(),
    BooleanVar() y StringVar()) u otro objeto al que se pueda asignar un listener que
    reporte cuando el valor da la variable cambió y de esa manera afectar a las variables
    dependientes (aquellas en que la/ las ecuaciones visible y/o enabled dependen del valor
    de la variable que cambió)

    '''

    def __init__(self):
        self.tokenizer = EqTokenizer(SCANNER)
        self.var_values = {}
        self.state_equations = {}
        # Este dicionario mapea el nombre de la variable a sus equaciones asociadas o en caso de
        # ser una variable de estado (definida por una ecuación) las variables de las que depende.
        self.dependents = {}
        self.seq = 0
        self._default_root = None
        self.enable_callbacks = True    # inhabilita la ejecución de self.var_change
        pass

    def default_root(self):
        self._default_root = self._default_root or tk._default_root
        return self._default_root

    def isStateVar(self, var_name):
        '''
        Si var_name tiene asociada una ecuación devuelve True, en caso contrario False.
        :param var_name:
        :return: bool. True es una variable que define un estado (tiene ecuación) o no.
        '''
        return var_name in self.state_equations

    def add_equation(self, equation, callback):
        '''
        Agrega una ecuación que determina el 'state' de una variable determinada.
        :param equation: str. Expresión con que se calcula el estado asociado.
        :param callback: callable. Callback function que recibe un parámetro bool.
        :return: None.
        '''
        self.seq += 1
        state_var = f'_STATE_VAR{self.seq}_'
        vars, python_equiv = self.pythonize(equation)
        self.dependents[state_var] = vars
        for var in vars:
            dependents = self.dependents.setdefault(var, set())
            if not dependents:
                self.register_variable(var, self.var_change)
            dependents.add(state_var)
        self.state_equations[state_var] = python_equiv
        # init_state = self.eval_equation(python_equiv)
        # tk_state_var = tk.BooleanVar(name=state_var, value=init_state)
        tk_state_var = tk.BooleanVar(name=state_var)
        self.register_variable(state_var, callback)
        # tk_state_var.set(init_state)
        self.var_values[state_var] = tk_state_var
        pass

    def freeze_equations(self):
        '''
        Función que establece que el sistema de ecuaciones esta completo por lo cual no se
        permite agregar nuevas ecuaciones al conjunto. Esto se hace luego de procesar por
        completo el archvo de layout y poder establecer si existen inconsistencias en el
        sistema que se describe.
        return:
        '''
        self.set_initial_widget_state()

    def pythonize(self, equation):
        '''
        Convierte 'equation' en una expresión válida en python. Asume que las variables de la
        ecaución son objetos que con el método 'get' entregan el valor de la variable.
        :param equation: str. Ecuación a procesar.
        :return: 2-tuple. Primer elemento: variables independientes; segundo elemento: python expression.
        '''
        py_str = ''
        equivalence = {
            'le': '<=', 'lt': '<', 'ge': '>=', 'gt': '>',
            'eq': '==', 'ne': '!=',
            'true': 'True', 'false': 'False',
            '!': 'not', '+': 'or', '*': 'and'
        }
        var_names = set()
        wait = []
        for item in self.tokenizer.tokenize(equation):
            if item.tag == 'FUNCTION':
                wait.append(item.value)
            elif item.tag == 'PUNCTUATION':
                value = wait.pop()
                py_str += ' ' + equivalence[value] + ' '
            elif item.tag == 'CONSTANT' and item.value in ('true', 'false'):
                py_str += equivalence[item.value]
            elif item.tag == 'OPERATOR':
                py_str += ' ' + equivalence[item.value] + ' '
            elif item.tag == 'NAME':
                var_names.add(item.value)
                py_str += item.value
            else:
                py_str += item.value
        return var_names, py_str

    def eval_equation(self, python_expresion, vars):
        '''
        Evalúa una expresión python con el dict de varsiables independientes como 'globals' .
        :param python_expresion: str. Expresión python a evaluar.
        :return: bool. Resultado lógico de evaluear la expresión.
        '''
        locales = {key: self.var_values[key] for key in vars}
        state = eval(python_expresion, locales)
        return state

    def register_variable(self, var_name, callback):
        # Se establece el callback listener
        # tk crea una nueva variable cuando var_name no existe en caso contrario
        # entrega la variable ya existente.
        default_root = self.default_root()
        # try:
        #     value = default_root.getvar(var_name)
        # except:
        #     value = None
        tkApp = default_root.tk
        if tkApp.getboolean(tkApp.call("info", "exists", var_name)):
            value = default_root.getvar(var_name)
            try:
                value = eval(value)
            except:
                pass
        else:
            value = None        # Acá se determina si la variable no existe
        cb = default_root.register(callback)
        tkApp.call('trace', 'add', 'variable', var_name, 'write', (cb,))
        # Se registra la variable.
        # self.var_values[var_name] = value

    def set_initial_widget_states(self):
        # Se inicializan los widgets asociados a variables de control
        # Se inhabilita la ejecución de los trace-write functions
        self.enable_callbacks = False
        vars = self.var_values.keys() - self.state_equations.keys()
        default_root = self.default_root()
        for var_name in vars:
            var_value = self.var_values[var_name]
            default_root.setvar(var_name, var_value)
        # Se habilita la ejecución de los trace-write functions
        self.enable_callbacks = True

        if self.state_equations:
            self.set_widget_state(self.state_equations.keys())

    def set_widget_state(self, to_calculate):
        '''
        Establece el valor de las variables de estado to_calcualte.
        :param to_calculate: list. List of names of state_vars to calculate.
        :return:
        '''
        independents = functools.reduce(lambda t, x: t | self.dependents[x], to_calculate, set())
        python_exp = str([self.state_equations[state_var] for state_var in to_calculate])
        state_values = self.eval_equation(python_exp.replace('"', ''), independents)
        changed_states = [
            (value, key) for key, value in zip(to_calculate, state_values)
            if self.var_values[key].get() != value
        ]
        changed_states.sort()
        [self.var_values[key].set(value) for value, key in changed_states]

    def old_set_widget_state(self, dependents):
        changed_states = []
        for var_name in dependents:
            python_exp = self.state_equations[var_name]
            act_value = self.var_values.get(var_name, None)
            new_value = self.eval_equation(python_exp)
            if act_value == new_value:
                continue
            changed_states.append((new_value, var_name))
        changed_states.sort()
        # default_root = self.default_root()
        for state_value, var_name in changed_states:
            # default_root.setvar(var_name, state_value)
            # self.var_values[var_name] = state_value
            self.var_values[var_name].set(state_value)

    def var_change(self, var_name, name2, op):
        if not self.enable_callbacks:
            return
        default_root = equations_manager.default_root()
        value = default_root.getvar(var_name)
        try:
            self.var_values[var_name] = eval(value)
        except:
            self.var_values[var_name] = value
        to_verify = self.dependents.get(var_name, set())
        self.set_widget_state(to_verify)

equations_manager = Equations()


