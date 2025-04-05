import pandas as pd
import Scripts.utils as u

class Badgeuse():

    def __init__(self, numero, fonction, signaleur, gain_temps=0, obligatoire = False, repetable=False, h_mass_start=None):

        """
        numero est le numero de la badgeuse
        fonction est la fonction de la badgeuse dans la liste ["depart", "fin", "gel", "degel", "gel_1_point", "entre_bo", "debut_grimpeur", "fin_grimpeur"]
        gain_temps est le gain de temps éventuel associé à la badgeuse
        signaleur est le signaleur qui a la badgeuse   
        repetable est en entier qui indique quelle occurence de la badgeuse on doit prendre en compte      
        """

        self.numero = numero
        self.gain_temps = gain_temps
        self.signaleur = signaleur
        self.fonction = fonction
        self.repetable = repetable
        self.h_mass_start = h_mass_start
        self.obligatoire = obligatoire

    
    def __str__(self):
        return f"Badgeuse {self.numero}"
        
        



class data_epreuve():

    """
    les data des epreuves sont renseignés dans un csv avec les colonnes :
    nom;participation;victoire;record;temps_ref;points_gain_min;points_perte_min;type
    """

    def __init__(self, nom):
        self.nom = nom 
        self.type =""
        pass

    def __str__(self):
        return f"Epreuve {self.nom}"

            

class data_epreuve_acti(data_epreuve):

    def __init__(self, nom, participation, victoire, record):
        super().__init__(nom)
        self.type = "acti"
        self.victoire = victoire
        self.record = record
        self.participation = participation
    



class data_epreuve_co(data_epreuve):

    def __init__(self, nom,participation):
        super().__init__(nom)
        self.type = "co"
        self.nom = nom
        self.participation = participation


class data_epreuve_avec_doigts(data_epreuve):

    def __init__(self, nom):
        super().__init__(nom)
    
    def check(self, nom, L_badgeuse):
        """
        L_badgeuse est une liste de badgeuse
        """
        if not self.is_L_badgeuse_valide(L_badgeuse):
            raise ValueError(f"erreur dans la construction de l'épreuve {nom}, on a {[L_badgeuse[i].numero for i in range(len(L_badgeuse))]}")

    def is_L_badgeuse_valide(self, L_badgeuse):
        pass

  
    
    def count_badgeuse(self, L_badgeuse_final, equipe):
        """
        on vérifie que l'on a bien le bon nombre de badgeuses pour une épreuve donnée
        """
        D_test = {self.ordre_badgeuse[i].signaleur:0 for i in range(len(self.ordre_badgeuse)) if self.ordre_badgeuse[i].obligatoire}
        for (badgeuse, temps) in L_badgeuse_final: 
            if badgeuse.obligatoire:
                D_test[badgeuse.signaleur] +=1

        D_ref = {self.ordre_badgeuse[i].signaleur:0 for i in range(len(self.ordre_badgeuse)) if self.ordre_badgeuse[i].obligatoire}
        for bagdgeuse in self.ordre_badgeuse:
            if badgeuse.obligatoire:
                D_ref[bagdgeuse.signaleur] += 1

        for signaleur in D_ref.keys():
            if D_test[signaleur] !=D_ref[signaleur]:
                raise ValueError(f"il y a un problème avec la badgeuse avec le signaleur {signaleur} pour l'épreuve {self.nom}: on trouve {D_test[signaleur]} occurences pour le doigt {equipe} ")


