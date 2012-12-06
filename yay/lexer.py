# Copyright 2012 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .errors import LexerError

from ply import lex

class Lexer(object):
    
    """ Leading significant whitespace lexing considered fugly. """
    
    def __init__(self):
        self.indents = {}
        # initial_indent holds the number of spaces prefixing the first real line
        # this is used as the leftmost indent level
        self.initial_indent = None
        self.remaining = []
        self.lineno = 0
        self.lexpos = 0
        self.finished = False
        
        # these handle state during token generation
        self.multiline = False
        self.template = None
        self.multiline_buffer = []
        self.last_level = 0
        self._generator = self._tokens()
        
    def input(self, text):
        self.remaining.extend(list(text))
        self.done() # is this right? PLY not clear
        
    def remaining_input(self):
        return "".join(self.remaining).strip()
    
    def read_line(self):
        """ Read a line from the input. """
        while self.remaining_input() or not self.finished:
            if not self.remaining:
                raise LexerError("Out of input", line=self.lineno)
            try:
                eol = self.remaining.index("\n")
            except ValueError:
                eol = len(self.remaining)
            line = self.remaining[:eol]
            self.remaining = self.remaining[eol+1:]
            self.lexpos += len(line)
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
        if self.initial_indent == None:
            self.initial_indent = spaces
        if spaces == self.initial_indent:
            # reset indenting
            self.indents = {}
            return 0
        if spaces < self.initial_indent:
            raise LexerError("Dedent below initial indent", line=self.lineno)
        if not self.indents:
            self.indents[spaces] = 1
            return 1
        level = self.indents.get(spaces, None)
        if level is not None:
            return level
        else:
            if spaces < max(self.indents.keys()):
                raise LexerError("Unindent to surprise level", line=self.lineno)
            else:
                self.indents[spaces] = max(self.indents.values())+1
                return self.indents[spaces]
            
    def get_spaces_for_level(self, level):
        insideout = dict((y,x) for (x,y) in self.indents.items())
        return insideout.get(level, 0)
            
    def done(self):
        self.finished = True
            
    def list_key_indent_level(self, line):
        """ This is the case where we have:
        
          - a: b
        
        We need to indent to the 'a' so we can continue to dict.
        """
        spaces, line = self.parse_indent(line)
        assert(line.startswith('-'))
        spaces2, line2 = self.parse_indent(line[1:])
        total_spaces = spaces + 1 + spaces2 # indent the '-' too
        return self.indent_level(total_spaces)

    def mktok(self, name, value=None):
        tok = lex.LexToken()
        tok.type = name
        tok.value = value
        tok.lineno = self.lineno
        tok.lexpos = self.lexpos
        return tok

    def emit_multiline(self):
        value = "\n".join(self.multiline_buffer) + "\n"
        if '{{' in value or \
           '\n%' in value:
            self.template = 'j2'
        if self.template is not None:
            token = self.mktok('TEMPLATE', (self.template, value))
        else:
            token = self.mktok('SCALAR', value)
        self.multiline = False
        self.template = None
        self.multiline_buffer = []
        return token
    
    def parse_key(self, key):
        """ Parse a key. Supports the following formats:
          key j2
          key extend j2
          key extend
          yay directive
          
          sets the template flag if required, and returns the key material and the extend flag
          
        """
        # TODO: cope with some weirdnesses like
        # yay include extend j2
        # which make no sense
        extend = False
        if ' ' not in key:
            return [self.mktok('KEY', key)]
        terms = key.split()
        if terms[-1] == 'j2':
            self.multiline = True
            self.template = 'j2'
            terms = terms[:-1]
        if terms[-1] == 'extend':
            extend = True
        if terms[0] == 'yay':
            return [self.mktok('DIRECTIVE', terms[1])]
        if extend:
            return [self.mktok('KEY', terms[0]), self.mktok('EXTEND')]
        else:
            return [self.mktok('KEY', terms[0])]
        
    def parse_value(self, value):
        """ Return either a template or a scalar, by sniffing the contents of
        the value """
        if value == '{}':
            return self.mktok('EMPTYDICT')
        elif value == '[]':
            return self.mktok('EMPTYLIST')
        if '{{' in value:
            return self.mktok('TEMPLATE', ('j2', value))
        else:
            return self.mktok('SCALAR', value)

    def _tokens(self):
        # this function is too long
        # but it is very hard to make shorter
        
        # initial block to wrap them all
        yield self.mktok('BLOCK')
        
        for raw_line in self.read_line():
            # handle indents
            spaces, line = self.parse_indent(raw_line)
            
            # blank lines are ignored, unless they are inside a multiline block
            # in which case they are included
            if not line:
                if self.multiline:
                    multiline_buffer.append('\n')
                continue
            
            # find the current indent level
            level = self.indent_level(spaces)
            
            # if the multiline flag is set we are not in standard token processing
            # this is a core state flag
            if self.multiline:
                if not self.multiline_buffer:
                    # first multiline
                    self.last_level = level
                if level == self.last_level:
                    self.multiline_buffer.append(line)
                    continue
                elif level < self.last_level:
                    yield self.emit_multiline()
                    # don't continue, go on to process what is on the line
                elif level > self.last_level:
                    prev_spaces = self.get_spaces_for_level(self.last_level)
                    self.multiline_buffer.append((spaces - prev_spaces) * ' ' + line)
                    continue
                
            # we are now processing non-multiline content
            
            # dedent with END tokens as required to achieve the correct level
            if level < self.last_level:
                for x in range(level, self.last_level):
                    yield self.mktok('END')
                    
            # stash the level
            self.last_level = level
            
            # see if the line starts with a key
            if ':' in line:
                
                # it's a key inside a list value
                if line.startswith('-'):
                    key, value = [x.strip() for x in line.split(":", 1)]
                    key = key[1:].strip()
                    yield self.mktok('LISTITEM')
                    yield self.mktok('BLOCK')
                    for token in self.parse_key(key):
                        yield token
                    yield self.mktok('BLOCK')
                    # push in the level so we end the block correctly
                    self.last_level = self.list_key_indent_level(raw_line)
                else:
                    key, value = [x.strip() for x in line.split(":", 1)]
                    for token in self.parse_key(key):
                        yield token
                    yield self.mktok('BLOCK')
                if value:
                    if value == '|':
                        self.multiline = True
                        continue
                    else:
                        yield self.parse_value(value)
                    yield self.mktok('END')
            else:
                if level == 0:
                    raise LexerError("No key found on a top level line", line=self.lineno)
                elif line.startswith("- "):
                    yield self.mktok('LISTITEM')
                    yield self.mktok('BLOCK')
                    yield self.parse_value(line[1:].strip())
                    yield self.mktok('END')
                else:
                    yield self.parse_value(line)
        if self.multiline:
            yield self.emit_multiline()
        for x in range(0, self.last_level):
            yield self.mktok('END')
        yield self.mktok('END')
        
    def token(self):
        return self._generator.next()
    
    def __iter__(self):
        for i in self._generator:
            yield i
                
    