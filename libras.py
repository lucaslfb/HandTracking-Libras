import cv2
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

detector = HandDetector(detectionCon=0.8, maxHands=2)

words = []
text_timer = 0


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
                threshold = 35  # Distância em pixels dos pontos da mão

                if (state == fingers_situation['index+middle+ring+pinky'] and
                        (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'ring_tip'),
                                            hand_points(hands.index(hand), 'middle_tip')) < threshold)):
                    config_text('b')

                if (state == fingers_situation['pinky'] and
                        (calculate_distance(hand_points(hands.index(hand), 'middle_dip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'thumb_ip'),
                                            hand_points(hands.index(hand), 'middle_dip')) < threshold)):
                    config_text('i')

                if (state == fingers_situation['index+middle'] and
                        (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'ring_mcp')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'pinky_dip'),
                                            hand_points(hands.index(hand), 'pinky_mcp')) < threshold)):
                    config_text('u')

                if (state == fingers_situation['thumb+index'] and
                        (calculate_distance(hand_points(hands.index(hand), 'middle_pip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'ring_pip'),
                                            hand_points(hands.index(hand), 'ring_mcp')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'pinky_pip'),
                                            hand_points(hands.index(hand), 'pinky_mcp')) < threshold)):
                    config_text('l')

                if (state == fingers_situation['thumb'] and
                        (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'index_tip')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'index_mcp'),
                                            hand_points(hands.index(hand), 'pinky_mcp')) < threshold)):
                    config_text('o')

                if (state == fingers_situation['thumb+pinky'] and
                        (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'index_tip')) > threshold * 1.5 and
                         calculate_distance(hand_points(hands.index(hand), 'index_mcp'),
                                            hand_points(hands.index(hand), 'pinky_mcp')) < threshold)):
                    config_text('c')

                if (state == fingers_situation['thumb'] and
                        (calculate_distance(hand_points(hands.index(hand), 'thumb_ip'),
                                            hand_points(hands.index(hand), 'index_mcp')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'middle_dip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold)):
                    config_text('a')

                if (state == fingers_situation['none'] and
                        (calculate_distance(hand_points(hands.index(hand), 'middle_tip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'middle_dip')) < threshold)):
                    config_text('s')

                if (state == fingers_situation['all'] and
                        (calculate_distance(hand_points(hands.index(hand), 'index_tip'),
                                            hand_points(hands.index(hand), 'middle_tip')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'middle_tip'),
                                            hand_points(hands.index(hand), 'ring_tip')) < threshold and
                         calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'index_tip')) < threshold)):
                    config_text('tudo')

                if (state == fingers_situation['thumb'] and
                        (calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'index_tip')) > threshold * 1.8 and
                         calculate_distance(hand_points(hands.index(hand), 'middle_tip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold)):
                    config_text('bem?')

                if (state == fingers_situation['index+middle'] and
                        (calculate_distance(hand_points(hands.index(hand), 'thumb_mcp'),
                                            hand_points(hands.index(hand), 'index_mcp')) < threshold)):
                    config_text('me chamo')

                if (state == fingers_situation['index'] and
                        (calculate_distance(hand_points(hands.index(hand), 'middle_dip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold)):
                    config_text('nao')

                if (state == fingers_situation['none'] and
                        (calculate_distance(hand_points(hands.index(hand), 'middle_pip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold * 0.5 and
                         calculate_distance(hand_points(hands.index(hand), 'thumb_tip'),
                                            hand_points(hands.index(hand), 'middle_dip')) < threshold)):
                    config_text('sim')

                if (state == fingers_situation['thumb+index+pinky'] and
                        (calculate_distance(hand_points(hands.index(hand), 'middle_dip'),
                                            hand_points(hands.index(hand), 'middle_mcp')) < threshold)):
                    config_text('eu te amo')

                if len(hands) == 2:  # Verifica se são duas mãos levantadas. Lógica para ambas as mãos abaixo:
                    state_other = detector.fingersUp(hands[1])  # Instancia a segunda mão e seus pontos

                    if (state == fingers_situation['thumb'] and state_other == fingers_situation['thumb'] and
                            (calculate_distance(hand_points(0, 'middle_tip'),
                                                hand_points(1, 'middle_tip')) < threshold) and
                            calculate_distance(hand_points(0, 'middle_mcp'),
                                               hand_points(1, 'middle_mcp')) > threshold):
                        config_text('por favor')

    draw_text()
    cv2.imshow('hands', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
