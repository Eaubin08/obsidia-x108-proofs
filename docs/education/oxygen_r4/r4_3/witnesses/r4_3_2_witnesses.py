"""Fresh R4.3.2 synthetic witnesses (independent reviewer). Invented word 'brelin', opaque senses B1/B2.
Items: (id, word, sentence, label, domain, register). Curricula C2/C3/C5 are disjoint (no sentence repeated)."""
W = "brelin"
C5 = [
 ("L5-1-1",W,"Le pêcheur pose son filet sur le brelin du voilier.","B1","x","c"),
 ("L5-1-2",W,"Les marins ont hissé la voile sur le brelin avant la tempête.","B1","x","c"),
 ("L5-1-3",W,"Une mouette se repose sur le brelin du port.","B1","x","c"),
 ("L5-1-4",W,"Le capitaine grimpe sur le brelin pour observer la mer.","B1","x","c"),
 ("L5-1-5",W,"On amarre la barque sur le brelin près du quai.","B1","x","c"),
 ("L5-2-1",W,"Le cuisinier fait mijoter la soupe dans le brelin en fonte.","B2","x","c"),
 ("L5-2-2",W,"Ma grand-mère prépare la confiture dans le brelin de cuivre.","B2","x","c"),
 ("L5-2-3",W,"Il faut remuer la sauce dans le brelin sans arrêt.","B2","x","c"),
 ("L5-2-4",W,"Le chef verse le bouillon dans le brelin bien chaud.","B2","x","c"),
 ("L5-2-5",W,"On cuit les légumes dans le brelin pendant une heure.","B2","x","c"),
]
C3 = [
 ("L3-1-1",W,"Le matelot attache la corde sur le brelin du navire.","B1","x","c"),
 ("L3-1-2",W,"Les vagues frappent sur le brelin du chalutier.","B1","x","c"),
 ("L3-1-3",W,"Le mousse s'assoit sur le brelin à la proue.","B1","x","c"),
 ("L3-2-1",W,"La cuisinière fait fondre le beurre dans le brelin.","B2","x","c"),
 ("L3-2-2",W,"Le pâtissier mélange la crème dans le brelin.","B2","x","c"),
 ("L3-2-3",W,"On fait bouillir l'eau dans le brelin pour les pâtes.","B2","x","c"),
]
C2 = [
 ("L2-1-1",W,"Le gardien du phare monte sur le brelin de la goélette.","B1","x","c"),
 ("L2-1-2",W,"Les pirates ont caché le trésor sur le brelin du galion.","B1","x","c"),
 ("L2-2-1",W,"Mon oncle fait revenir les oignons dans le brelin.","B2","x","c"),
 ("L2-2-2",W,"La serveuse réchauffe le potage dans le brelin.","B2","x","c"),
]
CURRICULA = {2: C2, 3: C3, 5: C5}
# POS-COV: 8 unseen questions (4 B1, 4 B2), run at n=2,3,5; obligatory at n=5 (>=1 answer, precision 1.0)
COV = [
 ("Q1",W,"Le vieux marin dort sur le brelin du voilier.","B1"),
 ("Q2",W,"Un pêcheur répare son filet sur le brelin du bateau.","B1"),
 ("Q3",W,"Le capitaine attend sur le brelin du port.","B1"),
 ("Q4",W,"Les mouettes crient sur le brelin face à la mer.","B1"),
 ("Q5",W,"Le chef fait mijoter le ragoût dans le brelin.","B2"),
 ("Q6",W,"Ma tante remue la soupe dans le brelin en fonte.","B2"),
 ("Q7",W,"On prépare la sauce dans le brelin de cuivre.","B2"),
 ("Q8",W,"Le cuisinier verse les légumes dans le brelin chaud.","B2"),
]
# (id, word, sentence, curriculum n, expected: label | 'HOLD' | 'LABEL_OR_HOLD:Bx' | 'MOT_INCONNU' | 'RAPPEL:Bx')
WITNESSES = [
 ("POS-1",W,"Le timonier navigue sur le brelin du cotre.",3,"LABEL_OR_HOLD:B1"),
 ("POS-2",W,"Le traiteur fait rissoler les échalotes dans le brelin.",3,"LABEL_OR_HOLD:B2"),
 ("NEG-UNREL-1",W,"Le brelin surgit sans prévenir.",5,"HOLD"),
 ("NEG-UNREL-2",W,"Un brelin passait par là hier.",5,"HOLD"),
 ("NEG-MIX-BAL",W,"Le capitaine du voilier verse le bouillon dans le brelin.",5,"HOLD"),
 ("NEG-MIX-UNBAL",W,"Le marin fait mijoter la soupe dans le brelin en fonte.",5,"HOLD"),
 ("NEG-NEWWORD","quorvel","Le quorvel flotte près du port.",5,"MOT_INCONNU"),
 ("ADV-1-constr-trompeuse",W,"Le cuisinier fait mijoter la soupe sur le brelin.",5,"HOLD"),
 ("ADV-2-mot-dans-autre-constr",W,"Le marin hisse la voile dans le brelin.",5,"HOLD"),
 ("ADV-3-genitif-seul",W,"Le brelin du voisin a disparu cette nuit.",5,"HOLD"),
 ("ADV-4-construction-partagee",W,"Le brelin est grand.",5,"HOLD"),
 ("ADV-5-mix-inverse-unbal",W,"La soupe du capitaine refroidit sur le brelin du voilier près du quai.",5,"HOLD"),
 ("RAPPEL",W,"Le pêcheur pose son filet sur le brelin du voilier.",5,"RAPPEL:B1"),
]
# CONTRA (on C5): exercise labelled B1, contested towards B2. Question leans only on it.
CONTRA_EXERCISE = ("EX-B1",W,"Le navigateur s'appuie sur le brelin du canot.","B1","x","c")
CONTRA_CORRECTION = ("CX-1","EX-B1","Ici brelin relève de B2.")
CONTRA_QUESTIONS = [
 ("CONTRA-q",W,"Le navigateur s'appuie sur le brelin du canot rouge.","HOLD_OR_NOT_FROM_EX"),
 ("CONTRA-rappel",W,"Le navigateur s'appuie sur le brelin du canot.","HOLD"),
]
