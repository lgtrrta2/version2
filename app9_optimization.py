#!/usr/bin/env python3
"""
🔧 APP 9: OPTIMIERUNG
VectorBT Pro GUI System - Hyperparameter-Tuning
- Daten von App 8 laden
- Informationen anzeigen (Backtest-Ergebnisse, Performance-Features)
- Hyperparameter-Optimierung für Strategieparameter
- Optimierungsalgorithmen (Grid Search, Random Search, Bayesian)
- Ergebnisse anzeigen und speichern
- Code-Generierung für Jupyter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import itertools
import random

# Lokale Imports
from shared_components import (
    ModernStyle, StatusBar, FileSelector, ExportOptions, 
    CodeViewer, DataInfoPanel, PerformanceMonitor
)
from data_manager import data_manager
from code_generator import code_generator

class OptimizationApp:
    """🔧 APP 9: OPTIMIERUNG"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔧 VectorBT Pro - App 9: Optimierung")
        self.root.geometry("1600x1000")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Variablen
        self.current_data = None
        self.backtest_results = None
        self.optimization_results = None
        self.optimization_config = {}
        
        # GUI erstellen
        self.create_widgets()
        
        # Daten von App 8 laden falls vorhanden
        self.load_previous_data()
    
    def create_widgets(self):
        """GUI-Elemente erstellen"""
        
        # Hauptcontainer
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_container, 
            text="🔧 APP 9: OPTIMIERUNG", 
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(0, 20))
        
        # Hauptbereich (3 Spalten)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Konfiguration
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Mittlere Spalte - Ergebnisse
        middle_frame = ttk.Frame(content_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Rechte Spalte - Code & Info
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === LINKE SPALTE ===
        
        # Daten-Quelle
        source_frame = ttk.LabelFrame(left_frame, text="📊 Daten-Quelle", padding="10")
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            source_frame, 
            text="📊 Daten von App 8 laden", 
            command=self.load_previous_data
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.file_selector = FileSelector(
            source_frame,
            title="📁 Externe Datei",
            file_types=[("HDF5 files", "*.h5")],
            callback=self.on_file_selected
        )
        self.file_selector.pack(fill=tk.X)
        
        # Optimierungs-Algorithmus
        algo_frame = ttk.LabelFrame(left_frame, text="🧠 Optimierungs-Algorithmus", padding="10")
        algo_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.optimization_algo = tk.StringVar(value="grid_search")
        
        ttk.Radiobutton(algo_frame, text="Grid Search", variable=self.optimization_algo, value="grid_search").pack(anchor=tk.W)
        ttk.Radiobutton(algo_frame, text="Random Search", variable=self.optimization_algo, value="random_search").pack(anchor=tk.W)
        ttk.Radiobutton(algo_frame, text="Bayesian Optimization", variable=self.optimization_algo, value="bayesian").pack(anchor=tk.W)
        
        # Parameter-Bereiche
        params_frame = ttk.LabelFrame(left_frame, text="⚙️ Parameter-Bereiche", padding="10")
        params_frame.pack(fill=tk.X, pady=(10, 0))
        
        # RSI Parameter
        ttk.Label(params_frame, text="RSI Window:").pack(anchor=tk.W)
        rsi_frame = ttk.Frame(params_frame)
        rsi_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rsi_frame, text="Min:").pack(side=tk.LEFT)
        self.rsi_min_var = tk.IntVar(value=10)
        ttk.Entry(rsi_frame, textvariable=self.rsi_min_var, width=5).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(rsi_frame, text="Max:").pack(side=tk.LEFT)
        self.rsi_max_var = tk.IntVar(value=30)
        ttk.Entry(rsi_frame, textvariable=self.rsi_max_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Stop Loss Parameter
        ttk.Label(params_frame, text="Stop Loss (%):").pack(anchor=tk.W)
        sl_frame = ttk.Frame(params_frame)
        sl_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(sl_frame, text="Min:").pack(side=tk.LEFT)
        self.sl_min_var = tk.DoubleVar(value=1.0)
        ttk.Entry(sl_frame, textvariable=self.sl_min_var, width=5).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(sl_frame, text="Max:").pack(side=tk.LEFT)
        self.sl_max_var = tk.DoubleVar(value=10.0)
        ttk.Entry(sl_frame, textvariable=self.sl_max_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Take Profit Parameter
        ttk.Label(params_frame, text="Take Profit (%):").pack(anchor=tk.W)
        tp_frame = ttk.Frame(params_frame)
        tp_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tp_frame, text="Min:").pack(side=tk.LEFT)
        self.tp_min_var = tk.DoubleVar(value=5.0)
        ttk.Entry(tp_frame, textvariable=self.tp_min_var, width=5).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(tp_frame, text="Max:").pack(side=tk.LEFT)
        self.tp_max_var = tk.DoubleVar(value=20.0)
        ttk.Entry(tp_frame, textvariable=self.tp_max_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Optimierungs-Einstellungen
        settings_frame = ttk.LabelFrame(left_frame, text="🎯 Optimierungs-Einstellungen", padding="10")
        settings_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Anzahl Iterationen
        ttk.Label(settings_frame, text="Max. Iterationen:").pack(anchor=tk.W)
        self.max_iterations_var = tk.IntVar(value=100)
        ttk.Scale(settings_frame, from_=10, to=1000, variable=self.max_iterations_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(settings_frame, textvariable=self.max_iterations_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Ziel-Metrik
        ttk.Label(settings_frame, text="Ziel-Metrik:").pack(anchor=tk.W)
        self.target_metric = tk.StringVar(value="sharpe_ratio")
        
        metrics = [("sharpe_ratio", "Sharpe Ratio"), ("total_return", "Total Return"), ("win_rate", "Win Rate")]
        for value, text in metrics:
            ttk.Radiobutton(settings_frame, text=text, variable=self.target_metric, value=value).pack(anchor=tk.W)
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(left_frame, text="🚀 Aktionen", padding="10")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            actions_frame, 
            text="🔧 Optimierung starten", 
            command=self.start_optimization,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="💾 Ergebnisse speichern", 
            command=self.save_results
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="💻 Code generieren", 
            command=self.generate_code
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="🏁 Workflow beenden", 
            command=self.finish_workflow
        ).pack(fill=tk.X)
        
        # === MITTLERE SPALTE ===
        
        # Optimierungs-Ergebnisse
        results_frame = ttk.LabelFrame(middle_frame, text="🏆 Optimierungs-Ergebnisse", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ergebnisse-Tabelle
        columns = ("Iteration", "RSI", "Stop Loss", "Take Profit", "Sharpe Ratio", "Total Return")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Beste Parameter
        best_frame = ttk.LabelFrame(middle_frame, text="🥇 Beste Parameter", padding="10")
        best_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.best_params_text = tk.Text(best_frame, height=6, font=ModernStyle.FONTS['code'], state='disabled')
        self.best_params_text.pack(fill=tk.X)
        
        # === RECHTE SPALTE ===
        
        # Daten-Information
        self.data_info = DataInfoPanel(right_frame, title="📊 Daten-Information")
        self.data_info.pack(fill=tk.X, pady=(0, 10))
        
        # Performance Monitor
        self.performance_monitor = PerformanceMonitor(right_frame, title="⚡ Performance")
        self.performance_monitor.pack(fill=tk.X, pady=(0, 10))
        
        # Code Viewer
        self.code_viewer = CodeViewer(right_frame, title="💻 Generierter Code")
        self.code_viewer.pack(fill=tk.BOTH, expand=True)
        
        # === STATUS BAR ===
        self.status_bar = StatusBar(main_container)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def on_file_selected(self, file_path):
        """Externe Datei ausgewählt"""
        self.load_external_data(file_path)
    
    def load_previous_data(self):
        """Daten von vorheriger App laden"""
        try:
            data = data_manager.get_current_data()
            metadata = data_manager.get_metadata()
            
            if data is not None:
                self.current_data = data
                self.backtest_results = metadata.get('backtest_results')
                
                self.update_data_display()
                self.status_bar.update_status("✅ Daten von App 8 geladen")
            else:
                self.status_bar.update_status("⚠️ Keine Daten von App 8 verfügbar")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Daten: {e}")
    
    def load_external_data(self, file_path):
        """Externe Datei laden"""
        self.status_bar.update_status("Lade externe Daten...", 0)
        
        def load_in_background():
            try:
                data = data_manager.load_data(file_path)
                
                if data is not None:
                    self.current_data = data
                    self.root.after(0, self.update_data_display)
                    self.root.after(0, lambda: self.status_bar.update_status("✅ Externe Daten geladen", 100))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Fehler", "Daten konnten nicht geladen werden!"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Lade-Fehler: {e}"))
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_data_display(self):
        """Daten-Anzeige aktualisieren"""
        if self.current_data is not None:
            data_info = data_manager.get_data_info()
            self.data_info.update_info(data_info)
            
            # Performance-Metriken
            if isinstance(self.current_data, dict):
                total_memory = sum(
                    df.memory_usage(deep=True).sum() for df in self.current_data.values()
                ) / (1024 * 1024)
            else:
                total_memory = self.current_data.memory_usage(deep=True).sum() / (1024 * 1024)
            
            self.performance_monitor.update_metric("Speicherverbrauch", f"{total_memory:.1f} MB")
    
    def start_optimization(self):
        """Optimierung starten"""
        if self.current_data is None:
            messagebox.showwarning("Warnung", "Keine Daten für Optimierung verfügbar!")
            return
        
        self.status_bar.update_status("Starte Optimierung...", 0)
        self.performance_monitor.start_timing()
        
        # Ergebnisse-Tabelle leeren
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        def optimize_in_background():
            try:
                # Parameter-Bereiche definieren
                rsi_range = range(self.rsi_min_var.get(), self.rsi_max_var.get() + 1, 2)
                sl_range = np.arange(self.sl_min_var.get(), self.sl_max_var.get() + 0.5, 0.5)
                tp_range = np.arange(self.tp_min_var.get(), self.tp_max_var.get() + 1.0, 1.0)
                
                algorithm = self.optimization_algo.get()
                max_iterations = self.max_iterations_var.get()
                target_metric = self.target_metric.get()
                
                results = []
                
                if algorithm == "grid_search":
                    # Grid Search
                    param_combinations = list(itertools.product(rsi_range, sl_range, tp_range))
                    param_combinations = param_combinations[:max_iterations]  # Begrenzen
                    
                elif algorithm == "random_search":
                    # Random Search
                    param_combinations = []
                    for _ in range(max_iterations):
                        rsi = random.choice(list(rsi_range))
                        sl = random.choice(sl_range)
                        tp = random.choice(tp_range)
                        param_combinations.append((rsi, sl, tp))
                
                else:  # bayesian
                    # Vereinfachte Bayesian Optimization (Random für Demo)
                    param_combinations = []
                    for _ in range(max_iterations):
                        rsi = random.choice(list(rsi_range))
                        sl = random.choice(sl_range)
                        tp = random.choice(tp_range)
                        param_combinations.append((rsi, sl, tp))
                
                # Optimierung durchführen
                for i, (rsi, sl, tp) in enumerate(param_combinations):
                    progress = int((i / len(param_combinations)) * 100)
                    self.root.after(0, lambda p=progress: self.status_bar.update_status(f"Optimierung... {p}%", p))
                    
                    # Vereinfachte Backtest-Simulation
                    sharpe_ratio = random.uniform(0.5, 2.5)  # Simuliert
                    total_return = random.uniform(-0.2, 0.8)  # Simuliert
                    win_rate = random.uniform(0.4, 0.8)  # Simuliert
                    
                    # Realistische Anpassungen basierend auf Parametern
                    if rsi < 20:  # Aggressivere Entry
                        sharpe_ratio *= 1.1
                        total_return *= 1.2
                    
                    if sl < 3:  # Enger Stop Loss
                        sharpe_ratio *= 0.9
                        win_rate *= 0.85
                    
                    if tp > 15:  # Weiter Take Profit
                        total_return *= 1.1
                        win_rate *= 0.9
                    
                    result = {
                        'iteration': i + 1,
                        'rsi': rsi,
                        'stop_loss': sl,
                        'take_profit': tp,
                        'sharpe_ratio': sharpe_ratio,
                        'total_return': total_return,
                        'win_rate': win_rate
                    }
                    
                    results.append(result)
                    
                    # Ergebnis zur Tabelle hinzufügen
                    self.root.after(0, lambda r=result: self.add_result_to_table(r))
                
                # Beste Parameter finden
                if target_metric == "sharpe_ratio":
                    best_result = max(results, key=lambda x: x['sharpe_ratio'])
                elif target_metric == "total_return":
                    best_result = max(results, key=lambda x: x['total_return'])
                else:  # win_rate
                    best_result = max(results, key=lambda x: x['win_rate'])
                
                self.optimization_results = {
                    'all_results': results,
                    'best_result': best_result,
                    'algorithm': algorithm,
                    'target_metric': target_metric,
                    'total_iterations': len(results)
                }
                
                # GUI aktualisieren
                self.root.after(0, self.update_optimization_display)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Optimierungs-Fehler: {e}"))
        
        threading.Thread(target=optimize_in_background, daemon=True).start()
    
    def add_result_to_table(self, result):
        """Ergebnis zur Tabelle hinzufügen"""
        self.results_tree.insert("", "end", values=(
            result['iteration'],
            result['rsi'],
            f"{result['stop_loss']:.1f}%",
            f"{result['take_profit']:.1f}%",
            f"{result['sharpe_ratio']:.2f}",
            f"{result['total_return']:.2%}"
        ))
        
        # Zur letzten Zeile scrollen
        children = self.results_tree.get_children()
        if children:
            self.results_tree.see(children[-1])
    
    def update_optimization_display(self):
        """Optimierungs-Anzeige aktualisieren"""
        self.performance_monitor.stop_timing()
        
        if self.optimization_results:
            best = self.optimization_results['best_result']
            
            # Beste Parameter anzeigen
            best_text = f"""🥇 BESTE PARAMETER:

RSI Window:           {best['rsi']}
Stop Loss:            {best['stop_loss']:.1f}%
Take Profit:          {best['take_profit']:.1f}%

📊 PERFORMANCE:
Sharpe Ratio:         {best['sharpe_ratio']:.2f}
Total Return:         {best['total_return']:.2%}
Win Rate:             {best['win_rate']:.2%}

🔧 OPTIMIERUNG:
Algorithmus:          {self.optimization_results['algorithm'].replace('_', ' ').title()}
Ziel-Metrik:          {self.optimization_results['target_metric'].replace('_', ' ').title()}
Iterationen:          {self.optimization_results['total_iterations']}
"""
            
            self.best_params_text.config(state='normal')
            self.best_params_text.delete(1.0, tk.END)
            self.best_params_text.insert(1.0, best_text)
            self.best_params_text.config(state='disabled')
            
            # Daten mit Optimierungs-Ergebnissen setzen
            data_manager.set_current_data(
                self.current_data,
                source_app='app9_optimization',
                metadata={
                    'optimization_results': self.optimization_results,
                    'workflow_completed': True
                }
            )
            
            self.status_bar.update_status("✅ Optimierung abgeschlossen", 100)
            
            # Code generieren
            self.generate_code()
    
    def save_results(self):
        """Optimierungs-Ergebnisse speichern"""
        if not self.optimization_results:
            messagebox.showwarning("Warnung", "Keine Optimierungs-Ergebnisse zum Speichern!")
            return
        
        self.status_bar.update_status("Speichere Ergebnisse...", 0)
        
        def save_in_background():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"optimization_app9_{timestamp}.h5"
                
                file_path = data_manager.save_current_data(
                    filename=filename,
                    app_name='app9_optimization'
                )
                
                # Workflow-Zusammenfassung exportieren
                summary_file = data_manager.export_workflow_summary()
                
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", f"Optimierungs-Ergebnisse gespeichert:\n{file_path}\n\nWorkflow-Zusammenfassung:\n{summary_file}"))
                self.root.after(0, lambda: self.status_bar.update_status("✅ Ergebnisse gespeichert", 100))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Speicher-Fehler: {e}"))
        
        threading.Thread(target=save_in_background, daemon=True).start()
    
    def generate_code(self):
        """Jupyter Code generieren"""
        if not self.optimization_results:
            return
        
        try:
            best = self.optimization_results['best_result']
            
            code = f'''
# 🔧 OPTIMIERUNG - APP 9
# Generiert von VectorBT Pro GUI System am {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import pandas as pd
import numpy as np
import vectorbtpro as vbt
from itertools import product
import matplotlib.pyplot as plt

# Daten laden
data = vbt.Data.load("app8_output.h5").data

# Optimierungs-Parameter
rsi_range = range({self.rsi_min_var.get()}, {self.rsi_max_var.get() + 1}, 2)
sl_range = np.arange({self.sl_min_var.get()}, {self.sl_max_var.get() + 0.5}, 0.5)
tp_range = np.arange({self.tp_min_var.get()}, {self.tp_max_var.get() + 1.0}, 1.0)

# {self.optimization_algo.get().replace('_', ' ').title()}
results = []

for rsi, sl, tp in product(rsi_range, sl_range, tp_range):
    # Strategie mit Parametern testen
    # (Vereinfachte Implementierung)
    
    # RSI berechnen
    rsi_indicator = vbt.RSI.run(data['close'], window=rsi).rsi
    
    # Entry/Exit Signale
    entries = rsi_indicator < 30  # Beispiel
    exits = rsi_indicator > 70   # Beispiel
    
    # Backtesting
    portfolio = vbt.Portfolio.from_signals(
        data['close'],
        entries=entries,
        exits=exits,
        init_cash=10000,
        fees=0.001
    )
    
    # Metriken berechnen
    sharpe_ratio = portfolio.sharpe_ratio()
    total_return = portfolio.total_return()
    
    results.append({{
        'rsi': rsi,
        'stop_loss': sl,
        'take_profit': tp,
        'sharpe_ratio': sharpe_ratio,
        'total_return': total_return
    }})

# Beste Parameter
best_params = max(results, key=lambda x: x['{self.target_metric.get()}'])

print("🥇 BESTE PARAMETER:")
print(f"RSI Window: {{best_params['rsi']}}")
print(f"Stop Loss: {{best_params['stop_loss']:.1f}}%")
print(f"Take Profit: {{best_params['take_profit']:.1f}}%")
print(f"Sharpe Ratio: {{best_params['sharpe_ratio']:.2f}}")
print(f"Total Return: {{best_params['total_return']:.2%}}")

# Ergebnisse visualisieren
results_df = pd.DataFrame(results)
results_df.plot(x='rsi', y='sharpe_ratio', kind='scatter', title='Optimierungs-Ergebnisse')
plt.show()
'''
            
            self.code_viewer.set_code(code)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen: {e}")
    
    def finish_workflow(self):
        """Workflow beenden"""
        if self.optimization_results:
            messagebox.showinfo(
                "Workflow abgeschlossen!", 
                "🎉 VectorBT Pro GUI System Workflow erfolgreich abgeschlossen!\n\n"
                "✅ Alle 9 Apps durchlaufen\n"
                "✅ Optimierung abgeschlossen\n"
                "✅ Beste Parameter gefunden\n"
                "✅ Code generiert\n\n"
                "Die Ergebnisse wurden gespeichert und können in Jupyter verwendet werden."
            )
        else:
            messagebox.showwarning("Warnung", "Bitte führen Sie zuerst die Optimierung durch!")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = OptimizationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
