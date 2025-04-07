import Scripts.utils as u
"""
Le type d'acti possible est 
-CO (on les gère éventuellement avec des gels/dégels ou avec un gel/gain de temps)
-BO
-Obli
-Grimpeur
-Acti
"""

class Epreuve():

    def __init__(self, peloton, epreuve):
        self.peloton = peloton
        self.nom = epreuve.nom
        self.epreuve = epreuve
        self.classement = {"H": [], "F": [], "M": [], "Hent" : [], "Fent": [], "Ment": []}
        pass
    
    def make_classement():
        pass

    def classer(self, equipe, temps):

        if equipe.ent:
            self.classement[equipe.mixite+"ent"].append((equipe, temps))
        else:
            self.classement[equipe.mixite].append((equipe, temps))

    def classement_finaux_epreuves(self):
        self.classement.sort(key = lambda x: x[1])


class Epreuve_co(Epreuve):

    """
    Pour une épreuve de type CO, on fait comme on avait fait au NND :
    - le respo CO envoie un fichier csv avec les équipes et le temps gagné directement 
    - on ne traite que les équipes qui ont fait la CO
    """

    def __init__(self, peloton, epreuve, data_co):
        super().__init__(peloton, epreuve)
        self.data_co = data_co

    def make_classement(self):
        data = self.data_co
        for num_equipe,res_co in data.items():
            equipe = self.peloton.find_equipe_num(num_equipe)
            if res_co != 0:
                self.classer(equipe, -res_co)
                equipe.add_epreuves(self.nom, -res_co) 


class Epreuve_acti(Epreuve):

    """
    Pour les actis, les respos infos envoient un excel à remplir avec toutes les actis. 
    Pour chaque acti, on a une page avec participation/victoire/record (éventuellement)
    Il faut que les noms des épreuves sur l'excel rempli par les staffeurs et dans l'excel coïncide pour qu'on note les points/temps gagnés
    Ici, on traite les actis une par une 
    """

    def __init__(self, peloton, epreuve, res_acti):
        super().__init__(peloton, epreuve)
        self.data_acti = res_acti


    def make_classement(self):
        data = self.data_acti
        for num_equipe,res_acti in data.items():
            equipe = self.peloton.find_equipe_num(num_equipe)
            if equipe != None:
                if data[num_equipe][0]: #si l'équipe participe à l'acti
                    res_epreuve = self.epreuve.participation
                    if self.epreuve.victoire != 0 and data[num_equipe][1]: #si elle gagne
                        res_epreuve=self.epreuve.victoire
                        if self.epreuve.record != 0 and data[num_equipe][2]: #si elle établit le record de l'acti
                            res_epreuve = self.epreuve.record
                    
                    self.classer(equipe, -res_epreuve) #l'équipe n'est classé sur l'acti que si elle a participé 
                    equipe.add_epreuves(self.nom, -res_epreuve) 
            else:
                raise ValueError(f"Erreur : l'équipe {num_equipe} n'existe pas dans le peloton")


class EpreuveGrimpeur(Epreuve):

    def __init__(self, peloton, epreuve, res_grimpeur):
        super().__init__(peloton, epreuve)  
        self.res_grimpeur = res_grimpeur
        self.res_inter = []

    def make_classement(self, peloton):
        
        res_inter = [(equipe, self.res_grimpeur[equipe][1][1]-self.res_grimpeur[equipe][0][1]) for equipe in self.res_grimpeur.keys()]
        res_inter.sort(key = lambda x: x[1])
        self.res_inter = res_inter


        for i in range(len(res_inter)):
            equipe = res_inter[i][0]
            temps_effectif = res_inter[i][1] - max(0, int(self.epreuve.participation*(20-i)/20))
            real_equipe = peloton.find_equipe_doigts(equipe)
            self.classer(real_equipe, temps_effectif)
            real_equipe.add_epreuves(self.nom, temps_effectif)
        

        for type_equipe in self.classement.keys():
            self.classement[type_equipe].sort(key = lambda x: x[1])

