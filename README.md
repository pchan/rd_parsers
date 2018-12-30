# rd_parsers
This repositary has a set of recursive descent parsers. I coded these to get some hands-on experience in recursive descent parsers.

The lexer is obtained from Eli Bendersky [blog](https://github.com/eliben/code-for-blog/ ). Each parser has the "grammar" as a comment at the top.

## Parser base class
File: parser.py
> This is a base class which offers token streaming and argument list. Intended to use OO concepts. Separtes core parser work i.e., defining the non-terminals (as functions) from generic parser work. The arithmetic parsers where coded before this so they don't use these. The CSV and other parsers use this.

## Basic BNF expressions parser
File: expr_bnf_parser.py 
Grammar:
> The initial grammer is ubiquitous expression grammer seen in the dragon book and elsewhere. It has left associtivity problems which is fixed using EBNF.

## EBNF expressions parser
File: expr_bnf_parser.py 
Grammar:
> Introduces EBNF format. Left associativity problems are fixed and power is introduced.

## CSV parser
File: csv_parser.py
Parses csv files. The semantic action is to currently replace the comma by space. 


