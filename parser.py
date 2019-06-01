#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Grammar used for the purposes of the assignment.

Stmt_list -> Stmt Stmt_list | ε .
Stmt -> id : Expr | print Expr.
Expr -> Term Term_tail.
Term_tail -> Xorop Term Term_tail | ε .
Term -> Factor Factor_tail.
Factor_tail -> Orop Factor Factor_tail | ε .
Factor -> Operand Operand_tail.
Operand_tail -> Andop Operand Operand_tail | ε .
Operand -> ( Expr ) | id | binary.
Xorop -> xor.
Orop -> or.
Andop -> and.

FIRST sets
----------
Stmt_list: id print ε
Stmt: id print
Term_tail:  xor ε
Term: id binary
Factor_tail: or ε
Factor: ( id binary
Operand_tail: and ε
Operand: ( id binary
Expr: ( id binary
Xorop: xor
Orop: or
Andop: and

FOLLOW sets
-----------
Stmt_list:
Stmt: id print
Term_tail: ) id print
Term: ) xor id print
Factor_tail: ) xor id print
Factor: ) or xor id print
Operand_tail: ) or xor id print
Operand: ) and or xor id print
Expr: ) id print
Xorop: ( id binary
Orop: ( id binary
Andop: ( id binary
"""


import plex


class ParseError(Exception):
    """ A user defined exception class, to describe parse errors. """
    pass


class MyParser:
    """ A class encapsulating all parsing functionality
    for a particular grammar. """

    def create_scanner(self, fp):
        """ Creates a plex scanner for a particular grammar 
        to operate on file object fp. """

        # define some pattern constructs
        letter = plex.Range("AZaz")
        digit = plex.Range("09")
        binary = plex.Rep1(plex.Any("01"))

        id = letter + plex.Rep(letter | digit)
        operator = plex.Str("and", "or", "xor", "=")
        paren = plex.Any("()")
        space = plex.Any(" \t\n")
        comment = plex.Str("{") + plex.Rep(plex.AnyBut("}")) + plex.Str("}")
        keyword = plex.NoCase(plex.Str("print"))

        # the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
        lexicon = plex.Lexicon([
            (binary, "binary"),
            (operator, plex.TEXT),
            (keyword, plex.TEXT),
            (paren, plex.TEXT),
            (space | comment, plex.IGNORE),
            (id, 'id')
        ])

        # create and store the scanner object
        self.scanner = plex.Scanner(lexicon, fp)

        # get initial lookahead
        self.la, self.val = self.next_token()

    def next_token(self):
        """ Returns tuple (next_token,matched-text). """

        return self.scanner.read()

    def position(self):
        """ Utility function that returns position in text in case of errors.
        Here it simply returns the scanner position. """

        return self.scanner.position()

    def match(self, token):
        """ Consumes (matches with current lookahead) an expected token.
        Raises ParseError if anything else is found. Acquires new lookahead. """

        if self.la == token:
            self.la, self.val = self.next_token()
        else:
            raise ParseError("found {} instead of {}".format(self.la, token))

    def parse(self, fp):
        """ Creates scanner for input file object fp and calls the parse logic code. """

        # create the plex scanner for fp
        self.create_scanner(fp)

        self.stmt_list()

    def stmt_list(self):
        '''Stmt_list -> Stmt Stmt_list | ε .'''
        if self.la == 'id' or self.la == 'print':
            self.stmt()
            self.stmt_list()
        elif self.la is None:
            return
        else:
            raise ParseError("in stmt_list: id or print expected")

    def stmt(self):
        '''Stmt -> id : Expr | print Expr.'''
        if self.la == 'id':
            self.match('id')
            self.match('=')
            self.expr()
        elif self.la == 'print':
            self.match('print')
            self.expr()
        else:
            raise ParseError("in stmt: id or print expected")

    def expr(self):
        '''Expr -> Term Term_tail.'''
        # print(self.la)
        if self.la in ['id', 'binary', '(']:
            self.term()
            self.term_tail()
        else:
            raise ParseError("in expr: id, binary or '(' expected")

    def term(self):
        '''Term -> Factor Factor_tail.'''
        if self.la in ['id', 'binary', '(']:
            self.factor()
            self.factor_tail()
        else:
            raise ParseError("in term: id, binary or '(' expected")

    def term_tail(self):
        '''Term_tail -> Xorop Term Term_tail | ε .'''
        if self.la == 'xor':
            self.match('xor')
            self.term()
            self.term_tail()
        elif self.la is None or self.la in [')', 'id', 'print']:
            return
        else:
            raise ParseError("in term_tail: xor expected")

    def factor(self):
        '''Factor -> Operand Operand_tail.'''
        if self.la in ['id', 'binary', '(']:
            self.operand()
            self.operand_tail()
        else:
            raise ParseError("in factor: id, binary or '(' expected")

    def factor_tail(self):
        '''Factor_tail -> Orop Factor Factor_tail | ε .'''
        # print(self.la)
        if self.la == 'or':
            self.match('or')
            self.factor()
            self.factor_tail()
        elif self.la is None or self.la in [')', 'xor', 'id', 'print']:
            return
        else:
            raise ParseError("in factor_tail: or expected")

    def operand(self):
        '''Operand -> ( Expr ) | id | binary.'''
        if self.la == 'id':
            self.match('id')
        elif self.la == 'binary':
            self.match('binary')
        elif self.la == '(':
            self.match('(')
            self.expr()
            self.match(')')
        else:
            raise ParseError("in operand: id, binary or '(' expected")

    def operand_tail(self):
        '''Operand_tail -> Andop Operand Operand_tail | ε .'''
        if self.la == 'and':
            self.match('and')
            self.operand()
            self.operand_tail()
        elif self.la is None or self.la in [')', 'xor', 'or', 'id', 'print']:
            return
        else:
            raise ParseError("in operand_tail: or or '?' expected")

# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("binary.txt", "r") as fp:

    # parse file
    try:
        parser.parse(fp)
    except plex.errors.PlexError:
        _, lineno, charno = parser.position()
        print("Scanner Error: at line {} char {}".format(lineno, charno+1))
    except ParseError as perr:
        _, lineno, charno = parser.position()
        print("Parser Error: {} at line {} char {}".format(perr, lineno, charno+1))
print('Done!')
