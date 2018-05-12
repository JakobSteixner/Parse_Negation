"""
Implements scope assignment using a predefined or newly trained model
currently only negation scope implemented.
"""

import time
import json
import glob
import plac
import spacy
import trainer
import negparse_helpers
import display_scope


class OpScope():
    """assigns a scope to tokens in a Doc based on the recognised
    operators (currnetly implemented: negation)
    by walking up/down a tree with defined breakpoints"""
    def __init__(self,
                 train_new=False,
                 #op_type="NEGATION", # no alternatives implemented
                 example_input = "TEST_EXAMPLES.json"):
        self.example_input = example_input
        self.docs, self.scoped = [], []
        if train_new:
            self.train =  train = trainer.Trainer(
                output_dir="trainedmodel"+time.strftime("%Y-%m-%d_%H-%M"),
                n_iter=100)
            self.nlp = train.nlp
        else:
            self.nlp = spacy.load(self.most_recent_model())
    def most_recent_model(self):
        """Defines the name of the most recent candidate model"""
        return glob.glob(negparse_helpers.model_name(include_timestamp=False)+"*")[-1]
        # assumes the models are consistently timestamped in a sort-friendly way
    def load_examples(self, example_input=None):
        """Loads text examples from a file."""
        if example_input is None:
            example_input = self.example_input
        # test novel examples
        with open(example_input, "r") as inputfile:
            #for example in json.load(inputfile):
            #    print (example)
            self.add_examples(json.load(inputfile))
            # making sure no unparsed/empty elements have entered docs list:
            self.docs = [doc for doc in self.docs
                         if any([isinstance(token, spacy.tokens.token.Token) for token in doc])
                         ]
    def add_example(self, example):
        """Add single example, can be used in interactive use.
        Accepts either a preprocessed, spacy.tokens.doc.Doc,
        or a string that yet has to be processed."""
        try:
            assert isinstance(example, spacy.tokens.doc.Doc)
            self.docs.append(example)
        except AssertionError:
            self.docs.append(self.nlp(example))
    def add_examples(self, example_list):
        """Add a batch of examples"""
        for example in example_list: self.add_example(example)
        self.docs.extend(example_list)
    def assign_scope_all(self, interactive=False):
        """Assign scope to the entire batch of examples in self.docs"""
        for doc in self.docs:
            self.assign_scope(doc, interactive)
    def assign_scope(self, doc, interactive=False):
        """assign scope to an individual example"""
        for token in doc:
            # first round: costum attribute `is_negated` assigned to negative items themselves
            token.set_extension("is_negated", default=False, force=True)
            token._.is_negated = token.ent_type_ == "NEGATION"
        for i in range(5):
            # second round: attribute `is_negated` is handed up/down the tree
            print("Run", i)
            for token in doc:
                if token._.is_negated:
                    for daughter in token.children:
                        # spread to children *except* in the case of negative verbs,
                        # where we only spread to the object (clausal or nominal)
                        if daughter.dep_ in ('oc', 'oa') or not (token.pos_ == "VERB" and
                                                                 token.ent_type_ == "NEGATION"):
                            daughter._.is_negated = True
                # spread to the head unless you're a verb, in which case you might
                # either be a negative verb, or we've likely arrived at a clause boundary
                if token._.is_negated and token.pos_ not in  ("VERB", "AUX"):
                    # undergenerates in verb clusters!
                    token.head._.is_negated = True
                
        self.scoped.append(doc) # add to list of docs with calculated scope
        if interactive:
            print([(token, token._.is_negated) for token in doc])
            display_scope.Display(doc, "is_negated", "_NG")
    def save(self, output_basename):
        """Save output to json"""
        negators = [[token.string for token in doc if token.ent_type_ == "NEGATION"]
            for doc in self.scoped]
        negated = [[token.string for token in doc if token._.is_negated]
            for doc in self.scoped]
        neg_and_scope = list(zip([doc.text for doc in self.scoped], negators, negated))
        with open(negparse_helpers.model_name(["results"],
            output_basename)+".json", "w") as outfile:
            print(output_basename)
            json.dump(neg_and_scope, outfile, indent=4, ensure_ascii=False)


@plac.annotations(
    train_new=("Train a new model with `trainer.py`. Default false", "option", "m", str),
    example_input=("Optional json list of input examples, defaults to `TEST_EXAMPLES.json",
                   "option", "i", str),
    output_basename=("Invariable name part of output json", "option", "o", str),
    interactive=("Display NER results on port 5000", "option", "I", bool)
    )
def __main__(output_basename="scope_output",
             train_new=False,
             example_input="TEST_EXAMPLES.json",
             interactive=False):
    """Run with defaults"""
    ops = OpScope(train_new=train_new, example_input=example_input)
    ops.load_examples(ops.example_input)
    ops.assign_scope_all(interactive=interactive)
    ops.save(output_basename)
    if train_new:
        ops.train.save()



if __name__ == '__main__':
    plac.call(__main__)
