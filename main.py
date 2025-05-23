import Scripts.data_parcours as d
import Scripts.traite_data_graid as t
import pandas as pd
import Scripts.utils as u
import Scripts.epreuve as e
import Scripts.equipe as eq
import sys

peloton = eq.Peloton()

if len(sys.argv) == 1:
    print("Aucun argument donné, le programme va s'arrêter.")
    sys.exit(1)

if len(sys.argv) > 1:
    if sys.argv[1] == "J1":
        path = "./Essec_J1/Resultat_brut/"
        peloton.construct("./Essec_J1/Data_equipes_parcours/")
        parcours = d.data_parcours("./Essec_J1/Data_equipes_parcours/")
    elif sys.argv[1] == "J2":
        path = "./Essec_J2/Resultat_brut/"
        peloton.construct("./Essec_J2/Data_equipes_parcours/")
        parcours = d.data_parcours("./Essec_J2/Data_equipes_parcours/")
    elif sys.argv[1] == "weekend":
        u.return_fusion_result('./Essec_J1/', './Essec_J2/')
        sys.exit(0)
    else:
        print("Argument non reconnu, le programme va s'arrêter.")
        sys.exit(1)


# print([parcours.epreuves[i].nom for i in range(len(parcours.epreuves))])
# print([parcours.epreuves[i].type for i in range(len(parcours.epreuves))])
# print([[parcours.epreuves[i].ordre_badgeuse[j].numero for j in range(len(parcours.epreuves[i].ordre_badgeuse))] for i in range(len(parcours.epreuves)) if parcours.epreuves[i].type == "obli"])
res = t.gather_results(parcours, path)
res_acti = t.traite_data_actis(path)
res_co = t.traite_datas_co(path)
res_penalties = t.traite_datas_penalties(path)



#fonction pour afficher les résultats
"""def affiche_resultats(res):
    for epreuve in res.keys():
        print(f"Résultats pour l'épreuve {epreuve.nom} :")
        for equipe in res[epreuve].keys():
            print(f"Equipe {equipe} : {[(res[epreuve][equipe][i][0].numero,u.heure_from_sec(res[epreuve][equipe][i][1])) for i in range(len(res[epreuve][equipe]))]}")
        print("\n")

affiche_resultats(res)"""

# print([parcours.epreuves[i].type for i in range(len(parcours.epreuves))])
# a=1/0

res_final = {}
for epreuve in res.keys():
    res_final[epreuve] = {}
    if epreuve.type == "obli": 
        epreuve_a_classer = e.EpreuveObli(parcours, epreuve, res[epreuve])
        epreuve_a_classer.make_classement(peloton)
        res_final[epreuve] = epreuve_a_classer.classement

        if epreuve.nom == "Obli CO":
            print(res_co)
            res_final[epreuve] = {mixite: [(res_final[epreuve][mixite][i][0],res_final[epreuve][mixite][i][1] - res_co[res_final[epreuve][mixite][i][0].numero]) for i in range(len(res_final[epreuve][mixite]))] for mixite in res_final[epreuve].keys()}

    elif epreuve.type == "grimpeur":
        epreuve_a_classer = e.EpreuveGrimpeur(parcours, epreuve, res[epreuve])
        epreuve_a_classer.make_classement(peloton)
        res_final[epreuve] = epreuve_a_classer.classement

    elif epreuve.type == "bo":
        epreuve_a_classer = e.EpreuveBo(parcours, epreuve, res[epreuve])
        epreuve_a_classer.make_classement(peloton)   
        res_final[epreuve] = epreuve_a_classer.classement
    
    elif epreuve.type == "acti":
        epreuve_a_classer = e.Epreuve_acti(peloton, epreuve, res_acti[epreuve.nom])
        epreuve_a_classer.make_classement()
        res_final[epreuve] = epreuve_a_classer.classement

    elif epreuve.type == "co":
        if not sys.argv[1] == "J2":
            epreuve_a_classer = e.Epreuve_co(peloton, epreuve, res_co)
            epreuve_a_classer.make_classement()
            res_final[epreuve] = epreuve_a_classer.classement



    print("\n")
    print(f"Classement pour l'épreuve {epreuve.nom} :")
    for mixite in res_final[epreuve].keys():
        print(f"Mixité {mixite} : {[(res_final[epreuve][mixite][i][0].numero,u.heure_from_sec(res_final[epreuve][mixite][i][1])) for i in range(len(res_final[epreuve][mixite]))]}")

for type in peloton.equipes.keys():
    for equipe in peloton.equipes[type]:
        equipe.temps_total += res_penalties[equipe.numero]
        if sys.argv[1] == "J1":
            equipe.traite_bo()
            equipe.traite_type()

if len(sys.argv) > 1:
    if sys.argv[1] == "J1":
        path = "./Essec_J1/"
    elif sys.argv[1] == "J2":
        path = "./Essec_J2/"

# for type in peloton.equipes.keys():
#     for equipe in peloton.equipes[type]:
#         if sys.argv[1] == "J1":
#             print(f"Equipe {equipe.numero} : {u.heure_from_sec(equipe.temps_total)}")

def affiche_resultats_generaux(peloton):
    """
    Affiche les résultats généraux triés par temps total croissant.
    """
    equipes = []
    for type in peloton.equipes.keys():
        for equipe in peloton.equipes[type]:
            equipes.append((equipe.numero, equipe.temps_total))
    
    # Trier les équipes par temps total croissant
    equipes_triees = sorted(equipes, key=lambda x: x[1])
    
    print("\nRésultats généraux :")
    for rank, (numero, temps_total) in enumerate(equipes_triees, start=1):
        print(f"{rank}. Équipe {numero} : {u.heure_from_sec(temps_total)}")

affiche_resultats_generaux(peloton)
u.res_final_to_csv(res_final, path)
