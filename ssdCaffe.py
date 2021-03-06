import numpy as np
import cv2
import fps
import caffe

caffe.set_mode_cpu()

#caffe.set_device(0)
#caffe.set_mode_gpu()


net_pretrained='./MobileNetSSD_deploy.caffemodel'
net_model_file='./MobileNetSSD_deploy.prototxt'

classNames = { 0: 'background',
    1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat',
    5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat', 9: 'chair',
    10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
    14: 'motorbike', 15: 'person', 16: 'pottedplant',
    17: 'sheep', 18: 'sofa', 19: 'train', 20: 'tvmonitor' }

net = cv2.dnn.readNetFromCaffe(net_model_file, net_pretrained)

cap = cv2.VideoCapture(0)
fpsWithTick = fps.fpsWithTick()

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    frame_resized = cv2.resize(frame, (300, 300))

    blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)

    net.setInput(blob)
    detections = net.forward()
    #print detections

    cols = frame_resized.shape[1]
    rows = frame_resized.shape[0]

    # For get the class and location of object detected,
    # There is a fix index for class, location and confidence
    # value in @detections array .
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]  # Confidence of prediction
        class_id = int(detections[0, 0, i, 1])  # Class label

        # Object location
        xLeftBottom = int(detections[0, 0, i, 3] * cols)
        yLeftBottom = int(detections[0, 0, i, 4] * rows)
        xRightTop = int(detections[0, 0, i, 5] * cols)
        yRightTop = int(detections[0, 0, i, 6] * rows)

        # Factor for scale to original size of frame
        heightFactor = frame.shape[0] / 300.0
        widthFactor = frame.shape[1] / 300.0
        # Scale object detection to frame
        xLeftBottom = int(widthFactor * xLeftBottom)
        yLeftBottom = int(heightFactor * yLeftBottom)
        xRightTop = int(widthFactor * xRightTop)
        yRightTop = int(heightFactor * yRightTop)
        # Draw location of object
        cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop),
                      (0, 255, 0))

        # Draw label and confidence of prediction in frame resized
        if class_id in classNames:
            label = classNames[class_id] + ": " + str(confidence)
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            yLeftBottom = max(yLeftBottom, labelSize[1])
            cv2.rectangle(frame, (xLeftBottom, yLeftBottom - labelSize[1]),
                          (xLeftBottom + labelSize[0], yLeftBottom + baseLine),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(frame, label, (xLeftBottom, yLeftBottom),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

            print label  # print class and confidence


    fps_output = str(fpsWithTick.get())
    cv2.putText(frame, "fps = " + fps_output, (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))


    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
