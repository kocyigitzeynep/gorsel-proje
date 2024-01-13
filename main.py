import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QMessageBox, QApplication, QTableWidgetItem, QLineEdit
from giris import girissinifi
from KULLANICI import KULLANICI
from yonetici2 import Ui_yonetici2
from pymongo import MongoClient
import string, random
import bbb

class anaPencere(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["Dosya"]
        self.collection = self.db["kullanicilar"]

        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setContentsMargins(0, 0, 0, 0)

        self.girisWidget = QWidget()
        self.yoneticiWidget = QWidget()
        self.kullaniciWidget = QWidget()

        self.stackedWidget.addWidget(self.girisWidget)
        self.stackedWidget.addWidget(self.yoneticiWidget)
        self.stackedWidget.addWidget(self.kullaniciWidget)

        self.vlayout.addWidget(self.stackedWidget)

        self.girisSayfasi()

        self.girisSayfasiOlustu = True
        self.yoneticiSayfasiOlustu = False
        self.kullaniciSayfasiOlustu = False

    def girisSayfasi(self):
        self.girisNesnesi = girissinifi()
        self.girisNesnesi.setupUi(self.girisWidget)
        self.girisButonu = self.girisNesnesi.pushButton_login
        self.sifreGoster = self.girisNesnesi.showPasswordCB
        self.sifreGoster.stateChanged.connect(self.showPassword)
        self.girisButonu.clicked.connect(self.giris)

    def showPassword(self):
        if self.girisNesnesi.lineEdit_sifre.echoMode() == QLineEdit.EchoMode.Password:
            self.girisNesnesi.lineEdit_sifre.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.girisNesnesi.lineEdit_sifre.setEchoMode(QLineEdit.EchoMode.Password)

    def girisSayfasinaGit(self):
        self.stackedWidget.setCurrentIndex(0)

    def giris(self):
        self.kullaniciAdiLogin = self.girisNesnesi.lineEdit_eposta.text().strip()
        self.sifreLogin = self.girisNesnesi.lineEdit_sifre.text().strip()

        user_data = self.collection.find_one({"kullanici adi": self.kullaniciAdiLogin, "sifre": self.sifreLogin})
        if user_data:
            if user_data["hesap turu"] == "yonetici":
                if not self.yoneticiSayfasiOlustu:
                    self.yoneticiSayfasi()
                    self.yoneticiSayfasiOlustu = True 
                QMessageBox.information(self, "Basarili!", "Basariyla giris yapildi, anasayfaya yonlendiriliyorsunuz.")
                self.stackedWidget.setCurrentIndex(1)
            elif user_data["hesap turu"] == "kullanici":
                if not self.kullaniciSayfasiOlustu:
                    self.kullaniciSayfasi()
                    self.kullaniciSayfasiOlustu = True
                    QMessageBox.information(self, "Basarili!", "Basariyla giris yapildi, anasayfaya yonlendiriliyorsunuz.")
                    self.stackedWidget.setCurrentIndex(2)

        else:
            QMessageBox.warning(self, "Basarisiz...", "Kullanici adi / email veya sifreniz yanlis.")

    def yoneticiSayfasi(self):
        self.anaNesne = Ui_yonetici2()
        self.anaNesne.setupUi(self.yoneticiWidget)
        self.anaNesne.pushButton_2.clicked.connect(self.uyeEkle)
        self.users = self.collection.find({})
        for row, item in enumerate(self.users):
            if item["hesap turu"] == "kullanici":
                self.anaNesne.tableWidget.insertRow(0)
                self.anaNesne.tableWidget.setItem(0, 0, QTableWidgetItem(item["kullanici adi"]))
                self.anaNesne.tableWidget.setItem(0, 1, QTableWidgetItem(item["sifre"]))

    def uyeEkle(self):
        username = self.anaNesne.lineEdit_2.text().strip()
        all_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
        password = ''.join(random.choice(all_chars) for _ in range(8))

        user_data = self.collection.find_one({"kullanici adi": username})

        if user_data:
            QMessageBox.warning(self, "Hata!", "Bu kullanıcı adına sahip bir hesap zaten var.")
        else:
            self.collection.insert_one({"kullanici adi": username, "sifre": password, "hesap turu": "kullanici"})
        self.users = self.collection.find({})
        self.anaNesne.tableWidget.clearContents()
        self.anaNesne.tableWidget.setRowCount(0)
        for row, item in enumerate(self.users):
            if item["hesap turu"] == "kullanici":
                self.anaNesne.tableWidget.insertRow(0)
                self.anaNesne.tableWidget.setItem(0, 0, QTableWidgetItem(item["kullanici adi"]))
                self.anaNesne.tableWidget.setItem(0, 1, QTableWidgetItem(item["sifre"]))

    def kullaniciSayfasi(self):
        self.kullaniciNesne = KULLANICI()
        self.kullaniciNesne.setupUi(self.kullaniciWidget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = anaPencere()
    window.show()
    sys.exit(app.exec())