class data_obli(data_epreuve_avec_doigts):

    def __init__(self, nom, L_badgeuse):   
        super().__init__(nom)
        self.type = "obli"
        self.check(nom, L_badgeuse)
        self.ordre_badgeuse = L_badgeuse

    
    def is_L_badgeuse_valide(self, L_badgeuse):
        """
        on vérifie si on a bien un départ, une arrivée, si un gel est toujours suivi d'un dégel unique
        """
        if len(L_badgeuse)>=2:
            res = L_badgeuse[0].fonction == "depart" and L_badgeuse[-1].fonction == "fin"
            i = 1
            while i <len(L_badgeuse) and res:
                if L_badgeuse[i].fonction == "gel":
                    res = L_badgeuse[i+1].fonction == "degel"
                    i+=2
                else:
                    i+=1
            return res           
        else :
            raise TypeError(f"erreur dans la construction de l'épreuve {self.nom}, on a {[L_badgeuse[i].numero for i in range(len(L_badgeuse))]}")
    
    def traite_doigts (self, L_badgeuse, equipe):
        """
        fonction qui s'assure que la liste des doigts est mis sous le bon format 
        L_badgeuse est une liste de couple (badgeuse, temps) associé à une épreuve
        on vérifie également que toutes les badgeuses obligatoires sont bien présentes
        equipe est le numéro de l'équipe, il sert pour le débuggage
        """


        L_badgeuse_final = []

        D={}
        for (badgeuse, temps) in L_badgeuse:
            if badgeuse.signaleur in [self.ordre_badgeuse[i].signaleur for i in range(len(self.ordre_badgeuse))]:
                if badgeuse.signaleur not in D:
                    D[badgeuse.signaleur] = []
                D[badgeuse.signaleur].append((badgeuse,temps))


        #on traite ici le cas spécial des mass start
        if self.ordre_badgeuse[0].h_mass_start not in ["", "nan"] and pd.notna(self.ordre_badgeuse[0].h_mass_start) : # and self.ordre_badgeuse[0].h_mass_start 
            try :
                L_badgeuse_final.append((self.ordre_badgeuse[0], u.sec_from_heure(self.ordre_badgeuse[0].h_mass_start)))
            except:
                raise ValueError(f"erreur dans la construction de l'épreuve {self.nom}, on a {[(L_badgeuse[i][0].numero,L_badgeuse[i][1]) for i in range(len(L_badgeuse))]} pour l'equipe {equipe}")


        for signaleur in D.keys():
            badgeuse_associe = D[signaleur][0][0]
            if not badgeuse_associe.repetable:

                if badgeuse_associe.fonction == "gel":
                    D[signaleur] = [D[signaleur][-1][1]]
                elif badgeuse_associe.fonction == "degel":
                    D[signaleur] = [D[signaleur][0][1]]
                elif badgeuse_associe.fonction == "depart":
                    D[signaleur] = [D[signaleur][-1][1]]
                elif badgeuse_associe.fonction == "fin":
                    D[signaleur] = [D[signaleur][0][1]]
                elif badgeuse_associe.fonction == "gel_1_point":
                    D[signaleur] = [D[signaleur][-1][1]]
                else:
                    raise ValueError(f"la badgeuse {badgeuse_associe.numero} n'est pas répétable et n'a pas de fonction valide")
                L_badgeuse_final.append((badgeuse_associe,D[signaleur][0]))
            else:


                for occurence in D[signaleur]:
                    L_badgeuse_final.append(occurence)

        self.count_badgeuse(L_badgeuse_final, equipe)

        return L_badgeuse_final
        
class data_bo(data_epreuve_avec_doigts):

    def __init__(self, nom, L_badgeuse):   
        super().__init__(nom)
        self.type = "bo"
        self.check(nom, L_badgeuse)
        self.ordre_badgeuse = L_badgeuse

    def is_L_badgeuse_valide(self, L_badgeuse):
        """
        on vérifie qu'on a bien un départ et une arrivée, si un gel est toujours suivi d'un dégel unique
        """
        if len(L_badgeuse)>=1:
            res = L_badgeuse[0].fonction == "depart" and L_badgeuse[-1].fonction == "fin" 
            i = 1
            while i <len(L_badgeuse) and res:
                if L_badgeuse[i].fonction == "gel":
                    res = L_badgeuse[i+1].fonction == "degel"
                    i+=2
                else:
                    i+=1
            return res           
        else :
            raise ValueError(f"erreur dans la construction de l'épreuve {self.nom}, on a {[L_badgeuse[i].numero for i in range(len(L_badgeuse))]}")
    
     
    def traite_doigts(self, L_badgeuse, equipe):
        """
        fonction qui s'assure que la liste des doigts est mis sous le bon format 
        L_badgeuse est une liste de couple (badgeuse, temps) associé à une épreuve
        on vérifie également que toutes les badgeuses obligatoires sont bien présentes
        equipe est le numéro de l'équipe, il sert pour le débuggage
        """


        L_badgeuse_final = []

        D={}
        for (badgeuse, temps) in L_badgeuse:
            if badgeuse.signaleur in [self.ordre_badgeuse[i].signaleur for i in range(len(self.ordre_badgeuse))]:
                if badgeuse.signaleur not in D:
                    D[badgeuse.signaleur] = []
                D[badgeuse.signaleur].append((badgeuse,temps))

        #on traite ici le cas spécial des mass start
        if self.type == "obli" and self.ordre_badgeuse[0].h_mass_start != '':
            L_badgeuse_final.append((self.ordre_badgeuse[0], u.sec_from_heure(self.ordre_badgeuse[0].h_mass_start)))



        for signaleur in D.keys():
            badgeuse_associe = D[signaleur][0][0]
            if badgeuse_associe.fonction == "gel":
                D[signaleur] = [D[signaleur][-1][1]]
            elif badgeuse_associe.fonction == "degel":
                D[signaleur] = [D[signaleur][0][1]]
            elif badgeuse_associe.fonction == "depart":
                D[signaleur] = [D[signaleur][0][1]]
            elif badgeuse_associe.fonction == "fin":
                D[signaleur] = [D[signaleur][-1][1]]
            elif badgeuse_associe.fonction == "gel_1_point":
                D[signaleur] = [D[signaleur][-1][1]]
            else:
                raise ValueError(f"la badgeuse {badgeuse_associe.numero} n'est pas répétable et n'a pas de fonction valide")
            L_badgeuse_final.append((badgeuse_associe,D[signaleur][0]))


        self.count_badgeuse(L_badgeuse_final, equipe)

        return L_badgeuse_final


