#!/usr/bin/env python3
"""
📊 APP 7: VISUALISIERUNG (STRATEGIE)
VectorBT Pro GUI System - Strategie-Visualisierung
- Daten von App 6 laden
- Informationen anzeigen (Zeitraum, Asset, Multi/Single-Timeframe, Indikatoren, Strategieparameter)
- Visualisierung von Einstiegen, Ausstiegen, Stop Loss etc. auf einem Chart
- Code-Generierung für Jupyter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Lokale Imports
from shared_components import (
    ModernStyle, StatusBar, FileSelector, CodeViewer, 
    DataInfoPanel, PerformanceMonitor
)
from data_manager import data_manager
from code_generator import code_generator

class StrategyVizApp:
    """📊 APP 7: VISUALISIERUNG (STRATEGIE)"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 VectorBT Pro - App 7: Strategie-Visualisierung")
        self.root.geometry("1600x1000")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Variablen
        self.current_data = None
        self.strategy_config = None
        self.signals = None
        
        # GUI erstellen
        self.create_widgets()
        
        # Daten von App 6 laden falls vorhanden
        self.load_previous_data()
    
    def create_widgets(self):
        """GUI-Elemente erstellen"""
        
        # Hauptcontainer
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_container, 
            text="📊 APP 7: STRATEGIE-VISUALISIERUNG", 
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(0, 20))
        
        # Hauptbereich (3 Spalten)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Konfiguration
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Mittlere Spalte - Chart
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
            text="📊 Daten von App 6 laden", 
            command=self.load_previous_data
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.file_selector = FileSelector(
            source_frame,
            title="📁 Externe Datei",
            file_types=[("HDF5 files", "*.h5")],
            callback=self.on_file_selected
        )
        self.file_selector.pack(fill=tk.X)
        
        # Strategie-Info
        strategy_frame = ttk.LabelFrame(left_frame, text="🎯 Strategie-Information", padding="10")
        strategy_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.strategy_info_text = tk.Text(strategy_frame, height=10, font=ModernStyle.FONTS['small'], state='disabled')
        self.strategy_info_text.pack(fill=tk.X)
        
        # Chart-Optionen
        chart_options_frame = ttk.LabelFrame(left_frame, text="📈 Chart-Optionen", padding="10")
        chart_options_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Anzahl Kerzen
        ttk.Label(chart_options_frame, text="Anzahl Kerzen:").pack(anchor=tk.W)
        self.chart_candles_var = tk.IntVar(value=200)
        ttk.Scale(
            chart_options_frame,
            from_=50, to=1000,
            variable=self.chart_candles_var,
            orient=tk.HORIZONTAL
        ).pack(fill=tk.X)
        ttk.Label(chart_options_frame, textvariable=self.chart_candles_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Chart-Elemente
        self.show_entries_var = tk.BooleanVar(value=True)
        self.show_exits_var = tk.BooleanVar(value=True)
        self.show_stop_loss_var = tk.BooleanVar(value=True)
        self.show_take_profit_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(chart_options_frame, text="Entry Signale", variable=self.show_entries_var).pack(anchor=tk.W)
        ttk.Checkbutton(chart_options_frame, text="Exit Signale", variable=self.show_exits_var).pack(anchor=tk.W)
        ttk.Checkbutton(chart_options_frame, text="Stop Loss", variable=self.show_stop_loss_var).pack(anchor=tk.W)
        ttk.Checkbutton(chart_options_frame, text="Take Profit", variable=self.show_take_profit_var).pack(anchor=tk.W)
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(left_frame, text="🚀 Aktionen", padding="10")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            actions_frame, 
            text="📊 Signale berechnen", 
            command=self.calculate_signals,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="📈 Chart erstellen", 
            command=self.create_chart
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="💻 Code generieren", 
            command=self.generate_code
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="➡️ Zu App 8", 
            command=self.go_to_app8
        ).pack(fill=tk.X)
        
        # === MITTLERE SPALTE ===
        
        # Chart-Container
        self.chart_frame = ttk.LabelFrame(middle_frame, text="📈 Strategie-Chart", padding="10")
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder
        self.chart_placeholder = ttk.Label(
            self.chart_frame,
            text="📊 Strategie-Chart wird hier angezeigt\n\nBitte laden Sie Daten und klicken Sie auf 'Signale berechnen'",
            font=ModernStyle.FONTS['normal'],
            anchor=tk.CENTER
        )
        self.chart_placeholder.pack(expand=True)
        
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
                self.strategy_config = metadata.get('strategy_config')
                
                self.update_data_display()
                self.update_strategy_info()
                self.status_bar.update_status("✅ Daten von App 6 geladen")
            else:
                self.status_bar.update_status("⚠️ Keine Daten von App 6 verfügbar")
                
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
    
    def update_strategy_info(self):
        """Strategie-Information aktualisieren"""
        self.strategy_info_text.config(state='normal')
        self.strategy_info_text.delete(1.0, tk.END)
        
        if self.strategy_config:
            info = "🎯 STRATEGIE-KONFIGURATION:\n\n"
            
            # Entry Conditions
            entry_conditions = self.strategy_config.get('entry_conditions', [])
            info += f"🟢 Entry Bedingungen ({len(entry_conditions)}):\n"
            for condition in entry_conditions:
                info += f"  • {condition['text']}\n"
            
            # Exit Conditions
            exit_conditions = self.strategy_config.get('exit_conditions', [])
            info += f"\n🔴 Exit Bedingungen ({len(exit_conditions)}):\n"
            for condition in exit_conditions:
                info += f"  • {condition['text']}\n"
            
            # Risk Management
            risk_mgmt = self.strategy_config.get('risk_management', {})
            info += f"\n⚠️ Risk Management:\n"
            info += f"  • Position Size: {risk_mgmt.get('position_size', 1.0)*100:.1f}%\n"
            info += f"  • Stop Loss: {risk_mgmt.get('stop_loss', 0.05)*100:.1f}%\n"
            info += f"  • Take Profit: {risk_mgmt.get('take_profit', 0.1)*100:.1f}%\n"
            
            # Logic
            logic = self.strategy_config.get('logic', 'AND')
            info += f"\n🧠 Logik: {logic}\n"
            
        else:
            info = "⚠️ Keine Strategie-Konfiguration gefunden.\n\nBitte laden Sie Daten von App 6."
        
        self.strategy_info_text.insert(1.0, info)
        self.strategy_info_text.config(state='disabled')
    
    def calculate_signals(self):
        """Trading-Signale berechnen"""
        if self.current_data is None or not self.strategy_config:
            messagebox.showwarning("Warnung", "Keine Daten oder Strategie-Konfiguration verfügbar!")
            return
        
        self.status_bar.update_status("Berechne Trading-Signale...", 0)
        self.performance_monitor.start_timing()
        
        def calculate_in_background():
            try:
                # Vereinfachte Signal-Berechnung
                if isinstance(self.current_data, dict):
                    # Multi-Timeframe: Erste Timeframe nehmen
                    data = list(self.current_data.values())[0]
                else:
                    data = self.current_data
                
                # Entry Signale
                entry_signals = pd.Series(False, index=data.index)
                for condition in self.strategy_config.get('entry_conditions', []):
                    indicator = condition['indicator']
                    operator = condition['operator']
                    value = float(condition['value'])
                    
                    if indicator in data.columns:
                        if operator == '>':
                            signal = data[indicator] > value
                        elif operator == '<':
                            signal = data[indicator] < value
                        elif operator == '>=':
                            signal = data[indicator] >= value
                        elif operator == '<=':
                            signal = data[indicator] <= value
                        elif operator == '==':
                            signal = data[indicator] == value
                        else:
                            signal = pd.Series(False, index=data.index)
                        
                        if self.strategy_config.get('logic', 'AND') == 'AND':
                            entry_signals = entry_signals & signal
                        else:
                            entry_signals = entry_signals | signal
                
                # Exit Signale
                exit_signals = pd.Series(False, index=data.index)
                for condition in self.strategy_config.get('exit_conditions', []):
                    indicator = condition['indicator']
                    operator = condition['operator']
                    value = float(condition['value'])
                    
                    if indicator in data.columns:
                        if operator == '>':
                            signal = data[indicator] > value
                        elif operator == '<':
                            signal = data[indicator] < value
                        elif operator == '>=':
                            signal = data[indicator] >= value
                        elif operator == '<=':
                            signal = data[indicator] <= value
                        elif operator == '==':
                            signal = data[indicator] == value
                        else:
                            signal = pd.Series(False, index=data.index)
                        
                        if self.strategy_config.get('logic', 'AND') == 'AND':
                            exit_signals = exit_signals & signal
                        else:
                            exit_signals = exit_signals | signal
                
                self.signals = {
                    'entries': entry_signals,
                    'exits': exit_signals,
                    'data': data
                }
                
                # GUI aktualisieren
                self.root.after(0, self.update_signals_display)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Signal-Berechnungs-Fehler: {e}"))
        
        threading.Thread(target=calculate_in_background, daemon=True).start()
    
    def update_signals_display(self):
        """Signale-Anzeige aktualisieren"""
        self.performance_monitor.stop_timing()
        
        if self.signals:
            entry_count = self.signals['entries'].sum()
            exit_count = self.signals['exits'].sum()
            
            self.status_bar.update_status(f"✅ Signale berechnet: {entry_count} Entries, {exit_count} Exits", 100)
            
            # Chart automatisch erstellen
            self.create_chart()
    
    def create_chart(self):
        """Strategie-Chart erstellen"""
        if not self.signals:
            messagebox.showwarning("Warnung", "Bitte berechnen Sie zuerst die Signale!")
            return
        
        self.status_bar.update_status("Erstelle Strategie-Chart...", 0)
        
        def create_in_background():
            try:
                # Chart-Container leeren
                self.root.after(0, self.clear_chart)
                
                data = self.signals['data']
                entries = self.signals['entries']
                exits = self.signals['exits']
                
                # Daten begrenzen
                candles = self.chart_candles_var.get()
                if len(data) > candles:
                    data = data.tail(candles)
                    entries = entries.tail(candles)
                    exits = exits.tail(candles)
                
                # Chart im Main Thread erstellen
                self.root.after(0, lambda: self.create_chart_widget(data, entries, exits))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Chart-Fehler: {e}"))
        
        threading.Thread(target=create_in_background, daemon=True).start()
    
    def clear_chart(self):
        """Chart-Container leeren"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
    
    def create_chart_widget(self, data, entries, exits):
        """Chart-Widget erstellen"""
        try:
            # Matplotlib Style
            plt.style.use('dark_background')
            
            # Figure erstellen
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
            fig.patch.set_facecolor('#2b2b2b')
            
            # Hauptchart (Preis)
            ax1.plot(data.index, data['close'], color='white', linewidth=1, label='Close Price')
            
            # Entry Signale
            if self.show_entries_var.get():
                entry_points = data[entries]
                if not entry_points.empty:
                    ax1.scatter(entry_points.index, entry_points['close'], 
                              color='green', marker='^', s=100, label='Entry', zorder=5)
            
            # Exit Signale
            if self.show_exits_var.get():
                exit_points = data[exits]
                if not exit_points.empty:
                    ax1.scatter(exit_points.index, exit_points['close'], 
                              color='red', marker='v', s=100, label='Exit', zorder=5)
            
            ax1.set_title('Strategie-Visualisierung')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Indikatoren-Chart (falls vorhanden)
            indicator_cols = [col for col in data.columns if col.lower() not in ['open', 'high', 'low', 'close', 'volume']]
            if indicator_cols:
                # Ersten Indikator anzeigen
                indicator = indicator_cols[0]
                ax2.plot(data.index, data[indicator], color='orange', label=indicator)
                ax2.set_title(f'Indikator: {indicator}')
                ax2.grid(True, alpha=0.3)
                ax2.legend()
            
            plt.tight_layout()
            
            # Canvas erstellen
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.status_bar.update_status("✅ Strategie-Chart erstellt", 100)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Chart-Widget-Fehler: {e}")
    
    def generate_code(self):
        """Jupyter Code generieren"""
        if not self.signals:
            return
        
        try:
            code = f'''
# 📊 STRATEGIE-VISUALISIERUNG - APP 7
# Generiert von VectorBT Pro GUI System am {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import pandas as pd
import matplotlib.pyplot as plt
import vectorbtpro as vbt

# Daten laden
data = vbt.Data.load("app6_output.h5").data

# Strategie-Konfiguration
strategy_config = {self.strategy_config}

# Signale berechnen (vereinfacht)
entries = pd.Series(False, index=data.index)
exits = pd.Series(False, index=data.index)

# Entry Bedingungen
for condition in strategy_config['entry_conditions']:
    indicator = condition['indicator']
    operator = condition['operator']
    value = float(condition['value'])
    
    if indicator in data.columns:
        if operator == '>':
            signal = data[indicator] > value
        elif operator == '<':
            signal = data[indicator] < value
        # Weitere Operatoren...
        
        entries = entries | signal  # OR Logik (vereinfacht)

# Chart erstellen
fig, ax = plt.subplots(figsize=(15, 8))

# Preis-Chart
ax.plot(data.index, data['close'], label='Close Price')

# Entry/Exit Signale
entry_points = data[entries]
exit_points = data[exits]

ax.scatter(entry_points.index, entry_points['close'], 
          color='green', marker='^', s=100, label='Entry')
ax.scatter(exit_points.index, exit_points['close'], 
          color='red', marker='v', s=100, label='Exit')

ax.set_title('Strategie-Visualisierung')
ax.legend()
ax.grid(True)

plt.show()

print(f"✅ {{entries.sum()}} Entry-Signale, {{exits.sum()}} Exit-Signale")
'''
            
            self.code_viewer.set_code(code)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen: {e}")
    
    def go_to_app8(self):
        """Zu App 8 wechseln"""
        if not self.signals:
            messagebox.showwarning("Warnung", "Bitte berechnen Sie zuerst die Signale!")
            return
        
        try:
            import app8_backtesting
            app8_window = tk.Toplevel(self.root)
            app8_backtesting.BacktestingApp(app8_window)
        except ImportError:
            messagebox.showinfo("Info", "App 8 wird als nächstes entwickelt...")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = StrategyVizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
