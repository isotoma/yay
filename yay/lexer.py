
class LexerError(Exception):
    
    def __init__(self, message, lineno=None, line=None):
        self.message = message
        self.lineno = lineno
        self.line = line

class Token(object):
    
    def __init__(self, value=None):
        self.value = value
        
    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.value)
    
    def __cmp__(self, x):
        if self.__class__.__name__ == x.__class__.__name__ and self.value == x.value:
            return 0
        return 1

class BLOCK(Token):
    def __repr__(self):
        return "<BLOCK>"

class KEY(Token):
    pass

class VALUE(Token):
    pass

class ENDBLOCK(Token):
    def __repr__(self):
        return "<ENDBLOCK>"

class LISTVALUE(Token):
    pass

class Lexer(object):
    
    def __init__(self):
        self.indents = {}
        self.remaining = []
        self.lineno = 0
        self.finished = False
        
    def input(self, text):
        self.remaining.extend(list(text))
        
    def remaining_input(self):
        return "".join(self.remaining).strip()
    
    def read_line(self):
        """ Read a line from the input. """
        while self.remaining_input() or not self.finished:
            if not self.remaining:
                raise LexerError("Out of input")
            try:
                eol = self.remaining.index("\n")
            except ValueError:
                raise LexerError("Out of lines")
            line = self.remaining[:eol]
            self.remaining = self.remaining[eol+1:]
            self.lineno += 1
            line = "".join(line).rstrip(" ")
            # skip comments
            if not line.lstrip().startswith("#"):
                yield line
            
    def parse_indent(self, line):
        spaces = 0
        for char in line:
            if char == " ":
                spaces += 1
            else:
                return spaces, line[spaces:]
        return spaces, ""
    
    def indent_level(self, spaces):
        """ Return the correct indent level for the number of spaces """
        if spaces == 0:
            # reset indenting
            self.indents = {}
            return 0
        if not self.indents:
            self.indents[spaces] = 1
            return 1
        level = self.indents.get(spaces, None)
        if level is not None:
            return level
        else:
            if spaces < max(self.indents.keys()):
                raise LexerError("Unindent to surprise level", self.lineno)
            else:
                self.indents[spaces] = max(self.indents.values())+1
                return self.indents[spaces]
            
    def done(self):
        self.finished = True
            
    def tokens(self):
        last_level = 0
        for line in self.read_line():
            # handle indents
            spaces, line = self.parse_indent(line)
            if not line:
                # we ignore blank lines completely
                continue
            level = self.indent_level(spaces)
            if level < last_level:
                for x in range(level, last_level):
                    yield ENDBLOCK()
            last_level = level
            # see if the line starts with a key
            if ':' in line:
                key, value = [x.strip() for x in line.split(":", 1)]
                yield KEY(key)
                if value:
                    yield VALUE(value)
                    yield ENDBLOCK()
            else:
                if level == 0:
                    raise LexerError("No key found on a top level line", lineno, line)
                elif line.startswith("- "):
                    yield LISTVALUE(line[2:])
                else:
                    yield VALUE(line)
        for x in range(0, last_level):
            yield ENDBLOCK()
                
            