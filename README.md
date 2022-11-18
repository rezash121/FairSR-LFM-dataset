# FairSR -- Fairness-aware Sequential Recommendationthrough Multi-task Learning with Preference GraphEmbeddings
we train and evaluate FairSR model on LFM User group dataset.
FairSR [paper](https://arxiv.org/pdf/2205.00313.pdf)
LFM User group [dataset](https://zenodo.org/record/3475975#.Y3fmMctBxBZ)

Usages
------
Train and evaluate the model
    python mainLFM.py 

The results will show the performance of FairSR by ranking metric Precision@k, NDCG@k, Recall@k and DIF@k.
