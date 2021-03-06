import os
import sys
import cv2
import numpy as np
import math
from pprint import pprint
import DB_Transactions as db
import User_Interface as uml



#  Settings
angleFix = 100
contoursLength = 40
startRange = 10
endRange = 10
dataStoreLength = 60
directory = "/Users/administrator/PyCharmProjects/HandDetection/"


dataStore = []
beginCount = 1
beginRecord = False
flip_camera_horizontally = True
cap = cv2.VideoCapture(0)



#   Functions Utilities
def _function_data_normalize(data):
    data = np.reshape(data, 8)

    min = np.amin(data)
    max = np.amax(data)
    mean = (min + max) / 2

    for i in range(len(data)):
        data[i] = (data[i] - mean) / mean

    return data



def _averaging_data_store(dataStore):
    dataAverageArray = []

    for j in range(4):
        bMean = 0
        cMean = 0

        for i in range(len(dataStore)):
            bMean += dataStore[i][j][0]
            cMean += dataStore[i][j][1]

        bMean = bMean/len(dataStore)
        cMean = cMean/len(dataStore)

        dataAverageArray.append([bMean, cMean])

    return dataAverageArray



def _get_height_ratio(array):
    tempArray = []

    for i in range(len(array)):
        tempArray.append(array[i][0])
        tempArray.append(array[i][1])

    ratioMatrix = []
    for i in range((len(tempArray) - 1)):
        for j in range((len(tempArray) - i) - 1):
            ratioMatrix.append(tempArray[i] / tempArray[((j + i) + 1)])

    return ratioMatrix




''' Some UML Executions '''
if uml._delete_current_user == True:
    query = "SELECT `id` FROM `persons` WHERE `name` LIKE '%s' AND  `surname` LIKE '%s'" % (uml._user_name, uml._surname)
    id = db.data_fetch(query)

    if not id:
        uml.tm.showinfo("Attenzione!", "User named %s, %s, %s" % (uml._user_name, uml._surname, "does not exist"))
    else:
        id = id[0][0]
        query_1 = "DELETE FROM `persons` WHERE `id` = %s " % id
        query_2 = "DELETE FROM `users_Ratio` WHERE `user_id` = '%s' " % id
        db.data_query(query_1)
        db.data_query(query_2)

    uml.tm.showinfo("Information", "User named %s, %s was removed" % (uml._user_name, uml._surname))
    os.execv(sys.executable, ['python'] + sys.argv)

elif uml._clear_database == True:
    db.data_query("DELETE FROM `persons` ")
    db.data_query("DELETE FROM `users_Ratio` ")

    uml.tm.showinfo("Information", "Database was cleared!")
    os.execv(sys.executable, ['python'] + sys.argv)




'''  Start Process   '''

