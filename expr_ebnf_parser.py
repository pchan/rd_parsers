#!/usr/bin/env python
# The grammar we use is an extension of the previous expressions grammar (with the left associativity removed) problems.
# This is in EBNF form
# Note that I won't use the "Standard EBNF" [1]
# Std EBNF -> Commonly used Idioms(?)
# {} -> *
# [] -> ?
# , - > <space>
# ELEM ELEM* -> +
# In a lexer rule, the characters inside square brackets define a character set. So ["] is the set with the single character ". Being a set, every character is either in the set or not, so defining a character twice, as in [""] makes no difference, it's the same as ["].

# [1] https://tomassetti.me/ebnf/

# The grammar is:
# start : expr | set ID = expr
# expr : term ( + term | - term )*
# term : power ( * power | / power)*
# power: factor ^ power
# factor : ID | '(' expr ')' | NUM
# 
# ID      : [a-zA-Z_]\w+
# NUM  : \d+

import argparse
import logging
import sys
#Please see README on how to get this lexer
import lexer

# Implements a recursive descent parser for thea above grammar(calculator)
# Since this is LL(1) no backtracking is needed
# Does not suffer from associativity problems.
class CalcParser(object):

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

    #update current token (uct)
    def uct(self, token):
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
            self.uct(self.next_token)
            self.gnt()
            self.dts(sys._getframe().f_code.co_name)
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
        
        #match for ()
        if self.match("LP"):
            result = self.expr()
            if self.match("RP"):
                return result
        return None

    def power(self):
        self.dts(sys._getframe().f_code.co_name)

        lhs = self.factor()

        if self.match("POWER"):
            return lhs ** self.power()

        return lhs


    def term(self):
        # term : factor ( * factor | / factor)*
        self.dts(sys._getframe().f_code.co_name)
    
        #Used for resolving factors (E -> T -> F ->P -> -> <Number>)
        rhs = self.power()

        # the * is implemented as a while loop
        #( * power | / power )*
        while True:
            #( * factor)
            if self.match("MULTIPLY"):
                val = self.power()
                rhs = rhs * val
            #( / factor)
            elif self.match("DIVIDE"):
                val = self.power()
                rhs = rhs / val
            else:
                #we have run out of tokens 
                if self.next_token is None:
                    break
                else:
                    #parse error? or upstream non-terminal case
                    return rhs
            logging.debug("irhs is {}".format(rhs))

        logging.debug("rhs is {}".format(rhs))

        #consumption finished
        return rhs

    def expr(self):
        self.dts(sys._getframe().f_code.co_name)

        # expr : term ( + term | - term )*
        # the first term is called here
        lhs = self.term()
        logging.debug("lhs after first term {}".format(lhs))
        self.dts(sys._getframe().f_code.co_name)

        rhs = 0
        # the * is implemented as a while loop
        #( + term | - term )*
        while True:
            #( + term)
            if self.match("PLUS"):
                logging.debug("before plus")
                val = self.term()
            #( - term)
            elif self.match("MINUS"):
                logging.debug("before minus")
                val = -self.term()
            else:
                #we have run out of tokens 
                if self.next_token is None:
                    break
                else:
                    #parse error? or upstream non-terminal case
                    return None

            #parse error? or upstream non-terminal case
            if val is None:
                return None

            rhs = rhs + val
            logging.debug("rhs is {}".format(rhs))

        logging.debug("lhs is {} rhs is {}".format(lhs,rhs))

        return lhs + rhs

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
    def parse(self, input="(5+6)"):
        print("input is {}".format(input))
        self.lx.input(input)
        success, result = self.start()
        if success:
            print("Success! Result is {}".format(result))
        else:
            print("Grammar Error")

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
        ('\^',              'POWER'),
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
    #cp.parse("x*8+7")
    #cp.parse("6-5-5")
    #cp.parse("5*8/4/2")
    cp.parse(args.input)

