import trainer, time

t = trainer.Trainer(output_dir="trainedmodel"+time.strftime("%Y-%m-%d_%H-%M"), n_iter=100)
nlp = t.nlp

# test novel examples
docs = [nlp(sentence) for sentence in [
                "Ich glaube nicht, dass du eine Ahnung hast", # all negated - OK
                "Ich bezweifle, dass du eine Ahnung hast", # misparse of "bezweifle" as ADJ means negation spreads wrongly to the subject
                "Ich glaube, das ist nicht, was du mir sagen willst.", # only embedded clause negated - OK
                "Ich weiß nicht, warum du mir das sagst", # all negated - OK
                "Ich bezweifle deine Redlichkeit.", # same as above - misparse of bezweifle means the rule doesn't apply as it should
                "Ich bestreite deine Redlichkeit.", # failure to generalise to "bestreite", no negation detected at all
                "Er bezweifelt immer noch, dass das wahr sein kann", # "bezweifeln" and the embedded clause negated, SUBJ and "immer noch" not - OK
                "China bestreitet die angeblichen Pläne, Taiwan zu sanktionieren.",
                "Wladimir Putin bestreitet beim heutigen Gipfeltreffen erneut, dass Russland in Syrien Angriffe vertuscht.", # only "bestreiten" and embedded clause negated - OK
                "Gestern stand in der Zeitung, dass es am Wochenende keinen Regen geben wird.", # stops short of spreading to the whole embedded clause because "keinen Regen" is parsed as a child of "geben" while the head of the EC is "wird"
                "Die Regierung scheint keinen Plan zu haben, um die Probleme der Landwirtschaft zu lösen", # OK
                "Die Regierung kündigte an, keine weiteren Zugeständnisse zu machen.", # EC only negated - OK
                "Die Regierung versprach keine weiteren Zugeständnisse." # all negated - OK
                ]]




for doc in docs:
    for token in doc:
        # costum attribute `is_negated`
        token.set_extension("is_negated", default = False, force=True)
        token._.is_negated = token.ent_type_ == "NEGATION"
    for i in range(5):
        
        for token in doc:
            if token._.is_negated:
                for daughter in token.children:
                    # spread to children *except* in the case of negative verbs, where we only spread to the object (clausal or nominal)
                    if daughter.dep_ in ('oc', 'oa') or not (token.pos_ == "VERB" and token.ent_type_ == "NEGATION"):
                        daughter._.is_negated = True
            # spread to the head unless you're a verb, in which case you might either be a negative verb, or we've likely arrived at a clause boundary
            if token._.is_negated and token.pos_ not in  ("VERB", "AUX"):
                token.head._.is_negated = True
    print([(token, token._.is_negated) for token in doc])

#Output
#=====
#[(Ich, True), (glaube, True), (nicht, True), (,, True), (dass, True), (du, True), (eine, True), (Ahnung, True), (hast, True)]
#[(Ich, True), (bezweifle, True), (,, True), (dass, True), (du, True), (eine, True), (Ahnung, True), (hast, True)]
#[(Ich, False), (glaube, False), (,, False), (das, True), (ist, True), (nicht, True), (,, True), (was, True), (du, True), (mir, True), (sagen, True), (willst, True), (., False)]
#[(Ich, True), (weiß, True), (nicht, True), (,, True), (warum, True), (du, True), (mir, True), (das, True), (sagst, True)]
#[(Ich, True), (bezweifle, True), (deine, True), (Redlichkeit, True), (., True)]
#[(Ich, False), (bestreite, False), (deine, False), (Redlichkeit, False), (., False)]
#[(Er, False), (bezweifelt, True), (immer, False), (noch, False), (,, False), (dass, True), (das, True), (wahr, True), (sein, True), (kann, True)]
#[(Wladimir, False), (Putin, False), (bestreitet, True), (beim, False), (heutigen, False), (Gipfeltreffen, False), (erneut, False), (,, False), (dass, True), (Russland, True), (in, True), (Syrien, True), (Angriffe, True), (vertuscht, True), (., False)]
#[(Gestern, False), (stand, False), (in, False), (der, False), (Zeitung, False), (,, False), (dass, False), (es, False), (am, True), (Wochenende, True), (keinen, True), (Regen, True), (geben, True), (wird, False), (., False)]
#[(Die, False), (Regierung, False), (scheint, False), (keinen, True), (Plan, True), (zu, True), (haben, True), (,, True), (um, True), (die, True), (Probleme, True), (der, True), (Landwirtschaft, True), (zu, True), (lösen, True)]
#[(Die, False), (Regierung, False), (kündigte, False), (an, False), (,, False), (keine, True), (weiteren, True), (Zugeständnisse, True), (zu, True), (machen, True), (., False)]
#[(Die, True), (Regierung, True), (versprach, True), (keine, True), (weiteren, True), (Zugeständnisse, True), (., True)]


for doc in docs:
    # pintpointing the problem: "bezweifle" is parsed as an adjective!
    print ([(token, token.pos_, token.ent_type_) for token in doc if token.head == token])
    

#[(glaube, 'VERB', '')]
#[(bezweifle, 'ADJ', 'NEGATION')]
#[(glaube, 'VERB', '')]
#[(weiß, 'VERB', '')]
#[(bezweifle, 'ADJ', 'NEGATION')]
#[(bestreite, 'VERB', '')]
#[(bezweifelt, 'VERB', 'NEGATION')]
#[(bestreitet, 'VERB', 'NEGATION')]
#[(stand, 'VERB', '')]
#[(scheint, 'VERB', '')]
#[(kündigte, 'VERB', '')]
#[(versprach, 'VERB', '')]

 