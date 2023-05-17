from Constraint import *
from Templates import *
from Alphabet import *
from ConstraintList import *
from ConstraintFactory import *
from Hierarchy import *
import random
from black_sat import *

class Model: 
    cf = ConstraintFactory()
    constraint = Constraint()
    constraintlist = ConstraintList()
    sigma = alphabet()
    # alpha = Alphabet(alphabet_size)

    def __init__(self, filename, alphabet_size, set_size, weights, templates = []):
        constraint_templates = Templates(templates).templates
        # self.constraint_list = Model.cf.create_random(alphabet_size, set_size, weights, templates)
        self.constraint_list = Model.cf.create_consistent_model(alphabet_size, set_size, weights, constraint_templates)
        self.ltl_list = self.model_to_ltl()

        self.activities = Alphabet(alphabet_size).alphabet
        self.file = self.save_model(self.constraint_list, self.activities, filename)
        # self.activities = self.alpha.get_alphabet()
        # return model

    def __len__(self): # get the number of constraints in the generated model
        return len(self.constraint_list)

    def create_model(self, alphabet_size, set_size, weights, templates):
        model = Model.cf.create_consistent_model(alphabet_size, set_size, weights, templates)
        return model
    
    def model_to_ltl(self):
        constraint = Constraint()
        ltl_list = []
        for i in self.constraint_list:
            ltl_expression = constraint.declare_to_ltl(i, self.sigma)
            ltl_list.append(ltl_expression)
        return ltl_list

    def count_rules(self):
        pass 

    def specialise_model(self,specialized_model=[]): # user can indicate that he wants to keep a part of the initial model
        # to empty list if you already specialized once 
        if specialized_model == []:
            specialized_model = []
        else: specialized_model = specialized_model

        hierarchy = Hierarchy()
        n_initial_model = self.__len__()

        # Add first specialized constraint to specialized model -- Indien er niet gespec kan worden, dan wordt de constraint overgenomen
        if n_initial_model == 0: 
            return Model.cf.end_model_message("No specialization of initial model could be generated, because initial model is empty.")
        else:
            first_specialized_constraint = hierarchy.generate_specialisation_candidate(self.constraint_list[0])
            specialized_model.append(first_specialized_constraint)
            
            for index in range(1, n_initial_model):
                initial_constraint = self.constraint_list[index]
                if self.has_specialisation_in_model(initial_constraint, specialized_model):
                        random_choice = random.randint(0, 1) # Op dit moment 50% kans -- CHANGE: user input 
                        if random_choice==1:
                            specialized_constraint = hierarchy.generate_specialisation_candidate(initial_constraint)
                            
                            if not self.constraint_list.contains_constraint(specialized_constraint, specialized_model): # Indien template niet onderhevig aan dependency, 
                                # dan toevoegen
                                specialized_model.append(specialized_constraint)
                            else: 
                                pass
                        else: 
                            pass
                else:
                    specialized_constraint = hierarchy.generate_specialisation_candidate(initial_constraint)
                    if not self.constraint_list.contains_constraint(specialized_constraint, specialized_model): 
                        specialized_model.append(specialized_constraint)                
    
            return specialized_model

    def has_specialisation_in_model(self, constraint, specialized_model): # In specialized model
        specialized_model_class = [specialized_constraint.__class__ for specialized_constraint in specialized_model]
        match constraint.__class__.__name__:
            case 'Precedence'|'Response'|'Succession'|'AlternatePrecedence'|'AlternateResponse'|'AlternateSuccession'|'ChainPrecedence'| \
                'ChainResponse'|'RespondedExistence'|'CoExistence'|'NotSuccession'|'NotChainSuccession'|'Choice':

                candidate_list = Hierarchy.specialisation_candidates[constraint.__class__.__name__]

                potential_templates = list(set(candidate_list) & set(specialized_model_class))
                # has_specialisation = bool(set(candidate_list) & set(specialized_model_class))

                if potential_templates == []: 
                    return False 
                else: 
                    # [specialized_constraint for specialized_constraint.__class__.__name__ in potential_templates]

                    # test 

                    # potential_templates = [ChainResponse]
                    # specialized_model = [ChainResponse("a","b"),Response("b","c"),ChainResponse("b","c")] 
                    # specialized_model_class = [i.__class__ for i in specialized_model]
                    # constraint = Response("a","b")

                    potential_constraints = []
                    for i in range(len(potential_templates)): 
                        for j in range(len(specialized_model)):
                            if potential_templates[i] == specialized_model_class[j]:
                                potential_constraints.append(specialized_model[j])

                    potential_constraints_str = [str(i) for i in potential_constraints]

                    action = constraint.get_action()
                    reaction = constraint.get_reaction()

                    return any("{0},{1}".format(action,reaction) in i for i in potential_constraints_str)

            case 'Absence'|'Existence':
                return True 

            case _: return False 

    def check_consistency_model(self):
        slv = solver()
        xi = scope(self.sigma)

        unpacked = self.sigma.top()

        for c in self.ltl_list:
            unpacked = unpacked & c

        f = unpacked # test consistency by testing the conjunction

        return slv.solve(xi,f,True)
    
    def save_model(self, constraint_list, activities, filename):
        file = open(filename, 'w') # overwrites if file already exists
        output = Model.constraintlist.list_to_decl_extension(constraint_list, activities)
        file.write(str(output))
        file.close()

# Test

alphabet_size = 10 
set_size = 4
weights = [1]
templates = [RespondedExistence]

## juist: filename van plaats veranderd
model = Model("model6.decl", alphabet_size, set_size, weights, templates)
model.constraint_list
model.specialise_model()
