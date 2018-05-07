Overview
===

Components
---
* `get_indices_from_string.py` -- a quick script to transform a list of sentences (.txt format, one sentence
per line) into a JSON to be read in by `trainer.py`, with the positions of negative items already defined.
* `trainer.py` trains the model either for a fixed number of runs (option -n), or until a certain threshold of
accuracy is reached (with the option `-t` as a float). With the latter, the number of successive iterations
for which the threshold has to be achieved can also be stated as `-s` (deault: 3).
* `spread_neg.py` -- introduces a user defined attribute "is_negated" and attempts to assign it to all and only
those words that are in the scope of negation. Currently, it does so by spreading downward unconditionally,
upward except when it has reached a VERB or AUX. This sometimes undergenerates in case of verb clusters,
but it doesn't/shouldn't overgenerate (the only case where it does is when the predefined model parses "bezweifle"
as an adjective and thus the stop condition isn't applied).
* display_scope.py -- displacy-interface that displays the recognised entities after appending a string to
any entity that is in the scope of a negation (or has any other user-defined feature). A recognised entity
"Google" will thus be displayed as, e.g. "Google ORG_NG" instead of "Google ORG" to indicate it's negated.

Usage
---
`get_indices_from_string` needs to be called separately, all the other components are called from `spread_neg`.
The simplest way to use it would thus be to call `python3.6 spread_neg.py` from the command line, or to
`from spread_neg import \*` in an interactive shell.

Status
===
Under development, the recognition of negative elements is still somewhat quirky -- while most of the time, alternate
morphs of "kein" are recognised, this isn't always true for "bestreiten", and the first person singular form of "bezweifeln"
is more often than not parsed as an adjective, implicating how it projects under the rules in `spread_neg.py`. Sometimes,
other named entities as mistakenly assigned a status as "NEGATION" (for some reason, particularly often "China").

To do
===

The package currently doesn't model interaction with other operators *at all*. This is a big hole, since the spreading
of negation in German interacts closely with the presence of other operators: "Niemand kam oft" means a very
different thing from "oft kam niemand". Even simple indefinite-marked nominals block the projection of negation:
While "Heute hat Peter niemanden getroffen" is the negation of "Heute hat Peter jemanden getroffen", "Heute hat ein Mann
niemanden getroffen" is *not* the negation of "Heute hat ein Mann jemanden getroffen" (That would be "heute hat kein
Mann jemanden/wen getroffen"). These intricacies are explained in more detail in `problem_description.md`.

