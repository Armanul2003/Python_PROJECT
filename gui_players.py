"""Players tab: create form with live ID preview, search/filter, table and delete."""
import tkinter as tk
from tkinter import ttk, messagebox
from models import POSITIONS


class PlayersTab(ttk.Frame):
    def __init__(self, parent, manager, on_change):
        super().__init__(parent, padding=10)
        self.manager = manager
        self.on_change = on_change

        self.name_var = tk.StringVar()
        self.team_var = tk.StringVar()
        self.jersey_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.id_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")

        self.build_form()
        self.build_table()

    def build_form(self):
        form_frame = ttk.LabelFrame(self, text="Create Player", padding=8)
        form_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(form_frame, text="Player Name:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form_frame, textvariable=self.name_var, width=22).grid(row=0, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(form_frame, text="Team:").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        self.team_combo = ttk.Combobox(
            form_frame, textvariable=self.team_var, values=self.manager.get_team_names(), state="readonly", width=20
        )
        self.team_combo.grid(row=0, column=3, sticky="w", padx=4, pady=4)
        self.team_combo.bind("<<ComboboxSelected>>", self.update_id_preview)

        ttk.Label(form_frame, text="Jersey (1-99):").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form_frame, textvariable=self.jersey_var, width=10).grid(row=1, column=1, sticky="w", padx=4, pady=4)
        self.jersey_var.trace_add("write", self.update_id_preview)

        ttk.Label(form_frame, text="Position:").grid(row=1, column=2, sticky="w", padx=4, pady=4)
        self.pos_combo = ttk.Combobox(
            form_frame, textvariable=self.position_var, values=POSITIONS, state="readonly", width=10
        )
        self.pos_combo.grid(row=1, column=3, sticky="w", padx=4, pady=4)

        ttk.Label(form_frame, text="Generated ID:").grid(row=1, column=4, sticky="w", padx=4, pady=4)
        ttk.Entry(form_frame, textvariable=self.id_var, state="readonly", width=12).grid(
            row=1, column=5, sticky="w", padx=4, pady=4
        )

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=6, sticky="w", pady=(6, 2))
        ttk.Button(btn_frame, text="Create", command=self.on_create).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Delete", command=self.on_delete).pack(side="left", padx=4)

        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(search_frame, text="Search (ID / Name / Team):").pack(side="left", padx=(0, 4))
        ttk.Entry(search_frame, textvariable=self.search_var, width=24).pack(side="left", padx=4)
        ttk.Label(search_frame, text="Position Filter:").pack(side="left", padx=(8, 4))
        ttk.Combobox(
            search_frame, textvariable=self.filter_var, values=("All",) + POSITIONS, state="readonly", width=8
        ).pack(side="left", padx=4)
        ttk.Button(search_frame, text="Search", command=self.on_search).pack(side="left", padx=4)
        ttk.Button(search_frame, text="Refresh", command=self.on_show_all).pack(side="left", padx=4)


    def build_table(self):
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        columns = ("player_id", "name", "team", "jersey", "position", "appearances")
        headings = ("Player ID", "Name", "Team", "Jersey", "Position", "Appearances")
        widths = (100, 180, 170, 80, 90, 110)

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, title, width in zip(columns, headings, widths):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # Recompute the live Generated ID
    def update_id_preview(self, *args):
        preview = self.manager.preview_player_id(self.team_var.get(), self.jersey_var.get())
        self.id_var.set(preview)

    # Clear and refill the Treeview rows
    def fill_table(self, player_list):
        self.tree.delete(*self.tree.get_children())
        for player in player_list:
            self.tree.insert(
                "",
                "end",
                values=(
                    player.player_id,
                    player.name,
                    player.team,
                    player.jersey,
                    player.position,
                    player.appearances,
                ),
            )


    # Reload the widgets from the manager data
    def refresh(self):
        self.fill_table(self.manager.get_all_players())


    # Create button handler: errors are shown in a message box, not raised
    def on_create(self):
        try:
            player = self.manager.create_player(
                self.name_var.get(),
                self.team_var.get(),
                self.jersey_var.get(),
                self.position_var.get(),
            )
            messagebox.showinfo("Success", f"Player created with ID {player.player_id}")
            self.clear_form()
            self.on_change()
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))

    # Delete button handler: needs a selected row and a confirmation
    def on_delete(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("No selection", "Please select a player in the table to delete")
            return
        values = self.tree.item(selected, "values")
        if not values:
            messagebox.showerror("No selection", "Please select a player in the table to delete")
            return
        player_id = values[0]
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete player {player_id}?"):
            return
        try:
            self.manager.delete_player(player_id)
            messagebox.showinfo("Deleted", f"Player {player_id} was deleted")
            self.on_change()
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))

    # Search button handler
    def on_search(self):
        results = self.manager.search_players(self.search_var.get(), self.filter_var.get())
        self.fill_table(results)
        if len(results) == 0:
            messagebox.showinfo("Search", "No players found")


    def on_show_all(self):
        self.search_var.set("")
        self.filter_var.set("All")
        self.refresh()


    def clear_form(self):
        self.name_var.set("")
        self.team_var.set("")
        self.jersey_var.set("")
        self.position_var.set("")
        self.id_var.set("")
