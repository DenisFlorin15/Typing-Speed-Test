import tkinter as tk
import time
import random
import os
import difflib


class TypingGameEngine:
    def __init__(self):
        self.sentences = [
            "To be or not to be, that is the question.",
            "The quick brown fox jumps over the lazy dog.",
            "Python is an interpreted high-level general-purpose programming language.",
            "Coding is not just about syntax but about solving problems.",
            "A journey of a thousand miles begins with a single step.",
            "Success is stumbling from failure to failure with no loss of enthusiasm."
        ]
        self.target_text = ""
        self.start_time = 0
        self.is_running = False
        self.player_name = "Player"
        self.highscore_file = "highscore.txt"

    def set_player_name(self, name):
        if name.strip():
            self.player_name = name.strip()

    def new_round(self):
        self.target_text = random.choice(self.sentences)
        self.start_time = 0
        self.is_running = False
        return self.target_text

    def start_timer(self):
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True

    def get_highscore(self):
        if not os.path.exists(self.highscore_file):
            return ("None", 0.0, 0.0)
        try:
            with open(self.highscore_file, "r") as f:
                content = f.read().strip()
                if content:
                    parts = content.split(",")
                    if len(parts) == 3:
                        return (parts[0], float(parts[1]), float(parts[2]))
                    elif len(parts) == 2:
                        return (parts[0], float(parts[1]), 0.0)
        except:
            return ("None", 0.0, 0.0)
        return ("None", 0.0, 0.0)

    def save_highscore(self, wpm, accuracy):
        current_name, current_best_wpm, current_acc = self.get_highscore()
        if wpm > current_best_wpm or (wpm == current_best_wpm and accuracy > current_acc):
            try:
                with open(self.highscore_file, "w") as f:
                    f.write(f"{self.player_name},{wpm:.2f},{accuracy:.2f}")
                return True
            except:
                print("Error saving high score.")
        return False

    def calculate_score(self, user_text):
        if not self.is_running:
            return None

        end_time = time.time()
        time_taken = end_time - self.start_time

        minutes = time_taken / 60
        wpm = (len(user_text) / 5) / minutes if minutes > 0 else 0

        matcher = difflib.SequenceMatcher(None, self.target_text, user_text)
        accuracy = matcher.ratio() * 100

        self.is_running = False

        is_new_record = self.save_highscore(wpm, accuracy)

        return {
            "wpm": wpm,
            "accuracy": accuracy,
            "new_record": is_new_record
        }


class TypingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Typing Speed Test")
        self.geometry("800x650")  # Made window slightly taller
        self.default_bg = "#f0f0f0"
        self.configure(bg=self.default_bg)

        self.game = TypingGameEngine()

        self._create_widgets()
        self.update_highscore_label()
        self.reset_game()

    def _create_widgets(self):
        # --- Top Section ---
        top_frame = tk.Frame(self, bg=self.default_bg)
        top_frame.pack(pady=10, fill="x", padx=50)

        tk.Label(top_frame, text="Player Name:", bg=self.default_bg, font=("Arial", 10)).pack(side="left")
        self.name_entry = tk.Entry(top_frame, width=15)
        self.name_entry.pack(side="left", padx=5)
        self.name_entry.insert(0, "Player")

        self.highscore_label = tk.Label(
            top_frame, text="🏆 Record: -",
            font=("Arial", 10, "bold"), fg="#d35400", bg=self.default_bg
        )
        self.highscore_label.pack(side="right")

        # --- Game Section ---
        self.header_label = tk.Label(self, text="Typing Speed Test", font=("Helvetica", 24, "bold"), bg=self.default_bg)
        self.header_label.pack(pady=10)

        self.instruction_label = tk.Label(self, text="Type the text below and press ENTER to finish.",
                                          font=("Arial", 12), bg=self.default_bg)
        self.instruction_label.pack(pady=5)

        # TARGET TEXT
        self.sample_label = tk.Label(
            self, text="", font=("Courier", 13),
            bg="white", padx=15, pady=15, relief="solid", wraplength=700, justify="left"
        )
        self.sample_label.pack(pady=10, padx=50, fill="x")

        # INPUT TEXT BOX
        self.input_text_frame = tk.Frame(self)
        self.input_text_frame.pack(pady=10, padx=50, fill="x")

        # Scrollbar for input
        scrollbar = tk.Scrollbar(self.input_text_frame)
        scrollbar.pack(side="right", fill="y")

        # The Text Widget
        self.input_text = tk.Text(
            self.input_text_frame, height=5, font=("Courier", 13),
            yscrollcommand=scrollbar.set, wrap="word"
        )
        self.input_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.input_text.yview)

        # Bindings
        self.input_text.bind("<KeyPress>", self.handle_keypress)
        self.input_text.bind("<Return>", self.finish_game)  # Enter key to finish

        self.result_label = tk.Label(self, text="Speed: - | Accuracy: -", font=("Helvetica", 14, "bold"),
                                     bg=self.default_bg)
        self.result_label.pack(pady=15)

        self.reset_btn = tk.Button(
            self, text="Reset / New Round", command=self.reset_game,
            font=("Arial", 12), bg="#4CAF50", fg="white", padx=20, pady=5
        )
        self.reset_btn.pack(pady=10)

    def set_color(self, color):
        self.configure(bg=color)
        self.header_label.configure(bg=color)
        self.instruction_label.configure(bg=color)
        self.result_label.configure(bg=color)

    def update_highscore_label(self):
        name, score, acc = self.game.get_highscore()
        if name == "None":
            self.highscore_label.config(text="🏆 Record: None")
        else:
            self.highscore_label.config(text=f"🏆 Record: {name} - {score:.2f} WPM ({acc:.2f}% Acc)")

    def reset_game(self):
        new_text = self.game.new_round()
        self.sample_label.config(text=new_text)
        self.set_color(self.default_bg)
        self.result_label.config(text="Speed: - | Accuracy: -")

        # Unlock and Clear Text Box
        self.input_text.config(state='normal')
        self.input_text.delete("1.0", tk.END)  # '1.0' means Line 1, Char 0
        self.input_text.focus_set()
        self.update_highscore_label()

    def handle_keypress(self, event):
        current_name = self.name_entry.get()
        self.game.set_player_name(current_name)

        # Start timer if it's not a modifier key
        if event.keysym not in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Return"]:
            self.game.start_timer()

    def finish_game(self, event):
        # Retrieve text from line 1.0 to the End (minus the last newline char)
        user_text = self.input_text.get("1.0", "end-1c")

        # If empty (user just pressed enter without typing), ignore
        if not user_text.strip():
            return "break"

        results = self.game.calculate_score(user_text)

        if results:
            msg = f"Speed: {results['wpm']:.2f} WPM | Accuracy: {results['accuracy']:.2f} %"
            if results['new_record']:
                msg += " (NEW RECORD!)"
                self.update_highscore_label()

            self.result_label.config(text=msg)

            if results['accuracy'] >= 80:
                self.set_color("#90EE90")
            else:
                self.set_color("#FFB6C1")

            self.input_text.config(state='disabled')

        # Return "break" prevents the Enter key from adding a new line in the text box
        return "break"


if __name__ == "__main__":
    app = TypingApp()
    app.mainloop()