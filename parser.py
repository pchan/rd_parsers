#!/usr/bin/env python

# This is the generic parser framework. 
# It initializes the lexer, defines the input string that make up
import logging
import sys
#Please see README on how to get this lexer
import lexer

# Implements a recursive descent parser for thea above grammar(calculator)
# Since this is LL(1) no backtracking is needed
# Does not suffer from associativity problems.
class Parser(object):

    def __init__(self, rules):
        # initialize the lex rules for the grammar 
        self.lx = lexer.Lexer(rules, skip_whitespace=True)
        self.cur_token = None
        self.next_token = None
        # dictionary for variables (e.g. set x  = 10)
        self.vars = {}

    #dump token status (including caller info)
    def dts(self, caller=sys._getframe().f_code.co_name):
        logging.debug("Caller {} \nCurrent token is {} \nNext token is {}".format
                (caller, self.cur_token, self.next_token));

    #get next token(gnt)
    def gnt(self):
        self.next_token = self.lx.token()
        return self.next_token

    #get current token (gct)
    def gct(self):
        if self.cur_token is None:
            return None
        return self.cur_token

    #check if next token exists
    def cnt(self):
        if self.next_token:
            return True
        return False

    #update current token (uct)
    def uct(self, token):
        self.cur_token = token
        return self.cur_token

    #get number from token
    def gnft(self, token=None):
        if token is None:
            token = self.cur_token
        if token.type is not "NUMBER":
            logging.critical("Called gnft on a non-number token")
            return None
        return int(token.val)

    def match(self, type):
        if (self.next_token and self.next_token.type == type):
            logging.info("Parsing token {}".format(self.next_token))
            self.uct(self.next_token)
            self.gnt()
            self.dts(sys._getframe().f_code.co_name)
            return True
        return False

    #derived classes NEED to implement this function
    def start(self):
        self.dts(sys._getframe().f_code.co_name)
        raise NotImplementedError()

    #parse 
    def parse(self, input="(5+6)"):
        logging.debug("input is {}".format(input))
        self.lx.input(input)
        success, result = self.start()
        if success:
            print("Success! Result is {}".format(result))
        else:
            print("Parse Error")

