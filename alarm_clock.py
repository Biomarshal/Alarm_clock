import sys, os, math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QListWidget, QTimeEdit,
    QMessageBox, QFileDialog, QSystemTrayIcon,
    QMenu, QSlider
)
from PyQt6.QtCore import (
    QTimer, QTime, QDateTime, Qt, QUrl,
    QPropertyAnimation
)
from PyQt6.QtGui import QPainter, QColor, QPen, QIcon, QAction
from PyQt6.QtMultimedia import QSoundEffect


# =============== ANALOG CLOCK ===============
class AnalogClock(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 200)

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        now = QTime.currentTime()

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(self.width()/2, self.height()/2)
        p.scale(side/200, side/200)

        p.setBrush(QColor("#2d2d2d"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(-90, -90, 180, 180)

        p.setPen(QPen(QColor("white"), 2))
        for _ in range(12):
            p.drawLine(0, -80, 0, -88)
            p.rotate(30)

        # hour
        p.setPen(QPen(QColor("#ff9800"), 6))
        p.save()
        p.rotate(30*((now.hour()+now.minute()/60)))
        p.drawLine(0, 0, 0, -50)
        p.restore()

        # minute
        p.setPen(QPen(QColor("#03a9f4"), 4))
        p.save()
        p.rotate(6*(now.minute()+now.second()/60))
        p.drawLine(0, 0, 0, -70)
        p.restore()

        # second
        p.setPen(QPen(QColor("#f44336"), 2))
        p.save()
        p.rotate(6*now.second())
        p.drawLine(0, 10, 0, -80)
        p.restore()


# =============== MAIN APP ===============
class AlarmApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Alarm Pro")
        self.resize(360, 560)

        self.alarms = []
        self.triggered = set()

        # SOUND
        self.sound = QSoundEffect()
        self.sound.setLoopCount(-2)
        self.sound.setVolume(0.5)

        # CLOCKS
        self.analog = AnalogClock()

        self.digital = QLabel()
        self.digital.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digital.setStyleSheet("font-size:22px;font-weight:bold;")

        # CONTROLS
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")

        add_btn = QPushButton("Add Alarm")
        add_btn.clicked.connect(self.add_alarm)

        tone_btn = QPushButton("Select Tone")
        tone_btn.clicked.connect(self.select_tone)

        self.list = QListWidget()

        del_btn = QPushButton("Delete Selected")
        del_btn.clicked.connect(self.delete_alarm)

        snooze_btn = QPushButton("Snooze 5 min")
        snooze_btn.clicked.connect(self.snooze)

        stop_btn = QPushButton("Stop Alarm")
        stop_btn.clicked.connect(self.stop_alarm)

        # VOLUME SLIDER
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.change_volume)

        # LAYOUT
        layout = QVBoxLayout(self)
        layout.addWidget(self.analog)
        layout.addWidget(self.digital)
        layout.addWidget(self.time_edit)
        layout.addWidget(add_btn)
        layout.addWidget(tone_btn)
        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.slider)
        layout.addWidget(self.list)
        layout.addWidget(del_btn)
        layout.addWidget(snooze_btn)
        layout.addWidget(stop_btn)

        # TIMER
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

        # SYSTEM TRAY
        self.tray = QSystemTrayIcon(QIcon.fromTheme("clock"))
        menu = QMenu()

        show = QAction("Show", self)
        quit = QAction("Quit", self)

        show.triggered.connect(self.show)
        quit.triggered.connect(app.quit)

        menu.addAction(show)
        menu.addAction(quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

        self.set_dark_theme()
        self.fade_in()

    # =============== ANIMATION ===============
    def fade_in(self):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    # =============== THEME ===============
    def set_dark_theme(self):
        self.setStyleSheet("""
            QWidget {background:#121212;color:white;}
            QPushButton {
                background:#1f1f1f;
                border-radius:12px;
                padding:10px;
            }
            QPushButton:hover {background:#333;}
            QListWidget,QTimeEdit {
                background:#1e1e1e;
                border-radius:10px;
                padding:6px;
            }
        """)

    # =============== TIME UPDATE ===============
    def update_time(self):
        now = QDateTime.currentDateTime()
        self.digital.setText(now.toString("dd MMM yyyy\nHH:mm:ss"))

        current = now.time().toString("HH:mm")

        for a in self.alarms:
            if a == current and a not in self.triggered:
                self.triggered.add(a)
                self.trigger_alarm()

    # =============== ALARMS ===============
    def add_alarm(self):
        t = self.time_edit.time().toString("HH:mm")
        self.alarms.append(t)
        self.list.addItem(t)

    def delete_alarm(self):
        r = self.list.currentRow()
        if r >= 0:
            self.alarms.pop(r)
            self.list.takeItem(r)

    def trigger_alarm(self):
        if self.sound.source().isEmpty():
            QMessageBox.warning(self,"No Tone","Select tone first")
            return

        self.sound.play()
        self.tray.showMessage("Alarm","Wake up!")
        QMessageBox.information(self,"Alarm","Wake up!")

    def stop_alarm(self):
        self.sound.stop()

    def snooze(self):
        self.sound.stop()
        t = QTime.currentTime().addSecs(300).toString("HH:mm")
        self.alarms.append(t)
        self.list.addItem(t)

    # =============== VOLUME ===============
    def change_volume(self,value):
        self.sound.setVolume(value/100)

    # =============== TONE PICKER ===============
    def select_tone(self):
        file,_ = QFileDialog.getOpenFileName(
            self,"Select Tone","","Audio (*.wav *.mp3)"
        )
        if file:
            self.sound.setSource(QUrl.fromLocalFile(file))

    # =============== TRAY CLOSE ===============
    def closeEvent(self,e):
        e.ignore()
        self.hide()
        self.tray.showMessage("Running","Minimized to tray")


app = QApplication(sys.argv)
window = AlarmApp()
window.show()
sys.exit(app.exec())
