#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' 
Bu kodda dokümandaki görevimiz olan 
robotu ileri doğru 5 saniye hareket ettirme ve ardından 90 derece döndürme işlemlerini yapıyoruz.
'''


import rospy
from geometry_msgs.msg import Twist                    # Hareket komutları için ekledik. (/cmd_vel)
from nav_msgs.msg import Odometry                      # Konum ve yönelim bilgisi için ekledik. (/odom)
from tf.transformations import euler_from_quaternion   # Dönüşümler için ekledik.
import math                                            # Matematiksel işlemler için ekledik.

class TurtleController:
    def __init__(self):
        rospy.init_node('turtle_controller_node', anonymous=True) # ROS düğümünü başlatıyoruz.
        
        # Dokümanda ekstra istenen görevlerden biri olan rosparam ile değer alma kısmı burası.
        # Launch dosyasında ilgili parametre bulunamazsa sağındaki değerini kullanırlardı.
        self.linear_speed = rospy.get_param('~linear_speed', 0.2)      # İleri gitme hızını verdik (m/s).
        self.linear_duration = rospy.get_param('~linear_duration', 5.0) # İleri gitme süresi (saniye).
        self.angular_speed = rospy.get_param('~angular_speed', 0.5)    # Dönüş hızı (rad/s).
        

        # Publisher ve Subscriber tanımları
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10) # Hareket komutlarını yayınlamak için Twist mesajı gönderiyoruz.
        self.sub = rospy.Subscriber('/odom', Odometry, self.odom_callback) # Konum ve yönelim bilgisi almak için Odometry mesajlarını dinliyoruz. Konum bilgisi geldikçe odom_callback fonksiyonu çağrılır.
        
        self.rate = rospy.Rate(10) # 10 Hz döngü hızı veriyoruz.
        self.ctrl_c = False
        rospy.on_shutdown(self.shutdownhook) # Düğüm kapanırken çağrılacak fonksiyon.

    def shutdownhook(self): # Burası düğüm kapanırken robotu durdurmak için.
        self.stop_robot() 
        self.ctrl_c = True 

    def stop_robot(self): # Burada robotun ileri hızı ve dönüş hızını sıfırlıyoruz.
        cmd = Twist()
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.pub.publish(cmd)

    def odom_callback(self, msg): # Odometry mesajı geldiğinde çağrılır. Pozisyon ve yönelim bilgilerini alır.
        position = msg.pose.pose.position 
        orientation = msg.pose.pose.orientation
        (roll, pitch, yaw) = euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w]) # Kuaterniyon formatındaki verimizi Euler açılarına çeviriyoruz.
        rospy.loginfo("X: {:.2f} | Y: {:.2f} | Yaw: {:.2f} rad".format(position.x, position.y, yaw))

    def move_forward_timed(self): # Bizden istenen süre yani 5 saniye boyunca ileri hareket fonksiyonu
        rospy.loginfo(f"İleri hareket başlıyor.") # Terminalde hareketin başladığını görebilelim diye yazdırıyoruz.
        
        cmd = Twist() # Hareket komutu oluşturuyoruz.
        cmd.linear.x = self.linear_speed # Parametreden gelen hızı kullanıyoruz.
        
        start_time = rospy.Time.now().to_sec() # Başlangıç zamanını alıyoruz.
        while (rospy.Time.now().to_sec() - start_time) < self.linear_duration: # Belirtilen süre yani 5 saniye boyunca döngü devam eder.
            self.pub.publish(cmd) # Hareket komutunu yayınlıyoruz.
            self.rate.sleep() 
        
        self.stop_robot() # Süre dolunca robotu durduruyoruz.
        rospy.loginfo("Süre doldu ve durdu.")

    def rotate_90_degrees(self): # 90 derece dönüş fonksiyonu
        rospy.loginfo("90 derece dönüş başlıyor.") # Terminalde dönüşün başladığını görebilelim diye yazdırıyoruz.
        cmd = Twist() # Hareket komutu oluşturuyoruz.
        cmd.angular.z = self.angular_speed # Parametreden gelen dönüş hızını kullanıyoruz.
        
        target_angle = math.pi / 2 # 90 dereceyi radyan cinsine çeviriyoruz.
        duration = target_angle / self.angular_speed # Dönüş süresini hesaplıyoruz.
        
        start_time = rospy.Time.now().to_sec() # Başlangıç zamanını alıyoruz.
        while (rospy.Time.now().to_sec() - start_time) < duration: # 90 dereceyi yakalamak için hesapladığımız süre boyunca dönme işlemi devam eder.
            self.pub.publish(cmd) 
            self.rate.sleep()
            
        self.stop_robot()
        rospy.loginfo("Dönüş tamamlandı.")

    def run_scenario(self): # Sırayla önce ileri hareket sonra 90 derece dönüş işlemini yapan metotları çağırdığımız fonksiyon.
        
        rospy.sleep(1)
        self.move_forward_timed() # Bu ileri hareket fonksiyonu.
        rospy.sleep(1)
        self.rotate_90_degrees()  # Bu 90 derece dönüş fonksiyonu.   
        rospy.spin()

if __name__ == '__main__': 
    try:   # Burada TurtleController sınıfından bir nesne oluşturuyoruz. Ardından run_scenario() metodunu çağırıyoruz.
        controller = TurtleController() 
        controller.run_scenario()
    except rospy.ROSInterruptException: # ROS kesintisi durumunda programın düzgün kapanması için.
        pass