class EpreuveObli(Epreuve):

    def __init__(self, peloton, epreuve, res_obli):
        super().__init__(peloton, epreuve)  
        self.res_obli = res_obli


    def make_classement(self, peloton):

        for equipe in self.res_obli.keys():
            compteur = 0
            temps_effectif = 0

            real_equipe = peloton.find_equipe_doigts(equipe)
            self.res_obli[equipe] = u.L_badgeuse_valide(self.res_obli[equipe], real_equipe, self.nom)
            while compteur < len(self.res_obli[equipe])-1:
                if self.res_obli[equipe][compteur][0].fonction == "depart":
                    temps_effectif += self.res_obli[equipe][compteur+1][1] - self.res_obli[equipe][compteur][1] - self.res_obli[equipe][compteur][0].gain_temps
                elif self.res_obli[equipe][compteur][0].fonction == "gel":
                    temps_effectif -= self.res_obli[equipe][compteur][0].gain_temps
                elif self.res_obli[equipe][compteur][0].fonction == "gel_1_point":
                    temps_effectif += self.res_obli[equipe][compteur+1][1] - self.res_obli[equipe][compteur][1]-self.res_obli[equipe][compteur][0].gain_temps
                elif self.res_obli[equipe][compteur][0].fonction == "fin":
                    temps_effectif -= self.res_obli[equipe][compteur][0].gain_temps
                    if self.res_obli[equipe][compteur][0].numero == 10:
                        a=1/0
                
                if self.res_obli[equipe][compteur][0].numero == 34:
                    real_equipe.a_vu_bo = True
                compteur += 1
                
                    


                
            # if real_equipe.numero == 139 and self.nom == "Obli 3":
            #     print(real_equipe.nom)
            #     print(equipe)
            #     print([(self.res_obli[1915558][i][0].fonction, self.res_obli[1915558][i][1])for i in range(len(self.res_obli[1915558]))])
            #     print([(self.res_obli[1915569][i][0].fonction, self.res_obli[1915569][i][1]) for i in range(len(self.res_obli[1915569]))])
            #     print([(self.res_obli[1000947][i][0].fonction, self.res_obli[1000947][i][1]) for i in range(len(self.res_obli[1000947]))])
            #     a=1/0

            try:
                self.classer(real_equipe, temps_effectif)
                real_equipe.add_epreuves(self.nom, temps_effectif)
            except:
                a=1
                # raise ValueError(f"Doigt {equipe} n'est pas dans le equipe.csv")
            
        
        for type_equipe in self.classement.keys():
            self.classement[type_equipe].sort(key = lambda x: x[1])


class EpreuveBo(Epreuve):

    
    def __init__(self, peloton, epreuve, res_bo):
        super().__init__(peloton, epreuve)  
        self.res_bo = res_bo


    def make_classement(self, peloton):

        for equipe in self.res_bo.keys():
            compteur = 0
            temps_effectif = 0
            

            # print(self.res_bo)
            real_equipe = peloton.find_equipe_doigts(equipe)
            while compteur <= len(self.res_bo[equipe])-2:
                if self.res_bo[equipe][compteur][0].fonction == "depart":
                    temps_effectif += self.res_bo[equipe][compteur+1][1] - self.res_bo[equipe][compteur][1] - self.res_bo[equipe][compteur][0].gain_temps
                elif self.res_bo[equipe][compteur][0].fonction == "degel":
                    temps_effectif += self.res_bo[equipe][compteur+1][1] - self.res_bo[equipe][compteur][1] - self.res_bo[equipe][compteur][0].gain_temps
                elif self.res_bo[equipe][compteur][0].fonction == "gel":
                    temps_effectif -= self.res_bo[equipe][compteur][0].gain_temps
                elif self.res_bo[equipe][compteur][0].fonction == "gel_1_point":
                    temps_effectif += self.res_bo[equipe][compteur+1][1] - self.res_bo[equipe][compteur][1]-self.res_bo[equipe][compteur][0].gain_temps
                elif self.res_bo[equipe][compteur][0].fonction == "fin":
                    temps_effectif -= self.res_bo[equipe][compteur][0].gain_temps
                compteur += 1


            self.classer(real_equipe, temps_effectif)
            real_equipe.add_epreuves(self.nom, temps_effectif)
        
        
        for type_equipe in self.classement.keys():
            self.classement[type_equipe].sort(key = lambda x: x[1])
     