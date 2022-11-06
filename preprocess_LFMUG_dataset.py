import random
import numpy as np
from interactions import Interactions
import os
import math


class Data_process:
    def __init__(self, args):
        data_path = os.getcwd() + '/dataset-LFM/'

        Events_path = data_path + 'eventsModified.txt'
        Users_path = data_path + 'usersModified.txt'
        tracks_path = data_path + 'tracksModified.txt'

        self.tracks = open(tracks_path, 'r').readlines()
        self.Events = open(Events_path, 'r').readlines()
        self.Users = open(Users_path, 'r').readlines()

        self.dict_restrict = {
            'year': [2012, 2013, 2014],
            'num_checkin': 10,
            'test_X_num': args.L_hgn,
            'test_Y_num': 10,
        }
        self.L_hgn, self.T_hgn = args.L_hgn, args.T_hgn
        self.args = args

    def run(self):
        print('/1')
        index, r_index = 0, 0
        dict_trackid_catid, dict_catid_to_index, dict_r_catid_to_index = {}, {}, {}
        for ny_vcat_i in self.tracks[1:]:
            ny_vcat_i = ny_vcat_i.split(';')
            trackid_ = ny_vcat_i[0]
            catid_ = ny_vcat_i[2]
            if trackid_ not in dict_trackid_catid:
                dict_trackid_catid[trackid_] = (catid_, int(catid_))
                if catid_ not in dict_catid_to_index:
                    dict_catid_to_index[catid_] = index
                    index += 1
                if int(catid_) not in dict_r_catid_to_index:
                    dict_r_catid_to_index[int(catid_)] = r_index
                    r_index += 1
        set_trackid_name = set(dict_trackid_catid.keys())
        trackid_name = list(set(dict_trackid_catid.keys()))
        catid_set = list(set(dict_catid_to_index.values()))
        relation_catid_set = list(set(dict_r_catid_to_index.values()))
        # print(set_trackid_name)
        # print(trackid_name)
        # print(catid_set)
        # print(relation_catid_set)
        print('/2')
        for i in range(len(trackid_name)):
            trackid_catid_ = dict_trackid_catid[trackid_name[i]]
            index_ = dict_catid_to_index[trackid_catid_[0]]
            r_index_ = dict_r_catid_to_index[trackid_catid_[1]]
            dict_trackid_catid[trackid_name[i]] = (index_, r_index_)
        # print(trackid_catid_)
        # print(index_)
        # print(r_index_)
        # print(dict_trackid_catid)
        print('/3')
        dict_uid_category, uid_category_set, gender_set, MS_set = {}, [], [], []
        for ny_demo_i in self.Users[1:]:
            ny_demo_i = ny_demo_i.split(';')
            uid_ = ny_demo_i[0]
            gender_ = int(ny_demo_i[3])
            MS_ = int(ny_demo_i[4].strip('\n'))
            category_ = int(ny_demo_i[1])
            dict_uid_category[uid_] = (category_, (gender_, MS_))
            uid_category_set.append(category_)
            gender_set.append(gender_)
            MS_set.append(MS_)
        uid_category_set = list(set(uid_category_set))
        uid_name = set(dict_uid_category.keys())
        self.gender_set = list(set(gender_set))
        self.MS_set = list(set(MS_set))
        print('/4')
        dict_uid_time_trackid = {}
        for i in range(len(self.Events) - 1):
            ny_checkin_i = self.Events[i + 1].split(';')
            uid_, time_, trackid_ = ny_checkin_i[0], ny_checkin_i[4].strip('\n'), ny_checkin_i[3]
            time_day, time_hms = time_.split()[0], time_.split()[1]
            if uid_ in uid_name and trackid_ in set_trackid_name:
                year_ = int(time_day.split('-')[0])
                if year_ in self.dict_restrict['year']:
                    if uid_ not in dict_uid_time_trackid:
                        dict_uid_time_trackid[uid_] = [(time_day, time_hms, trackid_)]
                    else:
                        dict_uid_time_trackid[uid_].append((time_day, time_hms, trackid_))
        print(dict_uid_time_trackid)
        print('/5')
        uid_name = list(set(dict_uid_time_trackid.keys()))
        dict_uid_trackid_relation, dict_trackid_to_entity, index = {}, {}, 0
        for u_i in range(len(uid_name)):
            uid_time_trackid_ = dict_uid_time_trackid[uid_name[u_i]]
            if len(uid_time_trackid_) >= self.dict_restrict['num_checkin']:
                sorted_uid_time_trackid_ = sorted(uid_time_trackid_)
                for i in range(len(sorted_uid_time_trackid_)):
                    time_day_, time_hms_, trackid_ = sorted_uid_time_trackid_[i][0], sorted_uid_time_trackid_[i][1], \
                                                     sorted_uid_time_trackid_[i][2]
                    daynum_time_day_ = int(time_day_.split('-')[1]) - 1
                    time_h = int(time_hms_.split('-')[0].split(':')[0])
                    if time_h > 11:
                        time_h = 1
                    else:
                        time_h = 0
                    relation_time = time_h * daynum_time_day_ + daynum_time_day_
                    sorted_uid_time_trackid_[i] = (trackid_, 0)
                    if trackid_ not in dict_trackid_to_entity:
                        dict_trackid_to_entity[trackid_] = index
                        index += 1
                dict_uid_trackid_relation[uid_name[u_i]] = sorted_uid_time_trackid_
        uid_name = list(set(dict_uid_trackid_relation.keys()))
        trackid_name = list(set(dict_trackid_to_entity.keys()))
        print('/6')
        test_X_num = self.dict_restrict['test_X_num']
        test_Y_num = self.dict_restrict['test_Y_num']
        train_set, test_set, test_X_set, test_Y_set, relation_time_set, data_set = [], [], [], [], [], []
        for i in range(len(uid_name)):
            uid_trackid_relation_ = dict_uid_trackid_relation[uid_name[i]]
            print("uid_trackid_relation_: ",uid_trackid_relation_)
            data_set_, catid_set_ = [], []
            for j in range(len(uid_trackid_relation_)):
                trackid_ = uid_trackid_relation_[j][0]
                catid_ = dict_trackid_catid[trackid_][0]
                entity_trackid_ = dict_trackid_to_entity[trackid_]
                relation_time_ = uid_trackid_relation_[j][1]
                data_set_.append(entity_trackid_)
                relation_time_set.append(relation_time_)
                catid_set_.append(catid_)
            data_set.append(data_set_)
            train_set_ = data_set_[:len(data_set_) - test_X_num - test_Y_num]
            test_X_set_ = data_set_[len(data_set_) - test_X_num - test_Y_num:len(data_set_) - test_Y_num]
            test_Y_set_ = data_set_[len(data_set_) - test_Y_num:]
            test_set_ = data_set_[len(data_set_) - test_X_num - test_Y_num:]
            train_set.append(train_set_)
            test_set.append(test_set_)
            test_X_set.append(test_X_set_)
            test_Y_set.append(test_Y_set_)
        self.test_X_set = np.array(test_X_set)
        relation_time_set = list(set(relation_time_set))
        entity_set = list(set(dict_trackid_to_entity.values()))
        print('/7')
        dict_uid_category_to_entity = {}
        for i in range(len(uid_category_set)):
            dict_uid_category_to_entity[uid_category_set[i]] = uid_category_set[i] + len(entity_set)
        dict_catid_to_entity = {}
        for i in range(len(catid_set)):
            dict_catid_to_entity[catid_set[i]] = len(entity_set) + len(uid_category_set) + catid_set[i]
        dict_relation_catid_to_r = {}
        for i in range(len(relation_catid_set)):
            dict_relation_catid_to_r[relation_catid_set[i]] = len(relation_time_set) + relation_catid_set[i]
        print('/8')
        self.dict_KG, self.uid_attribute_category = {}, []
        for i in range(len(uid_name)):
            uid_category_, uid_category_detail_ = dict_uid_category[uid_name[i]]
            entity_uid_category_ = dict_uid_category_to_entity[uid_category_]
            uid_trackid_relation_ = dict_uid_trackid_relation[uid_name[i]]
            gender_, MS_ = uid_category_detail_[0], uid_category_detail_[1]
            self.uid_attribute_category.append((gender_, MS_))
            for j in range(len(uid_trackid_relation_)):
                trackid_ = uid_trackid_relation_[j][0]
                relation_time_ = uid_trackid_relation_[j][1]
                entity_trackid_ = dict_trackid_to_entity[trackid_]
                catid_, relation_catid_ = dict_trackid_catid[trackid_][0], dict_trackid_catid[trackid_][1]
                entity_catid_ = dict_catid_to_entity[catid_]
                relation_catid_ = dict_relation_catid_to_r[relation_catid_]
                if entity_trackid_ not in self.dict_KG:
                    self.dict_KG[entity_trackid_] = {}
                    for k in range(len(self.gender_set)):
                        self.dict_KG[entity_trackid_]['gender' + '-' + str(self.gender_set[k])] = []
                        if self.gender_set[k] == gender_:
                            self.dict_KG[entity_trackid_]['gender' + '-' + str(self.gender_set[k])].append(
                                [entity_trackid_, relation_time_, entity_uid_category_])
                            self.dict_KG[entity_trackid_]['gender' + '-' + str(self.gender_set[k])].append(
                                [entity_trackid_, relation_catid_, entity_catid_])
                    for k in range(len(self.MS_set)):
                        self.dict_KG[entity_trackid_]['MS' + '-' + str(self.MS_set[k])] = []
                        if self.MS_set[k] == MS_:
                            self.dict_KG[entity_trackid_]['MS' + '-' + str(self.MS_set[k])].append(
                                [entity_trackid_, relation_time_, entity_uid_category_])
                            self.dict_KG[entity_trackid_]['MS' + '-' + str(self.MS_set[k])].append(
                                [entity_trackid_, relation_catid_, entity_catid_])
                else:
                    for k in range(len(self.gender_set)):
                        if self.gender_set[k] == gender_:
                            self.dict_KG[entity_trackid_]['gender' + '-' + str(self.gender_set[k])].append(
                                [entity_trackid_, relation_time_, entity_uid_category_])
                            self.dict_KG[entity_trackid_]['gender' + '-' + str(self.gender_set[k])].append(
                                [entity_trackid_, relation_catid_, entity_catid_])
                    for k in range(len(self.MS_set)):
                        if self.MS_set[k] == MS_:
                            self.dict_KG[entity_trackid_]['MS' + '-' + str(self.MS_set[k])].append(
                                [entity_trackid_, relation_time_, entity_uid_category_])
                            self.dict_KG[entity_trackid_]['MS' + '-' + str(self.MS_set[k])].append(
                                [entity_trackid_, relation_catid_, entity_catid_])

        self.dict_itemid_upfdf = dict()
        self.dict_itemid_eav = dict()
        for i in range(len(uid_name)):
            uid_upf_ = self.uid_attribute_category[i]
            uid_data_set_ = data_set[i]
            for j in range(len(uid_data_set_)):
                if uid_data_set_[j] not in self.dict_itemid_upfdf:
                    self.dict_itemid_upfdf[uid_data_set_[j]] = list()
                self.dict_itemid_upfdf[uid_data_set_[j]].append(uid_upf_)
        itemid_name = list(set(self.dict_itemid_upfdf.keys()))
        for i in range(len(itemid_name)):
            itemid_upfdf_ = self.dict_itemid_upfdf[itemid_name[i]]
            # print(itemid_upfdf_)
            b_0, b_1, b_2,b_3, b_4, b_5,b_6, b_7, b_8,b_9= 0, 0, 0, 0, 0, 0,0, 0, 0, 0
            g_0, g_1, g_2,g_3, g_4, g_5,g_6, g_7, g_8,g_9= 0, 0, 0, 0, 0, 0,0, 0, 0, 0
            for j in range(len(itemid_upfdf_)):
                if itemid_upfdf_[j] == (0, 0):
                    b_0 += 1
                elif itemid_upfdf_[j] == (0, 10):
                    b_1 += 1
                elif itemid_upfdf_[j] == (0, 20):
                    b_2 += 1
                elif itemid_upfdf_[j] == (0, 30):
                    b_3 += 1
                elif itemid_upfdf_[j] == (0, 40):
                    b_4 += 1
                elif itemid_upfdf_[j] == (0, 50):
                    b_5 += 1
                elif itemid_upfdf_[j] == (0, 60):
                    b_6 += 1
                elif itemid_upfdf_[j] == (0, 70):
                    b_7 += 1
                elif itemid_upfdf_[j] == (0, 80):
                    b_8 += 1
                elif itemid_upfdf_[j] == (0, 90):
                    b_9 += 1
                elif itemid_upfdf_[j] == (1, 0):
                    g_0 += 1
                elif itemid_upfdf_[j] == (1, 10):
                    g_1 += 1
                elif itemid_upfdf_[j] == (1, 20):
                    g_2 += 1
                elif itemid_upfdf_[j] == (1, 30):
                    g_3 += 1
                elif itemid_upfdf_[j] == (1, 40):
                    g_4 += 1
                elif itemid_upfdf_[j] == (1, 50):
                    g_5 += 1
                elif itemid_upfdf_[j] == (1, 60):
                    g_6 += 1
                elif itemid_upfdf_[j] == (1, 70):
                    g_7 += 1
                elif itemid_upfdf_[j] == (1, 80):
                    g_8 += 1
                elif itemid_upfdf_[j] == (1, 90):
                    g_9 += 1
                else:
                    print('Error!!')
            b_0_p, b_1_p, b_2_p,b_3_p, b_4_p, b_5_p,b_6_p, b_7_p, b_8_p,b_9_p = b_0 / len(itemid_upfdf_), b_1 / len(itemid_upfdf_), b_2 / len(itemid_upfdf_),b_3 / len(itemid_upfdf_), b_4 / len(itemid_upfdf_), b_5 / len(itemid_upfdf_),b_6 / len(itemid_upfdf_), b_7 / len(itemid_upfdf_), b_8 / len(itemid_upfdf_),b_9 / len(itemid_upfdf_)
            g_0_p, g_1_p, g_2_p,g_3_p, g_4_p, g_5_p,g_6_p, g_7_p, g_8_p,g_9_p = g_0 / len(itemid_upfdf_), g_1 / len(itemid_upfdf_), g_2 / len(itemid_upfdf_),g_3 / len(itemid_upfdf_), g_4 / len(itemid_upfdf_), g_5 / len(itemid_upfdf_),g_6 / len(itemid_upfdf_), g_7 / len(itemid_upfdf_), g_8 / len(itemid_upfdf_),g_9 / len(itemid_upfdf_)
            self.dict_itemid_upfdf[itemid_name[i]] = [b_0_p, b_1_p, b_2_p,b_3_p, b_4_p, b_5_p,b_6_p, b_7_p, b_8_p,b_9_p,g_0_p, g_1_p, g_2_p,g_3_p, g_4_p, g_5_p,g_6_p, g_7_p, g_8_p,g_9_p]
            self.dict_itemid_eav[itemid_name[i]] = 0
            for pv in self.dict_itemid_upfdf[itemid_name[i]]:
                # print(pv)
                if pv != 0:
                    self.dict_itemid_eav[itemid_name[i]] += pv * math.log(pv, 10)
            self.dict_itemid_eav[itemid_name[i]] = abs(-1 * self.dict_itemid_eav[itemid_name[i]])
        # print("dict item pv: ", self.dict_itemid_upfdf)
        # print("dict item eav: ", self.dict_itemid_eav)
        num_user = len(uid_name)
        num_item = len(entity_set)
        n_entities = len(entity_set) + len(uid_category_set) + len(catid_set)
        n_relation = len(relation_time_set) + len(relation_catid_set)

        train = Interactions(train_set, num_user, num_item)
        train.to_sequence(self.L_hgn, self.T_hgn)

        sequences_np = train.sequences.sequences
        targets_np = train.sequences.targets
        users_np = train.sequences.user_ids
        train_matrix = train.tocsr()

        param_ = [self.args, num_user, num_item, n_entities, n_relation]
        data_ = [users_np, sequences_np, targets_np, train_matrix]
        test_ = [train, self.test_X_set, test_Y_set, self.uid_attribute_category]

        train_data, test_data = list(), list()
        entity_set = set(entity_set)
        for i in range(len(train_set)):
            uid_ = i
            neg_entity_set_ = list(entity_set - set(train_set[i]))
            neg_train_set_ = random.sample(neg_entity_set_, len(train_set[i]))
            for j in range(len(train_set[i])):
                train_data.append([uid_, train_set[i][j], 1])
                train_data.append([uid_, neg_train_set_[j], 0])
        for i in range(len(test_set)):
            uid_ = i
            neg_entity_set_ = list(entity_set - set(test_set[i]))
            neg_test_set_ = random.sample(neg_entity_set_, len(test_set[i]))
            for j in range(len(test_set[i])):
                test_data.append([uid_, test_set[i][j], 1])
                test_data.append([uid_, neg_test_set_[j], 0])
        train_data = np.array(train_data)
        # print("train_data: ",train_data)

        eval_data = train_data
        test_data = np.array(test_data)
        # print("test_data: ", test_data)
        # print("sequences_np: ", sequences_np)
        user_history_dict = dict()
        for i in range(len(data_set)):
            uid_ = i
            user_history_dict[uid_] = data_set[i]

        pickle_data = {
            'train_data': train_data,
            'eval_data': eval_data,
            'test_data': test_data,
            'n_entity': n_entities,
            'n_relation': n_relation,
            'kg_np': self.KG_random_generator(),
            'user_history_dict': user_history_dict,
        }
        eav = self.dict_itemid_eav
        return param_, data_, test_,eav

    def KG_random_generator_(self):
        dict_KG = self.dict_KG
        list_entity = list(set(dict_KG.keys()))
        KG = []
        for i in range(len(list_entity)):
            attribute_category = list(dict_KG[list_entity[i]].keys())
            for j in range(len(attribute_category)):
                KG_ = dict_KG[list_entity[i]][attribute_category[j]]
                KG += KG_
        KG = np.array(KG)
        return KG

    def KG_random_generator(self):
        dict_KG = self.dict_KG
        list_entity = list(set(dict_KG.keys()))
        KG = dict()
        for i in range(len(list_entity)):
            if list_entity[i] not in KG:
                KG[list_entity[i]] = list()
            attribute_category = list(dict_KG[list_entity[i]].keys())
            key = True
            while key:
                random_attribute_category = random.choice(attribute_category)
                KG_ = dict_KG[list_entity[i]][random_attribute_category]
                if len(KG_) != 0:
                    for j in range(len(KG_)):
                        KG[list_entity[i]].append(KG_[j])
                    key = False
            KG[list_entity[i]] = np.array(KG[list_entity[i]])
        return KG


















