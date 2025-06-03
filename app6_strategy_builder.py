#!/usr/bin/env python3
"""
🎯 APP 6: STRATEGIEENTWICKLUNG (FORM-BASIERT)
VectorBT Pro GUI System - Form-basierter Strategie-Builder
- Daten von App 5 laden
- Informationen anzeigen (Indikatoren, Performance-Features, etc.)
- Form-basierter Strategie-Builder:
  - Einfache Formulare für Strategie-Parameter
  - Dropdown-Menüs für Indikatoren (Entry/Exit)
  - Bedingungen für Indikatoren (z.B. RSI < 30)
  - Logik-Auswahl (AND/OR/Custom)
  - Risk Management (Position Size, Max Drawdown)
- Speichern als VBT-konforme Datei mit Performance-Features
- Code-Generierung für Jupyter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import threading

# Lokale Imports
from shared_components import (
    ModernStyle, StatusBar, FileSelector, ExportOptions, 
    CodeViewer, DataInfoPanel, PerformanceMonitor, ParameterPanel
)
from data_manager import data_manager
from code_generator import code_generator

class StrategyBuilderApp:
    """🎯 APP 6: STRATEGIEENTWICKLUNG (FORM-BASIERT)"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 VectorBT Pro - App 6: Strategieentwicklung")
        self.root.geometry("1600x1000")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Variablen
        self.current_data = None
        self.available_indicators = []
        self.entry_conditions = []
        self.exit_conditions = []
        self.strategy_config = {}
        
        # GUI erstellen
        self.create_widgets()
        
        # Daten von App 5 laden falls vorhanden
        self.load_previous_data()
    
    def create_widgets(self):
        """GUI-Elemente erstellen"""
        
        # Hauptcontainer
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_container, 
            text="🎯 APP 6: STRATEGIEENTWICKLUNG (FORM-BASIERT)", 
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(0, 20))
        
        # Hauptbereich (4 Spalten)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Spalte 1 - Daten & Aktionen
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Spalte 2 - Entry Conditions
        entry_frame = ttk.Frame(content_frame)
        entry_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Spalte 3 - Exit Conditions & Risk Management
        exit_frame = ttk.Frame(content_frame)
        exit_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Spalte 4 - Code & Info
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === SPALTE 1: DATEN & AKTIONEN ===
        
        # Daten-Quelle
        source_frame = ttk.LabelFrame(left_frame, text="📊 Daten-Quelle", padding="10")
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            source_frame, 
            text="📊 Daten von App 5 laden", 
            command=self.load_previous_data
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.file_selector = FileSelector(
            source_frame,
            title="📁 Externe Datei",
            file_types=[("HDF5 files", "*.h5")],
            callback=self.on_file_selected
        )
        self.file_selector.pack(fill=tk.X)
        
        # Verfügbare Indikatoren
        indicators_frame = ttk.LabelFrame(left_frame, text="📈 Verfügbare Indikatoren", padding="10")
        indicators_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.indicators_listbox = tk.Listbox(indicators_frame, height=8, font=ModernStyle.FONTS['small'])
        self.indicators_listbox.pack(fill=tk.X)
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(left_frame, text="🚀 Aktionen", padding="10")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            actions_frame, 
            text="🎯 Strategie erstellen", 
            command=self.create_strategy,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="💾 Strategie speichern", 
            command=self.save_strategy
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="💻 Code generieren", 
            command=self.generate_code
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="➡️ Zu App 7", 
            command=self.go_to_app7
        ).pack(fill=tk.X)
        
        # === SPALTE 2: ENTRY CONDITIONS ===
        
        entry_conditions_frame = ttk.LabelFrame(entry_frame, text="🟢 Entry Bedingungen", padding="10")
        entry_conditions_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_conditions_widgets(entry_conditions_frame, "entry")
        
        # === SPALTE 3: EXIT CONDITIONS & RISK MANAGEMENT ===
        
        exit_conditions_frame = ttk.LabelFrame(exit_frame, text="🔴 Exit Bedingungen", padding="10")
        exit_conditions_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_conditions_widgets(exit_conditions_frame, "exit")
        
        # Risk Management
        risk_frame = ttk.LabelFrame(exit_frame, text="⚠️ Risk Management", padding="10")
        risk_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_risk_management_widgets(risk_frame)
        
        # Strategie-Logik
        logic_frame = ttk.LabelFrame(exit_frame, text="🧠 Strategie-Logik", padding="10")
        logic_frame.pack(fill=tk.X)
        
        self.create_logic_widgets(logic_frame)
        
        # === SPALTE 4: CODE & INFO ===
        
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
    
    def create_conditions_widgets(self, parent, condition_type):
        """Bedingungen-Widgets erstellen"""
        
        # Indikator-Auswahl
        ttk.Label(parent, text="Indikator:", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        
        indicator_var = tk.StringVar()
        indicator_combo = ttk.Combobox(parent, textvariable=indicator_var, state="readonly")
        indicator_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Operator-Auswahl
        ttk.Label(parent, text="Operator:", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        
        operator_var = tk.StringVar(value=">")
        operator_frame = ttk.Frame(parent)
        operator_frame.pack(fill=tk.X, pady=(0, 10))
        
        operators = [">", "<", ">=", "<=", "==", "!="]
        for i, op in enumerate(operators):
            ttk.Radiobutton(
                operator_frame, 
                text=op, 
                variable=operator_var, 
                value=op
            ).grid(row=0, column=i, padx=2)
        
        # Wert-Eingabe
        ttk.Label(parent, text="Wert:", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        
        value_var = tk.StringVar(value="30" if condition_type == "entry" else "70")
        value_entry = ttk.Entry(parent, textvariable=value_var)
        value_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Bedingung hinzufügen Button
        ttk.Button(
            parent, 
            text=f"➕ {condition_type.title()} Bedingung hinzufügen",
            command=lambda: self.add_condition(condition_type, indicator_var, operator_var, value_var)
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Aktuelle Bedingungen
        ttk.Label(parent, text=f"Aktuelle {condition_type.title()} Bedingungen:", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        
        conditions_listbox = tk.Listbox(parent, height=6, font=ModernStyle.FONTS['small'])
        conditions_listbox.pack(fill=tk.X, pady=(0, 5))
        
        # Entfernen Button
        ttk.Button(
            parent, 
            text="➖ Entfernen",
            command=lambda: self.remove_condition(condition_type, conditions_listbox)
        ).pack(fill=tk.X)
        
        # Variablen speichern
        if condition_type == "entry":
            self.entry_indicator_var = indicator_var
            self.entry_operator_var = operator_var
            self.entry_value_var = value_var
            self.entry_conditions_listbox = conditions_listbox
            self.entry_indicator_combo = indicator_combo
        else:
            self.exit_indicator_var = indicator_var
            self.exit_operator_var = operator_var
            self.exit_value_var = value_var
            self.exit_conditions_listbox = conditions_listbox
            self.exit_indicator_combo = indicator_combo
    
    def create_risk_management_widgets(self, parent):
        """Risk Management Widgets erstellen"""
        
        # Position Size
        ttk.Label(parent, text="Position Size (%):", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        self.position_size_var = tk.DoubleVar(value=100.0)
        ttk.Scale(parent, from_=1, to=100, variable=self.position_size_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(parent, textvariable=self.position_size_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Stop Loss
        ttk.Label(parent, text="Stop Loss (%):", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        self.stop_loss_var = tk.DoubleVar(value=5.0)
        ttk.Scale(parent, from_=0.1, to=20, variable=self.stop_loss_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(parent, textvariable=self.stop_loss_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Take Profit
        ttk.Label(parent, text="Take Profit (%):", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        self.take_profit_var = tk.DoubleVar(value=10.0)
        ttk.Scale(parent, from_=1, to=50, variable=self.take_profit_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(parent, textvariable=self.take_profit_var).pack(anchor=tk.W)
    
    def create_logic_widgets(self, parent):
        """Logik-Widgets erstellen"""
        
        ttk.Label(parent, text="Bedingungen-Logik:", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        
        self.logic_var = tk.StringVar(value="AND")
        
        ttk.Radiobutton(parent, text="AND (alle Bedingungen)", variable=self.logic_var, value="AND").pack(anchor=tk.W)
        ttk.Radiobutton(parent, text="OR (eine Bedingung)", variable=self.logic_var, value="OR").pack(anchor=tk.W)
        ttk.Radiobutton(parent, text="Custom Logic", variable=self.logic_var, value="CUSTOM").pack(anchor=tk.W)
        
        # Custom Logic Entry
        self.custom_logic_var = tk.StringVar(value="(C1 AND C2) OR C3")
        custom_entry = ttk.Entry(parent, textvariable=self.custom_logic_var)
        custom_entry.pack(fill=tk.X, pady=(5, 0))
    
    def on_file_selected(self, file_path):
        """Externe Datei ausgewählt"""
        self.load_external_data(file_path)
    
    def load_previous_data(self):
        """Daten von vorheriger App laden"""
        try:
            data = data_manager.get_current_data()
            
            if data is not None:
                self.current_data = data
                self.update_data_display()
                self.update_available_indicators()
                self.status_bar.update_status("✅ Daten von App 5 geladen")
            else:
                self.status_bar.update_status("⚠️ Keine Daten von App 5 verfügbar")
                
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
                    self.root.after(0, self.update_available_indicators)
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
    
    def update_available_indicators(self):
        """Verfügbare Indikatoren aktualisieren"""
        self.available_indicators = []
        
        if self.current_data is not None:
            if isinstance(self.current_data, dict):
                # Multi-Timeframe: Erste Timeframe nehmen
                first_timeframe = list(self.current_data.keys())[0]
                columns = self.current_data[first_timeframe].columns
            else:
                columns = self.current_data.columns
            
            # Indikatoren-Spalten finden
            for col in columns:
                if col.lower() not in ['open', 'high', 'low', 'close', 'volume']:
                    self.available_indicators.append(col)
            
            # Listbox und Comboboxes aktualisieren
            self.indicators_listbox.delete(0, tk.END)
            for indicator in self.available_indicators:
                self.indicators_listbox.insert(tk.END, indicator)
            
            # Comboboxes aktualisieren
            self.entry_indicator_combo['values'] = self.available_indicators
            self.exit_indicator_combo['values'] = self.available_indicators
    
    def add_condition(self, condition_type, indicator_var, operator_var, value_var):
        """Bedingung hinzufügen"""
        indicator = indicator_var.get()
        operator = operator_var.get()
        value = value_var.get()
        
        if not indicator:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Indikator aus!")
            return
        
        condition_text = f"{indicator} {operator} {value}"
        
        if condition_type == "entry":
            self.entry_conditions.append({
                'indicator': indicator,
                'operator': operator,
                'value': value,
                'text': condition_text
            })
            self.entry_conditions_listbox.insert(tk.END, condition_text)
        else:
            self.exit_conditions.append({
                'indicator': indicator,
                'operator': operator,
                'value': value,
                'text': condition_text
            })
            self.exit_conditions_listbox.insert(tk.END, condition_text)
        
        self.status_bar.update_status(f"{condition_type.title()} Bedingung hinzugefügt: {condition_text}")
    
    def remove_condition(self, condition_type, listbox):
        """Bedingung entfernen"""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Bedingung zum Entfernen aus!")
            return
        
        index = selection[0]
        
        if condition_type == "entry":
            del self.entry_conditions[index]
            self.entry_conditions_listbox.delete(index)
        else:
            del self.exit_conditions[index]
            self.exit_conditions_listbox.delete(index)
        
        self.status_bar.update_status(f"{condition_type.title()} Bedingung entfernt")
    
    def create_strategy(self):
        """Strategie erstellen"""
        if not self.entry_conditions and not self.exit_conditions:
            messagebox.showwarning("Warnung", "Bitte fügen Sie mindestens eine Entry- oder Exit-Bedingung hinzu!")
            return
        
        self.status_bar.update_status("Erstelle Strategie...", 0)
        
        # Strategie-Konfiguration sammeln
        self.strategy_config = {
            'entry_conditions': self.entry_conditions,
            'exit_conditions': self.exit_conditions,
            'logic': self.logic_var.get(),
            'custom_logic': self.custom_logic_var.get(),
            'risk_management': {
                'position_size': self.position_size_var.get() / 100.0,
                'stop_loss': self.stop_loss_var.get() / 100.0,
                'take_profit': self.take_profit_var.get() / 100.0
            },
            'created_timestamp': datetime.now().isoformat()
        }
        
        # Strategie in Data Manager setzen
        data_manager.set_current_data(
            self.current_data,
            source_app='app6_strategy_builder',
            metadata={
                'strategy_config': self.strategy_config,
                'strategy_created': True
            }
        )
        
        self.status_bar.update_status("✅ Strategie erstellt", 100)
        self.generate_code()
    
    def save_strategy(self):
        """Strategie speichern"""
        if not self.strategy_config:
            messagebox.showwarning("Warnung", "Bitte erstellen Sie zuerst eine Strategie!")
            return
        
        self.status_bar.update_status("Speichere Strategie...", 0)
        
        def save_in_background():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"strategy_app6_{timestamp}.h5"
                
                file_path = data_manager.save_current_data(
                    filename=filename,
                    app_name='app6_strategy_builder'
                )
                
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", f"Strategie gespeichert:\n{file_path}"))
                self.root.after(0, lambda: self.status_bar.update_status("✅ Strategie gespeichert", 100))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Speicher-Fehler: {e}"))
        
        threading.Thread(target=save_in_background, daemon=True).start()
    
    def generate_code(self):
        """Jupyter Code generieren"""
        if not self.strategy_config:
            return
        
        try:
            code = code_generator.generate_code('app6_strategy_builder', {
                'strategy': self.strategy_config,
                'input_file': 'app5_output.h5',
                'output_file': f"app6_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
            })
            
            self.code_viewer.set_code(code)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen: {e}")
    
    def go_to_app7(self):
        """Zu App 7 wechseln"""
        if not self.strategy_config:
            messagebox.showwarning("Warnung", "Bitte erstellen Sie zuerst eine Strategie!")
            return
        
        try:
            import app7_strategy_viz
            app7_window = tk.Toplevel(self.root)
            app7_strategy_viz.StrategyVizApp(app7_window)
        except ImportError:
            messagebox.showinfo("Info", "App 7 wird als nächstes entwickelt...")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = StrategyBuilderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
