import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QFontDatabase, QFont

# وارد کردن ویجت‌های نهایی و کامل همه بازی‌ها
from hokm_gui import HokmGameWidget
from shelem_gui import ShelemGameWidget
from chahar_barg_gui import ChaharBargGameWidget
from haft_khaj_gui import HaftKhajGameWidget
from rummy_gui import RummyGameWidget
from bibi_salam_gui import BibiSalamGameWidget
from bluff_gui import BluffGameWidget
from haft_o_nim_gui import HaftONimGameWidget
from bidel_gui import BidelGameWidget
from nakhoda_gui import NakhodaGameWidget
from chos_e_fil_gui import ChosEFilGameWidget
from ganjifeh_gui import GanjifehGameWidget
from amerikaii_gui import AmerikaiiGameWidget

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("مجموعه بازی‌های کارتی ایرانی")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet("""
            QMainWindow {
                border-image: url(resources/images/themes/default/background.jpg) 0 0 0 0 stretch stretch;
            }
            QTabWidget::pane {
                border-top: 2px solid #C2C7CB;
                background: rgba(255, 255, 255, 0.85); /* نیمه شفاف */
            } 
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                            stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                border: 1px solid #C4C4C3;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                color: #333;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                            stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
                color: #000;
            }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- افزودن تمام زبانه‌ها ---
        self.tabs.addTab(HokmGameWidget(), "حکم (Hokm)")
        self.tabs.addTab(ShelemGameWidget(), "شلم (Shelem)")
        self.tabs.addTab(ChaharBargGameWidget(), "چهاربرگ (Chahar Barg)")
        self.tabs.addTab(HaftKhajGameWidget(), "هفت خاج (Haft Khaj)")
        self.tabs.addTab(RummyGameWidget(), "ریم (Rummy)")
        self.tabs.addTab(BibiSalamGameWidget(), "بی‌بی سلام (Bibi Salam)")
        self.tabs.addTab(BluffGameWidget(), "بلوف (Bluff)")
        self.tabs.addTab(HaftONimGameWidget(), "هفت و نیم (Haft-o-Nim)")
        self.tabs.addTab(BidelGameWidget(), "بیدل (Bidel)")
        self.tabs.addTab(NakhodaGameWidget(), "ناخدا (Nakhoda)")
        self.tabs.addTab(ChosEFilGameWidget(), "چُس فیل (Chos-e Fil)")
        self.tabs.addTab(GanjifehGameWidget(), "گنجفه (Ganjifeh)")
        self.tabs.addTab(AmerikaiiGameWidget(), "آمریکایی (Amerikaii)")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # افزودن فونت سفارشی
    font_path = "resources/fonts/Vazirmatn-Regular.ttf"
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        vazir_font = QFont(font_family, 10)
        app.setFont(vazir_font)
        print(f"فونت '{font_family}' با موفقیت بارگذاری و اعمال شد.")
    else:
        print(f"هشدار: فایل فونت در مسیر '{font_path}' پیدا نشد. از فونت پیش‌فرض استفاده می‌شود.")
        
    window = MainAppWindow()
    window.show()
    sys.exit(app.exec_())
