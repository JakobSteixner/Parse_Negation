#/usr/bin/python3.6
# -*- coding: utf8 -*-

import spacy, plac, json
import random
from pathlib import Path
from spacy import displacy
nlp = spacy.load("de")

nlp.entity.add_label("NEGATION") # negative elements
nlp.entity.add_label("__NEG") # elements in the scope of negation


TRAIN_DATA = json.load(open("TRAINING_DATA.json"))


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
    threshold_success=("losses threshold to declare success", "option", "t", float),
    successive_successes=("Number of successful runs before terminating", "option", "s", int),
    input_data=("File name/path for training data", "option", "i", str),
    param = ("Parameter to be trained", "option", "p", str)
    )
class Trainer:
    def __init__(self, model=None, output_dir=None, n_iter=50, threshold_success=None, successive_successes=3, input_data = "TRAINING_DATA.json", param='ner'):
        """Load the model, set up the pipeline and train the entity recognizer."""
        if model is not None:
            self.nlp = nlp = spacy.load(model)  # load existing spaCy model
            print("Loaded model '%s'" % model)
        else:
            self.nlp = nlp = spacy.load('de', parser=False)  # load default `de` model
            print("Loaded existing 'de' model")
        self.output_dir = output_dir
        self.n_iter = n_iter
        self.threshold_success = threshold_success
        self.successive_successes = successive_successes
        self.TRAIN_DATA = json.load(open(input_data))
    
        self.train(param)
        self.test()
    def train(self, param):
        # create the built-in pipeline components and add them to the pipeline
        # nlp.create_pipe works for built-ins that are registered with spaCy
        if param not in nlp.pipe_names:
            ner = self.nlp.create_pipe(param)
            nlp.add_pipe(ner, last=True)
        # otherwise, get it so we can add labels
        else:
            ner = self.nlp.get_pipe(param)
    
        # add labels
        for _, annotations in self.TRAIN_DATA:
            for ent in annotations.get('entities'):
                ner.add_label(ent[2])
        
        def continue_condition(runs,successes):
            if self.threshold_success == None:
                if runs < self.n_iter:
                    return 1
                return 0
            if successes < self.successive_successes:
                return 1
            return 0
    
        # get names of other pipes to disable them during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != param]
        with self.nlp.disable_pipes(*other_pipes):  # only train NER
            optimizer = nlp.begin_training()
            successes = 0
            runs = 0
            while continue_condition(runs,successes):
                random.shuffle(self.TRAIN_DATA)
                losses = {}
                for text, annotations in self.TRAIN_DATA:
                    self.nlp.update(
                        [text],  # batch of texts
                        [annotations],  # batch of annotations
                        drop=0.5,  # dropout - make it harder to memorise data
                        sgd=optimizer,  # callable to update weights
                        losses=losses)
                print(losses)
                if self.threshold_success != None and losses["ner"] < self.threshold_success:
                    successes += 1
                else:
                    successes = 0
                runs += 1
    def test(self):
        # test the trained model
        for text, _ in self.TRAIN_DATA:
            doc = nlp(text)
            print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
            print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
    def save(self):
        # save model to output directory
        if self.output_dir is not None:
            output_dir = Path(self.output_dir)
            if not output_dir.exists():
                output_dir.mkdir()
            self.nlp.to_disk(output_dir)
            print("Saved model to", output_dir)

#
#if __name__ == '__main__':
#    t = plac.call(Trainer) # (**{"output_dir":"trainedmodel","n_iter":30
#    nlp2 = spacy.load(t)
#    displacy.serve(nlp2(u'In Österreich gibt es keine Löwen, das ist aber nicht schlimm'), style="ent") #
#    displacy.serve(nlp2(u'Das habe ich mit keinem Wort gesagt'), style="ent") # no token of `keinem` in training set, tests generalisation across inflection patterns of lemma
#    displacy.serve(nlp2("Ich kann dir nicht folgen"), style="ent") # 
#    displacy.serve(nlp2("Ich habe keine Lust auf Bier."), style="ent") # this should be the easiest case, as it's almost identical to one of the training examples
#    displacy.serve(nlp2("Ich esse nicht erst seit gestern kein Fleisch"), style="ent") # test generalisation to uninflected `kein`
#    displacy.serve(nlp2("Kein Mensch wartet auf dich."), style="ent")
#    displacy.serve(nlp2("Warum bestreitest du das immer noch?"), style="ent")
#    displacy.serve(nlp2("Warum glaubst du, dass er nur heute nicht kann?"), style = "ent")