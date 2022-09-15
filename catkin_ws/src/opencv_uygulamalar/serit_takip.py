#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 20:29:01 2022

@author: eyup
"""

"""
Şerit takip etme
"""
import cv2
import numpy as np
import rospy
from sensor_msgs.msg import Image #kameradan veri almak için
from geometry_msgs.msg import Twist # Hız yayınlamak için
from cv_bridge import CvBridge # kameradan gelen mesajları görüntüye çevirmek için

class SeritTakip():
    def __init__(self):
        rospy.init_node("serit_takip") #düğümü başlattık, oluşturduk
        self.bridge = CvBridge() # köprü oluşturduk artık abone olma işini gerçekleştirebiliriz.
        rospy.Subscriber("camera/rgb/image_raw", Image, self.kameraCallback) # subscriber ile camera/rgb/image_raw konusuna abone oluyoruz ve Image tipinde veriler kullanacak ve abone olduğumuzda kameraCallback isimli fonksiyona gidicek.
        self.pub = rospy.Publisher("cmd_vel", Twist, queue_size= 10) #publisher oluşturduk cmd_vel konusundan hız yayınlayacağız Twist tipinde yayınlanan mesajın kuyruk büyüklüğüde 10 olacak
        self.hiz_mesaji= Twist() #hız mesajını tanımladık twist tipinde hız mesajı kullanıyoruz.
        rospy.spin() # döngünün sürekli devam etmesi için rospayın spin metodunu kullandık
        
    def kameraCallback(self,mesaj): # fonksiyonu tanımladık ilk paremetre self ikinci parametre gelen mesaj olacak
        img = self.bridge.imgmsg_to_cv2(mesaj,"bgr8")#  gelen mesajı görüntüye çevirdik bunun için köprü kurduk bridge yardımıyla imgmsg_to_cv2( image mesajını cv2 ya çevir dedik) gelen mesaj bilgisini bgr8 formatında çevir diyoruz
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV) #şerit takip edeceğimiz için hsv uzayını kullanıyoruz. hsv tanımladık cv2.cvtColor (convertColor) ile gelen image i (img) bgr dan hsv ye çeviyoruz
        alt_sari = np.array([20,100,100]) # çizgi alt sınır tanımladık saf bir sarının hü değerin 10 eksiği alt sınırı saturation 100 ve value 100 
        ust_sari = np.array([40,255,255]) # çizgi üst sınır tanımladık hü değerinin 10 fazlası üst sınırı saturation 255 value 255
        maske = cv2.inRange(hsv, alt_sari, ust_sari) # maskeleme işlemini yaptık
        sonuc = cv2.bitwise_and(img,img,mask=maske) # maskeyi orjinal görüntü üzerine uyguladık
        h,w,d = img.shape # gelen görüntünün shape ini aldık yükseklik genişlik ve kanal bilgisi
        cv2.circle(img,(int(w/2),int(h/2)),5,(0,0,255),-1) # referans nokta belirledik
        M = cv2.moments(maske) # maske üzerinden momentleri centroidleri buluyoruz
        if M['m00'] > 0:
            cx = int(M['m10']/M['m00']) # moment üzerinden centroidi hesaplıyoruz
            cy = int(M['m01']/M['m00'])  # moment üzerinden centroidi hesaplıyoruz
            cv2.circle(img,(cx,cy),5,(255,0,0),-1) # cv2.circle yardımı ile orjinal görüntümüz ile merkez noktası cx, cy olacak şekilde yarıçapı 5 olacak şekilde rengi mavi olarak tanımladık ve içi dolu (-1)
            sapma = cx - w/2
            print(sapma)
            self.hiz_mesaji.linear.x =0.2 #hız mesajını tanımladık
            self.hiz_mesaji.angular.z = -sapma/100
            self.pub.publish(self.hiz_mesaji) # daha önce tanımladığımız publisher üzerinden hız mesajını gonderdik
        else:
            self.hiz_mesaji.linear.x = 0.0
            self.hiz_mesaji.angular.z = 0.0
            self.pub.publish(self.hiz_mesaji)
        cv2.imshow("Orjinal", img) 
        cv2.imshow("Maske", maske)
        cv2.imshow("Sonuc", sonuc)
        cv2.waitKey(1)
        
SeritTakip()