import cv2
import time
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

detector = HandDetector(detectionCon=0.8, maxHands=2)

words, hand_coordinates, sum_of_difference_x, sum_of_difference_y = [], [], [], []
start_time = {}
text_timer,  threshold = 0, 35


def calculate_movement(point, min_distance_x=None, min_distance_y=None, max_distance_x=None, max_distance_y=None):
    hand_coordinates.append(point)

    if len(hand_coordinates) > 10:
        hand_coordinates.pop(0)
        coordinate_difference_x = [hand_coordinates[i][0] - hand_coordinates[i - 1][0] for i in
                                   range(1, len(hand_coordinates))]
        coordinate_difference_y = [hand_coordinates[i][1] - hand_coordinates[i - 1][1] for i in
                                   range(1, len(hand_coordinates))]
        sum_of_difference_x.append(sum(coordinate_difference_x))
        sum_of_difference_y.append(sum(coordinate_difference_y))
        if len(sum_of_difference_x) > 5 and (min_distance_x is not None or max_distance_x is not None):
            sum_of_difference_x.pop(0)
            distance_difference_x = [sum_of_difference_x[i] - sum_of_difference_x[i - 1] for i in
                                     range(1, len(sum_of_difference_x))]
            if ((min_distance_x is not None and abs(sum(distance_difference_x)) > min_distance_x) or
                    (max_distance_x is not None and abs(sum(distance_difference_x)) < max_distance_x)):
                return True
        if len(sum_of_difference_y) > 5:
            sum_of_difference_y.pop(0)
            distance_difference_y = [sum_of_difference_y[i] - sum_of_difference_y[i - 1] for i in
                                     range(1, len(sum_of_difference_y))]
            if ((min_distance_y is not None and abs(sum(distance_difference_y)) > min_distance_y) or
                    (max_distance_y is not None and abs(sum(distance_difference_y)) < max_distance_y)):
                return True

    return False


def draw_text():
    global text_timer

    formatted_words = []

    for word in words:
        if len(word) > 1:
            formatted_words.append(' ' + word + ' ')
        else:
            formatted_words.append(word)

    for formatted_word in range(len(formatted_words) - 1):
        if formatted_words[formatted_word].endswith(' ') and formatted_words[formatted_word + 1].startswith(' '):
            formatted_words[formatted_word + 1] = formatted_words[formatted_word + 1].lstrip()

    text = ''.join(formatted_words)
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (255, 0, 0)
    scale, thickness = 2, 4

    if text_timer > 0:
        cv2.putText(frame, text, (40, 400), font, scale, color, thickness, cv2.LINE_AA)
        text_timer -= 1
    else:
        words.clear()


def counter_time(condition, gesture):
    global start_time

    if gesture not in start_time:
        start_time[gesture] = 0

    if condition:
        if start_time[gesture] == 0:
            start_time[gesture] = time.time()
        elif time.time() - start_time[gesture] >= 0.3:
            start_time[gesture] = 0
            return True
    else:
        start_time[gesture] = 0

    return False


def calculate_distance(point_0, point_1):
    distance = detector.findDistance(point_0, point_1)[0]

    return distance


def config_text(text):
    global text_timer

    if text not in words:
        words.append(text)
        print(words)

    text_timer = int(cap.get(cv2.CAP_PROP_FPS)) * 2

    return text_timer


