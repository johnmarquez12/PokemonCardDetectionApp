import numpy as np
import cv2

def main():
    print("Starting Camera")
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read();

        # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BAYER_BG2GRAY)
        # stack = np.hstack((gray_frame, frame))
        # cv2.imshow('frame', stack)
        cv2.imshow('frame', frame)



if __name__ == '__main__':
    main()
