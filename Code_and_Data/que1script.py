#!/usr/bin/env python3

import os
import json
import csv
import pandas
import numpy
from mapping import correct_dist_map

# file name which stored district and their adjacent district
# neighbor-districts-temp.json is generated by helper_for_mapping

neighbor_file = "neighbor-districts-temp.json"
in_file = open(neighbor_file)
neighbor_json = json.load(in_file)

# list of all district in above data
origdist_sorted_list = sorted(neighbor_json.keys())
# print(origdist_sorted_list)

origdist_name_list = []
for dist in origdist_sorted_list:
    temp = dist.split('/')
    origdist_name_list.append(temp[0])

keeporigdist_obsdist_map = {}
# consist of dist which are either directly present in obs dist list
# or mapped to one of obs_dist list
# name of this state must be of smaller case only upto this state
for dist in correct_dist_map.keys():
    if correct_dist_map[dist] != "*":
        keeporigdist_obsdist_map[correct_dist_map[dist]] = dist     # dist here represent observed dist, so value is observed one

file_name = "helper-data/obsdist-stateID/obsdist-stateID.csv"
obsdist_stateID_df = pandas.read_csv(file_name)
# print(obsdist_stateID_df)

obs_dist_name_list = list(obsdist_stateID_df["dist_transformed_name"])
for dist in obs_dist_name_list:
    if dist in origdist_name_list:
        keeporigdist_obsdist_map[dist] = dist

# print(keeporigdist_obsdist_map)
# print("temp_dist_to_keep_list", len(keeporigdist_obsdist_map))

orig_dist_to_keep_list = keeporigdist_obsdist_map.keys()

new_old_name_dict = {}
for dist in keeporigdist_obsdist_map.keys():
    new_name = keeporigdist_obsdist_map[dist] # new_name is obs_dist which is mapped with orig_dist
    for idx in obsdist_stateID_df.index:    # observed data frame
        if obsdist_stateID_df.loc[idx, "dist_transformed_name"] == new_name:
            name_observed = obsdist_stateID_df.loc[idx, "dist_name_at_portal"]
            new_old_name_dict[dist] = name_observed
            break
# print(new_old_name_dict)


neighbor_districts_modified = {}
for dist in neighbor_json.keys():
    # print(dist)
    temp = dist.split('/')  #split to separate name with Q id, temp[0] is name
    if temp[0] in orig_dist_to_keep_list:

        temp_adj_dist_list = [] # this list will keep all adjacent dist direct neighbor and 
        # and if some neighbor is about to delete then neighbor of that neighbor

        set_size = 0    # help to keep status whether at each iteration whether adj dist is being added or not
        # otherwise we can quit as, we are sure that we have added all neighbor including nighbor of about to delete neighnor
        temp_adj_dist_set = set()

        adj_dist_list = neighbor_json[dist]
        for dist1 in adj_dist_list:
            temp_adj_dist_set.add(dist1)
            
        while len(temp_adj_dist_set) != set_size:
            set_size = len(temp_adj_dist_set)   # to keep record of whether new element added to set or not
            temp_set = set()
            # iterate through each neighbor and add adj dist of neighbor which we are going to delete
            # from final neighbor list
            for dist2 in temp_adj_dist_set: #iterating in set
                temp2 = dist2.split('/')    # separate name from Q id of orig dist

                # we are not going to add neighbor of district which is already going to be there in final neighbor list
                if temp2[0] in orig_dist_to_keep_list:  
                    continue
                else:
                    # but add neighbor of all  those district which are going to be deleted from final neighbor list
                    temp_list_adj = neighbor_json[dist2]
                    for dist3 in temp_list_adj:
                        # temp3 = dist3.split('/')
                        # if temp3[0] in orig_dist_to_keep_list:
                        temp_set.add(dist3) # set will automatically remove repetition
            for set_elem in temp_set:
                temp_adj_dist_set.add(set_elem)
        for dist4 in temp_adj_dist_set:
            # print(adj_dist)
            temp4 = dist4.split('/')
            if temp4[0] in orig_dist_to_keep_list:
                old_name4 = new_old_name_dict[temp4[0]]
                old_name4 = old_name4 + "/" + temp4[1]
                temp_adj_dist_list.append(old_name4)
        old_name5 = new_old_name_dict[temp[0]]
        old_name5 = old_name5 + "/" + temp[1]
        # remove self loop as a district should not be district of itself
        if old_name5 in temp_adj_dist_list:
            temp_adj_dist_list.remove(old_name5)
        neighbor_districts_modified[old_name5] = temp_adj_dist_list


# assigning id's to neighbor-district-modified
dist_id_dict = {}
dist_list = sorted(neighbor_districts_modified.keys())
# print(dist_list)
id = 101
for dist in dist_list:
    dist_id_dict[dist] = id
    id += 1

# print(dist_id_dict)

dist_id_path = "origdist-id/"
if not os.path.exists(dist_id_path):
    os.mkdir(dist_id_path)
distid = os.path.join(dist_id_path, "origdist-id.json")
with open(distid, 'w') as fp_w :
    json.dump(dist_id_dict, fp_w, indent=4)
# print("saving district-id jason -> origdist-id/origdist-id.json")


file_name = "neighbor-districts-modified.json"
with open(file_name, 'w') as fp_w:
    json.dump(neighbor_districts_modified, fp_w, indent=4)
# print("saving neighbor-districts-modified.json ...")

folder_name = "helper-data/new-old-dist-name"
if not os.path.exists(folder_name):
    os.mkdir(folder_name)
file_name = "helper-data/new-old-dist-name/new-old-dist-name.json"
with open(file_name, 'w') as fp_w:
    json.dump(new_old_name_dict, fp_w, indent=4)
# print("A json to change original district name based on portal district name is saved -> helper-data/new-old-dist-name/new-old-dist-name.json")