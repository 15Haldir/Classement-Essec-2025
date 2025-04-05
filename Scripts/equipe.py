import csv

class Equipe():

    """
    classe représentant chaque équipe de la compétition, et qui contient toutes les infos qui lui sont associées
    mixite est de la forme ["H", "F", "M"] pour homme, femme, mixte
    complete est un booleen qui indique si l'équipe est complète ou non
    epreuves est la liste des epreuves auxquelles l'équipe a participé, chaque élément est un tuple (nom_epreuve, temps)
    """

    def __init__(self, numero, nom, doigts, mixite, complete=True, ent = False):
        self.numero = numero
        self.nom = nom
        self.doigts = doigts
        self.mixite = mixite
        self.complete = complete
        self.temps_total = 0
        self.points = 0
        self.ent = ent
        self.a_vu_bo = False
        self.epreuves = []
    
    def __str__(self):
        return f"Equipe {self.numero} : {self.nom} ({self.doigts} doigts)"
    
    def add_epreuves(self, nom_epreuves, temps):
        self.epreuves.append((nom_epreuves,temps))
        self.temps_total+=temps

    def traite_bo(self):
        if self.a_vu_bo and self.ent :
            self.temps_total -= 60*45

        if not self.a_vu_bo and not self.ent:
            self.temps_total += 60*50
    
    def traite_type(self):
        if not self.ent :
            self.temps_total -= 60*20




    

class Peloton():

    """
    ensemble d'équipe participant à un raid ou à un nnd. Ils sont séparés par mixité et par entreprise
    """

    def __init__(self):
        self.equipes = {"H": [], "F": [], "M": [], "Hent" : [], "Fent" : [], "Ment" : []}

    def ajoute_equipe(self, equipe):
        self.equipes[equipe.mixite].append(equipe)
    
    def construct(self, path):
        with open(path + "equipe.csv", "r") as csvfile:
            reader = csv.reader(csvfile, delimiter = '@')
            data = list(reader)
            for i in range(1,len(data)):
                row = data[i][0].split(";")
                if row[3] in ["H", "F", "M", "Hent", "Fent", "Ment"]:
                    print(row)
                    equipe = Equipe(int(row[0]), row[1], int(row[2]), row[3],  ent = int(row[4]))
                    self.ajoute_equipe(equipe)
                else:
                    print(f"Erreur : l'équipe {int(row[0])}, {row[3]} n'est pas un type de mixité valide")
                    a=1/0 
            
    def find_equipe_doigts(self, doigts):
        for mixite in self.equipes.keys():
            for equipe in self.equipes[mixite]:
                if equipe.doigts == doigts:
                    return equipe
        return None
    
    def find_equipe_num(self, num_equipe):
        for mixite in self.equipes.keys():
            for equipe in self.equipes[mixite]:
                if equipe.numero == num_equipe:
                    return equipe
        return None
    

