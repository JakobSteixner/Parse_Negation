# -*- coding: utf8 -*-
from spacy import displacy

class Display:
    def __init__(self,doc, user_property, short_id=None, mode="serve"):
        if short_id is None:
            short_id = user_property
        for token in doc:
            if eval("token._.%s" % user_property) == True:
                token.ent_type_ += short_id
        self.display(doc, mode)
    def display(self, doc, mode):
        eval("displacy."+mode)(doc, style="ent")