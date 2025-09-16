import random
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtCore import QObject, QEvent, Qt
import sys
import time
import os
from tqdm import tqdm
from collections import defaultdict

app = QApplication(sys.argv)

class Word:
    instances = {}  # dict: word -> Word object

    def __init__(self, name):
        self.name = name
        self.next_words = defaultdict(int)

    def add_next_word(self, word):
        self.next_words[word] += 1

    @classmethod
    def add_word(cls, name):
        if name not in cls.instances:
            cls.instances[name] = Word(name)
        return cls.instances[name]

    @classmethod
    def predict(cls, current_word):
        if current_word in cls.instances:
            instance = cls.instances[current_word]
            words = list(instance.next_words.keys())
            counts = list(instance.next_words.values())
            if words:
                return random.choices(words, weights=counts, k=1)[0]
        return ""




def process_file(file_path):
    # Count lines first (for progress bar)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        total_lines = sum(1 for _ in f)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in tqdm(f, total=total_lines, desc=f"Processing {os.path.basename(file_path)}"):
            f_words = line.strip().split()

            # loop in pairs: (word, next_word)
            for prev, curr in zip(f_words, f_words[1:]):
                prev = prev.strip()
                curr = curr.strip()

                # get or create word
                prev_word = Word.add_word(prev)

                # record connection
                prev_word.add_next_word(curr)


def process_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt") or file_name.endswith(".csv"):
            process_file(os.path.join(folder_path, file_name))

class KeyFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                print("TAB pressed!")
                update_text()
                return True
        return False

def on_text_changed():
    plain = input_box.toPlainText()

    if plain.endswith(" "):
        return

    pred_box.setText(plain)
    t_words = plain.split(" ")

    if len(t_words) > 0:
        next_word = Word.predict(t_words[-1])
        if next_word.strip() != "":
            pred_box.setPlainText(plain + " " + next_word)
            pred_word = next_word

   
def update_text():
    plain = pred_box.toPlainText()
    input_box.setPlainText(plain)
    cursor = input_box.textCursor()
    cursor.movePosition(QTextCursor.End)
    input_box.setTextCursor(cursor)


if __name__ == "__main__":
    # folder = "Harry_Potter"
    folder = "Sentences"
    process_folder(folder)

    print(f"\nTotal unique words: {len(Word.instances)}")


    window = QWidget()
    window.setWindowTitle("Word Predictor")
    window.setFixedSize(600, 200)  


    # User input
    input_box = QTextEdit(window)
    input_box.setGeometry(50, 50, 500, 100)
    input_box.setStyleSheet("background: transparent; color: white; font-size: 16px;")
    input_box.textChanged.connect(on_text_changed)
    filter_instance = KeyFilter()
    input_box.installEventFilter(filter_instance)

    # Bottom box: prediction + user text (ghost effect)
    pred_box = QTextEdit(window)
    pred_box.setGeometry(50, 50, 500, 100)
    pred_box.setReadOnly(True)
    pred_box.setStyleSheet("color: gray; font-size: 16px;")
    pred_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    pred_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # Make background transparent so user text shows clearly
    # palette = input_box.palette()
    # palette.setColor(input_box.backgroundRole(), QColor(0,0,0,0))
    # input_box.setPalette(palette)

    palette = pred_box.palette()
    palette.setColor(pred_box.backgroundRole(), QColor(0,0,0,0))
    pred_box.setPalette(palette)

    input_box.raise_()

    pred_box.setPlainText("Hello world (prediction)")

    # Show window
    window.show()
    # Run app
    sys.exit(app.exec_())
