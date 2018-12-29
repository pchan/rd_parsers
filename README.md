# rd_parsers
This repositary has a set of recursive descent parsers. I coded these to get some hands-on experience in recursive descent parsers.

The lexer is obtained from Eli Bendersky blog [1]. Each parser has the "grammar" as a comment at the top.

## Basic BNF expressions parser
File: expr_bnf_parser.py 
Grammar:
> The initial grammer is ubiquitous expression grammer seen in the dragon book and elsewhere. It has left associtivity problems which is fixed using EBNF.

## EBNF expressions parser
File: expr_bnf_parser.py 
Grammar:
> Introduces EBNF format. Left associativity problems are fixed and power is introduced.



[1] https://github.com/eliben/code-for-blog/