while cap.isOpened():
    ok, frame = cap.read()
    frame = cv2.flip(frame, 1)

    if not ok:
        print('Camera not detected')
        break

    if frame is not None:
        hands, frame = detector.findHands(frame)  # Identifica as mãos

        if hands:
            fingers_situation = {
                'thumb': [1, 0, 0, 0, 0],
                'index': [0, 1, 0, 0, 0],
                'middle': [0, 0, 1, 0, 0],
                'ring': [0, 0, 0, 1, 0],
                'pinky': [0, 0, 0, 0, 1],
                'all': [1, 1, 1, 1, 1],
                'none': [0, 0, 0, 0, 0],
                'thumb+index': [1, 1, 0, 0, 0],
                'thumb+pinky': [1, 0, 0, 0, 1],
                'thumb+index+pinky': [1, 1, 0, 0, 1],
                'index+middle': [0, 1, 1, 0, 0],
                'index+middle+ring+pinky': [0, 1, 1, 1, 1]
            }

            def hand_points(hand_index, point):
                try:
                    points = {
                        'wrist': hands[hand_index]['lmList'][0][0:2],
                        'thumb_cmc': hands[hand_index]['lmList'][1][0:2],
                        'thumb_mcp': hands[hand_index]['lmList'][2][0:2],
                        'thumb_ip': hands[hand_index]['lmList'][3][0:2],
                        'thumb_tip': hands[hand_index]['lmList'][4][0:2],
                        'index_mcp': hands[hand_index]['lmList'][5][0:2],
                        'index_pip': hands[hand_index]['lmList'][6][0:2],
                        'index_dip': hands[hand_index]['lmList'][7][0:2],
                        'index_tip': hands[hand_index]['lmList'][8][0:2],
                        'middle_mcp': hands[hand_index]['lmList'][9][0:2],
                        'middle_pip': hands[hand_index]['lmList'][10][0:2],
                        'middle_dip': hands[hand_index]['lmList'][11][0:2],
                        'middle_tip': hands[hand_index]['lmList'][12][0:2],
                        'ring_mcp': hands[hand_index]['lmList'][13][0:2],
                        'ring_pip': hands[hand_index]['lmList'][14][0:2],
                        'ring_dip': hands[hand_index]['lmList'][15][0:2],
                        'ring_tip': hands[hand_index]['lmList'][16][0:2],
                        'pinky_mcp': hands[hand_index]['lmList'][17][0:2],
                        'pinky_pip': hands[hand_index]['lmList'][18][0:2],
                        'pinky_dip': hands[hand_index]['lmList'][19][0:2],
                        'pinky_tip': hands[hand_index]['lmList'][20][0:2]
                    }

                    return points.get(point, None)

                except IndexError as e:
                    print(e)
                    return None


            for hand in hands:
                state = detector.fingersUp(hand)  # Verifica dedos levantados de cada mão

                b = (state == fingers_situation['index+middle+ring+pinky'] and
                     (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                         hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'ring_tip'),
                                         hand_points(hands.index(hand), 'middle_tip')) < threshold))

                i = (state == fingers_situation['pinky'] and
                     (calculate_distance(hand_points(hands.index(hand), 'middle_dip'),
                                         hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'thumb_ip'),
                                         hand_points(hands.index(hand), 'middle_dip')) < threshold))

                u = (state == fingers_situation['index+middle'] and
                     (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                         hand_points(hands.index(hand), 'ring_mcp')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'pinky_dip'),
                                         hand_points(hands.index(hand), 'pinky_mcp')) < threshold))

                l = (state == fingers_situation['thumb+index'] and
                     (calculate_distance(hand_points(hands.index(hand), 'middle_pip'),
                                         hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'ring_pip'),
                                         hand_points(hands.index(hand), 'ring_mcp')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'pinky_pip'),
                                         hand_points(hands.index(hand), 'pinky_mcp')) < threshold))

                o = (state == fingers_situation['thumb'] and
                     (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                         hand_points(hands.index(hand), 'index_tip')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'index_mcp'),
                                         hand_points(hands.index(hand), 'pinky_mcp')) < threshold))

                d = (state == fingers_situation['thumb+index'] and
                     (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                         hand_points(hands.index(hand), 'middle_tip')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'middle_mcp'),
                                         hand_points(hands.index(hand), 'pinky_mcp')) < threshold))

                c = (state == fingers_situation['thumb+pinky'] and
                     (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                         hand_points(hands.index(hand), 'index_tip')) > threshold * 1.5 and
                      calculate_distance(hand_points(hands.index(hand), 'index_mcp'),
                                         hand_points(hands.index(hand), 'pinky_mcp')) < threshold))

                a = (state == fingers_situation['thumb'] and
                     (calculate_distance(hand_points(hands.index(hand), 'thumb_ip'),
                                         hand_points(hands.index(hand), 'index_mcp')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'middle_dip'),
                                         hand_points(hands.index(hand), 'middle_mcp')) < threshold))

                s = (state == fingers_situation['none'] and
                     (calculate_distance(hand_points(hands.index(hand), 'middle_tip'),
                                         hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                      calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                         hand_points(hands.index(hand), 'middle_dip')) < threshold) and
                     calculate_movement(hand_points(hands.index(hand), 'middle_dip'), None, None, 5, 5))

                tudo = (state == fingers_situation['all'] and
                        (calculate_distance(hand_points(hands.index(hand), 'index_tip'),
                                            hand_points(hands.index(hand), 'middle_tip')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'middle_tip'),
                                            hand_points(hands.index(hand), 'ring_tip')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'index_tip')) < threshold))

                bem = (state == fingers_situation['thumb'] and
                       (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                           hand_points(hands.index(hand), 'index_tip')) > threshold * 1.8 and
                        calculate_distance(hand_points(hands.index(hand), 'middle_tip'),
                                           hand_points(hands.index(hand), 'middle_mcp')) < threshold))

                me_chamo = (state == fingers_situation['index+middle'] and
                            calculate_distance(hand_points(hands.index(hand), 'thumb_mcp'),
                                               hand_points(hands.index(hand), 'index_mcp')) < threshold)

                nao = (state == fingers_situation['index'] and
                       (calculate_distance(hand_points(hands.index(hand), 'middle_dip'),
                                           hand_points(hands.index(hand), 'middle_mcp')) < threshold) and
                       calculate_movement(hand_points(hands.index(hand), 'index_tip'), 80))

                sim = (state == fingers_situation['none'] and
                       (calculate_distance(hand_points(hands.index(hand), 'middle_pip'),
                                           hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                        calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                           hand_points(hands.index(hand), 'middle_dip')) < threshold) and
                       calculate_movement(hand_points(hands.index(hand), 'middle_pip'), None, 10))

                eu_te_amo = (state == fingers_situation['thumb+index+pinky'] and
                             calculate_distance(hand_points(hands.index(hand), 'middle_dip'),
                                                hand_points(hands.index(hand), 'middle_mcp')) < threshold)

                por_favor = (len(hands) == 2 and
                             state == fingers_situation['thumb'] and
                             detector.fingersUp(hands[1]) == fingers_situation['thumb'] and
                             calculate_distance(hand_points(0, 'middle_tip'),
                                                hand_points(1, 'middle_tip')) < threshold < calculate_distance(
                            hand_points(0, 'middle_mcp'), hand_points(1, 'middle_mcp')))

                g_words = {
                    'b': b,
                    'i': i,
                    'u': u,
                    'l': l,
                    'o': o,
                    'd': d,
                    'c': c,
                    'a': a,
                    's': s,
                    'tudo': tudo,
                    'bem': bem,
                    'me chamo': me_chamo,
                    'nao': nao,
                    'sim': sim,
                    'por favor': por_favor,
                    'eu te amo': eu_te_amo
                }

                for key, value in g_words.items():
                    if counter_time(value, key):
                        config_text(key)

    draw_text()
    cv2.imshow('hands', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
