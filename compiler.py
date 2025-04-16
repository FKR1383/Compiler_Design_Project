class Scanner:
    def __init__(self, input_path='input.txt'):
        self.input_path = input_path
        self.tokens_output_path = 'tokens.txt'
        self.errors_output_path = 'lexical_errors.txt'
        self.symbol_table_output_path = 'symbol_table.txt'

        self.line_number = 0
        self.symbol_table = {}
        self.symbol_table_index = 1
        self.tokens_by_line = {}
        self.errors_by_line = {}

        self.current_line = ''
        self.position = 0

        self.keywords = {'if', 'else', 'void', 'int', 'while', 'break', 'return'}
        self.symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<'}

        # Add all keywords to the symbol table initially
        for kw in sorted(self.keywords):
            self.symbol_table[kw] = self.symbol_table_index
            self.symbol_table_index += 1

    def read_file(self):
        with open(self.input_path, encoding='utf-8') as file:
            return file.readlines()

    def save_output_files(self):
        self.write_tokens()
        self.write_errors()
        self.write_symbol_table()

    def write_tokens(self):
        with open(self.tokens_output_path, 'w', encoding='utf-8') as f:
            for line in sorted(self.tokens_by_line.keys()):
                token_strs = ' '.join([f'({ttype}, {tval})' for (ttype, tval) in self.tokens_by_line[line]])
                f.write(f'{line}.	{token_strs}\n')

    def write_errors(self):
        with open(self.errors_output_path, 'w', encoding='utf-8') as f:
            if not self.errors_by_line:
                f.write('There is no lexical error.\n')
            else:
                for line in sorted(self.errors_by_line.keys()):
                    errs = ' '.join(self.errors_by_line[line])
                    f.write(f'{line}.	{errs}\n')

    def write_symbol_table(self):
        with open(self.symbol_table_output_path, 'w', encoding='utf-8') as f:
            for idx, lexeme in enumerate(self.symbol_table.keys(), start=1):
                f.write(f'{idx}.	{lexeme}\n')

    def scan(self):
        lines = self.read_file()
        while_comment = False
        comment_start_line = 0
        comment_buffer = ''
        for lineno, line in enumerate(lines, start=1):
            self.line_number = lineno
            self.current_line = line
            self.position = 0
            while self.position < len(self.current_line):
                if while_comment:
                    if self.current_line[self.position:self.position+2] == '*/':
                        while_comment = False
                        self.position += 2
                        continue
                    else:
                        comment_buffer += self.current_line[self.position]
                        self.position += 1
                        continue
                token = self.get_next_token()
                if token:
                    ttype, tval = token
                    if ttype == 'ERROR':
                        self.errors_by_line.setdefault(lineno, []).append(f'({tval[0]}, {tval[1]})')
                    elif ttype not in ['WHITESPACE', 'COMMENT']:
                        self.tokens_by_line.setdefault(lineno, []).append(token)

            if while_comment:
                comment_buffer += '\n'

        if while_comment:
            snippet = comment_buffer[:7] + '...' if len(comment_buffer) > 7 else comment_buffer
            self.errors_by_line.setdefault(comment_start_line, []).append(f'({snippet}, Unclosed comment)')

    def get_next_token(self):
        if self.position >= len(self.current_line):
            return None

        ch = self.current_line[self.position]

        if ch.isspace():
            self.position += 1
            return ('WHITESPACE', ch)

        # Comments
        if self.current_line[self.position:self.position+2] == '/*':
            end_pos = self.current_line.find('*/', self.position+2)
            if end_pos != -1:
                self.position = end_pos + 2
                return ('COMMENT', '/*...*/')
            else:
                self.position += 2
                return ('ERROR', ('/*', 'Unclosed comment'))

        if self.current_line[self.position:self.position+2] == '*/':
            self.position += 2
            return ('ERROR', ('*/', 'Unmatched comment'))

        # Two-char symbol: ==
        if self.current_line[self.position:self.position+2] == '==':
            self.position += 2
            return ('SYMBOL', '==')

        # SYMBOL with invalid follow-up (e.g., *#)
        if ch in self.symbols:
            if self.position + 1 < len(self.current_line):
                next_ch = self.current_line[self.position + 1]
                if next_ch not in self.symbols and not next_ch.isspace() and not next_ch.isalnum():
                    error_start = self.position
                    self.position += 2
                    return ('ERROR', (self.current_line[error_start:self.position], 'Invalid input'))
            self.position += 1
            return ('SYMBOL', ch)

        # NUM
        if ch.isdigit():
            start = self.position
            while self.position < len(self.current_line) and self.current_line[self.position].isdigit():
                self.position += 1
            num_end = self.position
            if self.position < len(self.current_line) and self.current_line[self.position].isalpha():
                self.position += 1
                return ('ERROR', (self.current_line[start:self.position], 'Invalid number'))
            return ('NUM', self.current_line[start:num_end])

        # ID or Keyword (with lookahead validation)
        if ch.isalpha():
            start = self.position
            while self.position < len(self.current_line) and self.current_line[self.position].isalnum():
                self.position += 1
            lexeme = self.current_line[start:self.position]

            if lexeme in self.keywords:
                if self.position < len(self.current_line) and self.current_line[self.position] not in self.symbols and not self.current_line[self.position].isspace():
                    while self.position < len(self.current_line) and self.current_line[self.position] not in self.symbols and not self.current_line[self.position].isspace():
                        self.position += 1
                    return ('ERROR', (self.current_line[start:self.position], 'Invalid input'))
                return ('KEYWORD', lexeme)
            else:
                if lexeme not in self.symbol_table:
                    self.symbol_table[lexeme] = self.symbol_table_index
                    self.symbol_table_index += 1
                return ('ID', lexeme)

        # Invalid input
        self.position += 1
        return ('ERROR', (ch, 'Invalid input'))


if __name__ == '__main__':
    scanner = Scanner()
    scanner.scan()
    scanner.save_output_files()
