import tkinter as tk
from tkinter import messagebox, ttk
import json
from pathlib import Path


class AdminPanel:
    BG = '#0b0f12'
    BLUE = '#1e90ff'
    WHITE = '#ffffff'
    GRAY = '#1a1e23'
    GREEN = '#2ecc71'
    RED = '#e74c3c'
    ORANGE = '#f39c12'

    def __init__(self, root, username, auth_service):
        self.root = root
        self.username = username
        self.auth_service = auth_service
        
        self.root.title(f'Admin Panel - {username}')
        self.root.configure(bg=self.BG)
        self.root.geometry('900x600')
        self.root.resizable(True, True)
        
        # Create menu bar
        menubar = tk.Menu(self.root, bg=self.GRAY, fg=self.WHITE, activebackground=self.BLUE)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, bg=self.GRAY, fg=self.WHITE, activebackground=self.BLUE)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Logout", command=self._on_logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Header
        header = tk.Frame(self.root, bg=self.ORANGE)
        header.pack(fill='x', padx=0, pady=0)
        
        title = tk.Label(header, text=f'Admin Panel - {username}', fg=self.BG, bg=self.ORANGE,
                        font=('Segoe UI', 14, 'bold'))
        title.pack(pady=10, padx=20, side='left')
        
        # Main container
        container = tk.Frame(self.root, bg=self.BG)
        container.pack(expand=True, fill='both', padx=15, pady=15)
        
        # Section title
        section_title = tk.Label(container, text='User Management', fg=self.WHITE, bg=self.BG,
                                font=('Segoe UI', 12, 'bold'))
        section_title.pack(anchor='w', pady=(0, 10))
        
        # Buttons frame
        btn_frame = tk.Frame(container, bg=self.BG)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        add_btn = tk.Button(btn_frame, text='+ Create User', bg=self.GREEN, fg=self.BG,
                           font=('Segoe UI', 10, 'bold'), relief='flat',
                           command=self._show_create_user)
        add_btn.pack(side='left', padx=(0, 5), ipady=5, ipadx=10)
        
        refresh_btn = tk.Button(btn_frame, text='Refresh', bg=self.BLUE, fg=self.BG,
                               font=('Segoe UI', 10, 'bold'), relief='flat',
                               command=self._load_users)
        refresh_btn.pack(side='left', padx=(0, 5), ipady=5, ipadx=10)
        
        export_btn = tk.Button(btn_frame, text='Export Users', bg=self.BLUE, fg=self.BG,
                              font=('Segoe UI', 10, 'bold'), relief='flat',
                              command=self._export_users)
        export_btn.pack(side='left', ipady=5, ipadx=10)
        
        # Treeview for users
        tree_frame = tk.Frame(container, bg=self.GRAY)
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(tree_frame, columns=('Username', 'Role', 'Status'), 
                                 height=20, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('Username', anchor='w', width=250)
        self.tree.column('Role', anchor='center', width=150)
        self.tree.column('Status', anchor='center', width=150)
        
        self.tree.heading('#0', text='', anchor='w')
        self.tree.heading('Username', text='Username', anchor='w')
        self.tree.heading('Role', text='Role', anchor='center')
        self.tree.heading('Status', text='Status', anchor='center')
        
        # Configure treeview style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=self.GRAY, foreground=self.WHITE,
                       fieldbackground=self.GRAY, borderwidth=0)
        style.map('Treeview', background=[('selected', self.BLUE)])
        style.configure('Treeview.Heading', background=self.GRAY, foreground=self.BLUE,
                       borderwidth=1)
        style.map('Treeview.Heading', background=[('active', self.GRAY)])
        
        self.tree.pack(fill='both', expand=True)
        
        # Actions frame
        actions_frame = tk.Frame(container, bg=self.BG)
        actions_frame.pack(fill='x')
        
        promote_btn = tk.Button(actions_frame, text='Make Admin', bg=self.ORANGE, fg=self.BG,
                               font=('Segoe UI', 9, 'bold'), relief='flat',
                               command=self._on_promote)
        promote_btn.pack(side='left', padx=(0, 5), ipady=4, ipadx=8)
        
        demote_btn = tk.Button(actions_frame, text='Demote Admin', bg=self.ORANGE, fg=self.BG,
                              font=('Segoe UI', 9, 'bold'), relief='flat',
                              command=self._on_demote)
        demote_btn.pack(side='left', padx=(0, 5), ipady=4, ipadx=8)
        
        reset_btn = tk.Button(actions_frame, text='Reset Password', bg=self.BLUE, fg=self.BG,
                             font=('Segoe UI', 9, 'bold'), relief='flat',
                             command=self._on_reset_password)
        reset_btn.pack(side='left', padx=(0, 5), ipady=4, ipadx=8)
        
        delete_btn = tk.Button(actions_frame, text='Delete User', bg=self.RED, fg=self.WHITE,
                              font=('Segoe UI', 9, 'bold'), relief='flat',
                              command=self._on_delete)
        delete_btn.pack(side='left', ipady=4, ipadx=8)
        
        # Load users (marque les utilisateurs actuels comme "deja vus", pas de notif au demarrage)
        self._load_users(notify=False)

        # Verifie periodiquement l'arrivee de nouveaux utilisateurs
        self.root.after(5000, self._poll_new_users)

    def _seen_users_path(self):
        return Path(__file__).resolve().parents[1] / "database" / "seen_users.json"

    def _load_seen_users(self):
        """Charge la liste des utilisateurs deja notifies"""
        path = self._seen_users_path()
        if not path.exists():
            return set()
        try:
            return set(json.loads(path.read_text(encoding='utf-8')))
        except Exception:
            return set()

    def _save_seen_users(self, seen):
        self._seen_users_path().write_text(
            json.dumps(sorted(seen), indent=2), encoding='utf-8'
        )

    def _poll_new_users(self):
        """Rappelle _load_users toutes les 5s tant que le panneau est ouvert"""
        if self.root.winfo_exists():
            self._load_users(notify=True)
            self.root.after(5000, self._poll_new_users)

    def _load_users(self, notify=True):
        """Load users from JSON file"""
        self.tree.delete(*self.tree.get_children())
        
        users_path = Path(__file__).resolve().parents[1] / "database" / "users.json"
        admins = self.auth_service._load_admins()
        
        try:
            if users_path.exists():
                users = json.loads(users_path.read_text(encoding='utf-8'))
                current_usernames = set(users.keys())
                seen = self._load_seen_users()
                new_users = current_usernames - seen

                if notify and new_users:
                    messagebox.showinfo(
                        "Nouvel utilisateur",
                        "Nouvelle(s) inscription(s) detectee(s) :\n" + "\n".join(sorted(new_users))
                    )

                self.tree.tag_configure('new', foreground=self.ORANGE)

                for username in sorted(users.keys()):
                    is_admin = username in admins
                    role = 'Admin' if is_admin else 'User'
                    status = 'Nouveau' if username in new_users else 'Active'
                    tag = 'new' if username in new_users else ''

                    self.tree.insert('', 'end', values=(username, role, status), tags=(tag,))

                # Une fois affiches/notifies, on les marque comme vus
                self._save_seen_users(current_usernames)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {e}")
    
    def _show_create_user(self):
        """Show create user dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title('Create New User')
        dialog.configure(bg=self.BG)
        dialog.geometry('350x250')
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Username
        tk.Label(dialog, text='Username:', fg=self.WHITE, bg=self.BG, 
                font=('Segoe UI', 10)).pack(anchor='w', padx=15, pady=(15, 0))
        username_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE)
        username_entry.pack(fill='x', padx=15, pady=(0, 10))
        username_entry.focus()
        
        # Password
        tk.Label(dialog, text='Password (leave empty for auto-generate):', fg=self.WHITE, bg=self.BG,
                font=('Segoe UI', 10)).pack(anchor='w', padx=15, pady=(0, 0))
        pwd_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE, show='*')
        pwd_entry.pack(fill='x', padx=15, pady=(0, 10))
        
        # Make Admin checkbox
        is_admin_var = tk.BooleanVar(value=False)
        admin_check = tk.Checkbutton(dialog, text='Create as Admin', variable=is_admin_var,
                                    bg=self.BG, fg=self.WHITE, selectcolor=self.BG,
                                    activebackground=self.BG, activeforeground=self.WHITE)
        admin_check.pack(anchor='w', padx=15, pady=(0, 15))
        
        def create_user():
            username = username_entry.get().strip()
            password = pwd_entry.get() if pwd_entry.get() else None
            is_admin = is_admin_var.get()
            
            if not username:
                messagebox.showwarning("Validation", "Username is required")
                return
            
            try:
                # Register user
                if not self.auth_service.register_user(username, password):
                    messagebox.showerror("Error", "Username already exists")
                    return
                
                # Make admin if selected
                if is_admin:
                    admins_path = Path(__file__).resolve().parents[1] / "database" / "admins.json"
                    admins = json.loads(admins_path.read_text(encoding='utf-8'))
                    if username not in admins:
                        admins.append(username)
                        admins_path.write_text(json.dumps(admins, indent=2), encoding='utf-8')
                
                # Show generated password if auto-generated
                msg = f"User '{username}' created successfully!"
                if self.auth_service.last_generated_password:
                    msg += f"\n\nGenerated Password:\n{self.auth_service.last_generated_password}\n\nPlease share this with the user."
                
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self._load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create user: {e}")
        
        btn_frame = tk.Frame(dialog, bg=self.BG)
        btn_frame.pack(fill='x', padx=15, pady=(10, 15))
        
        create_btn = tk.Button(btn_frame, text='Create', bg=self.GREEN, fg=self.BG,
                              relief='flat', command=create_user)
        create_btn.pack(side='left', padx=(0, 5), ipady=5, ipadx=15)
        
        cancel_btn = tk.Button(btn_frame, text='Cancel', bg=self.GRAY, fg=self.WHITE,
                              relief='flat', command=dialog.destroy)
        cancel_btn.pack(side='left', ipady=5, ipadx=15)
    
    def _on_promote(self):
        """Promote user to admin"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Selection", "Please select a user to promote")
            return
        
        values = self.tree.item(item, 'values')
        username = values[0]
        
        if username == self.username:
            messagebox.showwarning("Error", "You cannot change your own role")
            return
        
        if values[1] == 'Admin':
            messagebox.showinfo("Info", "User is already an admin")
            return
        
        try:
            admins_path = Path(__file__).resolve().parents[1] / "database" / "admins.json"
            admins = json.loads(admins_path.read_text(encoding='utf-8'))
            
            if username not in admins:
                admins.append(username)
                admins_path.write_text(json.dumps(admins, indent=2), encoding='utf-8')
                messagebox.showinfo("Success", f"{username} is now an admin")
                self._load_users()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to promote user: {e}")
    
    def _on_demote(self):
        """Demote admin to user"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Selection", "Please select an admin to demote")
            return
        
        values = self.tree.item(item, 'values')
        username = values[0]
        
        if username == self.username:
            messagebox.showwarning("Error", "You cannot change your own role")
            return
        
        if values[1] == 'User':
            messagebox.showinfo("Info", "User is not an admin")
            return
        
        if messagebox.askyesno("Confirm", f"Demote {username} from admin?"):
            try:
                admins_path = Path(__file__).resolve().parents[1] / "database" / "admins.json"
                admins = json.loads(admins_path.read_text(encoding='utf-8'))
                
                if username in admins:
                    admins.remove(username)
                    admins_path.write_text(json.dumps(admins, indent=2), encoding='utf-8')
                    messagebox.showinfo("Success", f"{username} is no longer an admin")
                    self._load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to demote user: {e}")
    
    def _on_reset_password(self):
        """Reset user password"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Selection", "Please select a user")
            return
        
        values = self.tree.item(item, 'values')
        username = values[0]
        
        if messagebox.askyesno("Confirm", f"Reset password for {username}?"):
            try:
                new_password = self.auth_service.generate_password()
                users_path = Path(__file__).resolve().parents[1] / "database" / "users.json"
                users = json.loads(users_path.read_text(encoding='utf-8'))
                
                users[username] = self.auth_service._hash_password(new_password)
                users_path.write_text(json.dumps(users, indent=2), encoding='utf-8')
                
                messagebox.showinfo("Success", f"New password for {username}:\n\n{new_password}")
                self._load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset password: {e}")
    
    def _on_delete(self):
        """Delete user"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Selection", "Please select a user to delete")
            return
        
        values = self.tree.item(item, 'values')
        username = values[0]
        
        if username == self.username:
            messagebox.showerror("Error", "You cannot delete your own account")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete user '{username}' and all associated data? This action cannot be undone."):
            try:
                # Delete from users
                users_path = Path(__file__).resolve().parents[1] / "database" / "users.json"
                users = json.loads(users_path.read_text(encoding='utf-8'))
                
                if username in users:
                    del users[username]
                    users_path.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding='utf-8')
                
                # Remove from admins if admin
                admins_path = Path(__file__).resolve().parents[1] / "database" / "admins.json"
                admins = json.loads(admins_path.read_text(encoding='utf-8'))
                if username in admins:
                    admins.remove(username)
                    admins_path.write_text(json.dumps(admins, indent=2), encoding='utf-8')
                
                # Delete user's passwords
                passwords_path = Path(__file__).resolve().parents[1] / "database" / "passwords.json"
                if passwords_path.exists():
                    passwords = json.loads(passwords_path.read_text(encoding='utf-8'))
                    if username in passwords:
                        del passwords[username]
                        passwords_path.write_text(json.dumps(passwords, indent=2, ensure_ascii=False), encoding='utf-8')
                
                messagebox.showinfo("Success", f"User '{username}' and all associated data have been deleted successfully")
                self._load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {e}")
    
    def _export_users(self):
        """Export users list to text file"""
        try:
            users_path = Path(__file__).resolve().parents[1] / "database" / "users.json"
            admins = self.auth_service._load_admins()
            users = json.loads(users_path.read_text(encoding='utf-8'))
            
            export_path = Path(__file__).resolve().parents[1] / "database" / "users_export.txt"
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write("USER LIST EXPORT\n")
                f.write("=" * 50 + "\n\n")
                
                for username in sorted(users.keys()):
                    role = "Admin" if username in admins else "User"
                    f.write(f"Username: {username}\n")
                    f.write(f"Role: {role}\n")
                    f.write("-" * 30 + "\n\n")
            
            messagebox.showinfo("Success", f"Users exported to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export users: {e}")
    
    def _on_logout(self):
        """Logout and return to login"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
