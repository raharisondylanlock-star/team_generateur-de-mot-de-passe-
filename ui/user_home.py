import tkinter as tk
from tkinter import messagebox, ttk
import json
from pathlib import Path


class UserHomePage:
    # Couleurs modernes
    BG_DARK = '#0a0d14'
    NAV_DARK = '#1f1347'
    BLUE_HERO = '#0e2452'
    WHITE = '#ffffff'
    TEXT_MUTED = '#a0a5b5'
    BLUE_ACCENT = '#00b4d8'
    GREEN_ACCENT = '#2ecc71'
    CARD_BLUE = '#112f6d'
    CARD_LIGHT = '#e3e7f1'
    CARD_BLACK = '#0d131e'

    def __init__(self, root, username, auth_service, password_service):
        self.root = root
        self.username = username
        self.auth_service = auth_service
        self.password_service = password_service

        self.root.title(f'my social - {username}')
        self.root.configure(bg=self.BG_DARK)
        self.root.geometry('1100x750')
        self.root.resizable(True, True)

        main_container = tk.Frame(self.root, bg=self.BG_DARK)
        main_container.pack(expand=True, fill='both')

        # TOP BAR
        top_info = tk.Frame(main_container, bg=self.BG_DARK, height=30)
        top_info.pack(fill='x', padx=20, pady=5)
        tk.Label(top_info, text="🔒 DONNÉES SÉCURISÉES", fg=self.WHITE, bg=self.BG_DARK, font=('Segoe UI', 8)).pack(side='right', padx=15)
        tk.Button(
            top_info,
            text="🚪 DÉCONNEXION",
            fg=self.TEXT_MUTED,
            bg=self.BG_DARK,
            bd=0,
            activebackground=self.BG_DARK,
            activeforeground=self.WHITE,
            font=('Segoe UI', 8, 'bold'),
            command=self._on_logout,
        ).pack(side='right', padx=15)
        tk.Label(top_info, text=f"👤 Connecté: {username}", fg=self.TEXT_MUTED, bg=self.BG_DARK, font=('Segoe UI', 8)).pack(side='right', padx=15)

        # NAVBAR PRINCIPALE
        navbar = tk.Frame(main_container, bg=self.NAV_DARK, height=70)
        navbar.pack(fill='x')
        navbar.pack_propagate(False)

        logo_frame = tk.Frame(navbar, bg=self.NAV_DARK)
        logo_frame.pack(side='left', padx=30)
        tk.Label(logo_frame, text="🔐 mamy", fg=self.BLUE_ACCENT, bg=self.NAV_DARK, font=('Segoe UI', 20, 'bold')).pack(side='left')
        tk.Label(logo_frame, text=" password manager", fg=self.WHITE, bg=self.NAV_DARK, font=('Segoe UI', 14)).pack(side='left')

        title_frame = tk.Frame(navbar, bg=self.NAV_DARK)
        title_frame.pack(side='left', expand=True, fill='both', padx=40)
        tk.Label(title_frame, text="Votre gestionnaire de mots de passe sécurisé", fg=self.TEXT_MUTED, bg=self.NAV_DARK, font=('Segoe UI', 11)).pack()

        menu_frame = tk.Frame(navbar, bg=self.NAV_DARK)
        menu_frame.pack(side='right', padx=30)
        tk.Label(menu_frame, text="⚙ AIDE", fg=self.WHITE, bg=self.NAV_DARK, font=('Segoe UI', 9, 'bold')).pack()

        # SUB-NAVBAR — vrais onglets cliquables avec indicateur actif
        sub_nav = tk.Frame(main_container, bg=self.NAV_DARK, height=48)
        sub_nav.pack(fill='x')
        sub_nav.pack_propagate(False)

        tab_defs = [
            ("Accueil", "🏠"),
            ("Mes Mots de Passe", "🔑"),
            ("Sécurité", "🛡"),
            ("Comptes Liés", "🔗"),
            ("Paramètres", "⚙"),
        ]
        tabs_frame = tk.Frame(sub_nav, bg=self.NAV_DARK)
        tabs_frame.pack(side='left', fill='y', padx=10)

        self.active_menu = tab_defs[0][0]
        self.menu_tabs = {}
        for name, icon in tab_defs:
            tab = tk.Frame(tabs_frame, bg=self.NAV_DARK, cursor='hand2')
            tab.pack(side='left', fill='y')
            label = tk.Label(tab, text=f'{icon}  {name}', bg=self.NAV_DARK, fg=self.TEXT_MUTED,
                              font=('Segoe UI', 10, 'bold'), padx=16, pady=14, cursor='hand2')
            label.pack()
            indicator = tk.Frame(tab, bg=self.NAV_DARK, height=3)
            indicator.pack(fill='x', side='bottom')
            for widget in (tab, label):
                widget.bind('<Button-1>', lambda e, m=name: self._on_menu_click(m))
                widget.bind('<Enter>', lambda e, m=name: self._on_tab_hover(m, True))
                widget.bind('<Leave>', lambda e, m=name: self._on_tab_hover(m, False))
            self.menu_tabs[name] = {'label': label, 'indicator': indicator}

        right_box = tk.Frame(sub_nav, bg=self.NAV_DARK)
        right_box.pack(side='right', padx=20)
        self.status_label = tk.Label(right_box, text="✓ ACTIF", fg=self.GREEN_ACCENT, bg=self.NAV_DARK, font=('Segoe UI', 10, 'bold'))
        self.status_label.pack(side='left')

        # FOOTER — bandeau persistant en bas de fenêtre
        footer = tk.Frame(main_container, bg=self.CARD_BLACK, height=42)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        tk.Label(footer, text="🔒 Sécurité renforcée : authentification + chiffrement AES/Fernet des mots de passe", fg=self.BLUE_ACCENT, bg=self.CARD_BLACK, font=('Segoe UI', 10, 'bold')).pack(pady=10)

        # ZONE DE CONTENU — change selon l'onglet sélectionné
        self.menu_content = tk.Frame(main_container, bg=self.BG_DARK)
        self.menu_content.pack(fill='both', expand=True, padx=20, pady=(15, 10))
        self._set_active_menu(self.active_menu)
        self._render_menu_content(self.active_menu)

    def _set_active_menu(self, active_menu):
        self.active_menu = active_menu
        for name, widgets in self.menu_tabs.items():
            label = widgets['label']
            indicator = widgets['indicator']
            if name == active_menu:
                label.config(fg=self.BLUE_ACCENT)
                indicator.config(bg=self.BLUE_ACCENT)
            else:
                label.config(fg=self.TEXT_MUTED)
                indicator.config(bg=self.NAV_DARK)

    def _on_tab_hover(self, menu_name, entering):
        if menu_name == self.active_menu:
            return
        label = self.menu_tabs[menu_name]['label']
        label.config(fg=self.WHITE if entering else self.TEXT_MUTED)

    def _is_pro(self) -> bool:
        pro_path = Path(__file__).resolve().parents[1] / 'database' / 'pro.json'
        try:
            if not pro_path.exists():
                pro_path.write_text('{}', encoding='utf-8')
            pro_data = json.loads(pro_path.read_text(encoding='utf-8') or '{}')
            return bool(pro_data.get(self.username, False)) if isinstance(pro_data, dict) else False
        except Exception:
            return False

    def _upgrade_to_pro(self):
        pro_path = Path(__file__).resolve().parents[1] / 'database' / 'pro.json'
        try:
            if not pro_path.exists():
                pro_path.write_text('{}', encoding='utf-8')
            pro_data = json.loads(pro_path.read_text(encoding='utf-8') or '{}')
            if not isinstance(pro_data, dict):
                pro_data = {}
            pro_data[self.username] = True
            pro_path.write_text(json.dumps(pro_data, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            messagebox.showerror('Erreur', f"Impossible d'activer PRO: {e}")
            return
        self._render_menu_content('Sécurité')
        self._set_active_menu('Sécurité')

    def _run_pro_audit(self, score: int, risk: str):
        messagebox.showinfo('Audit PRO (mock)', f"Résultat : {score}/100\nStatut : {risk}\n\nAnalyse simulée locale : utilisez ce panneau comme base pour une version complète.")

    def _render_menu_content(self, menu_name):
        for widget in self.menu_content.winfo_children():
            widget.destroy()

        if menu_name != 'Accueil':
            tk.Label(self.menu_content, text=menu_name, fg=self.WHITE, bg=self.BG_DARK, font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        content = tk.Frame(self.menu_content, bg=self.BG_DARK)
        content.pack(fill='both', expand=True, pady=10)

        if menu_name == 'Accueil':
            entries = self.password_service.list_passwords(self.username)
            is_pro = self._is_pro()

            # Analyse rapide (réutilisation & robustesse) pour donner du sens aux stats
            pw_values = [str(e.get('password')) for e in entries if e.get('password')]
            total = len(pw_values)
            seen = set()
            reused = 0
            for p in pw_values:
                if p in seen:
                    reused += 1
                else:
                    seen.add(p)
            weak = sum(1 for p in pw_values if len(p) < 10)

            hero = tk.Frame(content, bg=self.BLUE_HERO, height=200)
            hero.pack(fill='x', pady=(0, 20))
            hero.pack_propagate(False)

            tv_mockup = tk.Frame(hero, bg='#071635', width=260)
            tv_mockup.pack(side='left', fill='y', padx=20)
            tk.Label(tv_mockup, text="🔐", fg='#1b356a', bg='#071635', font=('Segoe UI', 50)).pack(expand=True)
            tk.Label(tv_mockup, text="Vos données\nsont en sécurité", fg='#1b356a', bg='#071635', font=('Segoe UI', 11, 'bold'), justify='center').pack(expand=True)

            hero_text_frame = tk.Frame(hero, bg=self.BLUE_HERO)
            hero_text_frame.pack(side='right', fill='both', expand=True, padx=50, pady=25)
            tk.Label(hero_text_frame, text="BIENVENUE", fg=self.WHITE, bg=self.BLUE_HERO, font=('Segoe UI', 28, 'bold'), anchor='w').pack(fill='x')
            tk.Label(hero_text_frame, text=f"{self.username}", fg=self.BLUE_ACCENT, bg=self.BLUE_HERO, font=('Segoe UI', 16, 'bold'), anchor='w').pack(fill='x')
            tk.Label(hero_text_frame, text="Votre coffre-fort numérique : centralisez, protégez et retrouvez tous vos mots de passe en un seul endroit.", fg=self.WHITE, bg=self.BLUE_HERO, font=('Segoe UI', 12), anchor='w', wraplength=520, justify='left').pack(fill='x', pady=8)

            quick_row = tk.Frame(hero_text_frame, bg=self.BLUE_HERO)
            quick_row.pack(fill='x', pady=(6, 0), anchor='w')
            tk.Button(quick_row, text='➕ Ajouter un mot de passe', bg=self.GREEN_ACCENT, fg=self.BG_DARK,
                      font=('Segoe UI', 9, 'bold'), relief='flat', padx=12, pady=6,
                      command=lambda: self._on_menu_click('Mes Mots de Passe')).pack(side='left', padx=(0, 8))
            tk.Button(quick_row, text='🛡 Voir la sécurité', bg=self.BLUE_ACCENT, fg=self.BG_DARK,
                      font=('Segoe UI', 9, 'bold'), relief='flat', padx=12, pady=6,
                      command=lambda: self._on_menu_click('Sécurité')).pack(side='left')

            # Statistiques rapides — reflètent réellement l'état du coffre
            stats_frame = tk.Frame(content, bg=self.BG_DARK)
            stats_frame.pack(fill='x', pady=(0, 20))
            for i in range(4):
                stats_frame.grid_columnconfigure(i, weight=1)

            reuse_color = '#e74c3c' if reused else self.GREEN_ACCENT
            weak_color = '#e74c3c' if weak else self.GREEN_ACCENT
            stats = [
                ('🔐', str(total), 'Mots de passe enregistrés', self.WHITE),
                ('♻️', str(reused), 'Mots de passe réutilisés', reuse_color),
                ('⚠️', str(weak), 'Mots de passe faibles (<10 car.)', weak_color),
                ('⭐' if is_pro else '☆', 'PRO' if is_pro else 'Free', 'Statut du compte', self.BLUE_ACCENT if is_pro else self.WHITE),
            ]
            for i, (icon, value, label_text, value_color) in enumerate(stats):
                stat_card = tk.Frame(stats_frame, bg=self.CARD_BLACK, height=90)
                stat_card.grid(row=0, column=i, padx=8, sticky='ew')
                stat_card.grid_propagate(False)
                row = tk.Frame(stat_card, bg=self.CARD_BLACK)
                row.pack(expand=True)
                tk.Label(row, text=icon, bg=self.CARD_BLACK, font=('Segoe UI', 20)).pack(side='left', padx=(0, 10))
                col = tk.Frame(row, bg=self.CARD_BLACK)
                col.pack(side='left')
                tk.Label(col, text=value, fg=value_color, bg=self.CARD_BLACK, font=('Segoe UI', 16, 'bold')).pack(anchor='w')
                tk.Label(col, text=label_text, fg=self.TEXT_MUTED, bg=self.CARD_BLACK, font=('Segoe UI', 9)).pack(anchor='w')

            # Cartes d'action — chacune mène directement vers la fonctionnalité correspondante
            cards_frame = tk.Frame(content, bg=self.BG_DARK)
            cards_frame.pack(fill='x')
            for i in range(3):
                cards_frame.grid_columnconfigure(i, weight=1)

            def make_card(parent, col, bg, fg_title, icon, title, desc, action_text, command):
                c = tk.Frame(parent, bg=bg, height=180, bd=0, cursor='hand2')
                c.grid(row=0, column=col, padx=8, sticky='ew')
                c.pack_propagate(False)
                tk.Label(c, text=icon, bg=bg, font=('Segoe UI', 28)).pack(anchor='w', padx=18, pady=(14, 4))
                tk.Label(c, text=title, fg=fg_title, bg=bg, font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=18)
                tk.Label(c, text=desc, fg=self.WHITE if bg != self.CARD_LIGHT else self.BG_DARK, bg=bg, font=('Segoe UI', 11, 'bold'), wraplength=200, justify='left').pack(anchor='w', padx=18, pady=5)
                btn = tk.Button(c, text=action_text, bg=self.BLUE_ACCENT, fg=self.BG_DARK, font=('Segoe UI', 9, 'bold'),
                                 relief='flat', bd=0, padx=10, pady=5, command=command)
                btn.pack(side='bottom', anchor='w', padx=18, pady=12)
                return c

            make_card(cards_frame, 0, self.CARD_BLUE, self.TEXT_MUTED, '🔐', 'STOCKAGE SÉCURISÉ',
                      'Vos mots de passe sont chiffrés (AES/Fernet) avant stockage',
                      'Gérer mes mots de passe', lambda: self._on_menu_click('Mes Mots de Passe'))

            make_card(cards_frame, 1, self.CARD_LIGHT, 'gray', '🛡', 'AUDIT DE SÉCURITÉ',
                      'Détectez les mots de passe faibles ou réutilisés',
                      'Lancer l\'audit', lambda: self._on_menu_click('Sécurité'))

            make_card(cards_frame, 2, self.CARD_BLACK, self.BLUE_ACCENT, '🔗', 'COMPTES LIÉS',
                      'Connectez Google, Facebook et vos autres comptes',
                      'Voir les comptes liés', lambda: self._on_menu_click('Comptes Liés'))

            if weak or reused:
                alert = tk.Frame(content, bg='#3a1a1a')
                alert.pack(fill='x', pady=(15, 0))
                msg = []
                if weak:
                    msg.append(f"{weak} mot(s) de passe court(s)")
                if reused:
                    msg.append(f"{reused} réutilisation(s) détectée(s)")
                tk.Label(alert, text=f"⚠️  {' · '.join(msg)} — pensez à les renforcer dans « Mes Mots de Passe ».",
                         fg='#ff8787', bg='#3a1a1a', font=('Segoe UI', 10, 'bold'), anchor='w',
                         wraplength=900, justify='left').pack(fill='x', padx=15, pady=10)

        elif menu_name == 'Mes Mots de Passe':
            tk.Label(content, text='Accédez à votre coffre-fort personnel pour gérer tous vos identifiants et mots de passe en un seul endroit.', fg=self.TEXT_MUTED, bg=self.BG_DARK, font=('Segoe UI', 11), wraplength=860, justify='left').pack(anchor='w')

            actions_frame = tk.Frame(content, bg=self.BG_DARK)
            actions_frame.pack(fill='x', pady=10)
            tk.Button(
                actions_frame,
                text='➕ Ajouter un mot de passe',
                bg=self.GREEN_ACCENT,
                fg=self.BG_DARK,
                font=('Segoe UI', 10, 'bold'),
                bd=0,
                padx=15,
                pady=8,
                activebackground='#27ae60',
                activeforeground=self.WHITE,
                command=self._show_add_password,
            ).pack(side='left', padx=(0, 5))
            tk.Button(
                actions_frame,
                text='👁 Voir',
                bg=self.BLUE_ACCENT,
                fg=self.BG_DARK,
                font=('Segoe UI', 10, 'bold'),
                bd=0,
                padx=15,
                pady=8,
                command=self._show_selected_password,
            ).pack(side='left', padx=(0, 5))
            tk.Button(
                actions_frame,
                text='✏ Modifier',
                bg='#8e7cff',
                fg=self.BG_DARK,
                font=('Segoe UI', 10, 'bold'),
                bd=0,
                padx=15,
                pady=8,
                command=self._edit_selected_password,
            ).pack(side='left', padx=(0, 5))
            tk.Button(
                actions_frame,
                text='🗑 Supprimer',
                bg='#e74c3c',
                fg=self.WHITE,
                font=('Segoe UI', 10, 'bold'),
                bd=0,
                padx=15,
                pady=8,
                command=self._delete_selected_password,
            ).pack(side='left', padx=(0, 5))
            tk.Button(
                actions_frame,
                text='🔑 Changer mot de passe principal',
                bg='#f59e0b',
                fg=self.BG_DARK,
                font=('Segoe UI', 10, 'bold'),
                bd=0,
                padx=15,
                pady=8,
                activebackground='#e67e22',
                activeforeground=self.BG_DARK,
                command=self._show_change_master_password,
            ).pack(side='right')

            list_frame = tk.Frame(content, bg=self.CARD_BLACK)
            list_frame.pack(fill='both', expand=True, pady=10)
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side='right', fill='y')

            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Passwords.Treeview', background=self.CARD_BLACK, foreground=self.WHITE,
                             fieldbackground=self.CARD_BLACK, borderwidth=0, rowheight=26)
            style.map('Passwords.Treeview', background=[('selected', self.BLUE_ACCENT)])
            style.configure('Passwords.Treeview.Heading', background=self.NAV_DARK, foreground=self.WHITE, borderwidth=0)

            self.passwords_tree = ttk.Treeview(
                list_frame,
                columns=('site', 'username', 'password'),
                show='headings',
                selectmode='browse',
                yscrollcommand=scrollbar.set,
                style='Passwords.Treeview',
            )
            scrollbar.config(command=self.passwords_tree.yview)
            self.passwords_tree.heading('site', text='Site / Application')
            self.passwords_tree.heading('username', text='Identifiant')
            self.passwords_tree.heading('password', text='Mot de passe')
            self.passwords_tree.column('site', width=260, anchor='w')
            self.passwords_tree.column('username', width=260, anchor='w')
            self.passwords_tree.column('password', width=200, anchor='w')
            self.passwords_tree.pack(fill='both', expand=True, padx=10, pady=10)
            self.passwords_tree.bind('<Double-1>', lambda e: self._show_selected_password())
            self._load_passwords_list()

        elif menu_name == 'Sécurité':
            is_pro = self._is_pro()
            tk.Label(content, text='Sécurité : protection par authentification et contrôle des accès.', fg=self.TEXT_MUTED, bg=self.BG_DARK, font=('Segoe UI', 11), wraplength=860, justify='left').pack(anchor='w')

            if is_pro:
                # Audit local (simple) sur les mots de passe déchiffrés de l'utilisateur
                entries = self.password_service.list_passwords(self.username)
                pw_values = [str(e.get('password')) for e in entries if e.get('password')]

                total = len(pw_values)
                avg_len = (sum(len(p) for p in pw_values) / total) if total else 0
                seen = set()
                reuse_count = 0
                for p in pw_values:
                    if p in seen:
                        reuse_count += 1
                    else:
                        seen.add(p)

                score = 100
                if avg_len:
                    score -= max(0, int((8 - avg_len) * 6))
                if reuse_count:
                    score -= min(50, reuse_count * 10)
                score = max(0, min(100, score))

                risk = 'Risque élevé' if score < 50 else ('Risque moyen' if score < 80 else 'Risque faible')
                risk_color = '#e74c3c' if score < 50 else ('#f59e0b' if score < 80 else self.GREEN_ACCENT)

                # Header PRO
                tk.Label(content, text='★ Mode PRO — Audit de sécurité & recommandations renforcées', fg=self.BLUE_ACCENT, bg=self.BG_DARK, font=('Segoe UI', 12, 'bold'), justify='left').pack(anchor='w', pady=(10, 10))

                score_card = tk.Frame(content, bg=self.CARD_BLACK)
                score_card.pack(fill='x', pady=(0, 14))
                score_inner = tk.Frame(score_card, bg=self.CARD_BLACK)
                score_inner.pack(fill='x', padx=18, pady=16)
                tk.Label(score_inner, text=str(score), fg=self.BLUE_ACCENT, bg=self.CARD_BLACK, font=('Segoe UI', 32, 'bold')).pack(side='left')
                tk.Label(score_inner, text='/100', fg=self.TEXT_MUTED, bg=self.CARD_BLACK, font=('Segoe UI', 14)).pack(side='left', anchor='s', pady=(0, 8), padx=(2, 20))
                score_text_col = tk.Frame(score_inner, bg=self.CARD_BLACK)
                score_text_col.pack(side='left')
                tk.Label(score_text_col, text='Score de sécurité', fg=self.WHITE, bg=self.CARD_BLACK, font=('Segoe UI', 11, 'bold')).pack(anchor='w')
                tk.Label(score_text_col, text=risk, fg=risk_color, bg=self.CARD_BLACK, font=('Segoe UI', 10, 'bold')).pack(anchor='w')

                # Checklist premium (plus pro)
                tk.Label(content, text='Checklist PRO', fg=self.WHITE, bg=self.BG_DARK, font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(0, 6))

                pro_bullets = []
                if total == 0:
                    pro_bullets.append('Aucun mot de passe détecté (base vide)')
                else:
                    if avg_len < 10:
                        pro_bullets.append('Longueur moyenne faible : rotation recommandée')
                    else:
                        pro_bullets.append('Longueur moyenne correcte : renforcer la variété')

                    if reuse_count > 0:
                        pro_bullets.append('Réutilisation probable : réduire les doublons exacts')
                    else:
                        pro_bullets.append('Aucune réutilisation exacte détectée')

                    pro_bullets.append('Rotation priorisée : comptes à fort impact d’abord (mock)')
                    pro_bullets.append('Bonnes pratiques : passphrases + diversité + gestion des exceptions (mock)')
                    pro_bullets.append('Conformité : check-list sécurité (mock)')

                checklist_card = tk.Frame(content, bg=self.CARD_BLACK)
                checklist_card.pack(fill='x', pady=(0, 14))
                for bullet in pro_bullets:
                    tk.Label(checklist_card, text=f'✓  {bullet}', fg=self.WHITE, bg=self.CARD_BLACK, font=('Segoe UI', 10), anchor='w', wraplength=800, justify='left').pack(fill='x', padx=18, pady=5)

                tk.Button(content, text='▶ Lancer l’audit', bg='#22c55e', fg=self.BG_DARK, font=('Segoe UI', 10, 'bold'), relief='flat', padx=15, pady=8, command=lambda: self._run_pro_audit(score, risk)).pack(anchor='w')

            else:
                tips_card = tk.Frame(content, bg=self.CARD_BLACK)
                tips_card.pack(fill='x', pady=(10, 0))
                tips = [
                    '🔍  Vérifiez la force de vos mots de passe',
                    '📋  Consultez les recommandations de sécurité',
                    '🔔  Activez des protections supplémentaires à venir',
                ]
                for tip in tips:
                    tk.Label(tips_card, text=tip, fg=self.WHITE, bg=self.CARD_BLACK, font=('Segoe UI', 11), anchor='w').pack(fill='x', padx=18, pady=6)

                pro_box = tk.Frame(content, bg=self.CARD_BLUE, bd=0)
                pro_box.pack(fill='x', pady=(15, 0))
                tk.Label(pro_box, text='⭐ Upgrade vers le Mode PRO', fg=self.WHITE, bg=self.CARD_BLUE, font=('Segoe UI', 12, 'bold'), justify='left').pack(anchor='w', padx=15, pady=(12, 0))
                tk.Label(pro_box, text='Accédez à des recommandations avancées, alertes & analyses renforcées.', fg=self.TEXT_MUTED, bg=self.CARD_BLUE, font=('Segoe UI', 10, 'bold'), justify='left', wraplength=820).pack(anchor='w', padx=15, pady=(6, 4))
                tk.Button(pro_box, text='Passer en Pro', bg='#22c55e', fg=self.BG_DARK, font=('Segoe UI', 10, 'bold'), relief='flat', padx=15, pady=8, command=self._upgrade_to_pro).pack(anchor='w', padx=15, pady=(6, 14))

        elif menu_name == 'Comptes Liés':
            tk.Label(content, text='Centralisez vos connexions en liant vos comptes externes à votre coffre-fort.', fg=self.TEXT_MUTED, bg=self.BG_DARK, font=('Segoe UI', 11), wraplength=860, justify='left').pack(anchor='w')

            grid = tk.Frame(content, bg=self.BG_DARK)
            grid.pack(fill='x', pady=15)
            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)

            providers = [
                ('Google', '🟢'),
                ('Facebook', '🔵'),
                ('Apple', '⬛'),
                ('LinkedIn', '🔷'),
            ]
            for idx, (provider, icon) in enumerate(providers):
                row, col = divmod(idx, 2)
                card = tk.Frame(grid, bg=self.CARD_BLACK, bd=0)
                card.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
                inner = tk.Frame(card, bg=self.CARD_BLACK)
                inner.pack(fill='x', padx=18, pady=16)

                tk.Label(inner, text=icon, bg=self.CARD_BLACK, font=('Segoe UI', 22)).pack(side='left', padx=(0, 14))

                text_col = tk.Frame(inner, bg=self.CARD_BLACK)
                text_col.pack(side='left', fill='x', expand=True)
                tk.Label(text_col, text=provider, fg=self.WHITE, bg=self.CARD_BLACK, font=('Segoe UI', 12, 'bold')).pack(anchor='w')
                tk.Label(text_col, text='●  Non connecté', fg='#e74c3c', bg=self.CARD_BLACK, font=('Segoe UI', 9)).pack(anchor='w', pady=(2, 0))

                tk.Button(
                    inner, text='Connecter', bg=self.BLUE_ACCENT, fg=self.BG_DARK,
                    font=('Segoe UI', 9, 'bold'), relief='flat', bd=0, padx=14, pady=6,
                    activebackground='#0096c7', activeforeground=self.WHITE,
                    command=lambda p=provider: messagebox.showinfo('Comptes liés', f"L'intégration avec {p} sera bientôt disponible."),
                ).pack(side='right')

            info_card = tk.Frame(content, bg=self.NAV_DARK)
            info_card.pack(fill='x', pady=(5, 0))
            tk.Label(
                info_card,
                text="ℹ️  Aucune intégration active pour le moment. En attendant, ajoutez et gérez vos identifiants manuellement depuis « Mes Mots de Passe ».",
                fg=self.TEXT_MUTED, bg=self.NAV_DARK, font=('Segoe UI', 10), wraplength=820, justify='left',
            ).pack(anchor='w', padx=15, pady=12)
        else:
            self._render_settings(content)

    def _render_settings(self, content):
        """Page Paramètres façon Facebook/Google : menu latéral de catégories + panneau de contenu."""
        is_pro = self._is_pro()

        wrapper = tk.Frame(content, bg=self.BG_DARK)
        wrapper.pack(fill='both', expand=True)

        sidebar = tk.Frame(wrapper, bg=self.CARD_BLACK, width=230)
        sidebar.pack(side='left', fill='y', padx=(0, 16))
        sidebar.pack_propagate(False)

        panel = tk.Frame(wrapper, bg=self.BG_DARK)
        panel.pack(side='left', fill='both', expand=True)

        categories = [
            ('compte', '👤', 'Informations du compte'),
            ('securite', '🔒', 'Mot de passe et sécurité'),
            ('confidentialite', '🕵', 'Confidentialité'),
            ('notifications', '🔔', 'Notifications'),
            ('aide', '❓', 'Aide et assistance'),
        ]

        if not hasattr(self, '_settings_category'):
            self._settings_category = 'compte'

        sidebar_widgets = {}

        tk.Label(sidebar, text='⚙ Paramètres', fg=self.WHITE, bg=self.CARD_BLACK, font=('Segoe UI', 13, 'bold')).pack(anchor='w', padx=16, pady=(16, 12))

        for key, icon, label in categories:
            row = tk.Frame(sidebar, bg=self.CARD_BLACK, cursor='hand2')
            row.pack(fill='x', padx=8, pady=2)
            lbl = tk.Label(row, text=f'{icon}  {label}', bg=self.CARD_BLACK, fg=self.TEXT_MUTED,
                            font=('Segoe UI', 10, 'bold'), anchor='w', padx=10, pady=10, cursor='hand2')
            lbl.pack(fill='x')
            for widget in (row, lbl):
                widget.bind('<Button-1>', lambda e, k=key: select_category(k))
            sidebar_widgets[key] = (row, lbl)

        def highlight_sidebar():
            for key, (row, lbl) in sidebar_widgets.items():
                active = key == self._settings_category
                bg = self.NAV_DARK if active else self.CARD_BLACK
                fg = self.BLUE_ACCENT if active else self.TEXT_MUTED
                row.config(bg=bg)
                lbl.config(bg=bg, fg=fg)

        def section_title(parent, text):
            tk.Label(parent, text=text, fg=self.WHITE, bg=self.BG_DARK, font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 12))

        def row_item(parent, icon, title, desc, action_text=None, command=None, value_text=None):
            card = tk.Frame(parent, bg=self.CARD_BLACK)
            card.pack(fill='x', pady=6)
            inner = tk.Frame(card, bg=self.CARD_BLACK)
            inner.pack(fill='x', padx=16, pady=12)
            tk.Label(inner, text=icon, bg=self.CARD_BLACK, font=('Segoe UI', 16)).pack(side='left', padx=(0, 12))
            text_col = tk.Frame(inner, bg=self.CARD_BLACK)
            text_col.pack(side='left', fill='x', expand=True)
            tk.Label(text_col, text=title, fg=self.WHITE, bg=self.CARD_BLACK, font=('Segoe UI', 11, 'bold')).pack(anchor='w')
            if desc:
                tk.Label(text_col, text=desc, fg=self.TEXT_MUTED, bg=self.CARD_BLACK, font=('Segoe UI', 9),
                         wraplength=420, justify='left').pack(anchor='w', pady=(2, 0))
            if value_text:
                tk.Label(inner, text=value_text, fg=self.TEXT_MUTED, bg=self.CARD_BLACK, font=('Segoe UI', 9)).pack(side='right', padx=(10, 0))
            if action_text and command:
                tk.Button(inner, text=action_text, bg=self.BLUE_ACCENT, fg=self.BG_DARK, font=('Segoe UI', 9, 'bold'),
                          relief='flat', bd=0, padx=12, pady=6, command=command).pack(side='right')

        def build_account(parent):
            section_title(parent, 'Informations du compte')
            avatar_row = tk.Frame(parent, bg=self.BG_DARK)
            avatar_row.pack(fill='x', pady=(0, 16))
            tk.Label(avatar_row, text=self.username[:1].upper(), fg=self.WHITE, bg=self.BLUE_ACCENT,
                     font=('Segoe UI', 20, 'bold'), width=3, height=1).pack(side='left', padx=(0, 14))
            info_col = tk.Frame(avatar_row, bg=self.BG_DARK)
            info_col.pack(side='left')
            tk.Label(info_col, text=self.username, fg=self.WHITE, bg=self.BG_DARK, font=('Segoe UI', 14, 'bold')).pack(anchor='w')
            tk.Label(info_col, text='Compte PRO' if is_pro else 'Compte gratuit',
                     fg=self.BLUE_ACCENT if is_pro else self.TEXT_MUTED, bg=self.BG_DARK, font=('Segoe UI', 9, 'bold')).pack(anchor='w')

            row_item(parent, '👤', "Nom d'utilisateur", 'Identifiant utilisé pour la connexion', value_text=self.username)
            row_item(parent, '⭐', 'Type de compte', "Passez en PRO pour débloquer l'audit de sécurité avancé",
                      action_text=('Actif ✓' if is_pro else 'Passer en PRO'),
                      command=(None if is_pro else self._upgrade_to_pro))
            row_item(parent, '🗑', 'Supprimer le compte', 'Action définitive : toutes vos données seront perdues',
                      action_text='Supprimer', command=lambda: messagebox.showinfo('Suppression', 'Cette fonctionnalité sera bientôt disponible.'))

        def build_security(parent):
            section_title(parent, 'Mot de passe et sécurité')
            row_item(parent, '🔑', 'Mot de passe principal', 'Modifiez le mot de passe qui protège votre coffre-fort',
                      action_text='Modifier', command=self._show_change_master_password)
            row_item(parent, '🛡', 'Chiffrement des données', 'Vos mots de passe sont chiffrés avec AES/Fernet', value_text='Activé ✓')
            row_item(parent, '📶', 'Sessions actives', 'Gérez les appareils connectés à votre compte',
                      action_text='Voir', command=lambda: messagebox.showinfo('Sessions', 'Une seule session active : cet appareil.'))
            row_item(parent, '🚪', 'Déconnexion', 'Fermer votre session sur cet appareil',
                      action_text='Déconnexion', command=self._on_logout)

        def build_privacy(parent):
            section_title(parent, 'Confidentialité')
            row_item(parent, '🕵', 'Visibilité des mots de passe', 'Masqués par défaut, affichés uniquement sur demande', value_text='Masqué ✓')
            row_item(parent, '📤', 'Export des données', 'Téléchargez une copie de vos identifiants enregistrés',
                      action_text='Exporter', command=lambda: messagebox.showinfo('Export', 'Cette fonctionnalité sera bientôt disponible.'))
            row_item(parent, '📜', "Journal d'activité", 'Historique des connexions et modifications',
                      action_text='Voir', command=lambda: messagebox.showinfo('Journal', 'Cette fonctionnalité sera bientôt disponible.'))

        def build_notifications(parent):
            section_title(parent, 'Notifications')
            for text in (
                'Alertes de sécurité (mot de passe faible ou réutilisé)',
                'Conseils et bonnes pratiques',
            ):
                row = tk.Frame(parent, bg=self.CARD_BLACK)
                row.pack(fill='x', pady=6)
                inner = tk.Frame(row, bg=self.CARD_BLACK)
                inner.pack(fill='x', padx=16, pady=12)
                tk.Label(inner, text=text, fg=self.WHITE, bg=self.CARD_BLACK, font=('Segoe UI', 10, 'bold'),
                         wraplength=420, justify='left').pack(side='left')
                var = tk.BooleanVar(value=True)
                tk.Checkbutton(inner, variable=var, bg=self.CARD_BLACK, selectcolor=self.CARD_BLACK,
                               activebackground=self.CARD_BLACK).pack(side='right')

        def build_help(parent):
            section_title(parent, 'Aide et assistance')
            row_item(parent, '📖', "Centre d'aide", "Consultez nos guides d'utilisation",
                      action_text='Ouvrir', command=lambda: messagebox.showinfo('Aide', 'Documentation à venir.'))
            row_item(parent, '✉️', 'Contacter le support', 'Une question ? Écrivez-nous',
                      action_text='Contacter', command=lambda: messagebox.showinfo('Support', 'support@mamy-password.local'))
            row_item(parent, 'ℹ️', 'À propos', 'mamy password manager', value_text='v1.0')

        def refresh_panel():
            for widget in panel.winfo_children():
                widget.destroy()
            highlight_sidebar()
            builders = {
                'compte': build_account,
                'securite': build_security,
                'confidentialite': build_privacy,
                'notifications': build_notifications,
                'aide': build_help,
            }
            builders.get(self._settings_category, build_account)(panel)

        def select_category(key):
            self._settings_category = key
            refresh_panel()

        refresh_panel()

    def _on_menu_click(self, menu_name):
        self._set_active_menu(menu_name)
        self._render_menu_content(menu_name)

    def _load_passwords_list(self):
        """Recharge la liste des mots de passe de l'utilisateur depuis PasswordService (déchiffrés à la volée)."""
        try:
            for row in self.passwords_tree.get_children():
                self.passwords_tree.delete(row)
            entries = self.password_service.list_passwords(self.username)
            for entry in entries:
                self.passwords_tree.insert(
                    '', tk.END, iid=entry['id'],
                    values=(entry['site'], entry['username'], '•' * 10),
                )
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des mots de passe: {e}")

    def _get_selected_entry(self):
        selection = self.passwords_tree.selection()
        if not selection:
            messagebox.showwarning('Sélection', "Veuillez sélectionner un mot de passe dans la liste.")
            return None
        entry_id = selection[0]
        for entry in self.password_service.list_passwords(self.username):
            if entry['id'] == entry_id:
                return entry
        return None

    def _show_add_password(self):
        self._open_password_dialog(mode='add')

    def _edit_selected_password(self):
        entry = self._get_selected_entry()
        if entry:
            self._open_password_dialog(mode='edit', entry=entry)

    def _show_selected_password(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Mot de passe — {entry['site']}")
        dialog.configure(bg=self.BG_DARK)
        dialog.geometry('420x220')
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text=entry['site'], fg=self.WHITE, bg=self.BG_DARK, font=('Segoe UI', 13, 'bold')).pack(pady=(16, 4))
        tk.Label(dialog, text=f"Identifiant : {entry['username']}", fg=self.TEXT_MUTED, bg=self.BG_DARK).pack(pady=(0, 10))

        pwd_entry = tk.Entry(dialog, bg=self.CARD_BLACK, fg=self.WHITE, insertbackground=self.WHITE, justify='center', font=('Consolas', 12))
        pwd_entry.insert(0, entry['password'])
        pwd_entry.config(state='readonly', readonlybackground=self.CARD_BLACK)
        pwd_entry.pack(fill='x', padx=24, pady=(0, 14))

        def copy_password():
            self.root.clipboard_clear()
            self.root.clipboard_append(entry['password'])
            self.root.update()
            messagebox.showinfo('Copié', 'Mot de passe copié dans le presse-papiers', parent=dialog)

        tk.Button(dialog, text='📋 Copier', bg=self.BLUE_ACCENT, fg=self.BG_DARK, relief='flat', font=('Segoe UI', 10, 'bold'), command=copy_password).pack(pady=(4, 8), ipadx=10, ipady=4)
        tk.Button(dialog, text='Fermer', bg=self.CARD_BLACK, fg=self.WHITE, relief='flat', command=dialog.destroy).pack()

    def _delete_selected_password(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        if messagebox.askyesno('Confirmer', f"Supprimer le mot de passe de « {entry['site']} » ?"):
            if self.password_service.delete_password(self.username, entry['id']):
                self._load_passwords_list()
            else:
                messagebox.showerror('Erreur', "Impossible de supprimer cette entrée.")

    def _open_password_dialog(self, mode='add', entry=None):
        """Boîte de dialogue unique pour ajouter ou modifier un mot de passe,
        avec générateur de mots de passe sécurisés personnalisable."""
        dialog = tk.Toplevel(self.root)
        dialog.title('Ajouter un mot de passe' if mode == 'add' else 'Modifier le mot de passe')
        dialog.configure(bg=self.BG_DARK)
        dialog.geometry('440x440')
        dialog.resizable(False, False)
        dialog.grab_set()

        def field(label_text, show=None, initial=''):
            tk.Label(dialog, text=label_text, fg=self.WHITE, bg=self.BG_DARK).pack(anchor='w', padx=20, pady=(12, 2))
            e = tk.Entry(dialog, bg=self.CARD_BLACK, fg=self.WHITE, insertbackground=self.WHITE, show=show)
            e.insert(0, initial)
            e.pack(fill='x', padx=20)
            return e

        site_entry = field('Site / Application', initial=entry['site'] if entry else '')
        user_entry = field("Identifiant / Nom d'utilisateur", initial=entry['username'] if entry else '')

        tk.Label(dialog, text='Mot de passe', fg=self.WHITE, bg=self.BG_DARK).pack(anchor='w', padx=20, pady=(12, 2))
        pwd_row = tk.Frame(dialog, bg=self.BG_DARK)
        pwd_row.pack(fill='x', padx=20)
        pwd_entry = tk.Entry(pwd_row, bg=self.CARD_BLACK, fg=self.WHITE, insertbackground=self.WHITE)
        pwd_entry.insert(0, entry['password'] if entry else '')
        pwd_entry.pack(side='left', fill='x', expand=True)

        show_pwd_var = tk.BooleanVar(value=False)

        def toggle_show():
            pwd_entry.config(show='' if show_pwd_var.get() else '*')

        pwd_entry.config(show='*')
        tk.Checkbutton(dialog, text='Afficher', variable=show_pwd_var, command=toggle_show,
                        fg=self.WHITE, bg=self.BG_DARK, selectcolor=self.CARD_BLACK,
                        activebackground=self.BG_DARK, activeforeground=self.WHITE).pack(anchor='w', padx=18)

        # --- Générateur ---
        gen_box = tk.LabelFrame(dialog, text='Générateur de mot de passe sécurisé', fg=self.BLUE_ACCENT, bg=self.BG_DARK, font=('Segoe UI', 9, 'bold'))
        gen_box.pack(fill='x', padx=20, pady=(14, 6))

        len_row = tk.Frame(gen_box, bg=self.BG_DARK)
        len_row.pack(fill='x', padx=10, pady=(8, 4))
        tk.Label(len_row, text='Longueur :', fg=self.WHITE, bg=self.BG_DARK).pack(side='left')
        length_var = tk.IntVar(value=16)
        tk.Spinbox(len_row, from_=6, to=64, width=5, textvariable=length_var,
                   bg=self.CARD_BLACK, fg=self.WHITE, insertbackground=self.WHITE, buttonbackground=self.CARD_BLACK).pack(side='left', padx=8)

        upper_var = tk.BooleanVar(value=True)
        lower_var = tk.BooleanVar(value=True)
        digits_var = tk.BooleanVar(value=True)
        symbols_var = tk.BooleanVar(value=True)

        opts_row = tk.Frame(gen_box, bg=self.BG_DARK)
        opts_row.pack(fill='x', padx=10, pady=(0, 4))
        for text, var in (
            ('Majuscules (A-Z)', upper_var),
            ('Minuscules (a-z)', lower_var),
            ('Chiffres (0-9)', digits_var),
            ('Symboles (!@#…)', symbols_var),
        ):
            tk.Checkbutton(opts_row, text=text, variable=var, fg=self.WHITE, bg=self.BG_DARK,
                            selectcolor=self.CARD_BLACK, activebackground=self.BG_DARK,
                            activeforeground=self.WHITE, anchor='w').pack(anchor='w')

        def generate():
            try:
                new_pw = self.password_service.generate_password(
                    length=length_var.get(),
                    use_upper=upper_var.get(),
                    use_lower=lower_var.get(),
                    use_digits=digits_var.get(),
                    use_symbols=symbols_var.get(),
                )
            except Exception as e:
                messagebox.showerror('Erreur', f"Impossible de générer un mot de passe: {e}", parent=dialog)
                return
            pwd_entry.delete(0, tk.END)
            pwd_entry.insert(0, new_pw)
            show_pwd_var.set(True)
            toggle_show()

        tk.Button(gen_box, text='🎲 Générer automatiquement', bg=self.BLUE_ACCENT, fg=self.BG_DARK,
                  font=('Segoe UI', 9, 'bold'), relief='flat', command=generate).pack(pady=(4, 10), ipadx=8, ipady=4)

        def save():
            site = site_entry.get().strip()
            account_username = user_entry.get().strip()
            password = pwd_entry.get()

            if not site or not account_username or not password:
                messagebox.showwarning('Validation', 'Tous les champs sont requis.', parent=dialog)
                return

            if mode == 'add':
                self.password_service.add_password(self.username, site, account_username, password)
            else:
                self.password_service.update_password(self.username, entry['id'], site, account_username, password)

            dialog.destroy()
            self._load_passwords_list()

        action_frame = tk.Frame(dialog, bg=self.BG_DARK)
        action_frame.pack(fill='x', padx=20, pady=(6, 16))
        tk.Button(action_frame, text='Enregistrer (chiffré)', bg=self.GREEN_ACCENT, fg=self.BG_DARK,
                  font=('Segoe UI', 10, 'bold'), relief='flat', command=save).pack(side='left', ipady=6, ipadx=12)
        tk.Button(action_frame, text='Annuler', bg=self.CARD_BLACK, fg=self.WHITE, relief='flat', command=dialog.destroy).pack(side='left', padx=10, ipady=6, ipadx=12)

    def _show_change_master_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title('Changer le mot de passe principal')
        dialog.configure(bg=self.BG_DARK)
        dialog.geometry('420x260')
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text='Ancien mot de passe', fg=self.WHITE, bg=self.BG_DARK).pack(anchor='w', padx=20, pady=(20, 4))
        old_entry = tk.Entry(dialog, bg=self.CARD_BLACK, fg=self.WHITE, insertbackground=self.WHITE, show='*')
        old_entry.pack(fill='x', padx=20, pady=(0, 10))

        tk.Label(dialog, text='Nouveau mot de passe', fg=self.WHITE, bg=self.BG_DARK).pack(anchor='w', padx=20, pady=(0, 4))
        new_entry = tk.Entry(dialog, bg=self.CARD_BLACK, fg=self.WHITE, insertbackground=self.WHITE, show='*')
        new_entry.pack(fill='x', padx=20, pady=(0, 10))

        tk.Label(dialog, text='Confirmer le nouveau mot de passe', fg=self.WHITE, bg=self.BG_DARK).pack(anchor='w', padx=20, pady=(0, 4))
        confirm_entry = tk.Entry(dialog, bg=self.CARD_BLACK, fg=self.WHITE, insertbackground=self.WHITE, show='*')
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

        action_frame = tk.Frame(dialog, bg=self.BG_DARK)
        action_frame.pack(fill='x', padx=20, pady=(0, 20))

        tk.Button(action_frame, text='Valider', bg=self.BLUE_ACCENT, fg=self.BG_DARK, relief='flat', font=('Segoe UI', 10, 'bold'), command=change_password).pack(side='left', ipady=6, ipadx=15)
        tk.Button(action_frame, text='Annuler', bg=self.CARD_BLACK, fg=self.WHITE, relief='flat', font=('Segoe UI', 10), command=dialog.destroy).pack(side='left', padx=10, ipady=6, ipadx=15)

    def _on_logout(self):
        if messagebox.askyesno("Déconnexion", "Êtes-vous sûr de vouloir vous déconnecter?"):
            self.root.destroy()

