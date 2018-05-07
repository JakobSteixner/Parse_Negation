#/usr/bin/python3.6
# -*- coding: utf8 -*-
# turns a plain list of sentences into a JSON
# file with some common negation elements automatically
# assigned an index in the way the trainer module can parse
# USAGE:
# $ python get_indices_from_string <intput_file> <output_file> (<mode>)
# The optional `mode` can be a/append or w/write - it speficies whether
# to overwrite an existing file with that name, default is `a`

import json, string, sys
from itertools import cycle

negitems = "kein", "nicht", "bezweif", "bestreit", "niemand", "nirgend"

def getindices(sentence, searchterm):
    for idx,word in enumerate(sentence.split()):
        if searchterm in word.lower() and word.lower().index(searchterm) == 0: # very rough method to exclude false positives, excludes "Vernichtung", but not "Nichte"
            return (sentence.index(word), sentence.index(word) + len(word.strip(string.punctuation)))


sentences = "Ich finde meine Geldbörse nirgends.", "Ich habe keine Lust auf Bier.", "Ich habe niemandem etwas angetan.", "Ich bin mir keiner Schuld bewusst.", "Ich glaube nicht, dass du das niemandem gesagt hast."

def define_neg_ner(sentence):
    return [(getindices(sentence, word) + ("NEGATION",)) for word in negitems if getindices(sentence,word)]
    for word in negitems:
            if getindices(sentence, word):
                return (getindices(sentence, word) + ("NEGATION",))

if __name__ == '__main__':
    if len(sys.argv) > 3:
        mode = sys.argv[3]
    else:
        mode = "a"
    with open(sys.argv[1]) as inputfile:
        raw_sentences = inputfile.read().split("\n")
    print (raw_sentences)
    annotated_sentences = [define_neg_ner(sentence) for sentence in raw_sentences]
    print (annotated_sentences)
    output = list(
            zip(
                    raw_sentences,
                    zip(cycle(("entities",)), annotated_sentences)
                )
        )
    output = [[sub[0], {sub[1][0]:sub[1][1]}] for sub in output]
    with open(sys.argv[2], mode) as outfile:
        json.dump(output, outfile, indent=4)
    
    
