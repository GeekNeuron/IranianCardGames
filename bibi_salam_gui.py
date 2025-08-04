from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from bibi_salam_game import BibiSalamGame, Card
from audio_manager import AudioManager
import random

class BibiSalamGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_game_step)
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی بی‌بی سلام، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید بی‌بی سلام")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)

        self.card_needed_layout = QVBoxLayout()
        self.card_needed_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.card_needed_layout)
        
        self.main_layout.addStretch()

        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)
        
    def start_new_game(self):
        self.game = BibiSalamGame(num_players=4)
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.update_displays()
        self.timer.start(1200)

    def process_game_step(self):
        if self.game.is_game_over:
            self.timer.stop()
            self.status_label.setText(f"بازی تمام شد! برنده: {self.game.winner.name}")
            self.start_button.show()
            self.audio_manager.play("win")
            return

        card_needed = self.game.get_card_to_play()
        player_with_card = self.game.find_player_with_card(card_needed)

        if player_with_card == self.game.players[0]:
            self.timer.stop()
            self.play_button.show()
            self.status_label.setText("نوبت شماست! کارت را بازی کنید.")
        else:
            self.audio_manager.play("play")
            played_card_owner = self.game.play_next_card()
            self.update_displays()
            if card_needed and card_needed.rank == 'Q':
                self.handle_salam_event(played_card_owner)

    def on_play_card_clicked(self):
        self.audio_manager.play("play")
        card_needed = self.game.get_card_to_play()
        played_card_owner = self.game.play_next_card()
        self.play_button.hide()
        
        if card_needed and card_needed.rank == 'Q':
            self.handle_salam_event(played_card_owner)
        else:
            self.timer.start(1200)
            self.update_displays()

    def handle_salam_event(self, player_who_played_q):
        self.timer.stop()
        self.status_label.setText("بی‌بی سلام! سریع کلیک کن!")
        
        self.salam_button = QPushButton("سلام!")
        self.salam_button.setFixedSize(150, 150)
        self.salam_button.setStyleSheet("font-size: 30px; font-weight: bold; background-color: #ffc107; border-radius: 75px;")
        self.salam_button.clicked.connect(lambda: self.on_salam_clicked(player_who_played_q))
        self.card_needed_layout.addWidget(self.salam_button)

        QTimer.singleShot(random.randint(2000, 4000), lambda: self.salam_timeout(player_who_played_q))

    def on_salam_clicked(self, player_who_played_q):
        if not hasattr(self, 'salam_button') or self.salam_button.isHidden(): return
        
        self.status_label.setText("آفرین! شما سریع بودید.")
        self.salam_button.hide()
        self.game._handle_salam_penalty(player_who_played_q, human_was_slow=False)
        QTimer.singleShot(1500, self.update_and_resume)

    def salam_timeout(self, player_who_played_q):
        if not hasattr(self, 'salam_button') or self.salam_button.isHidden(): return

        self.status_label.setText("دیر کردی! شما جریمه شدید.")
        self.salam_button.hide()
        self.game._handle_salam_penalty(player_who_played_q, human_was_slow=True)
        QTimer.singleShot(1500, self.update_and_resume)

    def update_and_resume(self):
        self.update_displays()
        self.timer.start(1200)

    def update_displays(self):
        self.clear_layout(self.card_needed_layout)
        card_needed = self.game.get_card_to_play()
        
        if card_needed:
            card_needed_text = str(card_needed)
            player_with_card = self.game.find_player_with_card(card_needed)
            owner_name = player_with_card.name if player_with_card else "نامشخص"
            self.status_label.setText(f"کارت مورد نیاز: {card_needed_text} (در دست {owner_name})")
            
            card_needed_lbl = QLabel(card_needed_text)
            card_needed_lbl.setStyleSheet("font-size: 36px; font-weight: bold; border: 2px solid green; padding: 20px; background-color: white;")
            self.card_needed_layout.addWidget(card_needed_lbl, 0, Qt.AlignCenter)
            
            self.play_button = QPushButton("بازی کن")
            self.play_button.clicked.connect(self.on_play_card_clicked)
            self.play_button.hide()
            self.card_needed_layout.addWidget(self.play_button, 0, Qt.AlignCenter)

        self.clear_layout(self.player_hand_layout)
        player = self.game.players[0]
        for card in sorted(player.hand, key=lambda c: (c.suit, RANK_VALUES[c.rank])):
            lbl = QLabel()
            pixmap = QIcon(f"resources/images/themes/default/cards/{card.image_filename}").pixmap(QSize(60, 88))
            lbl.setPixmap(pixmap)
            self.player_hand_layout.addWidget(lbl)
            
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
