class Node:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()

def direct_method(regex):
    postfix = []
    stack = []
    prec = {'*': 3, '.': 2, '|': 1, '(': 0}
    for token in regex:
        if token == '(':
            stack.append(token)
        elif token == ')':
            while stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        elif token in '|*.':
            while stack and prec[token] <= prec.get(stack[-1], -1):
                postfix.append(stack.pop())
            stack.append(token)
        else:
            postfix.append(token)
    while stack:
        postfix.append(stack.pop())

    stack = []
    for token in postfix:
        if token in '|*.':
            node = Node(token)
            node.right = stack.pop()
            node.left = stack.pop()
            if token == '|':
                node.nullable = node.left.nullable or node.right.nullable
                node.firstpos = node.left.firstpos | node.right.firstpos
                node.lastpos = node.left.lastpos | node.right.lastpos
            elif token == '*':
                node.nullable = True
                node.firstpos = node.left.firstpos
                node.lastpos = node.left.lastpos
            elif token == '.':
                node.nullable = node.left.nullable and node.right.nullable
                node.firstpos = node.left.firstpos
                if node.left.nullable:
                    node.firstpos |= node.right.firstpos
                node.lastpos = node.right.lastpos
                if node.right.nullable:
                    node.lastpos |= node.left.lastpos
            stack.append(node)
        else:
            node = Node(token)
            node.nullable = False
            node.firstpos = {len(stack)}
            node.lastpos = {len(stack)}
            stack.append(node)
    root = stack.pop()

    followpos = [set() for _ in range(len(stack) + 1)]
    def traverse(node):
        if node:
            traverse(node.left)
            traverse(node.right)
            if node.value == '.':
                for i in node.left.lastpos:
                    followpos[i] |= node.right.firstpos
            elif node.value == '*':
                for i in node.lastpos:
                    followpos[i] |= node.firstpos
    traverse(root)

    states = [root.firstpos]
    dfa = {}
    i = 0
    while i < len(states):
        state = states[i]
        for c in set(regex):
            if c != '|' and c != '*' and c != '.':
                new_state = set()
                for j in state:
                    if regex[j] == c:
                        new_state |= followpos[j]
                if new_state and new_state not in states:
                    states.append(new_state)
                dfa[(i, c)] = states.index(new_state) if new_state else None
        i += 1

    def traverse2(node):
      if node:
          traverse2(node.left)
          traverse2(node.right)
          if node.value == '|':
              node.firstpos = node.left.firstpos | node.right.firstpos
              node.lastpos = node.left.lastpos | node.right.lastpos
          elif node.value == '*':
              node.firstpos = node.left.firstpos
              node.lastpos = node.left.lastpos
          elif node.value == '.':
              node.firstpos = node.left.firstpos
              if node.left.nullable:
                  node.firstpos |= node.right.firstpos
              node.lastpos = node.right.lastpos
              if node.right.nullable:
                  node.lastpos |= node.left.lastpos
          else:
              node.firstpos = {node.value}
              node.lastpos = {node.value}
    traverse2(root)

    return dfa, followpos, root.firstpos, root.lastpos

def match_lexemes(sample_code, dfa, start_state=0):
    current_state = start_state
    lexemes = []
    lexeme = ''
    for i, c in enumerate(sample_code):
        if (current_state, c) in dfa:
            current_state = dfa[(current_state, c)]
            lexeme += c
            if current_state is None:
                lexeme = lexeme[:-1]
                lexemes.append(lexeme)
                lexeme = ''
                current_state = start_state
        else:
            if lexeme:
                lexemes.append(lexeme)
                lexeme = ''
                current_state = start_state
    if lexeme:
        lexemes.append(lexeme)
    return lexemes

def main():
    ident_regex = '[a-zA-Z_][a-zA-Z0-9_]*'
    num_regex = '\d+(\.\d+)?'

    sample_code = 'int num = 123; double pi = 3.14; String name = "John Doe";'


    ident_dfa, ident_followpos, ident_firstpos, ident_lastpos = direct_method(ident_regex)
    num_dfa, num_followpos, num_firstpos, num_lastpos = direct_method(num_regex)
    ident_lexemes = match_lexemes(sample_code, ident_dfa)
    num_lexemes = match_lexemes(sample_code, num_dfa)

    print('Sample code:', sample_code)
    print('Identifier DFA:', ident_dfa)
    print('Identifier followpos:', ident_followpos)
    print('Identifier firstpos:', ident_firstpos)
    print('Identifier lastpos:', ident_lastpos)
    print('Identifiers:', ident_lexemes)
    print('Numeric value DFA:', num_dfa)
    print('Numeric value followpos:', num_followpos)
    print('Numeric value firstpos:', num_firstpos)
    print('Numeric value lastpos:', num_lastpos)
    print('Numeric values:', num_lexemes)

main()