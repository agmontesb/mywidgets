import collections
import typing


class Tokenizer(typing.Iterable):

    Token = collections.namedtuple('Token', 'tag value')

    def __init__(self, scanner, skipTokens=('WHITESPACE',)):
        super(Tokenizer, self).__init__()
        self.scanner = scanner
        self.skipTokens = skipTokens

    def tokenize(self, strin):
        self.strIn = strin
        self.pos = 0
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

    def getPrevToken(self):
        return self._prevToken[1]
