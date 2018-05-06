#/usr/bin/python3.6
# -*- coding: utf8 -*-

import spacy, plac
import random
from pathlib import Path
from spacy import displacy
nlp = spacy.load("de")

nlp.entity.add_label("NEGATION")
nlp.entity.add_label("NEGID")


TRAIN_DATA = [
    
    #('Ich sage das nicht nur, weil ich ihn nicht mag.', {
    #    'entities': [(13, 18, "NEGATION"), (19, 22, 'NEGID'), (37, 42, "NEGATION")]
    #}),
    #('Er bestreitet, jemals dort gewesen zu sein', {
    #    'entities': [(3, 13, 'NEGID')]
    #}),
    #('Ich zweifle, dass er heute noch anruft.', {
    #    'entities': [(4, 11, 'NEGID')]
    #}),
    ('Warum kommst du heute nicht?', {
        'entities': [(22, 27, 'NEGATION')]
    }),
    ('Ich habe keine Lust auf Apfelmus', {
        'entities': [(9, 14, "NEGATION")]
    }),
    ('Peter will lieber nicht heute kommen', {
        "entities": [(0, 5, "PERS"), (18, 23, "NEGATION")]
        }
    ),
    (u'In China leben keine Kängurus.', {
        "entities": [(3, 8, "GPE"), (15, 20, "NEGATION")]
        }
     ),
    
    (u'Ich bin mir keiner Schuld bewusst.', {
        "entities": [(12, 18, "NEGATION")]
        }
     ),
    
    (u'Schild habe ich keines gesehen.', {
        "entities": [(16, 22, "NEGATION")]
        }
     ),
    
    (u'Donald Trump bezweifelt, dass Nordkorea zur Abrüstung bereit ist.', {
        "entities": [(13, 23,"NEGATION")]
        }
    ),
     
    
    (u'Es bleibt zu bezweifeln, dass die Friedensverhandlungen zu einer Lösung führen werden.', {
        "entities": [(13, 23,"NEGATION")]
        }
     ),
    
    
    (u'Ich bezweifle, dass du mir das sagen kannst.', {
        "entities": [(4, 13,"NEGATION")]
        }
     ),
    
    (u'Immer noch bestreitet er, dass er etwas falsch gemacht hat.', {
        "entities": [(11, 21, "NEGATION")]
        }
     ),
    
    (u'Niemand wird dir das glauben.', {
        "entities": [(0, 7, "NEGATION")]
        }
     ),
    
    (u'Da bin ich ja nochmal günstig davongekommen', {
        "entities": []
        }
    ),
    
    (u'Ich schaffe es doch erst morgen.', {
        "entities": []
        }
     )
    
]

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
    threshold_success=("losses threshold to declare success", "option", "t", float),
    successive_successes=("Number of successful runs before terminating", "option", "s", int))
class Trainer:
    def __init__(self, model=None, output_dir=None, n_iter=50, threshold_success=None, successive_successes=3):
        """Load the model, set up the pipeline and train the entity recognizer."""
        if model is not None:
            self.nlp = nlp = spacy.l
            oad(model)  # load existing spaCy model
            print("Loaded model '%s'" % model)
        else:
            self.nlp = nlp = spacy.load('de', parser=False)  # load default `de` model
            print("Loaded existing 'de' model")
        self.output_dir = output_dir
        self.n_iter = n_iter
        self.threshold_success = threshold_success
        self.successive_successes = successive_successes
        self.train()
    def train(self):
        # create the built-in pipeline components and add them to the pipeline
        # nlp.create_pipe works for built-ins that are registered with spaCy
        if 'ner' not in nlp.pipe_names:
            ner = self.nlp.create_pipe('ner')
            nlp.add_pipe(ner, last=True)
        # otherwise, get it so we can add labels
        else:
            ner = self.nlp.get_pipe('ner')
    
        # add labels
        for _, annotations in TRAIN_DATA:
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
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != 'ner']
        with self.nlp.disable_pipes(*other_pipes):  # only train NER
            optimizer = nlp.begin_training()
            successes = 0
            runs = 0
            while continue_condition(runs,successes):
                random.shuffle(TRAIN_DATA)
                losses = {}
                for text, annotations in TRAIN_DATA:
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
        for text, _ in TRAIN_DATA:
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


if __name__ == '__main__':
    t = plac.call(Trainer) # (**{"output_dir":"trainedmodel","n_iter":30
    nlp2 = spacy.load(t)
    displacy.serve(nlp2(u'In Österreich gibt es keine Löwen, das ist aber nicht schlimm'), style="ent") #
    displacy.serve(nlp2(u'Das habe ich mit keinem Wort gesagt'), style="ent") # no token of `keinem` in training set, tests generalisation across inflection patterns of lemma
    displacy.serve(nlp2("Ich kann dir nicht folgen"), style="ent") # 
    displacy.serve(nlp2("Ich habe keine Lust auf Bier."), style="ent") # this should be the easiest case, as it's almost identical to one of the training examples
    displacy.serve(nlp2("Ich esse nicht erst seit gestern kein Fleisch"), style="ent") # test generalisation to uninflected `kein`
    displacy.serve(nlp2("Kein Mensch wartet auf dich."), style="ent")
    displacy.serve(nlp2("Warum bestreitest du das immer noch?"), style="ent")
    displacy.serve(nlp2("Warum glaubst du, dass er nur heute nicht kann?"), style = "ent")