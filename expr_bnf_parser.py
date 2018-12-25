#!/usr/bin/env python
#
# Simple expressions grammer found in Dragon book. Suffers from associativity problems.
# Example: 6-5-5 => 5-5 gets evaluated first by the parse tree
#          leading to 6 as result instead of -4 (6-5-5 -> 6-0 -> 6)
#
# Note that the grammer favors multiplication/division over plus/minus by placing them at 
# "bottom" of the recursive descent tree thereby guranteeing their precedence.
#
# This grammer comes from ELI Bendersky's blog and adds things like set command etc to 
# support identifiers
#
# BNF:
#
# <stmt>    : set <id> = <expr>
#           | <expr>
# <expr>    : <term> + <expr>
#           | <term> - <expr>
#           | <term>
# <term>    : <factor> * <term>
#           | <factor> / <term>
#           | <factor>
# <factor>  : <id>
#           | <number>
#           | ( <expr> )
#
# <id>      : [a-zA-Z_]\w+
# <number>  : \d+
#

import argparse
import logging
import sys
#Please see README on how to get this lexer
import lexer

# Implements a recursive descent parser for a specific grammer(calculator)
# Since this is LL(1) no backtracking is needed
class CalcParser(object):

    def __init__(self, rules):
        # initialize the lex rules for the grammer 
        self.lx = lexer.Lexer(rules, skip_whitespace=True)
        # current result (do we need this ?)
        self.result=0
        self.cur_token = None
        self.next_token = None
        # dictionary for variables (e.g. set x  = 10)
        self.vars = {}

    #dump token status (including caller info)
    def dts(self, caller=sys._getframe().f_code.co_name):
        logging.debug("Caller {} \nCurrent token is {} \nNext token is {}".format
                (caller, self.cur_token, self.next_token));

    #get next token(calls lexer)
    def gnt(self):
        self.next_token = self.lx.token()
        return self.next_token

    #get current token
    def gct(self):
        if self.cur_token is None:
            return None
        return self.cur_token

    #update the current token
    def update_cur_token(self, token):
        self.cur_token = token
        return self.cur_token

    #This is called when you expect the current (or passed) token to be a number
    #modify to check for errors
    def get_number(self, token=None):
        if token is None:
            token = self.cur_token
        return int(token.val)

    def match(self, type):
        if (self.next_token and self.next_token.type == type):
            logging.info("Parsing token {}".format(self.next_token))
            self.update_cur_token(self.next_token)
            self.gnt()
            return True
        return False

    def factor(self):
        self.dts(sys._getframe().f_code.co_name)

        if self.match("NUMBER"):
            return self.get_number()
        if self.match("IDENTIFIER"):
            try:
                return self.vars[self.gct().val]
            except KeyError:
                logging.critical("Identifier {} not set".format(self.gct()))
                sys.exit(1)
        return None

    def term(self):
        self.dts(sys._getframe().f_code.co_name)
    
        #Used for resolving factors (E -> T -> F -> <Number>)
        lhs = self.factor()

        # <term>    : <factor> * <term>
        if self.match("MULTIPLY"):
            return lhs * self.term()
        # <term>    : <factor> / <term>
        if self.match("DIVIDE"):
            return lhs / self.term()

        logging.debug("result is {}".format(lhs))
        #consumption finished
        return lhs

    def expr(self):
        self.dts(sys._getframe().f_code.co_name)
        #Used for resolving Terms (E -> T -> F * T)
        #Also Used for resolving factors (E -> T -> F -> <Number>)
        lhs  = self.term()

        # <expr>    : <term> + <expr>
        if self.match("PLUS"):
            return lhs + self.expr()
        # <expr>    : <term> - <expr>
        if self.match("MINUS"):
            return lhs - self.expr()

        logging.debug("result is {}".format(lhs))
        #we have consumed all we can consume now return
        return lhs

    def start(self):
        self.dts(sys._getframe().f_code.co_name)
        result = None
        self.gnt()
        if self.next_token:
            #prod1 : set x = 10
            if self.match("SET"):
                if self.match("IDENTIFIER") :
                    lval = self.cur_token.val
                    if self.match("EQUALS"):
                        result = self.expr()
                        if result is not None:
                            self.vars[lval] = int(result)
            #prod2 : <expr>
            else:
                result = self.expr()

        if self.next_token:
            logging.debug("parsing not complete still have is {}".format
                    (self.next_token))
            return False

        return True, result


    #parse 
    def parse(self, input="5+6"):
        print("input is {}".format(input))
        self.lx.input(input)
        success, result = self.start()
        if success:
            print("Success! Result is {}".format(result))
        else:
            print("Grammer Error")

def parse_arguments():
    """ deal with all the options being passed in"""

    parser = argparse.ArgumentParser(description="CalcParser arguments")

    parser.add_argument('--input', dest='input', action='store', default="5+6", type=str, help='Specify input to parser')
    parser.add_argument("-v", "--verbose", help="increase output verbosity(debug)",
                                action="store_true")

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    rules = [
        ('set',             'SET'),
        ('\d+',             'NUMBER'),
        ('[a-zA-Z_]\w*',    'IDENTIFIER'),
        ('\+',              'PLUS'),
        ('\-',              'MINUS'),
        ('\*',              'MULTIPLY'),
        ('\/',              'DIVIDE'),
        ('\(',              'LP'),
        ('\)',              'RP'),
        ('=',               'EQUALS'),
    ]

    args = parse_arguments()
    if args.verbose:
        level=logging.DEBUG
    else:
        level=logging.INFO

    FORMAT = "%(levelname)s[%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT, level=level)

    cp = CalcParser(rules)
    cp.parse("set x = 10+4*7")
    cp.parse("x*8+7")
    #cp.parse(args.input)

