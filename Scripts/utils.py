import csv

def sec_from_heure(temps):
    """Convertit un temps donné dans l'un des deux formats ci-dessous en secondes depuis minuit :
    hh:mm:ss
    xxhmm (xx l'heure)"""
    if ":" in temps:
        return sum(int(x) * 60 ** (2 - i) for i, x in enumerate(temps.split(":")))
    if "h" in temps:
        return sum(int(x) * 60 ** (2 - i) for i, x in enumerate(temps.split("h")))

def n_digits(nb, n=2):
    return ("0" * n + str(nb))[-n:]

def heure_from_sec(secondes):
    secondes = int(secondes)
    if not secondes:
        return "-"
    sign = "-" if secondes < 0 else ""
    secondes = abs(secondes)
    res = f"{n_digits(secondes // 3600, 2)}h {n_digits((secondes // 60) % 60, 2)}m {n_digits(secondes % 60, 2)}s"

    while res[0] == "0" or not res[0].isdigit():
        res = res[1:]
        
    return sign + res

def maj_liste_acti(L):
    """
    fonction qui est chargé de dire que si une équipe a gagné, et bien, elle a aussi participé
    """
    n = len(L)
    L2 = [False] * n
    prochain_vrai = False

    for i in range(n - 1, -1, -1):
        if L[i]:
            prochain_vrai = True
        L2[i] = prochain_vrai
    return L2

def prep_res_to_csv(res):
    """
    on commence par préparer la liste en virant les objets créés auparavant
    """
    res_inter = {epreuve.nom : {mixite: {equipe.numero : res_num for (equipe,res_num) in res[epreuve][mixite]} for mixite in res[epreuve].keys()} for epreuve in res.keys()}
    """
    on vire la mixité 
    """
    return {epreuve.nom: {(equipe.numero, equipe.mixite, equipe.ent, equipe.nom, equipe.temps_total) : res_num for mixite in res[epreuve] for (equipe, res_num) in res[epreuve][mixite]}for epreuve in res}

def res_final_to_csv(res_final, path):
    
    res = prep_res_to_csv(res_final)
    # Get all unique teams
    all_teams = sorted({team for teams in res.values() for team in teams})

    # Get all race names (columns)
    races = sorted(res.keys())

    # Create CSV file
    csv_filename = path + "race_results.csv"
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        
        # Write header (Race names as columns)
        writer.writerow(["Team"] + ["Mixite"] + ["Ent"] + ["Nom"] +["Temps total"] + races)

        # Write rows for each team
        for team in all_teams:
            row = [team[i] for i in range(len(team))] + [res[race].get(team, "") for race in races]  # Ensure res[race] is used
            writer.writerow(row)

    print(f"CSV file '{csv_filename}' has been created successfully!")

def return_fusion_result(path1, path2):
    result = {}
    team = {}
    J1_results = {}
    J2_results = {}
    header = []
    with open(path1 + "race_results.csv", mode="r", newline="") as file1:
        reader1 = csv.reader(file1, delimiter=";")
        header = [elem.replace("Temps total", "Temps J1") for elem in next(reader1)]
        for row in reader1:
            J1_results[row[0]] = row[4:]
            team = row[:5] + [False]
            team[-2] = int(team[-2])
            result[team[0]] = team[1:]
    
    with open(path2 + "race_results.csv", mode="r", newline="") as file2:
        reader2 = csv.reader(file2, delimiter=";")
        header += [elem.replace("Temps total", "Temps J2") for elem in next(reader2)[4:]]
        for row in reader2:
            J2_results[row[0]] = row[4:]
            team = row[:5] + [False]
            team[-2] = int(team[-2])
            if team[0] in result:
                result[team[0]][-2] += team[-2]
                result[team[0]][-1] = True
            else:
                result[team[0]] = team[1:]
    
    with open("fusion_results.csv", mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        header.insert(4, "Temps total")
        writer.writerow(header)
        for team in result.keys():
            if result[team][-1]:
                writer.writerow([team] + result[team][:-1] + J1_results[team] + J2_results[team])
    pass


def L_badgeuse_valide(res_equipe, equipe, epreuve): 

    if res_equipe == None or len(res_equipe) <= 1:
        return []

    res_equipe_clear = []
    i = 0
    while i <len(res_equipe)-1:
        (badgeuse,temps) = res_equipe[i]
        (badgeuse_suivante, temps_suivant) = res_equipe[i+1]
        if badgeuse.fonction != "gel":
            res_equipe_clear.append((badgeuse,temps))
        else: 
            if badgeuse_suivante.fonction == "degel":
                res_equipe_clear.append((badgeuse,temps))
        i+=1
    try:
        res_equipe_clear.append((res_equipe[-1][0], res_equipe[-1][1]))
        return res_equipe_clear
    except:
        raise ValueError(f"Erreur dans l'épreuve {epreuve} pour l'équipe {equipe.numero} : {res_equipe}")
    
print(heure_from_sec(14109))

