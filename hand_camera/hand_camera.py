import cv2
import pyrealsense2 as rs
import mediapipe as mp
import time
import pandas as pd
import statistics
import keyboard
from datetime import datetime
from realsense_depth import *
#cap = cv2.VideoCapture(0)

ctx = rs.context()
devices = ctx.query_devices()
for dev in devices:
    dev.hardware_reset()
print('reset done')

# 手を検出するモデルを作成する
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands()
b=0

columns2 = ['X_Coordinate','Y_Coordinate', 'Distance(median)', 'Distance(direct)','Date']
df = pd.DataFrame(columns=columns2)

prevTime = 0
dc = DepthCamera()

with mp_hands.Hands(max_num_hands=1,
                    min_detection_confidence=0.5) as hands:
    while True:
        #success, img = cap.read()
        if keyboard.is_pressed("space"):
            b=1

        ret, depth_frame, color_frame = dc.get_frame()

        #imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB = cv2.cvtColor(color_frame, cv2.COLOR_BGR2RGB)

        imgRGB.flags.writeable = False
        # モデルで手を検出する
        results = hands.process(imgRGB)

        imgRGB.flags.writeable = True
        #image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = cv2.cvtColor(color_frame, cv2.COLOR_BGR2RGB)

        try:
            if results.multi_hand_landmarks: # 手が検出された場合
                for hand_lms in results.multi_hand_landmarks:
                    for id ,lm in enumerate(hand_lms.landmark):
                        if id == 0:
                            righthandX, righthandY = float(lm.x*640), float(lm.y*480)
                            #print(righthandX, righthandY)
                            lst = []
                            for y in range(int(righthandY) - 15, int(righthandY) + 16):  # float値では奥行きは計測できない
                                for x in range(int(righthandX) - 15, int(righthandX) + 16):  # 右手首の座標を中心に30px×30pxの正方形範囲で座標をまとめて取得
                                    distance0 = depth_frame[x, y]
                                    lst.append(distance0)
                            lst2 = [i for i in lst if i != 0]  # 奥行き0を排除
                            lst2.sort()
                            Righthand = [[righthandX, righthandY,
                                          statistics.median(lst2),  # 奥行きリスト中央値を出力
                                          depth_frame[int(righthandX), int(righthandY)],  # 直接取得した奥行き
                                          datetime.now().isoformat(sep=' ', timespec='milliseconds')]]
                            print(Righthand)
                #mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)    # 手のランドマークを描画する
                mp_draw.draw_landmarks(color_frame, hand_lms, mp_hands.HAND_CONNECTIONS)    # 手のランドマークを描画する
            else:
                Righthand = [[0, 0, 0, 0, datetime.now().isoformat(sep=' ', timespec='milliseconds')]]
                print(Righthand)

            if b == 1:
                df1 = pd.DataFrame(data=Righthand, columns=columns2)
                df2 = df.append(df1, ignore_index=True)
                df = df2
        except:
            pass

        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime
        cv2.putText(color_frame, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 2)
        #cv2.imshow("Image", img)
        cv2.imshow("Image", color_frame)

        if cv2.waitKey(5) & 0xFF == 27:
            df.to_csv('pose.csv')
            break
