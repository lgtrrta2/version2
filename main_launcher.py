#!/usr/bin/env python3
"""
🚀 VECTORBT PRO GUI SYSTEM - HAUPTMENÜ
Launcher für alle 9 Apps des VectorBT Pro GUI Systems

VOLLSTÄNDIGES SYSTEM:
✅ App 1: Historische Daten Loader
✅ App 2: Daten Resampling  
✅ App 3: Indikatoren Manager
✅ App 4: Visualisierung (Kontrolle)
✅ App 5: VBT Features & Strategieparameter
✅ App 6: Strategieentwicklung
✅ App 7: Strategie-Visualisierung
✅ App 8: Backtesting
✅ App 9: Optimierung

🚀 PERFORMANCE-FEATURES:
- VectorBT Pro optimiert
- Blosc Kompression
- Numba Acceleration
- Memory Optimization
- Cache Management
- Parallel Processing
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
from datetime import datetime
import threading

# Lokale Imports
from shared_components import ModernStyle, StatusBar, DataInfoPanel, PerformanceMonitor
from data_manager import data_manager

class MainLauncher:
    """🚀 HAUPTMENÜ - VectorBT Pro GUI System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 VectorBT Pro GUI System - Hauptmenü")
        self.root.geometry("1200x800")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Apps-Konfiguration
        self.apps = [
            {
                'id': 1,
                'name': 'Historische Daten Loader',
                'description': 'Daten laden, Zeitraumauswahl, VBT-konforme Speicherung',
                'file': 'app1_data_loader.py',
                'icon': '📊',
                'status': 'ready'
            },
            {
                'id': 2,
                'name': 'Daten Resampling',
                'description': 'Multi/Single-Timeframe Resampling',
                'file': 'app2_resampling.py',
                'icon': '🔄',
                'status': 'ready'
            },
            {
                'id': 3,
                'name': 'Indikatoren Manager',
                'description': '551 Indikatoren mit Parameter-Validierung',
                'file': 'app3_indicators.py',
                'icon': '📈',
                'status': 'ready'
            },
            {
                'id': 4,
                'name': 'Visualisierung (Kontrolle)',
                'description': 'TradingView-ähnliche Charts, CSV-Export',
                'file': 'app4_visualization.py',
                'icon': '📊',
                'status': 'ready'
            },
            {
                'id': 5,
                'name': 'VBT Features & Strategieparameter',
                'description': 'VBT Pro Features, Strategieparameter-Setup',
                'file': 'app5_features.py',
                'icon': '⚙️',
                'status': 'ready'
            },
            {
                'id': 6,
                'name': 'Strategieentwicklung',
                'description': 'Form-basierter Strategie-Builder',
                'file': 'app6_strategy_builder.py',
                'icon': '🎯',
                'status': 'ready'
            },
            {
                'id': 7,
                'name': 'Strategie-Visualisierung',
                'description': 'Entry/Exit/Stop-Loss Visualisierung',
                'file': 'app7_strategy_viz.py',
                'icon': '📊',
                'status': 'ready'
            },
            {
                'id': 8,
                'name': 'Backtesting',
                'description': 'Performance-optimiertes Backtesting',
                'file': 'app8_backtesting.py',
                'icon': '🚀',
                'status': 'ready'
            },
            {
                'id': 9,
                'name': 'Optimierung',
                'description': 'Hyperparameter-Tuning',
                'file': 'app9_optimization.py',
                'icon': '🔧',
                'status': 'ready'
            }
        ]
        
        # GUI erstellen
        self.create_widgets()
        
        # System-Check durchführen
        self.check_system()
    
    def create_widgets(self):
        """GUI-Elemente erstellen"""
        
        # Hauptcontainer
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Titel
        title_label = ttk.Label(
            header_frame,
            text="🚀 VectorBT Pro GUI System",
            font=('Segoe UI', 24, 'bold')
        )
        title_label.pack()
        
        # Untertitel
        subtitle_label = ttk.Label(
            header_frame,
            text="Vollständiges Trading-System mit 9 Apps | Performance-optimiert | Professionell",
            font=ModernStyle.FONTS['subtitle']
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Hauptbereich (2 Spalten)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Apps
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Rechte Spalte - Info & Status
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === LINKE SPALTE: APPS ===
        
        # Apps-Header
        apps_header_frame = ttk.Frame(left_frame)
        apps_header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            apps_header_frame,
            text="📱 Verfügbare Apps",
            font=ModernStyle.FONTS['title']
        ).pack(side=tk.LEFT)
        
        # Workflow-Buttons
        workflow_frame = ttk.Frame(apps_header_frame)
        workflow_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            workflow_frame,
            text="🔄 Sequenzieller Workflow",
            command=self.start_sequential_workflow
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            workflow_frame,
            text="🎯 Direkt zu App...",
            command=self.show_app_selector
        ).pack(side=tk.LEFT)
        
        # Apps-Grid
        self.apps_frame = ttk.Frame(left_frame)
        self.apps_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_apps_grid()
        
        # === RECHTE SPALTE: INFO & STATUS ===
        
        # System-Status
        self.system_status_frame = ttk.LabelFrame(right_frame, text="🖥️ System-Status", padding="15")
        self.system_status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.system_status_text = tk.Text(
            self.system_status_frame, 
            height=8, 
            width=40,
            font=ModernStyle.FONTS['small'],
            state='disabled'
        )
        self.system_status_text.pack(fill=tk.X)
        
        # Workflow-Status
        self.workflow_status_frame = ttk.LabelFrame(right_frame, text="📋 Workflow-Status", padding="15")
        self.workflow_status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.workflow_status_text = tk.Text(
            self.workflow_status_frame, 
            height=6, 
            width=40,
            font=ModernStyle.FONTS['small'],
            state='disabled'
        )
        self.workflow_status_text.pack(fill=tk.X)
        
        # Performance Monitor
        self.performance_monitor = PerformanceMonitor(right_frame, title="⚡ System-Performance")
        self.performance_monitor.pack(fill=tk.X, pady=(0, 20))
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(right_frame, text="🚀 Aktionen", padding="15")
        actions_frame.pack(fill=tk.X)
        
        ttk.Button(
            actions_frame,
            text="🔄 System-Check",
            command=self.check_system
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame,
            text="📊 Daten-Manager",
            command=self.open_data_manager
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame,
            text="📋 Workflow-Zusammenfassung",
            command=self.show_workflow_summary
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame,
            text="❌ Beenden",
            command=self.root.quit
        ).pack(fill=tk.X)
        
        # === STATUS BAR ===
        self.status_bar = StatusBar(main_container)
        self.status_bar.pack(fill=tk.X, pady=(20, 0))
    
    def create_apps_grid(self):
        """Apps-Grid erstellen"""
        
        # 3x3 Grid für 9 Apps
        for i, app in enumerate(self.apps):
            row = i // 3
            col = i % 3
            
            # App-Frame
            app_frame = ttk.LabelFrame(
                self.apps_frame, 
                text=f"{app['icon']} App {app['id']}: {app['name']}", 
                padding="15"
            )
            app_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Beschreibung
            desc_label = ttk.Label(
                app_frame,
                text=app['description'],
                font=ModernStyle.FONTS['small'],
                wraplength=200
            )
            desc_label.pack(pady=(0, 10))
            
            # Status
            status_color = "green" if app['status'] == 'ready' else "orange"
            status_label = ttk.Label(
                app_frame,
                text=f"Status: {app['status'].title()}",
                font=ModernStyle.FONTS['small']
            )
            status_label.pack(pady=(0, 10))
            
            # Launch Button
            launch_button = ttk.Button(
                app_frame,
                text=f"🚀 App {app['id']} starten",
                command=lambda a=app: self.launch_app(a)
            )
            launch_button.pack(fill=tk.X)
        
        # Grid-Gewichte setzen
        for i in range(3):
            self.apps_frame.columnconfigure(i, weight=1)
        for i in range(3):
            self.apps_frame.rowconfigure(i, weight=1)
    
    def launch_app(self, app):
        """App starten"""
        self.status_bar.update_status(f"Starte {app['name']}...", 0)
        
        def launch_in_background():
            try:
                if os.path.exists(app['file']):
                    # App in neuem Fenster starten
                    if app['file'] == 'app1_data_loader.py':
                        import app1_data_loader
                        app_window = tk.Toplevel(self.root)
                        app1_data_loader.DataLoaderApp(app_window)
                    elif app['file'] == 'app2_resampling.py':
                        import app2_resampling
                        app_window = tk.Toplevel(self.root)
                        app2_resampling.ResamplingApp(app_window)
                    elif app['file'] == 'app3_indicators.py':
                        import app3_indicators
                        app_window = tk.Toplevel(self.root)
                        app3_indicators.IndicatorsApp(app_window)
                    elif app['file'] == 'app4_visualization.py':
                        import app4_visualization
                        app_window = tk.Toplevel(self.root)
                        app4_visualization.VisualizationApp(app_window)
                    elif app['file'] == 'app5_features.py':
                        import app5_features
                        app_window = tk.Toplevel(self.root)
                        app5_features.FeaturesApp(app_window)
                    elif app['file'] == 'app6_strategy_builder.py':
                        import app6_strategy_builder
                        app_window = tk.Toplevel(self.root)
                        app6_strategy_builder.StrategyBuilderApp(app_window)
                    elif app['file'] == 'app7_strategy_viz.py':
                        import app7_strategy_viz
                        app_window = tk.Toplevel(self.root)
                        app7_strategy_viz.StrategyVizApp(app_window)
                    elif app['file'] == 'app8_backtesting.py':
                        import app8_backtesting
                        app_window = tk.Toplevel(self.root)
                        app8_backtesting.BacktestingApp(app_window)
                    elif app['file'] == 'app9_optimization.py':
                        import app9_optimization
                        app_window = tk.Toplevel(self.root)
                        app9_optimization.OptimizationApp(app_window)
                    
                    self.root.after(0, lambda: self.status_bar.update_status(f"✅ {app['name']} gestartet", 100))
                    
                else:
                    self.root.after(0, lambda: messagebox.showerror("Fehler", f"App-Datei nicht gefunden: {app['file']}"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Fehler beim Starten von {app['name']}: {e}"))
        
        threading.Thread(target=launch_in_background, daemon=True).start()
    
    def start_sequential_workflow(self):
        """Sequenziellen Workflow starten"""
        messagebox.showinfo(
            "Sequenzieller Workflow",
            "🔄 SEQUENZIELLER WORKFLOW\n\n"
            "1. Starten Sie mit App 1 (Daten Loader)\n"
            "2. Folgen Sie der Reihenfolge App 1 → 2 → 3 → ... → 9\n"
            "3. Jede App lädt automatisch Daten von der vorherigen App\n"
            "4. Am Ende haben Sie ein vollständiges Trading-System\n\n"
            "Klicken Sie auf 'App 1 starten' um zu beginnen!"
        )
        
        # App 1 automatisch starten
        self.launch_app(self.apps[0])
    
    def show_app_selector(self):
        """App-Auswahl Dialog anzeigen"""
        selector_window = tk.Toplevel(self.root)
        selector_window.title("App auswählen")
        selector_window.geometry("400x500")
        selector_window.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        ttk.Label(
            selector_window,
            text="🎯 Direkt zu App springen",
            font=ModernStyle.FONTS['title']
        ).pack(pady=20)
        
        # App-Liste
        for app in self.apps:
            app_frame = ttk.Frame(selector_window)
            app_frame.pack(fill=tk.X, padx=20, pady=5)
            
            ttk.Button(
                app_frame,
                text=f"{app['icon']} App {app['id']}: {app['name']}",
                command=lambda a=app: [self.launch_app(a), selector_window.destroy()]
            ).pack(fill=tk.X)
    
    def check_system(self):
        """System-Check durchführen"""
        self.status_bar.update_status("Führe System-Check durch...", 0)
        
        def check_in_background():
            try:
                status_info = "🖥️ SYSTEM-STATUS:\n\n"
                
                # Python Version
                status_info += f"Python: {sys.version.split()[0]} ✅\n"
                
                # VectorBT Pro Check
                try:
                    import vectorbtpro as vbt
                    status_info += f"VectorBT Pro: ✅ Verfügbar\n"
                except ImportError:
                    status_info += f"VectorBT Pro: ❌ Nicht verfügbar\n"
                
                # Numba Check
                try:
                    import numba
                    status_info += f"Numba: ✅ Verfügbar\n"
                except ImportError:
                    status_info += f"Numba: ❌ Nicht verfügbar\n"
                
                # Blosc Check
                try:
                    import blosc
                    status_info += f"Blosc: ✅ Verfügbar\n"
                except ImportError:
                    status_info += f"Blosc: ❌ Nicht verfügbar\n"
                
                # App-Dateien Check
                status_info += f"\n📱 APP-DATEIEN:\n"
                for app in self.apps:
                    if os.path.exists(app['file']):
                        status_info += f"App {app['id']}: ✅\n"
                    else:
                        status_info += f"App {app['id']}: ❌\n"
                
                # Ordner Check
                status_info += f"\n📁 ORDNER:\n"
                folders = ['historical_data', 'output', 'temp', 'configs']
                for folder in folders:
                    if os.path.exists(folder):
                        status_info += f"{folder}: ✅\n"
                    else:
                        status_info += f"{folder}: ❌ (wird erstellt)\n"
                        os.makedirs(folder, exist_ok=True)
                
                # GUI aktualisieren
                self.root.after(0, lambda: self.update_system_status(status_info))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"System-Check Fehler: {e}"))
        
        threading.Thread(target=check_in_background, daemon=True).start()
    
    def update_system_status(self, status_info):
        """System-Status aktualisieren"""
        self.system_status_text.config(state='normal')
        self.system_status_text.delete(1.0, tk.END)
        self.system_status_text.insert(1.0, status_info)
        self.system_status_text.config(state='disabled')
        
        self.status_bar.update_status("✅ System-Check abgeschlossen", 100)
        
        # Workflow-Status aktualisieren
        self.update_workflow_status()
    
    def update_workflow_status(self):
        """Workflow-Status aktualisieren"""
        workflow_state = data_manager.get_workflow_state()
        
        workflow_info = "📋 WORKFLOW-STATUS:\n\n"
        workflow_info += f"Aktuelle App: {workflow_state.get('current_app', 'Keine')}\n"
        workflow_info += f"Abgeschlossene Apps: {len(workflow_state.get('completed_apps', []))}/9\n\n"
        
        workflow_info += "✅ Abgeschlossen:\n"
        for app in workflow_state.get('completed_apps', []):
            workflow_info += f"  • {app}\n"
        
        if workflow_state.get('data_pipeline'):
            workflow_info += f"\n📊 Daten-Pipeline:\n"
            for entry in workflow_state['data_pipeline'][-3:]:  # Letzte 3
                workflow_info += f"  • {entry['app']}: {entry['file_size_mb']:.1f} MB\n"
        
        self.workflow_status_text.config(state='normal')
        self.workflow_status_text.delete(1.0, tk.END)
        self.workflow_status_text.insert(1.0, workflow_info)
        self.workflow_status_text.config(state='disabled')
    
    def open_data_manager(self):
        """Daten-Manager öffnen"""
        messagebox.showinfo(
            "Daten-Manager",
            "📊 DATEN-MANAGER\n\n"
            "Der Daten-Manager läuft im Hintergrund und verwaltet:\n\n"
            "• Datenfluss zwischen Apps\n"
            "• Performance-Optimierungen\n"
            "• Metadaten-Tracking\n"
            "• Cache-Management\n"
            "• Export-Funktionen\n\n"
            "Alle Apps nutzen automatisch den Daten-Manager."
        )
    
    def show_workflow_summary(self):
        """Workflow-Zusammenfassung anzeigen"""
        try:
            summary_file = data_manager.export_workflow_summary()
            if summary_file:
                messagebox.showinfo("Erfolg", f"Workflow-Zusammenfassung exportiert:\n{summary_file}")
            else:
                messagebox.showwarning("Warnung", "Keine Workflow-Daten zum Exportieren verfügbar.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export-Fehler: {e}")

def main():
    """Hauptfunktion"""
    print("🚀 VectorBT Pro GUI System wird gestartet...")
    print("=" * 60)
    print("📱 9 Apps verfügbar")
    print("🚀 Performance-optimiert")
    print("💾 VBT Pro Features aktiviert")
    print("=" * 60)
    
    root = tk.Tk()
    app = MainLauncher(root)
    
    # Fenster zentrieren
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
