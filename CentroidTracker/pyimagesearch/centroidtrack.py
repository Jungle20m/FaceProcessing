from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


def get_rows_cols(D):
    check = False

    rows = D.min(axis=1).argsort()
    cols = D.argmin(axis=1)[rows]

    # prev_step and current_step are dictionary
    # to save rows and cols with key = row, value = col
    prev_step = {}
    current_step = {}

    # init prev_step
    for (row, col) in zip(rows, cols):
        prev_step.update({row: col})

    while not check:
        # print(D)
        # rows = D.min(axis=1).argsort()
        # cols = D.argmin(axis=1)[rows]

        # seen dictionary to know duplicate indicate in cols
        seen = {}

        # head to tail set value to MAX at duplicate indicate
        check_step = True
        for i in range(len(cols)):
            if cols[i] in seen:
                # MAX = 100
                D[rows[i]][cols[i]] = 10000
                check_step = False
                break
            else:
                seen.update({cols[i]: 0})

        if check_step:
            break

        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]

        # init current_step
        current_step.clear()
        for (row, col) in zip(rows, cols):
            current_step.update({row: col})

        # if step un_change, we return
        if prev_step == current_step:
            break
        else:
            prev_step.clear()
            prev_step = current_step.copy()
    return rows, cols


class CentroidTrack(object):
    def __init__(self, max_disappear):
        # nhung cai cu
        self.next_checked_object_id = 0
        self.checked_objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_dissapear = max_disappear

        # PHAN DUOC THEM ------------------------------------
        # checkObjects : chua tat ca cac doi tuong duoc bound
        # khong phan biet do co phai mat nguoi hay khong
        # check_appeared : dem so lan xuat hien cua cac object
        # nhan duoc o ben tren
        self.checking_objects = OrderedDict()
        self.appeared = OrderedDict()
        self.next_checking_object_id = -1
        self.min_appear = -10
        self.max_appear = 10
        # ----------------------------------------------------

    def register(self, centroid):
        self.checked_objects[self.next_checked_object_id] = centroid
        self.disappeared[self.next_checked_object_id] = 0
        self.next_checked_object_id += 1

    def deregister(self, object_id):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.checked_objects[object_id]
        del self.disappeared[object_id]

    # PHAN DUOC THEM -----------------------------------------
    def register_checking_object(self, centroid):
        self.checking_objects[self.next_checking_object_id] = centroid
        self.appeared[self.next_checking_object_id] = 0
        self.next_checking_object_id -= 1

    def deregister_checking_object(self, object_id):
        del self.checking_objects[object_id]
        del self.appeared[object_id]
    # ---------------------------------------------------------

    def update(self, rects):
        # print('checked object: ', len(self.checked_objects))
        # print('checked object next id: ', self.next_checked_object_id)
        # print('checking object: ', len(self.checking_objects))
        # print('checking object next id: ', self.next_checking_object_id)
        # print('-----------------------------')



        if len(rects) == 0:
            for object_id in self.disappeared.keys():
                self.disappeared[object_id] += 1

                # if self.disappeared[object_id] > self.max_dissapear:
                #     self.deregister(object_id)

            # PHAN DUOC THEM ------------------------------------
            for appeared_object_id in self.appeared.keys():
                self.appeared[appeared_object_id] -= 1

                # if self.appeared[appeared_object_id] < self.min_appear:
                #     self.deregister_checking_object(appeared_object_id)
            # ---------------------------------------------------
            # return self.checked_objects
        else:
            input_centroids = np.zeros((len(rects), 2), dtype='int')

            for (i, (x_strart, y_start, x_end, y_end)) in enumerate(rects):
                x_centroid = int((x_strart + x_end) / 2.0)
                y_centroid = int((y_start + y_end) / 2.0)
                input_centroids[i] = (x_centroid, y_centroid)
            # PHAN DUOC SUA ------------------------------------------
            if len(self.checking_objects) == 0 and len(self.checked_objects) == 0:
                for i in range(0, len(input_centroids)):
                    self.register_checking_object(input_centroids[i])
            # --------------------------------------------------------
            else:
                object_ids = list(self.checked_objects.keys()) + list(self.checking_objects.keys())
                object_centroids = list(self.checked_objects.values()) + list(self.checking_objects.values())

                distance_matix = dist.cdist(np.array(object_centroids), input_centroids)

                rows, cols = get_rows_cols(distance_matix)

                used_rows = set()
                used_cols = set()

                for (row, col) in zip(rows, cols):
                    if row in used_rows or col in used_cols:
                        continue

                    object_id = object_ids[row]
                    if object_id >= 0:
                        self.checked_objects[object_id] = input_centroids[col]
                        self.disappeared[object_id] = 0
                    else:
                        self.checking_objects[object_id] = input_centroids[col]
                        self.appeared[object_id] += 1

                    used_rows.add(row)
                    used_cols.add(col)

                unused_rows = set(range(0, distance_matix.shape[0])).difference(used_rows)
                unused_cols = set(range(0, distance_matix.shape[1])).difference(used_cols)
                if distance_matix.shape[0] >= distance_matix.shape[1]:
                    for r in unused_rows:
                        object_id = object_ids[r]
                        if object_id >= 0:
                            self.disappeared[object_id] += 1
                            # if self.disappeared[object_id] > self.max_dissapear:
                            #     self.deregister(object_id)
                        else:
                            self.appeared[object_id] -= 1
                            # if self.appeared[object_id] < self.min_appear:
                            #     self.deregister_checking_object(object_id)
                else:
                    for c in unused_cols:
                        self.register_checking_object(input_centroids[c])

        # checking_object_ids = list(self.checking_objects.keys())
        # checking_object_centroids = list(self.checking_objects.values())
        #
        # checked_object_ids = list(self.checked_objects.keys())
        # checked_object_centroids = list(self.checked_objects.values())

        for id in self.checked_objects:
            print('ID %s disappeared: %s' % (id, self.disappeared[id]))
        print('----------------------------------')

        for checking_id in self.checking_objects.copy():
            if self.appeared[checking_id] > self.max_appear:
                self.register(self.checking_objects[checking_id])
                self.deregister_checking_object(checking_id)
            elif self.appeared[checking_id] < self.min_appear:
                self.deregister_checking_object(checking_id)
            else:
                continue

        for checked_id in self.checked_objects.copy():
            if self.disappeared[checked_id] > self.max_dissapear:
                self.deregister(checked_id)

        # return the set of trackable objects
        return self.checked_objects







