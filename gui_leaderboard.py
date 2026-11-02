"""Leaderboard tab: ranked players by position with projected stats and summary."""
import tkinter as tk
from tkinter import ttk
from models import POSITIONS


class LeaderboardTab(ttk.Frame):

    def __init__(self, parent, manager, on_change):
        super().__init__(parent, padding=10)
        self.manager = manager
        self.on_change = on_change

        self.position_var = tk.StringVar(value="FWD")
        self.summary_var = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(top_frame, text="Position:").pack(side="left", padx=(0, 4))
        pos_combo = ttk.Combobox(
            top_frame, textvariable=self.position_var, values=POSITIONS, state="readonly", width=10
        )
        pos_combo.pack(side="left", padx=4)
        pos_combo.bind("<<ComboboxSelected>>", self.on_show)
        ttk.Button(top_frame, text="Show", command=self.on_show).pack(side="left", padx=4)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, pady=(0, 8))

        columns = ("rank", "name", "team", "appearances", "projected", "score")
        headings = ("Rank", "Player", "Team", "Apps", "Projected 38-match stats", "Score")
        widths = (60, 160, 150, 60, 520, 90)

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, title, width in zip(columns, headings, widths):
            self.tree.heading(col, text=title)
            anchor = "w" if col == "projected" else "center"
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(self, textvariable=self.summary_var, font=("TkDefaultFont", 10, "bold")).pack(anchor="w")

    # Reload the widgets from the manager data
    def refresh(self):
        position = self.position_var.get()
        if position not in POSITIONS:
            position = "FWD"
            self.position_var.set(position)

        rows = self.manager.get_leaderboard(position)
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=(
                row["rank"], row["name"], row["team"], row["appearances"],
                row["projected"], row["score"]))

        s = self.manager.get_summary(position)
        self.summary_var.set(
            f"{position} summary | Qualified players: {s['count']} | "
            f"Average: {s['average']} | Highest: {s['highest']} | Lowest: {s['lowest']}")

    def on_show(self, event=None):
        self.refresh()
