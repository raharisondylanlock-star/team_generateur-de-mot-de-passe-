import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
from pathlib import Path


class UserDashboard:
    BG = '#0b0f12'
    BLUE = '#1e90ff'
    WHITE = '#ffffff'
    GRAY = '#1a1e23'
    GREEN = '#2ecc71'
    RED = '#e74c3c'

    def __init__(self, root, username, auth_service, password_service):
        self.root = root
        self.username = username
        self.auth_service = auth_service
        self.password_service = password_service
        
        self.root.title(f'my social - {username}')
        self.root.configure(bg=self.BG)
        self.root.geometry('700x500')
        self.root.resizable(True, True)
        
        # Create menu bar
        menubar = tk.Menu(self.root, bg=self.GRAY, fg=self.WHITE, activebackground=self.BLUE)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, bg=self.GRAY, fg=self.WHITE, activebackground=self.BLUE)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Change Password", command=self._show_change_password)
        file_menu.add_command(label="Logout", command=self._on_logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Header
        header = tk.Frame(self.root, bg=self.BLUE)
        header.pack(fill='x', padx=0, pady=0)
        
        title = tk.Label(header, text=f'Welcome, {username}!', fg=self.BG, bg=self.BLUE,
                        font=('Segoe UI', 14, 'bold'))
        title.pack(pady=10, padx=20, side='left')
        
        # Main container
        container = tk.Frame(self.root, bg=self.BG)
        container.pack(expand=True, fill='both', padx=15, pady=15)
        
        # Section title
        section_title = tk.Label(container, text='Your Passwords', fg=self.WHITE, bg=self.BG,
                                font=('Segoe UI', 12, 'bold'))
        section_title.pack(anchor='w', pady=(0, 10))
        
        # Buttons frame
        btn_frame = tk.Frame(container, bg=self.BG)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        add_btn = tk.Button(btn_frame, text='+ Add Password', bg=self.GREEN, fg=self.BG,
                           font=('Segoe UI', 10, 'bold'), relief='flat',
                           command=self._show_add_password)
        add_btn.pack(side='left', padx=(0, 5), ipady=5, ipadx=10)
        
        refresh_btn = tk.Button(btn_frame, text='Refresh', bg=self.BLUE, fg=self.BG,
                               font=('Segoe UI', 10, 'bold'), relief='flat',
                               command=self._load_passwords)
        refresh_btn.pack(side='left', ipady=5, ipadx=10)
        
        # Treeview for passwords
        tree_frame = tk.Frame(container, bg=self.GRAY)
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(tree_frame, columns=('Website', 'Username', 'Password'), 
                                 height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('Website', anchor='w', width=200)
        self.tree.column('Username', anchor='w', width=150)
        self.tree.column('Password', anchor='w', width=150)
        
        self.tree.heading('#0', text='', anchor='w')
        self.tree.heading('Website', text='Website', anchor='w')
        self.tree.heading('Username', text='Username', anchor='w')
        self.tree.heading('Password', text='Password (Click to show)', anchor='w')
        
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
        self.tree.bind('<Double-1>', self._on_item_double_click)
        
        # Actions frame
        actions_frame = tk.Frame(container, bg=self.BG)
        actions_frame.pack(fill='x')
        
        change_btn = tk.Button(actions_frame, text='Change Password', bg='#f59e0b', fg=self.BG,
                                font=('Segoe UI', 9, 'bold'), relief='flat',
                                command=self._show_change_password)
        change_btn.pack(side='left', padx=(0, 5), ipady=4, ipadx=8)
        
        edit_btn = tk.Button(actions_frame, text='Edit', bg=self.BLUE, fg=self.BG,
                            font=('Segoe UI', 9, 'bold'), relief='flat',
                            command=self._on_edit)
        edit_btn.pack(side='left', padx=(0, 5), ipady=4, ipadx=8)
        
        delete_btn = tk.Button(actions_frame, text='Delete', bg=self.RED, fg=self.WHITE,
                              font=('Segoe UI', 9, 'bold'), relief='flat',
                              command=self._on_delete)
        delete_btn.pack(side='left', ipady=4, ipadx=8)
        
        # Load passwords
        self._load_passwords()
    
    def _load_passwords(self):
        """Load passwords from JSON file"""
        self.tree.delete(*self.tree.get_children())
        
        passwords_path = Path(__file__).resolve().parents[1] / "database" / "passwords.json"
        try:
            if passwords_path.exists():
                data = json.loads(passwords_path.read_text(encoding='utf-8'))
                user_passwords = data.get(self.username, {})
                
                for site, creds in user_passwords.items():
                    username = creds.get('username', '')
                    password = '••••••••' if creds.get('password') else ''
                    self.tree.insert('', 'end', values=(site, username, password))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load passwords: {e}")
    
    def _show_add_password(self):
        """Show add password dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title('Add Password')
        dialog.configure(bg=self.BG)
        dialog.geometry('400x250')
        dialog.resizable(False, False)
        
        # Website
        tk.Label(dialog, text='Website:', fg=self.WHITE, bg=self.BG).pack(anchor='w', padx=15, pady=(15, 0))
        website_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE)
        website_entry.pack(fill='x', padx=15, pady=(0, 10))
        website_entry.focus()
        
        # Username
        tk.Label(dialog, text='Username:', fg=self.WHITE, bg=self.BG).pack(anchor='w', padx=15, pady=(0, 0))
        username_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE)
        username_entry.pack(fill='x', padx=15, pady=(0, 10))
        
        # Password
        tk.Label(dialog, text='Password:', fg=self.WHITE, bg=self.BG).pack(anchor='w', padx=15, pady=(0, 0))
        pwd_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE)
        pwd_entry.pack(fill='x', padx=15, pady=(0, 15))
        
        def save_password():
            website = website_entry.get().strip()
            username = username_entry.get().strip()
            password = pwd_entry.get()
            
            if not website or not username or not password:
                messagebox.showwarning("Validation", "All fields are required")
                return
            
            try:
                passwords_path = Path(__file__).resolve().parents[1] / "database" / "passwords.json"
                data = {}
                if passwords_path.exists():
                    data = json.loads(passwords_path.read_text(encoding='utf-8'))
                
                if self.username not in data:
                    data[self.username] = {}
                
                data[self.username][website] = {
                    'username': username,
                    'password': password
                }
                
                passwords_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
                messagebox.showinfo("Success", "Password added successfully")
                dialog.destroy()
                self._load_passwords()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save password: {e}")
        
        btn_frame = tk.Frame(dialog, bg=self.BG)
        btn_frame.pack(fill='x', padx=15, pady=(10, 15))
        
        save_btn = tk.Button(btn_frame, text='Save', bg=self.GREEN, fg=self.BG,
                            relief='flat', command=save_password)
        save_btn.pack(side='left', padx=(0, 5), ipady=5, ipadx=15)
        
        cancel_btn = tk.Button(btn_frame, text='Cancel', bg=self.GRAY, fg=self.WHITE,
                              relief='flat', command=dialog.destroy)
        cancel_btn.pack(side='left', ipady=5, ipadx=15)
    
    def _on_item_double_click(self, event):
        """Show password on double-click"""
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item, 'values')
        if values:
            website = values[0]
            password = self._get_actual_password(website)
            if password:
                messagebox.showinfo(f"Password for {website}", f"Password: {password}")
    
    def _get_actual_password(self, website):
        """Get the actual password from storage"""
        try:
            passwords_path = Path(__file__).resolve().parents[1] / "database" / "passwords.json"
            if passwords_path.exists():
                data = json.loads(passwords_path.read_text(encoding='utf-8'))
                return data.get(self.username, {}).get(website, {}).get('password')
        except:
            pass
        return None
    
    def _on_edit(self):
        """Edit selected password"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Selection", "Please select a password to edit")
            return
        
        values = self.tree.item(item, 'values')
        website = values[0]
        
        password = self._get_actual_password(website)
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f'Edit - {website}')
        dialog.configure(bg=self.BG)
        dialog.geometry('400x200')
        dialog.resizable(False, False)
        
        tk.Label(dialog, text='Username:', fg=self.WHITE, bg=self.BG).pack(anchor='w', padx=15, pady=(15, 0))
        username_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE)
        username_entry.insert(0, values[1])
        username_entry.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(dialog, text='Password:', fg=self.WHITE, bg=self.BG).pack(anchor='w', padx=15, pady=(0, 0))
        pwd_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE)
        pwd_entry.insert(0, password or '')
        pwd_entry.pack(fill='x', padx=15, pady=(0, 15))
        
        def update_password():
            new_username = username_entry.get().strip()
            new_password = pwd_entry.get()
            
            if not new_username or not new_password:
                messagebox.showwarning("Validation", "All fields are required")
                return
            
            try:
                passwords_path = Path(__file__).resolve().parents[1] / "database" / "passwords.json"
                data = json.loads(passwords_path.read_text(encoding='utf-8'))
                
                data[self.username][website]['username'] = new_username
                data[self.username][website]['password'] = new_password
                
                passwords_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
                messagebox.showinfo("Success", "Password updated successfully")
                dialog.destroy()
                self._load_passwords()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update password: {e}")
        
        btn_frame = tk.Frame(dialog, bg=self.BG)
        btn_frame.pack(fill='x', padx=15, pady=(10, 15))
        
        save_btn = tk.Button(btn_frame, text='Update', bg=self.BLUE, fg=self.BG,
                            relief='flat', command=update_password)
        save_btn.pack(side='left', padx=(0, 5), ipady=5, ipadx=15)
        
        cancel_btn = tk.Button(btn_frame, text='Cancel', bg=self.GRAY, fg=self.WHITE,
                              relief='flat', command=dialog.destroy)
        cancel_btn.pack(side='left', ipady=5, ipadx=15)
    
    def _on_delete(self):
        """Delete selected password"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Selection", "Please select a password to delete")
            return
        
        values = self.tree.item(item, 'values')
        website = values[0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete password for {website}?"):
            try:
                passwords_path = Path(__file__).resolve().parents[1] / "database" / "passwords.json"
                data = json.loads(passwords_path.read_text(encoding='utf-8'))
                
                if website in data.get(self.username, {}):
                    del data[self.username][website]
                    passwords_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
                    messagebox.showinfo("Success", "Password deleted successfully")
                    self._load_passwords()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete password: {e}")
    
    def _show_change_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title('Changer mon mot de passe')
        dialog.configure(bg=self.BG)
        dialog.geometry('420x260')
        dialog.resizable(False, False)
        dialog.grab_set()
        
        tk.Label(dialog, text='Ancien mot de passe', fg=self.WHITE, bg=self.BG).pack(anchor='w', padx=20, pady=(20, 4))
        old_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE, show='*')
        old_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(dialog, text='Nouveau mot de passe', fg=self.WHITE, bg=self.BG).pack(anchor='w', padx=20, pady=(0, 4))
        new_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE, show='*')
        new_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(dialog, text='Confirmer le nouveau mot de passe', fg=self.WHITE, bg=self.BG).pack(anchor='w', padx=20, pady=(0, 4))
        confirm_entry = tk.Entry(dialog, bg=self.GRAY, fg=self.WHITE, insertbackground=self.WHITE, show='*')
        confirm_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        def change_password():
            old_pw = old_entry.get()
            new_pw = new_entry.get()
            confirm_pw = confirm_entry.get()
            
            if not old_pw or not new_pw or not confirm_pw:
                messagebox.showwarning('Validation', 'Tous les champs sont requis', parent=dialog)
                return
            if new_pw != confirm_pw:
                messagebox.showwarning('Validation', 'Les nouveaux mots de passe ne correspondent pas', parent=dialog)
                return
            if self.auth_service.change_password(self.username, old_pw, new_pw):
                messagebox.showinfo('Succès', 'Votre mot de passe a été mis à jour', parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror('Erreur', 'Impossible de changer le mot de passe. Vérifiez votre mot de passe actuel.', parent=dialog)
        
        action_frame = tk.Frame(dialog, bg=self.BG)
        action_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Button(action_frame, text='Valider', bg=self.BLUE, fg=self.WHITE, relief='flat', command=change_password).pack(side='left', ipady=6, ipadx=15)
        tk.Button(action_frame, text='Annuler', bg=self.GRAY, fg=self.WHITE, relief='flat', command=dialog.destroy).pack(side='left', padx=10, ipady=6, ipadx=15)
    
    def _on_logout(self):
        """Logout and return to login"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
