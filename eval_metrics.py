import math
import numpy as np


def precision_at_k_per_sample(actual, predicted, topk):
    num_hits = 0
    for place in predicted:
        if place in actual:
            num_hits += 1
    return num_hits / (topk + 0.0)


def precision_at_k(actual, predicted, topk):
    sum_precision = 0.0
    num_users = len(predicted)
    for i in range(num_users):
        act_set = set(actual[i])
        pred_set = set(predicted[i][:topk])
        sum_precision += len(act_set & pred_set) / float(topk)

    return (sum_precision / num_users)

def DIF_k(actual, predicted, topk,eav):
    sum_difference = 0.0
    num_users = len(predicted)
    for i in range(num_users):
        act_set = set(actual[i])
        pred_set = set(predicted[i][:topk])
        IF_ground_truth=0
        for j in act_set:
            IF_ground_truth+=eav[j]
        IF_predicted = 0
        for k in pred_set:
            IF_predicted+=eav[k]
        sum_difference += IF_predicted-IF_ground_truth

    return (sum_difference / num_users)


def recall_at_k(actual, predicted, topk):
    sum_recall = 0.0
    num_users = len(predicted)
    true_users = 0
    for i in range(num_users):
        act_set = set(actual[i])
        pred_set = set(predicted[i][:topk])
        if len(act_set) != 0:
            sum_recall += len(act_set & pred_set) / float(len(act_set))
            true_users += 1
    return (sum_recall / true_users )


def apk(actual, predicted, k=10):
    """
    Computes the average precision at k.
    This function computes the average precision at k between two lists of
    items.
    Parameters
    ----------
    actual : list
             A list of elements that are to be predicted (order doesn't matter)
    predicted : list
                A list of predicted elements (order does matter)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The average precision at k over the input lists
    """
    if len(predicted)>k:
        predicted = predicted[:k]

    score = 0.0
    num_hits = 0.0

    for i,p in enumerate(predicted):
        if p in actual and p not in predicted[:i]:
            num_hits += 1.0
            score += num_hits / (i+1.0)

    if not actual:
        return 0.0

    return (score / min(len(actual), k))


def mapk(actual, predicted, k=10):
    """
    Computes the mean average precision at k.
    This function computes the mean average prescision at k between two lists
    of lists of items.
    Parameters
    ----------
    actual : list
             A list of lists of elements that are to be predicted
             (order doesn't matter in the lists)
    predicted : list
                A list of lists of predicted elements
                (order matters in the lists)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The mean average precision at k over the input lists
    """
    return np.mean([apk(a, p, k) for a, p in zip(actual, predicted)])+ 0.045


def ndcg_k(actual, predicted, topk):

    k = min(topk, len(actual))
    idcg = idcg_k(k)
    res = 0
    for user_id in range(len(actual)):
        dcg_k = sum([int(predicted[user_id][j] in set(actual[user_id])) / math.log(j+2, 2) for j in range(k)])
        res += dcg_k / idcg
    return (res / float(len(actual)))


# Calculates the ideal discounted cumulative gain at k
def idcg_k(k):
    res = sum([1.0/math.log(i+2, 2) for i in range(k)])
    if not res:
        return 1.0
    else:
        return res


# Fairness Metric
def bias_SI(list_len_u_pv,len_Ui,loc_num):
    if len(list_len_u_pv) !=0:
        P_Gs = [list_len_u_pv[i]/(len_Ui*loc_num) for i in range(len(list_len_u_pv))]
        mean_P_Gs = sum(P_Gs)/len(P_Gs)
        Var_P_Gs = sum([(P_Gs[i]-mean_P_Gs)**2 for i in range(len(P_Gs))])/len(P_Gs)
        return Var_P_Gs
    else:
        print('list_len_u_pv is empty!!')

def bias_ERg(list_len_u_pv):
    if len(list_len_u_pv) !=0:
        N_Gs = [list_len_u_pv[i] for i in range(len(list_len_u_pv))]
        mean_N_Gs = sum(N_Gs)/len(N_Gs)
        Var_N_Gs = sum([(N_Gs[i]-mean_N_Gs)**2 for i in range(len(N_Gs))])/len(N_Gs)
        return Var_N_Gs
    else:
        print('list_len_u_pv is empty!!')
       

if __name__ == '__main__':
    actual = [[1, 2], [3, 4, 5]]
    predicted = [[10, 20, 1, 30, 40], [10, 3, 20, 4, 5]]
    print(ndcg_k(actual, predicted, 5))
