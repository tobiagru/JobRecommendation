# Job Recommendr System
A system that recommends Jobs for Users. Implementation based on ideas that we developed at cofoundme (www.cofoundme.org). The goal was to recommend the most relevant jobs for users. The implementation is as such that it should work with Django Models or SQlAlchemy Models.

## Architecture
The system consists of three levels to recommend optimal jobs to users. The three approaches would be weighted or ensembled.  

1.) Level: was already in place and computed a hotness score for a job. The more traffic a job recieved or the more often it or its respective company was updated the hotter the job.  

2.) Level: recommend a job based on relevance of the job according to the skills. The better the fit of a job on skill level the higher the relevance. Fit is measured by calculating the similarity based on the word embedding of the skills (using Gensim  https://radimrehurek.com/gensim/). Where the total similarity score is the ordered sum of the best pairs with a penalty for a mismatch in number of skills. (Due to the fact that we noticed that business people tend to choose a lot of skills even if they know those merely, while software developers would choose less skills but only those they truly know.)  

3.) Level: Collaborative filtering based on what other users were previously looking at. There are two implementations a memory-based and a model based. The memory based uses top-k users and cosine distance between user-job vectors to predict similar jobs interesting to the user (https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html). The model based uses matrix factorization from the implicit library, with the alternating least squares implementation to predict relevant jobs (https://implicit.readthedocs.io/en/latest/als.html).

## Running the system
You can either implement the functions into your system or just run the respective tests to see how they perform. Tests are randomized thus might not make any sense.

### Running Tests
``python test_<type of test>.py`` should print relevant results.  
