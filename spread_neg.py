import time, json, display_scope, spacy, glob

import trainer, negparse_helpers



class OpScope():
    # assigns a scope to tokens in a Doc based on the recognised
    # operators (currnetly implemented: negation)
    # by walking up/down a tree with defined breakpoints
    def __init__(self, train_new=False, op_type="NEGATION", example_input = "TEST_EXAMPLES.json"):
        self.example_input = example_input    
        self.docs, self.scoped = [], []
        if train_new:
            t = trainer.Trainer(output_dir="trainedmodel"+time.strftime("%Y-%m-%d_%H-%M"), n_iter=100)
            self.nlp = t.nlp
        else:
            self.nlp = spacy.load(self.most_recent_model())
    def most_recent_model(self):
        return glob.glob(negparse_helpers.model_name(include_timestamp=False)+"*")[-1] # assumes the models are consistently timestamped in a sort-friendly way
    def load_examples(self, example_input=None):
        if example_input is None: example_input = self.example_input
        # test novel examples
        with open(example_input, "r") as inputfile:
            self.add_examples(json.load(inputfile))
    def add_example(self, example):
        """add example manually"""
        try:
            assert isinstance(example, spacy.tokens.doc.Doc)
            self.docs.append(example)
        except AssertionError: self.docs.append(self.nlp(example))
    def add_examples(self, example_list):
        for example in example_list: self.add_example(example)
        self.docs.extend(example_list)
    def assign_scope_all(self, interactive=False):
        for doc in self.docs:
            self.assign_scope(doc, interactive)
    def assign_scope(self, doc, interactive=False):
        for token in doc:
            # first round: costum attribute `is_negated` assigned to negative items themselves
            token.set_extension("is_negated", default = False, force=True)
            token._.is_negated = token.ent_type_ == "NEGATION"
        for i in range(5):
            # second round: attribute `is_negated` is handed up/down the tree
            for token in doc:
                if token._.is_negated:
                    for daughter in token.children:
                        # spread to children *except* in the case of negative verbs, where we only spread to the object (clausal or nominal)
                        if daughter.dep_ in ('oc', 'oa') or not (token.pos_ == "VERB" and token.ent_type_ == "NEGATION"):
                            daughter._.is_negated = True
                # spread to the head unless you're a verb, in which case you might either be a negative verb, or we've likely arrived at a clause boundary
                if token._.is_negated and token.pos_ not in  ("VERB", "AUX"): # undergenerates in verb clusters!
                    token.head._.is_negated = True
        self.scoped.append(doc) # add to list of docs with calculated scope
        if interactive:
            print([(token, token._.is_negated) for token in doc])
            display_scope.Display(doc, "is_negated", "_NG")
    def save(self):
        negators = [[token.string for token in doc if token.ent_type_ == "NEGATION"] for doc in self.scoped]
        negated = [[token.string for token in doc if token._.is_negated == True] for doc in self.scoped]
        neg_and_scope = list(zip([doc.text for doc in self.scoped], negators, negated))
        with open(negparse_helpers.model_name(["results"], "scope_output")+".json", "w") as outfile:
            json.dump(neg_and_scope, outfile, indent=4, ensure_ascii = False)

def __main__():
    op = OpScope()
    op.load_examples(op.example_input)
    op.assign_scope_all(interactive=True)
    op.save()
    
    

if __name__ == '__main__':
    __main__()


#Output
#=====
#[(Ich, True), (glaube, True), (nicht, True), (,, True), (dass, True), (du, True), (eine, True), (Ahnung, True), (hast, True)] # GOOD!
#[(Ich, True), (bezweifle, True), (,, True), (dass, True), (du, True), (eine, True), (Ahnung, True), (hast, True)] # Ich should be outside, bezweifle is misparsed as ADJ
#[(Ich, False), (glaube, False), (,, False), (das, True), (ist, True), (nicht, True), (,, True), (was, True), (du, True), (mir, True), (sagen, True), (willst, True), (., False)] # GOOD!
#[(Ich, True), (weiß, True), (nicht, True), (,, True), (warum, True), (du, True), (mir, True), (das, True), (sagst, True)] # GOOD!
#[(Ich, True), (bezweifle, True), (deine, True), (Redlichkeit, True), (., True)] # "bezweifle" misparsed again
#[(Ich, False), (bestreite, False), (deine, False), (Redlichkeit, False), (., False)] # "bestreite" not recognised
#[(Er, False), (bezweifelt, True), (immer, False), (noch, False), (,, False), (dass, True), (das, True), (wahr, True), (sein, True), (kann, True)] # GOOD
#[(Wladimir, False), (Putin, False), (bestreitet, True), (beim, False), (heutigen, False), (Gipfeltreffen, False), (erneut, False), (,, False), (dass, True), (Russland, True), (in, True), (Syrien, True), (Angriffe, True), (vertuscht, True), (., False)] # GOOD
#[(Gestern, False), (stand, False), (in, False), (der, False), (Zeitung, False), (,, False), (dass, False), (es, False), (am, True), (Wochenende, True), (keinen, True), (Regen, True), (geben, True), (wird, False), (., False)] # almost good, entire embedded clause would be better
#[(Die, False), (Regierung, False), (scheint, False), (keinen, True), (Plan, True), (zu, True), (haben, True), (,, True), (um, True), (die, True), (Probleme, True), (der, True), (Landwirtschaft, True), (zu, True), (lösen, True)] # GOOD
#[(Die, False), (Regierung, False), (kündigte, False), (an, False), (,, False), (keine, True), (weiteren, True), (Zugeständnisse, True), (zu, True), (machen, True), (., False)] # GOOD
#[(Die, True), (Regierung, True), (versprach, True), (keine, True), (weiteren, True), (Zugeständnisse, True), (., True)] # GOOD