class data_Grimpeur(data_epreuve_avec_doigts):

    def __init__(self, nom, participation,L_badgeuse):   
        super().__init__(nom)
        self.type = "grimpeur"
        self.ordre_badgeuse = None
        self.participation = participation #participation représente le nombre de points gagnés par le premier du grimpeur 
        self.check(nom, L_badgeuse)
        self.ordre_badgeuse = L_badgeuse


    def is_L_badgeuse_valide(self, L_badgeuse):
        """
        on vérifie qu'on a bien un départ et une arrivée (on n'autorise pas les gels/dégels sur les grimpeurs)
        """
        if len(L_badgeuse)==2: 
            return (L_badgeuse[0].fonction == "depart" and L_badgeuse[-1].fonction == "fin")
        else :
            raise ValueError(f"erreur dans la construction de l'épreuve {self.nom}, on a {[L_badgeuse[i].numero for i in range(len(L_badgeuse))]}")
    
    def traite_doigts (self, L_badgeuse, equipe):
        if L_badgeuse[0][0].fonction == "depart" and L_badgeuse[-1][0].fonction == "fin":
            self.count_badgeuse(L_badgeuse, equipe)
            return L_badgeuse
        else:
            raise ValueError(f"erreur dans la construction de l'épreuve {self.nom}, on a {[(L_badgeuse[i][0].numero,L_badgeuse[i][1]) for i in range(len(L_badgeuse))]} pour l'equipe {equipe}")


class data_parcours():
    """
    classe qui a pour but de stocker toutes les infos du parcours parès les avoir lu sur le csv. Les épreuves seront stockés via les classes au-dessus
    tout celà est indépendant de ce qu'il y a au-dessus
    rajouter une badgeuse 0 dans le fichier des badgeuse si on a une masse start
    """
    def __init__(self, path):

        df = pd.read_csv(path + "POLIS_parcours.csv", sep=";")
        self.epreuves = []
        for i in range(df.shape[0]):
            row = df.iloc[i]
            if row["type"] == "acti":
                epreuve = data_epreuve_acti(row["nom"], int(row["participation"]), int(row["victoire"]), int(row["record"]))
            elif row["type"] == "co":
                epreuve = data_epreuve_co(row["nom"], row["participation"])
            else: 
                POLIS_badgeuse = pd.read_csv(path + "POLIS_badgeuses.csv", sep=";")
                L_badgeuse = self.create_L_badgeuse(row["nom"], POLIS_badgeuse)
                if row["type"] == "Obli":
                    epreuve = data_obli(row["nom"], L_badgeuse)
                elif row["type"] == "bo":
                    epreuve = data_bo(row["nom"], L_badgeuse)
                elif row["type"] == "Grimpeur":
                    epreuve = data_Grimpeur(row["nom"], row["participation"], L_badgeuse)
                else:
                    raise TypeError(f"Erreur : le type {row['type']} n'est pas un type d'épreuve valide")
            # if epreuve.nom == "Obli 2":
            #     print(epreuve.nom, epreuve.ordre_badgeuse[0].h_mass_start)
            #     a=1/0
            self.epreuves.append(epreuve)

    def create_L_badgeuse(self, nom, POLIS_badgeuse):
        """
        on crée la liste des badgeuses pour une épreuve donnée
        """
        L_badgeuse = []
        for i in range(POLIS_badgeuse.shape[0]):
            row = POLIS_badgeuse.iloc[i]
            if row["epreuve"] == nom:
                L_badgeuse.append(Badgeuse(row["numero"], row["fonction"], row["signaleur"], gain_temps=row["temps bonus"], obligatoire= pd.notna(row["obligatoire"]), repetable= int(row["repetable"]), h_mass_start=row["heure mass start"]))

        return L_badgeuse

    def get_badgeuse(self, res_clear):

        """
        fonction qui, à chaque occurence d'une badgeuse, associe la bonne badgeuse. 
        """

        res = []           
        D_occurence = {num_badgeuse:0 for (num_badgeuse, temps) in res_clear}
        for num_badgeuse, temps in res_clear:
            D_occurence[num_badgeuse] += 1
            for epreuve in self.epreuves:
                if epreuve.type in ["obli", "bo", "grimpeur"]:
                    for badgeuse in epreuve.ordre_badgeuse:
                        if epreuve.type == "bo":
                            L= epreuve.ordre_badgeuse
                        if badgeuse.numero == num_badgeuse:
                            if badgeuse.repetable == D_occurence[badgeuse.numero]:
                                res.append((badgeuse, temps))

        return res 