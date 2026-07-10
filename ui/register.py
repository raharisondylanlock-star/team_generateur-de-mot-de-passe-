import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin pour les imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from security.auth_service import AuthService


class RegisterApp:
    BG = '#0b0f12'
    BLUE = '#1e90ff'
    WHITE = '#ffffff'

    def __init__(self, root, auth_service=None, on_registered=None):
        self.root = root
        self.auth_service = auth_service or AuthService()
        self.on_registered = on_registered

        root.title('Inscription - Password Manager')
        root.configure(bg=self.BG)
        root.geometry('420x360')
        root.resizable(False, False)

        container = tk.Frame(root, bg=self.BG)
        container.pack(expand=True, fill='both')

        title = tk.Label(container, text='Créer un compte', fg=self.WHITE, bg=self.BG,
                         font=('Segoe UI', 18, 'bold'))
        title.pack(pady=(18, 6))

        subtitle = tk.Label(container, text='Enregistrez-vous pour gérer vos mots de passe', fg=self.BLUE, bg=self.BG,
                            font=('Segoe UI', 10))
        subtitle.pack(pady=(0, 14))

        self.username = self._entry(container, 'Nom d\'utilisateur')
        self._info_label = tk.Label(
            container,
            text='Un mot de passe aléatoire sera généré automatiquement pour votre compte.',
            fg='#93c5fd',
            bg=self.BG,
            font=('Segoe UI', 9),
            wraplength=320,
        )
        self._info_label.pack(pady=(4, 8))

        btn = tk.Button(container, text='S\'inscrire', bg=self.BLUE, fg=self.BG, activebackground=self.BLUE,
                        activeforeground=self.WHITE, command=self._on_register, relief='flat')
        btn.pack(pady=(16, 8), ipadx=10, ipady=6)

        self.msg = tk.Label(container, text='', fg=self.WHITE, bg=self.BG, font=('Segoe UI', 9))
        self.msg.pack(pady=(4, 2))

        link = tk.Label(container, text='Déjà un compte ? Se connecter', fg=self.BLUE, bg=self.BG,
                        cursor='hand2')
        link.pack(pady=(12, 0))
        link.bind('<Button-1>', lambda e: self._go_to_login())

        root.bind('<Return>', lambda e: self._on_register())
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

    def _on_register(self):
        user = self.username.get().strip()

        if not user:
            self._set_message('Veuillez saisir un nom d\'utilisateur', 'red')
            return

        if self.auth_service.register_user(user):
            generated_password = self.auth_service.last_generated_password or ''
            self._set_message('Compte créé avec succès', '#22c55e')
            self.root.after(300, self._show_generated_password_dialog, generated_password, user)
        else:
            self._set_message('Ce nom d\'utilisateur existe déjà', 'red')

    def _show_generated_password_dialog(self, generated_password, username):
        dialog = tk.Toplevel(self.root)
        dialog.title('Mot de passe généré')
        dialog.configure(bg=self.BG)
        dialog.geometry('420x220')
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text='Votre mot de passe temporaire', bg=self.BG, fg=self.WHITE,
                 font=('Segoe UI', 14, 'bold')).pack(pady=(16, 10))
        tk.Label(dialog, text='Copiez-le et gardez-le en sécurité.', bg=self.BG, fg='#93c5fd').pack()

        entry = tk.Entry(dialog, bg='#0f1316', fg=self.WHITE, insertbackground=self.WHITE, justify='center')
        entry.insert(0, generated_password)
        entry.pack(fill='x', padx=24, pady=(12, 10))

        def copy_password():
            self.root.clipboard_clear()
            self.root.clipboard_append(generated_password)
            self.root.update()
            messagebox.showinfo('Copié', 'Mot de passe copié dans le presse-papiers', parent=dialog)

        tk.Button(dialog, text='Copier', bg=self.BLUE, fg=self.WHITE, command=copy_password).pack(pady=(6, 8))
        tk.Button(dialog, text='Continuer', bg='#22c55e', fg=self.WHITE, command=lambda: self._finish_registration(username)).pack()

    def _finish_registration(self, username):
        self.root.destroy()
        if self.on_registered:
            self.on_registered(username)

    def _go_to_login(self):
        self.root.destroy()
        if self.on_registered is not None:
            self.on_registered(None)


def main():
    root = tk.Tk()
    RegisterApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
