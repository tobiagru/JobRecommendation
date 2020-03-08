from scipy import sparse
import numpy as np
import math
import implicit
import logging
logger = logging.getLogger(__name__)


def predict_most_similar(visits, num_users, num_jobs, UserJobs, factors=50, cut_off=300, log_discrete=True):
    """
    Matrix Factorization based
    
    Still Collaborative filtering but this time based on alternating
    least squares with an efficient implementation from implicit.
    
    Still not very fast as some of the list to matrix stuff still applies.
    But it should scale better. Maybe it is worth storing this in memory
    and requesting values when a user needs some
    
    args:
        visits: a list of objects with a user_id, job_id and duration value
        num_users: integer, number of users = max user_id
        num_jobs: integer, number of jobs = max job_id
        UserJobs: django or SQLAlechmy model where the similarities are saved
        cut_off: integer, top cut off time in seconds
        log_discrete: boolean, if true converts to log discrete values
    """
    
    tic = datetime.now()
    #we only operate on the user vectors
    #this expects integer ids as users if this isn't the case you might want
    # to have a dict for row & col keys
    M_t = sparse.csr_matrix((num_jobs, num_users), dtype=np.uint8)
    
    #TODO can you vectorize this?
    for visit in visits:
        def calc_time(val):
            if val > 300:
                val = 300
            if log_discrete:
                return int(math.log(val, cut_off) * 255)
            else:
                return int(val / cut_off * 255)
        
        M_t[visit.job_id, visit.user_id] = calc_time(visit.duration)
    logger.debug("M_t took {} ms".format((datetime.now() - tic).microseconds))
    
    tic = datetime.now()
    # initialize a model
    model = implicit.als.AlternatingLeastSquares(factors=factors)
    logger.debug("Loading model took {} ms".format((datetime.now() - tic).microseconds))
    
    tic = datetime.now()
    # train the model on a sparse matrix of item/user/confidence weights
    model.fit(M_t)
    logger.debug("Fitting model took {} ms".format((datetime.now() - tic).microseconds))
    
    tic = datetime.now()
    # recommend items for a user
    for user_id in range(num_users):
        preds = model.recommend(user_id, M_t.T)
        only saves the non-zero ones
        for pred in preds:
            userjob = UserJobs.objects.filter(user_id=user_id, job_id=pred[0]).first()
            if userjob is None:
                UserJobs.create(user_id=user_id, job_id=pred[0], similarity_Skill=None, similarity_CF=pred[1])
            else:
                userjob.similarity_CF = pred[1]
    logger.debug("Predicting took {} ms".format((datetime.now() - tic).microseconds))
