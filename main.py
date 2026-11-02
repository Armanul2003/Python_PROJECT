"""Entry point: builds the Tkinter window with three tabs (Players, Match Day, Leaderboard)."""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from manager import PlayerManager
from gui_players import PlayersTab
from gui_matchday import MatchDayTab
from gui_leaderboard import LeaderboardTab

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    manager = PlayerManager(os.path.join(BASE_DIR, "data", "players.csv"))
    manager.load_all()

    root = tk.Tk()
    root.title("La Liga Player Analyzer")
    root.geometry("1120x720")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tabs = []                                  


    def refresh_all():
        for tab in tabs:
            tab.refresh()

    tabs.append(PlayersTab(notebook, manager, refresh_all))
    tabs.append(MatchDayTab(notebook, manager, refresh_all))
    tabs.append(LeaderboardTab(notebook, manager, refresh_all))
    for tab, title in zip(tabs, ("Players", "Match Day", "Leaderboard")):
        notebook.add(tab, text=title)

    def save_now():
        if manager.save_all():
            messagebox.showinfo("Saved", "Saved successfully.")
        else:
            messagebox.showerror("Save failed", "Could not save the file.")


    menu = tk.Menu(root)
    file_menu = tk.Menu(menu, tearoff=0)
    file_menu.add_command(label="Save", command=save_now)
    file_menu.add_command(label="Exit", command=root.destroy)
    menu.add_cascade(label="File", menu=file_menu)
    root.config(menu=menu)

    refresh_all()
    root.mainloop()


if __name__ == "__main__":
    main()
