import tkinter as tk

from security.auth_service import AuthService
from security.password_service import PasswordService

from ui.register import RegisterApp
from ui.user_home import UserHomePage
from ui.admin_panel import AdminPanel


from security.session import Session
from security.guards import require_admin




class LoginApp:
    BG = '#0b0f12'
    BLUE = '#1e90ff'
    WHITE = '#ffffff'

    def __init__(self, root, auth_service=None):
        self.root = root
        self.auth_service = auth_service or AuthService()

        root.title('Connexion - my social')
        root.configure(bg=self.BG)
        root.geometry('420x340')
        root.resizable(False, False)

        container = tk.Frame(root, bg=self.BG)
        container.pack(expand=True, fill='both')

        title = tk.Label(container, text='my social', fg=self.WHITE, bg=self.BG,
                         font=('Segoe UI', 18, 'bold'))
        title.pack(pady=(18, 6))

        subtitle = tk.Label(container, text='Connectez-vous à votre espace', fg=self.BLUE, bg=self.BG,
                            font=('Segoe UI', 10))
        subtitle.pack(pady=(0, 14))

        self.username = self._entry(container, 'Nom d\'utilisateur')
        self.password = self._entry(container, 'Mot de passe', show='*')

        btn = tk.Button(container, text='Se connecter', bg=self.BLUE, fg=self.BG, activebackground=self.BLUE,
                        activeforeground=self.WHITE, command=self._on_login, relief='flat')
        btn.pack(pady=(16, 8), ipadx=10, ipady=6)

        self.msg = tk.Label(container, text='', fg=self.WHITE, bg=self.BG, font=('Segoe UI', 9))
        self.msg.pack(pady=(4, 2))

        link = tk.Label(container, text='Pas encore de compte ? S\'inscrire', fg=self.BLUE, bg=self.BG,
                        cursor='hand2')
        link.pack(pady=(12, 0))
        link.bind('<Button-1>', lambda e: self._open_register())

        root.bind('<Return>', lambda e: self._on_login())
        self.username.focus_set()

    def _entry(self, parent, label_text, show=None):
        frame = tk.Frame(parent, bg=self.BG)
        frame.pack(padx=28, pady=(4, 6), fill='x')
        label = tk.Label(frame, text=label_text, fg=self.WHITE, bg=self.BG)
        label.pack(anchor='w')
        entry = tk.Entry(frame, bg='#0f1316', fg=self.WHITE, insertbackground=self.WHITE, relief='flat', show=show)
        entry.pack(fill='x', pady=4)
        return entry

    def _set_message(self, text, color):
        self.msg.config(text=text, fg=color)

    def _on_login(self):
        user = self.username.get().strip()
        pw = self.password.get()

        if not user or not pw:
            self._set_message('Veuillez remplir tous les champs', 'red')
            return

        if self.auth_service.authenticate(user, pw):
            self._set_message('Connexion réussie', '#22c55e')
            # create a UI session and open protected screens
            self.session = Session(username=user)
            self.root.after(500, lambda: self._open_dashboard(user))

        else:
            self._set_message('Nom d\'utilisateur ou mot de passe incorrect', 'red')

    def _open_dashboard(self, username):
        self.root.destroy()
        dashboard_root = tk.Tk()
        
        # Enforce authorization at UI level
        if self.auth_service.is_admin(username):
            if not require_admin(dashboard_root, self.session, self.auth_service):
                return
            AdminPanel(dashboard_root, username, self.auth_service)
        else:
            # For regular users, only require authentication
            if not self.session.is_authenticated():
                # block access
                return
            password_service = PasswordService()
            UserHomePage(dashboard_root, username, self.auth_service, password_service)


        
        dashboard_root.mainloop()


    def _open_register(self):
        self.root.destroy()
        register_root = tk.Tk()
        RegisterApp(register_root, auth_service=self.auth_service, on_registered=self._back_to_login)
        register_root.mainloop()

    def _back_to_login(self, username=None):
        self.root = tk.Tk()
        LoginApp(self.root, auth_service=self.auth_service)
        self.root.mainloop()


def main():
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()