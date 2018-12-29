#!/usr/bin/env python

# This is the generic parser framework. 
# It initializes the lexer, defines the input string that make up
import logging
import sys
import argparse
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

    #get val(str) from token
    def gsft(self, token=None):
        if token is None:
            token = self.cur_token
        if token is None:
            logging.critical("token not present")
            return None
        return str(token.val)

    def match(self, type):
        if (self.next_token and self.next_token.type == type):
            logging.info("Parsing token {}".format(self.next_token))
            self.uct(self.next_token)
            self.gnt()
            #self.dts(sys._getframe().f_code.co_name)
            return True
        return False

    #derived classes NEED to implement this function
    def start(self):
        raise NotImplementedError()

    #parse the input
    def parse(self, input="(5+6)"):
        logging.debug("input is {}".format(input))
        self.lx.input(input)
        success, result = self.start()

        if success:
            print("Success! Result is {}".format(result))
        else:
            print("Parse Error")

    #parse the argument input
    def parse_arguments(self):
        """ deal with all the options being passed in"""

        arg_parser = argparse.ArgumentParser(description="Parser arguments")
        arg_parser.add_argument('--input', dest='input', action='store', default="5", type=str, help='Specify input to parser')
        arg_parser.add_argument("-v", "--verbose", help="increase output verbosity(debug)",
                action="store_true")
        arg_parser.add_argument("-t", "--trace", help="trace the execution",
                action="store_true")
        args = arg_parser.parse_args()

        return args

