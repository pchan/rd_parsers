#!/usr/bin/env python
# Notes on EBNF format:
# {} -> *
# [] -> ?
# , - > <space>
# ELEM ELEM* -> +
# In a lexer rule, the characters inside square brackets define a character set. So ["] is the set with the single character ".
# Being a set, every character is either in the set or not, so defining a character twice, as in [""] makes no difference, it's the same as ["].
# Non-terminals are in lower-case, Terminals are in upper-case.
# [1] https://tomassetti.me/ebnf/

# The grammar is:
# start: field (COMMA field)* 
# field: QUOTE ( COMMA | STRING )* QUOTE | STRING
# COMMMA : ,
# QUOTE : "
# STRING: [^,"] #all strings not matching comma or quotes
# Note: Grammar does not allows nested quotes. TODO: Make it nested.

from parser import Parser
import logging
import sys
import trace

# Implements a recursive descent parser for thea above grammar(csv)
# Since this is LL(1) no backtracking is needed
class CsvParser(Parser):

    def __init__(self, rules):
        Parser.__init__(self,rules)

    # we have lhs,rhs...what do you wish to do
    def sem_action(self,s1,s2):
        action = ' '
        if s1 and s2:
            if len(s1) > 0 and len(s2) > 0:
                logging.debug("s1 is {} s2 is {}".format(s1,s2))
                return s1 + action + s2
            elif len(s1) > 0 :
                return s1
            else: 
                return s2
        elif s1:
            return s1
        elif s2:
            return s2

        return None

    #stringify none
    def sn(self, string):
        if string is None:
            return ""
        return str(string)

    def field (self):
        self.dts(sys._getframe().f_code.co_name)
        s = ""
        if self.match("STRING"):
            s = self.sn(self.gsft())

        if self.match("QUOTE"):
            s = s + "\""
            while True:
                if self.match("COMMA"):
                    s = s + ","

                if self.match("STRING"):
                    s = s + self.sn(self.gsft())

                if self.match("QUOTE"):
                    s = s + "\""
                    break

                if self.cnt() is False:
                    logging.critical("Improperly nested QUOTE ")
                    break
        return s

    def start(self):
        self.gnt()
        self.dts(sys._getframe().f_code.co_name)
        s1 = self.field()
        s3 = ""
        while True:
            if self.match("COMMA"):
                s2 = self.field() 
                #s3 = s3 + s2 + " "
                s3 = self.sem_action(s3, s2)
            self.dts(sys._getframe().f_code.co_name)

            if self.cnt() is False:
                break

        result = self.sem_action(s1,s3)
        logging.debug("result is {}".format(result))
        return True, result

if __name__ == '__main__':
    rules = [
        ('\,',             'COMMA'),
        ('\"',             'QUOTE'),
        ('[^,"]*',             'STRING'),
    ]

    tracer = trace.Trace( ignoredirs=[sys.prefix, sys.exec_prefix],
	trace=1, count=0)

    cp = CsvParser(rules)
    args = cp.parse_arguments()
    if args.verbose:
        level=logging.DEBUG
    else:
        level=logging.INFO

    FORMAT = "%(levelname)s[%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT, level=level)

    #cp.parse("5,6,7")
    if args.trace:
        tracer.run("cp.parse(args.input)")
    else:
        cp.parse(args.input)
    

