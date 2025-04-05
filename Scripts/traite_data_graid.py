import csv
import os 
import pandas as pd
import Scripts.utils as u

# ne pas utiliser 
def create_total_data(path):
    L_data_graid = []
    for file_name in os.listdir("""Resultat_brut/Data_graids"""):
        print(file_name)
        L_data_graid.append(pd.read_csv("""Resultat_brut/Data_graids/""" + file_name, sep = ";"))
    res = pd.concat(L_data_graid)
    (res.drop(res.columns[0], axis=1)).to_csv("Resultat_brut/data_graid_final.csv", sep = ";") 

def traite_data_graid(parcours, path):

    """
    Prend en entrée le fichier datas_graid.csv et retourne un dictionnaire avec comme clés le numéro de doigts de l'équipe et comme valeur une liste de couple badgeuse/temps 
    """
    D_correction = traite_data_correction(path)

    with open(path + 'datas_graid.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter = '@')
        data = list(reader)
        data_par_equipe = {}
        for i in range(1,len(data)):
            row = data[i]
            temps = row[0].split(';')
            if temps[2] not in data_par_equipe:
                equipe = int(temps[2])
                data_par_equipe[equipe] = []
                res_a_clear = []
                for i in range(len(temps) - 44): #int(temps[44])
                    if 47+3*i <len(temps) and temps[45+3*i] != "":
                        num_badgeuse = int(temps[45+3*i])
                        temps_badgeuse = u.sec_from_heure(temps[47+3*i])
                        res_a_clear.append((num_badgeuse, temps_badgeuse))
                    
                res_clear = clear_anomalies(res_a_clear)
                res_completement_clear = insert_correction(equipe, res_clear, D_correction)
                L_badgeuse = parcours.get_badgeuse(res_completement_clear)
                # print([L_badgeuse[i][0].signaleur for i in range(len(L_badgeuse))])
                # a=1/0
                for badgeuse, temps_badgeuse in L_badgeuse:
                    data_par_equipe[equipe].append([badgeuse, temps_badgeuse])
                    
            else:
                print("on rajoutera une erreur après")
                a=1/0
        return data_par_equipe


def clear_anomalies(res_equipe):
    """
    fonction qui vient clear les différents résultats en supprimant les occurences trop proches de deux bipages de badgeuse. On dit que 2 itérations sont trop proches si elles sont séparés de moins de 10s. On supprime alors la deuxième itération
    """
    res_equipe_clear = []
    i = 0
    while i <len(res_equipe)-1:
        (num_badgeuse,temps) = res_equipe[i]
        res_equipe_clear.append((num_badgeuse,temps))
        (num_badgeuse_suivante, temps_suivant) = res_equipe[i+1]
        if num_badgeuse_suivante == num_badgeuse:
            if abs(temps-temps_suivant)<=10:
                i+=1
        i+=1
    if i == len(res_equipe)-1:
        (num_badgeuse,temps) = res_equipe[i]
        res_equipe_clear.append((num_badgeuse,temps))
    return res_equipe_clear




def gather_results(parcours, path):

    """
    doigts est un dictionnaire avec comme clé le numéro de doigts de l'équipe et comme valeur une liste de couple badgeuse/temps
    On récupère les données de la badge, que l'on trie par épreuve
    On a la structure suivante :
    - on a un dictionnaire avec comme clé les épreuves
    - pour chaque épreuve, on a un dictionnaire avec comme clé les badgeuses et comme valeur une liste de couple numero de badgeuse/temps
    """

    doigts = traite_data_graid(parcours, path)
    res = {}

    for epreuve in parcours.epreuves:
        if epreuve.type in ["obli", "bo", "grimpeur"]:
            res[epreuve] = {}
            for num_equipe in doigts.keys():
                res[epreuve][num_equipe] = []

                for badgeuse, temps in doigts[num_equipe]:
                    if badgeuse.signaleur in [epreuve.ordre_badgeuse[i].signaleur for i in range(len(epreuve.ordre_badgeuse))]:
                        res[epreuve][num_equipe].append((badgeuse, temps))   

                res[epreuve][num_equipe]= epreuve.traite_doigts(res[epreuve][num_equipe], num_equipe)

        if epreuve.type == "acti":
            res[epreuve]={}
        
        if epreuve.type == "co":
            res[epreuve]={}
            
    return res


def traite_data_actis(path):

    # Charger le fichier Excel avec toutes les feuilles
        file_path = path + "datas_actis.xlsx"  # Remplace par ton fichier
        sheets = pd.read_excel(file_path, sheet_name=None)  # Lire toutes les feuilles en dictionnaire

        # Dictionnaire pour stocker les résultats de chaque feuille
        result = {}

        # Traiter chaque feuille individuellement
        for sheet_name, df in sheets.items():
            key_column = df.columns[0]  # La première colonne est la clé
            
            # Construire le dictionnaire pour cette feuille
            bool_dict = {int(row[key_column]): row.iloc[1:].notna().tolist()  for _, row in df.iterrows()}

            # Ajouter au résultat global
            result[sheet_name] = bool_dict

        return {nom_acti:{num_equipe : u.maj_liste_acti(result[nom_acti][num_equipe]) for num_equipe in result[nom_acti].keys()} for nom_acti in result.keys()}

def traite_datas_co(path):
    """
    Lit un fichier CSV et retourne un dictionnaire associant chaque numéro d'équipe à son score total.
    
    :param nom_fichier: Nom du fichier CSV
    :return: Dictionnaire {numero_equipe: score_total}
    """
    scores = {}
    file_path = path + "datas_co.csv"
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        data = list(reader)
        for i in range(1,len(data)):
            row = data[i]
            if len(row) >= 2:  # Vérifier qu'il y a bien au moins 2 colonnes
                num_equipe = int(row[0])
                try:
                    score = int(row[1])  # Convertir le score en nombre flottant
                    scores[num_equipe] = scores.get(num_equipe, 0) + score  # Ajouter au score total
                except ValueError:
                    print(f"Valeur invalide pour le score : {row[1]}")
    
    return scores


def traite_data_correction(path):

    """
    on structure les corrections sous la forme 
    equipe -> (numero badgeuse - occurence) -> le temps 
    """

    correction = {}
    file_path = path + "datas_correction.csv"
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        data = list(reader)
        for i in range(1,len(data)):
            row = data[i]
            if len(row) == 4:  # Les colonnes prises encompte ne sont que les colonnes pleines
                num_doigts = int(row[0])
                if not num_doigts in correction.keys():
                    correction[num_doigts] = {}

                num_badgeuse = int(row[1])  # Convertir le score en nombre flottant
                occurence = int(row[2])
                heure = u.sec_from_heure(row[3])
                correction[num_doigts][(num_badgeuse, occurence)] = heure    
    return correction

def insert_correction(num_badgeuse, L_badgeuse, D_correction): #au moment d'insérer les corrections, on doit mettre d'abord les suppressions puis les ajouts de badgeuse pour une équipe

    if num_badgeuse in D_correction.keys(): #si l'équipe a en effet des corrections apportés à son data graid 
        for (badgeuse, occurence),temps in D_correction[num_badgeuse].items():


            peut_inser = False  #on ne s'autorise à insérer les badgeuses que si les temps ne font pas n'importe quoi
            doit_supprimer = temps ==None

            if doit_supprimer:
                deja_vu = 0
            else:
                deja_vu = 1

            for  i in range(len(L_badgeuse)):
                (num_L_badgeuse,temps_badgeuse) = L_badgeuse[i]
                if peut_inser and not doit_supprimer and temps>=temps_badgeuse and (i == len(L_badgeuse)-1 or temps <= L_badgeuse[i+1][1]):
                    L_badgeuse.insert(i+1, (badgeuse, temps))
                    break
                if num_L_badgeuse == badgeuse:
                    deja_vu +=1
                if deja_vu == occurence:
                    peut_inser = True
                    deja_vu+=1
                    if doit_supprimer:
                        L_badgeuse.pop(i)
                        break
    return L_badgeuse


def traite_datas_penalties(path):

    penalties = {}
    file_path = path + "datas_penalties.csv"
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        data = list(reader)
        for i in range(1,len(data)):
            row = data[i]
            num_equipe = int(row[0])
            penalties[num_equipe] = 0
            if len(row) != 1 and row[1] != '':
                penalties[num_equipe] = int(row[1])

    return penalties