import sys
sys.path.append('D:\\opencv249\\opencv\\build\\python\\2.7\\x64')
import numpy as np
import argparse
import cv2
import time

def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis

def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:,:,0], flow[:,:,1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx+fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[...,0] = ang*(180/np.pi/2)
    hsv[...,1] = 255
    hsv[...,2] = np.minimum(v*4, 255)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr

def draw_hsv_v1(flow):
    h, w = flow.shape[:2]
    hsv = np.zeros((h, w, 3), np.uint8)
    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,1] = 255
    hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

    return rgb

def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LINEAR)
    return res

if __name__ == "__main__":
    show_hsv = False
    show_glitch = False
    show_flow = True
    video = '../office2/video_1.avi'
    camera = cv2.VideoCapture(video)
    ret, prvs_frame = camera.read()
    prvs_gray = cv2.cvtColor(prvs_frame,cv2.COLOR_BGR2GRAY)
    cur_glitch = prvs_frame.copy()

    while(1):
        ret, next_frame = camera.read()
        next_gray = cv2.cvtColor(next_frame,cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prvs_gray, next_gray, 0.5, 3, 15, 3, 5, 1.2, 0)
        prvs_gray = next_gray

        if show_flow:
            cv2.imshow('flow', draw_flow(next_gray, flow))
        if show_hsv:
            cv2.imshow('flow HSV', draw_hsv(flow))
            # cv2.imshow('flow HSV', draw_hsv_v1(flow))
        if show_glitch:
            cur_glitch = warp_flow(cur_glitch, flow)
            cv2.imshow('glitch', cur_glitch)

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
        elif k == ord('s'):
            cv2.imwrite('opticalfb' + time.strftime("-%Y-%m-%d-%H-%M-%S", time.localtime())  + '.png',next_frame)

    camera.release()
    cv2.destroyAllWindows()

