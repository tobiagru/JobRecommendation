import gensim.downloader as api
from datetime import timedelta
import numpy as np

def calc_similarity(sim_func, user_tags, job_tags):
    """
    calculates the similarity between to lists of tags.
    Sorts by pairs for strongest similarity.
    Adds a penalty for extra length in any list.
    
    args:
        sim_func: a numpy vectorized version of the model similarity function
        user_tags: list 1 of words
        job_tags: list 2 of words
    """
    #calculat an array of of all pairwise similarities
    M_similarities = sim_func(np.array([[tag.lower() for tag in user_tags]]),
                              np.array([[tag.lower() for tag in job_tags]]).T)
    M_similarities = np.ma.array(M_similarities, mask=False)
    
    
    #we only need to consider the shorter length
    dim_x, dim_y = M_similarities.shape
    if dim_x > dim_y:
        M_similarities = M_similarities.T
        dim_x, dim_y = dim_y, dim_x
        user_tags, job_tags = job_tags, user_tags
    
    #pick the strongest pairs
    sim_sum = 0
    
    M_similarities = M_similarities[np.argsort(M_similarities.max(axis=1))[::-1],:]
    for idx in range(M_similarities.shape[0]):
        idy = np.argmax(M_similarities[idx,])
        M_similarities.mask[:,idy] = True
        sim_sum += M_similarities[idx,idy]
    
    #apply a penalty
    return sim_sum * dim_x / dim_y

            
# In a flask setup this function would be run as a celery task
def update_users_jobs_similarity(users, jobs, UserJob, date):
    """
    updates the similarity between users and jobs for those where
    something changed since date
    
    args:
        users: list of users
        jobs: list of jobs
        UserJob: sqlalechmy or django.models Model
        date: datetime
    """
    # keep the model alive for the duration of the update
    tic = datetime.now()
    #model = api.load("conceptnet-numberbatch-17-06-300")
    def similarity_safe(wordA, wordB):
        try:
            return model.similarity(wordA, wordB)
        except:
            return 0.0
    vsim = np.vectorize(similarity_safe)
    print("download took: ", (datetime.now()-tic).seconds)
    
    tic = datetime.now()
    #we only want to update combinations where either side was updated
    #since date
    def updated(user, job, date):
        #change date_updated to the name of your update datetime
        return ((user.date_updated - date).seconds > 0 or
                (job.date_updated - date).seconds > 0)
    
    for user in users:
        for job in [job for job in jobs if updated(user, job, date)]:
            #we combined interests and skills, replace .skills and 
            # .interests by you fields
            #add preprocessing to turn them into a list if necessary
            user_tags = user.skills.all()
            job_tags = job.skills.all()
            sim = calc_similarity(vsim, user_tags, job_tags)
            userjob = UserJob.objects.filter(user_id=user.id, job_id=job.id).first()
            if userjob is None:
                UserJob.create(user_id=user.id, job_id=job.id, similarity=sim)
            else:
                userjob.similarity = sim
    print("update took: ", (datetime.now()-tic).seconds)
