"""
pygments lexer for Elementary Language (ELAN)

- Rainer Hahn, Peter Stock: ELAN Handbuch. 1979.
- Rainer Hahn, Dietmar Heinrichs, Peter Heyderhoff: EUMEL Benutzerhandbuch Version 1.7. 1984.
"""

from pygments.lexer import RegexLexer, bygroups, include, words
from pygments.token import *

__all__ = ['ElanLexer']

def uppercaseWords (l):
    """
    Match only uppercase words provided in l. For example FOR should not match
    FORMAT.
    """
    return words (l, prefix=r'(?<![A-Z])', suffix=r'(?![A-Z])')

class ElanLexer(RegexLexer):
    name = 'ELAN'
    aliases = ['elan']
    filenames = ['*.elan']

    tokens = {
        'root': [
            include('comment'),
            # strings
            (r'"', String.Double, 'string'),
            # numbers. lookbehind, because identifiers may contain numbers too
            (r'([-+]|(?<![a-z]))\d+', Number.Integer),
            (r'[-+]?\d+\.\d+(E[+-]?\d+)?', Number.Float),
            # keywords
            (uppercaseWords ((
                # not sure
                'CONCR',
                # if-then-else
                'IF', 'THEN', 'ELSE', 'ELIF', 'ENDIF', 'END IF',
                # found in the wild:
                'FI',
                # select statement
                'SELECT', 'OF', 'CASE', 'OTHERWISE', 'ENDSELECT', 'END SELECT',
                # loops
                'FOR', 'FROM', 'DOWNTO', 'UPTO', 'WHILE', 'REPEAT', 'UNTIL',
                'ENDREPEAT', 'END REPEAT',
                # found in the wild:
                'REP', 'PER', 'END REP',
                # return statements
                'LEAVE', 'WITH',
                )), Keyword.Reserved),
            (uppercaseWords ((
                # type declaration
                'TYPE',
                # shorthand declaration
                'LET',
                )), Keyword.Declaration),
            (uppercaseWords ((
                # proper packet
                'DEFINES',
                )), Keyword.Namespace),
            (uppercaseWords (('VAR', 'CONST', 'BOUND')), Name.Attribute),
            (uppercaseWords (('BOOL', 'INT', 'REAL', 'TEXT', 'STRUCT', 'ROW',
            'DATASPACE')), Keyword.Type),
            # thruth values
            (uppercaseWords (('TRUE', 'FALSE')), Name.Builtin),
            # semi-builtin functions/operators, see Benutzerhandbuch pp. 329
            # "Standartpakete"
            (uppercaseWords ((
                # boolean
                'NOT', 'AND', 'OR', 'XOR',
                # text
                'CAT', 'LENGTH', 'TIMESOUT',
                # math
                'DECR', 'DIV', 'INCR', 'MOD', 'SUB',
            )), Operator),
            # and the same with symbols
            (words ((
                # assignments
                ':=', '::',
                # comparison
                '=', '<>', '<=', '>=', '<', '>',
                # math
                '**', '*','+', '-', '/',
                ), prefix=r'(?<![:=<>*+-/])', suffix=r'(?![:=<>*+-/])'),
                Operator),
            # packets, function and operators
            # no space required between keyword and identifier
            # XXX comments may be allowed between keyword and name
            (r'((?:END\s*)?PACKET)([^A-Za-z]*)([a-z][a-z0-9 ]+)',
                    bygroups (Keyword.Declaration, Text, Name.Namespace)),
            (r'((?:END\s*)?PROC)([^A-Za-z]*)([a-z][a-z0-9 ]+)',
                    bygroups (Keyword.Declaration, Text, Name.Function)),
            (r'((?:END\s*)?OP)([^A-Za-z]*)([^a-z0-9 (;]+)',
                    bygroups (Keyword.Declaration, Text, Name.Function)),
            # Refinements
            (r'\.(?![a-z])', Text, 'refinement'),
            (r'.', Text),
        ],
        'comment': [
            (r'\(\*', Comment, 'comment-inside1'),
            (r'\{', Comment, 'comment-inside2'),
            (r'#\(', Comment, 'comment-inside3'),
        ],
        'comment-inside1': [
            # comment can be nested
            include('comment'),
            (r'\*\)', Comment, '#pop'),
            (r'(.|\n)', Comment),
        ],
        'comment-inside2': [
            # comment can be nested
            include('comment'),
            (r'\}', Comment, '#pop'),
            (r'(.|\n)', Comment),
        ],
        'comment-inside3': [
            # comment can be nested
            include('comment'),
            (r'#\)', Comment, '#pop'),
            (r'(.|\n)', Comment),
        ],
        'string': [
            # "" equals '\"', "12" is '\12'
            (r'"[0-9]*"', String.Escape),
            (r'"', String.Double, '#pop'),
            (r'.', String.Double),
        ],
        'refinement': [
            include('comment'),
            (r'\s+', Text),
            (r'([a-z][a-z0-9 ]*)(:\s+)', bygroups(Name.Label, Text), '#pop'),
            (r'', Text, '#pop'),
        ]
    }

