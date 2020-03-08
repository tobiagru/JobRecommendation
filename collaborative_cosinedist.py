from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
import numpy as np
import math
import logging
logger = logging.getLogger(__name__)

def predict_most_similar(visits, num_users, num_jobs, UserJobs, k=20, cut_off=300, log_discrete=True, epsilon=1e-9):
    """
    Cosine Distance based
    
    creates a sparse matrix of the time a user spent on a job
    top cut off at cut_off sec (to overcome outliers). Time values
    are turned into log disrcete values between 0 and cut_off
    on a 0-255 basis (uint8) if log_discrete=True.
    
    Most of this is fairly slow due to the list structure which limits vectorization.
    
    args:
        visits: a list of objects with a user_id, job_id and duration value
        num_users: integer, number of users = max user_id
        num_jobs: integer, number of jobs = max job_id
        UserJobs: django or SQLAlechmy model where the similarities are saved
        k: integer,  top k users to use for the prediction
        cut_off: integer, top cut off time in seconds
        log_discrete: boolean, if true converts to log discrete values
        epsilon: zero division shift
    """
    
    tic = datetime.now()
    #we only operate on the user vectors
    #this expects integer ids as users if this isn't the case you might want
    # to have a dict for row & col keys
    M_t = sparse.csr_matrix((num_users, num_jobs), dtype=np.uint8)
    
    #TODO can you vectorize this?
    for visit in visits:
        def calc_time(val):
            if val > 300:
                val = 300
            if log_discrete:
                return int(math.log(val, cut_off) * 255)
            else:
                return int(val / cut_off * 255)
        
        M_t[visit.user_id, visit.job_id] = calc_time(visit.duration)
    logger.debug("M_t took {} ms".format((datetime.now() - tic).microseconds))
        
    tic = datetime.now()
    M_s = cosine_similarity(M_t, M_t, dense_output=False)
    logger.debug("M_s took {} ms".format((datetime.now() - tic).microseconds))
    
    #row by row to save memory
    #if it is guaranteed that there is a userjob per user and job then
    # this can be speed up by inversing it and iterating through the userjob query 
    # --> less SQL querries
    # further you could switch to a batch update with save()
    tic = datetime.now()
    M_k = np.argsort(M_s.toarray(), axis=1)[:-k-1:-1]
    for user_id in range(num_users):
        top_k_users = np.argsort(M_s.getcol(user_id).toarray())[:-k-1:-1].squeeze()
        sim_sum = np.sum(np.abs(M_s[user_id, top_k_users]))
        if sim_sum != 0:
            pred = M_s[user_id, top_k_users].dot(M_t[top_k_users,:]) / sim_sum
        else:
            pred = np.zeros((1,num_jobs))
        for job_id in range(num_jobs):
            userjob = UserJobs.objects.filter(user_id=user_id, job_id=job_id).first()
            if userjob is None:
                UserJobs.create(user_id=user_id, job_id=job_id, similarity_Skill=None, similarity_CF=pred[0, job_id])
            else:
                userjob.similarity_CF = pred[0, job_id]
    
    logger.debug("Prediction took {} ms".format((datetime.now() - tic).microseconds))
