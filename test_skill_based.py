import random
from datetime import datetime, timedelta
from skill_based import update_users_jobs_similarity

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
    
    class Elem:
        def __init__(self):
            pass
        
        def __str__(self):
            return ", ".join(self.__dict__)
    
    def create(self, **kwargs):
        self.objects.add(self.Elem(**kwargs))
        

class Job(Model):
    class Elem:
        def __init__(self, id, skills, date_updated):
            self.id = id
            self.skills = skills
            self.date_updated = date_updated
            
        def __str__(self):
            return ", ".join(self.__dict__)
            
    
class User(Model):
    class Elem:
        def __init__(self, id, skills, date_updated):
            self.id = id
            self.skills = skills
            self.date_updated = date_updated
            
        def __str__(self):
            return ", ".join(self.__dict__)

class UserJob(Model):
    class Elem:
        def __init__(self, user_id, job_id, similarity):
            self.user_id = user_id
            self.job_id = job_id
            self.similarity = similarity
            
        def __str__(self):
            return ", ".join(self.__dict__)

skills = ["Python", "C++", "Javascript", "HTML", "CSS", "Golang", "Perl", "Ruby", "C#", "SQL", "Swift", "XCode", "Java", "Kotlin", "CAD", "CAM", "FEM", "Scrum", "Software Development", "Data Science", "Web Development", "Android Development", "iOS Development", "Market Analysis", "Marketing", "Business", "Sales", "Project Management", "Accounting", "Strategy", "Pricing", "Banking", "Retail", "Manufacturing", "Consumer Goods", "Software", "IT"]
        
if __name__ == "__main__":
    date = datetime.now()

    users = User()
    for idx in range(50):
        users.create(id=idx,
                     skills=DBTable([skills[random.randrange(len(skills))] for _ in range(random.randrange(3,10))]),
                     date_updated=date - timedelta(seconds=100))


    jobs = Job()
    for idx in range(30):
        jobs.create(id=idx, 
                    skills=DBTable([skills[random.randrange(len(skills))] for _ in range(random.randrange(3,10))]),
                    date_updated=date - timedelta(seconds=100))


    userjob = UserJob()
    update_users_jobs_similarity(users.objects.all(), jobs.objects.all(), userjob, date)
    
    for uj in userjob.objects.all():
        print(userjob)
