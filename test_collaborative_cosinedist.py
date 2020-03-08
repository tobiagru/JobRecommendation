import random
from datetime import datetime, timedelta
from collaborative_cosinedist import predict_most_similar

class DBTable:
    def __init__(self, elems=[]):
        self.elems = elems
    
    def add(self, elem):
        self.elems.append(elem)
    
    def filter(self, **kwargs):
        return DBTable([elem for elem in self.elems if all(getattr(elem, key, False) == val for key, val in kwargs.items())])
    
    def all(self):
        if len(self.elems) == 0:
            return None
        return self.elems
    
    def first(self):
        if len(self.elems) == 0:
            return None
        return self.elems[0]

class Model:
    def __init__(self):
        self.elems = []
        self._elem_unsaved = None
        self.objects = DBTable([])
    
    class ElemBase:
        def __init__(self):
            pass
        
        def __str__(self):
            return ", ".join(self.__dict__)
    
    def create(self, **kwargs):
        self.objects.add(self.Elem(**kwargs))

class UserJob(Model):
    class Elem(Model.ElemBase):
        def __init__(self, user_id, job_id, similarity_Skill, similarity_CF):
            self.user_id = user_id
            self.job_id = job_id
            self.similarity_Skill = similarity_Skill
            self.similarity_CF = similarity_CF

class Visit(Model):
    class Elem(Model.ElemBase):
        def __init__(self, user_id, job_id, duration):
            self.user_id = user_id
            self.job_id = job_id
            self.duration = duration
            
                
if __name__ == "__main__":
    date = datetime.now()

    num_users = 50
    num_jobs = 20
    
    visits = Visit()
    for idx in range(int(num_jobs * num_jobs / 2)):
        visits.create(user_id=random.randrange(num_users),
                      job_id=random.randrange(num_jobs),
                      duration=math.exp(random.randrange(57000)/10000))

    userjob = UserJob()
    predict_most_similar(visits.objects.all(), num_users, num_jobs, userjob)
    
