Negation and Scope
===

Negation in German frequently takes scope in a higher position than where it's expressed


This only works with direct negation - the scope of indirect negation like the one contained in verbs like "deny" or "doubt" scopes locally:

Du musst das Erstlingswerk von keinem Linguisten gelesen haben. NOT(MUST(read))

Ich muss bezweifeln, dass du "Syntactic Structures" gelesen hast. MUST(NOT(believe that...))

Negation doesn't usually spread across Quantifiers and quantifying adverbs:

- Dieses Jahr hat in fast allen Fächern kein Schüler einen Fünfer gehabt. ALL(NO)
- Dieses Jahr hat kein Schüler in fast allen Fächern einen Fünfer gehabt. NO(ALL)

- Weil oft niemand gekommen ist, mussten wir zusperren. OFTEN(NOBODY)
- Weil niemand oft gekommen ist, blieben sich die Gäste fremd. NOBODY(OFTEN)

...but negation can spread across modal verbs:

- Ich muss heute niemanden treffen. NOT(MUST(meet ANYbody)) or MUST(NOT(meet ANYbody))

Negation does *not* spread up the tree across an unnegated indefinite:
Eine Katze hat keine Maus gefangen != Keine Katze hat eine Maus gefangen.

- Ich kann dir das Erstlingswerk von keinem Linguisten empfehlen. is interpreted most naturally as "I can not recommend any linguist's debut" rather than as
I can recommend the debut of someone who's not a linguist. That is NOT(CAN(recommend ANY))

Only direct negation spreads. indirect negation such as in negative adverbs is interpreted locally:

- Putin bestritt heute, dass P = Putin behauptete heute, dass nicht P != Putin behauptete heute nicht, dass P.

In no case does negation take scope outside an embedded clause in which it 

The goal definition is thus: have negation spread up a tree:
* if it's not in the form of a negative verb
* No further than to the next highest clause boundary
* Conditionally jumping other operators, but at any rate registering such encounters as they can lead to ambiguities
* not jumping certain types of operators.


Misparses
===
Some of my test examples are misparsed by the base model, e.g. "bezweifle" is parsed as an adjective. Generalisation to morphs not present in the input
works mostly but not 100% reliably.

Verb Clusters
___
The parser's decisions which elements in an (embedded) sentence to assign as children of the invinitive/participle and which as children of the auxiliary/modal verb
seem fairly arbitrary.


