#/usr/bin/python3.6
# -*- coding: utf8 -*-

import spacy, plac
import random
from pathlib import Path
from spacy import displacy
nlp = spacy.load("de")

nlp.entity.add_label("NEGATION")


TRAIN_DATA = [
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
    
    (u'Niemand wird dir das glauben.', {
        "entities": [(0, 7, "NEGATION")]
        }
     )
]

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))
def main(model=None, output_dir=None, n_iter=50):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.load('de', parser=False)  # create blank Language class
        print("Loaded existing 'de' model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe('ner')

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                nlp.update(
                    [text],  # batch of texts
                    [annotations],  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print(losses)

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        TRAIN_DATA.append(('Kein Mensch wartet auf dich.', {
        'entities': [(0, 4, 'NEGATION')]
    }))
        TRAIN_DATA.append((u'In Österreich gibt es keine Löwen, das ist aber nicht schlimm', {
        'entities': []
    }))
        TRAIN_DATA.append((u'Das habe ich mit keinem Wort gesagt', {
        'entities': []
    }))
        nlp2 = spacy.load(output_dir)
        for text, _ in TRAIN_DATA:
            doc = nlp2(text)
            print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
            print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])


if __name__ == '__main__':
    plac.call(main) # (**{"output_dir":"trainedmodel","n_iter":30
    nlp2 = spacy.load("trainedmodel")
    displacy.serve(nlp2("Ich kann dir nicht folgen"), style="ent")
    displacy.serve(nlp2("Ich habe keine Lust auf Bier."), style="ent")
    displacy.serve(nlp2("Ich esse nicht erst seit gestern kein Fleisch"), style="ent")