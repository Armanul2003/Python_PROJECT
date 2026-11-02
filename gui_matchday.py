"""Match Day tab: pick a player and enter one match of statistics."""
import tkinter as tk
from tkinter import ttk, messagebox
from models import STAT_FIELDS


class MatchDayTab(ttk.Frame):
    
    def __init__(self, parent, manager, on_change):
        super().__init__(parent, padding=10)
        self.manager = manager
        self.on_change = on_change

        self.player_var = tk.StringVar()
        self.info_var = tk.StringVar(value="Select a player to see current appearances.")
        self.stat_vars = {}
        for field in STAT_FIELDS:
            self.stat_vars[field] = tk.StringVar(value="0")

        self.build_ui()

    def build_ui(self):
        top_frame = ttk.LabelFrame(self, text="Select Player", padding=8)
        top_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(top_frame, text="Player:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.player_combo = ttk.Combobox(
            top_frame, textvariable=self.player_var, values=self.manager.get_player_labels(), state="readonly", width=34
        )
        self.player_combo.grid(row=0, column=1, sticky="w", padx=4, pady=4)
        self.player_combo.bind("<<ComboboxSelected>>", self.on_player_selected)

        ttk.Label(top_frame, textvariable=self.info_var).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=4, pady=4
        )

        stats_frame = ttk.LabelFrame(self, text="Enter Match Day Stats (counts as 1 appearance)", padding=8)
        stats_frame.pack(fill="x", pady=(0, 10))

        for row_index, field in enumerate(STAT_FIELDS):
            label_text = field.replace("_", " ").title() + ":"
            ttk.Label(stats_frame, text=label_text).grid(row=row_index, column=0, sticky="w", padx=6, pady=4)
            ttk.Entry(stats_frame, textvariable=self.stat_vars[field], width=10).grid(
                row=row_index, column=1, sticky="w", padx=6, pady=4
            )

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Add Match Day Stats", command=self.on_add).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Reset Stats to 0", command=self.clear_stats).pack(side="left", padx=4)


    # Reload the widgets from the manager data
    def refresh(self):
        labels = self.manager.get_player_labels()
        self.player_combo["values"] = labels
        current = self.player_var.get()
        if current not in labels:
            self.player_var.set("")
            self.info_var.set("Select a player to see current appearances.")
        else:
            self.on_player_selected()


    def on_player_selected(self, event=None):
        selected_text = self.player_var.get()
        if not selected_text:
            return
        player_id = selected_text.split(" | ")[0]
        player = self.manager.find_player(player_id)
        if player is not None:
            self.info_var.set(
                f"{player.name} | {player.team} | {player.position} | Appearances: {player.appearances}"
            )


    # Add Match Day Stats handler
    def on_add(self):
        selected_text = self.player_var.get()
        if not selected_text:
            messagebox.showerror("No player", "Please select a player")
            return
        player_id = selected_text.split(" | ")[0]
        try:
            stat_texts = {field: var.get() for field, var in self.stat_vars.items()}
            self.manager.add_matchday_stats(player_id, stat_texts)
            messagebox.showinfo("Saved", "Match day stats added")
            self.clear_stats()
            self.on_player_selected()
            self.on_change()
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))

    def clear_stats(self):
        for field in STAT_FIELDS:
            self.stat_vars[field].set("0")
