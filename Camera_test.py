import cv2
cap = cv2.VideoCapture(4)  # 换1、2、3、4
flag = cap.isOpened()
index = 1
while flag:
    ret, frame = cap.read()
    cv2.imshow("Capture", frame)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('s'):  # 按s保存图片
        cv2.imwrite("H:/yolov8/HT_UI/Capture/" + str(index) + ".jpg", frame)
        print("successful")
        print("-------------------------")
        index += 1
    elif k == ord('q'):  # 按q键退出
        break
cap.release()
cv2.destroyAllWindows()