while (cap.isOpened()):

    ret, img = cap.read()
    #img = cv2.flip(img, flip_camera_horizontally)

    cv2.rectangle(img, (500, 400), (0, 0), (0, 255, 0), 0)
    crop_img = img[5:395, 5:495]
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)
    _, thresh1 = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    #cv2.imshow('Thresholded', thresh1)

    (version, _, _) = cv2.__version__.split('.')

    if version is '3':
        image, contours, hierarchy = cv2.findContours(thresh1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    elif version is '2':
        contours, hierarchy = cv2.findContours(thresh1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    cnt = max(contours, key=lambda x: cv2.contourArea(x))

    # x, y, w, h = cv2.boundingRect(cnt)
    # cv2.rectangle(crop_img, (x, y), (x + w, y + h), (0, 0, 255), 0)
    hull = cv2.convexHull(cnt)
    drawing = np.zeros(crop_img.shape, np.uint8)
    cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 0)
    hull = cv2.convexHull(cnt, returnPoints=False)
    defects = cv2.convexityDefects(cnt, hull)


    # cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

    # print(defects)
    # print(defects.shape[0])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        beginCount += 1
        if beginCount % 2 == 0:
            beginRecord = True
        else:
            beginRecord = False

    count_defects = 0
    currentTempArray = []

    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

        angle = math.acos((b**2 + c**2 - a**2) / (2 * b * c)) * 57

        if angle <= angleFix and a >= contoursLength:
            count_defects += 1
            if beginRecord == True:
                currentTempArray.append([b, c])

            if count_defects == 4 and beginRecord == True:
                dataStore.append(currentTempArray)
            cv2.circle(crop_img, far, 5, [0, 0, 255], -1)

        if a >= contoursLength:
            cv2.line(crop_img, start, end, [0, 255, 0], 2)

        #dist = cv2.pointPolygonTest(cnt, far, True)


    if count_defects == 4 and beginRecord == True:
        text = "%s: %s" % (dataStoreLength, len(dataStore))
        cv2.putText(img, text, (340, 390), cv2.FONT_HERSHEY_SIMPLEX, 1, (34, 240, 247), 2)

        if len(dataStore) == dataStoreLength:
            for i in range(0, endRange):
                del dataStore[-(i + 1)]
            for i in range(0, startRange):
                del dataStore[i]



            data = _function_data_normalize(_averaging_data_store(dataStore))  # Contains new detected informations about user
            dataRatio = _get_height_ratio(_averaging_data_store(dataStore))    # Contains all current user ratio


            ''' Complete UML Executions  '''
            if uml._add_new_user == True:
                global _id
                query = "INSERT INTO persons (name, surname)  VALUES('%s', '%s') " % (uml._user_name, uml._surname)
                db.data_query(query)

                query = "SELECT `id` FROM `persons` WHERE `name` LIKE '%s' AND `surname` LIKE '%s' " % (uml._user_name, uml._surname)
                _id = db.data_fetch(query)[0][0]

                query = "UPDATE `persons` SET `h_11` = '%s', `h_12` = '%s', `h_21` = '%s', `h_22` = '%s', `h_31` = '%s', `h_32` = '%s', " \
                        "`h_41` = '%s', `h_42` = '%s' WHERE `id` = '%s' " % (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], _id)
                db.data_query(query)

                ''' Insert ratio '''
                k = -1
                for i in range(7):
                    for j in range(7 - i):
                        k += 1
                        text = "ratio_%s%d" % (i, ((j + i) + 1))
                        query = "INSERT INTO `users_Ratio` (`user_id`, `userRatioText`, `user_ratio`) VALUES('%s', '%s', '%s') " % \
                                (_id, text, dataRatio[k])
                        db.data_query(query)

                uml.tm.showinfo("Information", "User named %s, %s was added" % (uml._user_name, uml._surname))
                os.execv(sys.executable, ['python'] + sys.argv)

            elif uml._user_also_exist == True:
                userName = ''
                userSurName = ''
                majority_vote = []
                db_Data = db.data_fetch("SELECT * FROM `persons`")

                for i in range(8):
                    min = math.inf
                    current_id = 0

                    for j in range(len(db_Data)):
                        tempMin = (db_Data[j][i + 3] - data[i]) ** 2
                        if tempMin < min:
                            min = tempMin
                            current_id = db_Data[j][0]

                            majority_vote.append(current_id)

                user_id = np.argmax(np.bincount(majority_vote))  # We took most common user id in the list

                for k in range(len(db_Data)):
                    if db_Data[k][0] == user_id:
                        userName = db_Data[k][1]
                        userSurName = db_Data[k][2]

                if uml._include_ratio == False:
                    uml.tm.showinfo("Result without a ratio of fingers:", "With the greatest probability the hand belongs to %s, %s" % (userName, userSurName))
                    os.execv(sys.executable, ['python'] + sys.argv)
                else:
                    majority_vote_ratio = []
                    users_id = db.data_fetch("SELECT `id` FROM `persons` ORDER BY `id` ")
                    users_ratio = db.data_fetch("SELECT `user_ratio`, `user_id` FROM `users_Ratio` ORDER BY `id` ")

                    pprint(dataRatio)
                    print("\n")
                    pprint(users_ratio)
                    print("\n", users_id, "\n\n", len(dataRatio))

                    for i in range(len(dataRatio)):
                        count = i
                        user_id = ''
                        minimum = math.inf

                        for j in range(len(users_id)):
                            if minimum > (dataRatio[i] - users_ratio[count][0]) ** 2:
                                minimum = (dataRatio[i] - users_ratio[count][0]) ** 2
                                user_id = users_ratio[count][1]
                            count += len(dataRatio)

                        majority_vote_ratio.append(user_id)

                    print(majority_vote_ratio, " - ", np.argmax(np.bincount(majority_vote_ratio)), " - ", len(majority_vote_ratio), np.argmax(np.bincount(majority_vote)), "\n")
                    print(majority_vote_ratio, majority_vote)









            '  "db_Data" - contains all always existed informations about users '
            '''db_Data = db.data_fetch("SELECT * FROM persons LIMIT 0, 5")


            pprint(data)
            print("\n\n")
            pprint(db_Data)
            print("\n\n")
            pprint(_averaging_data_store(dataStore))
            print("\n\n")
            pprint(_get_height_ratio(_averaging_data_store(dataStore)))


            'Fill the users_Ratio tabel with ratios between heights'
            k = -1
            for i in range(7):
                for j in range(7 - i):
                    k += 1
                    text = "ratio_%s%d" % (i, ((j + i) + 1))
                    query_2 = "INSERT INTO users_Ratio (user_id, userRatioText, user_ratio) " \
                              "VALUES(%s, '%s', %s)" % (db_Data[0][0], text, _get_height_ratio(_averaging_data_store(dataStore))[k])
                    #db.data_query(query_2)



            ' "majority_vote" - contains all minimum squared distances between all the features and appropriate users id '
            majority_vote = []
            for i in range(8):
                min = math.inf
                current_id = 0

                for j in range(len(db_Data)):
                    tempMin = (db_Data[j][i + 3] - data[i]) ** 2
                    if tempMin < min:
                        min = tempMin
                        current_id = db_Data[j][0]

                majority_vote.append(current_id)


            userName = ''
            userSurName = ''
            user_id = np.argmax(np.bincount(majority_vote))  # We took most common user id in the list
            for k in range(len(db_Data)):
                if db_Data[k][0] == user_id:
                    userName = db_Data[k][1]
                    userSurName = db_Data[k][2]

            print(" id: ", user_id, "\n name: ", userName, "\n surname: ", userSurName)'''

            break

        cv2.putText(img, "Well Done!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 43, 247), 2)
    else:
        cv2.putText(img, "Please fix your hand ('q')!", (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (242, 113, 33), 2)


    "Take A Picture"
    #if cv2.waitKey(1) & 0xFF == ord('q'):
        #break


    cv2.imshow("Gesture", img)
    all_img = np.hstack((drawing, crop_img))
    #cv2.imshow('Contours', all_img)
    k = cv2.waitKey(10)

    if k == 27: break

