#!/usr/bin/env python3
"""
⚙️ APP 5: VBT PRO FEATURES & STRATEGIEPARAMETER
VectorBT Pro GUI System - VBT Features und Strategieparameter
- Daten von App 3 laden
- Informationen anzeigen (Multi/Single-Timeframe, Indikatoren, Zeiträume, aktivierte VBT Pro Features)
- Auswahl weiterer VBT Pro Features (z.B. Data Object Export, Parallel Cache)
- Einstellung von Strategieparametern
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

class FeaturesApp:
    """⚙️ APP 5: VBT PRO FEATURES & STRATEGIEPARAMETER"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ VectorBT Pro - App 5: VBT Features & Strategieparameter")
        self.root.geometry("1400x900")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Variablen
        self.current_data = None
        self.vbt_features = {}
        self.strategy_params = {}
        
        # GUI erstellen
        self.create_widgets()
        
        # Daten von App 3 laden falls vorhanden
        self.load_previous_data()
    
    def create_widgets(self):
        """GUI-Elemente erstellen"""
        
        # Hauptcontainer
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_container, 
            text="⚙️ APP 5: VBT PRO FEATURES & STRATEGIEPARAMETER", 
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(0, 20))
        
        # Hauptbereich (3 Spalten)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Konfiguration
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Mittlere Spalte - Features & Parameter
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
            text="📊 Daten von App 3 laden", 
            command=self.load_previous_data
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.file_selector = FileSelector(
            source_frame,
            title="📁 Externe Datei",
            file_types=[("HDF5 files", "*.h5")],
            callback=self.on_file_selected
        )
        self.file_selector.pack(fill=tk.X)
        
        # Aktuelle Features Anzeige
        current_frame = ttk.LabelFrame(left_frame, text="📋 Aktuelle Features", padding="10")
        current_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.current_features_text = tk.Text(current_frame, height=8, font=ModernStyle.FONTS['small'], state='disabled')
        self.current_features_text.pack(fill=tk.X)
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(left_frame, text="🚀 Aktionen", padding="10")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            actions_frame, 
            text="⚙️ Features anwenden", 
            command=self.apply_features,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="💾 Daten speichern", 
            command=self.save_data
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="💻 Code generieren", 
            command=self.generate_code
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="➡️ Zu App 6", 
            command=self.go_to_app6
        ).pack(fill=tk.X)
        
        # === MITTLERE SPALTE ===
        
        # VBT Pro Features
        vbt_features_frame = ttk.LabelFrame(middle_frame, text="🚀 VectorBT Pro Features", padding="10")
        vbt_features_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_vbt_features_widgets(vbt_features_frame)
        
        # Strategieparameter
        self.strategy_params_panel = ParameterPanel(middle_frame, title="🎯 Strategieparameter")
        self.strategy_params_panel.pack(fill=tk.BOTH, expand=True)
        
        self.create_strategy_params()
        
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
    
    def create_vbt_features_widgets(self, parent):
        """VBT Pro Features Widgets erstellen"""
        
        # Performance Features
        perf_frame = ttk.LabelFrame(parent, text="⚡ Performance Features", padding="5")
        perf_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.vbt_features = {}
        
        performance_features = [
            ("numba_acceleration", "Numba Acceleration", True),
            ("parallel_processing", "Parallel Processing", True),
            ("memory_optimization", "Memory Optimization", True),
            ("cache_optimization", "Cache Optimization", True),
            ("vectorized_operations", "Vectorized Operations", True)
        ]
        
        for i, (key, text, default) in enumerate(performance_features):
            var = tk.BooleanVar(value=default)
            ttk.Checkbutton(perf_frame, text=text, variable=var).grid(
                row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2
            )
            self.vbt_features[key] = var
        
        # Data Features
        data_frame = ttk.LabelFrame(parent, text="📊 Data Features", padding="5")
        data_frame.pack(fill=tk.X, pady=(0, 10))
        
        data_features = [
            ("vbt_data_objects", "VBT Data Objects", True),
            ("blosc_compression", "Blosc Compression", True),
            ("metadata_tracking", "Metadata Tracking", True),
            ("data_validation", "Data Validation", False)
        ]
        
        for i, (key, text, default) in enumerate(data_features):
            var = tk.BooleanVar(value=default)
            ttk.Checkbutton(data_frame, text=text, variable=var).grid(
                row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2
            )
            self.vbt_features[key] = var
        
        # Advanced Features
        advanced_frame = ttk.LabelFrame(parent, text="🔬 Advanced Features", padding="5")
        advanced_frame.pack(fill=tk.X)
        
        advanced_features = [
            ("ray_engine", "Ray Engine (Distributed)", False),
            ("gpu_acceleration", "GPU Acceleration", False),
            ("streaming_data", "Streaming Data Support", False),
            ("custom_indicators", "Custom Indicators", False)
        ]
        
        for i, (key, text, default) in enumerate(advanced_features):
            var = tk.BooleanVar(value=default)
            ttk.Checkbutton(advanced_frame, text=text, variable=var).grid(
                row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2
            )
            self.vbt_features[key] = var
    
    def create_strategy_params(self):
        """Standard Strategieparameter erstellen"""
        
        # Trading Parameter
        self.strategy_params_panel.add_parameter("initial_cash", "float", 10000.0, "Startkapital")
        self.strategy_params_panel.add_parameter("fees", "float", 0.001, "Gebühren (0.1%)")
        self.strategy_params_panel.add_parameter("slippage", "float", 0.001, "Slippage (0.1%)")
        
        # Risk Management
        self.strategy_params_panel.add_parameter("max_position_size", "float", 1.0, "Max Position Size (100%)")
        self.strategy_params_panel.add_parameter("stop_loss", "float", 0.05, "Stop Loss (5%)")
        self.strategy_params_panel.add_parameter("take_profit", "float", 0.10, "Take Profit (10%)")
        
        # Strategy Specific
        self.strategy_params_panel.add_parameter("signal_threshold", "float", 0.7, "Signal Threshold")
        self.strategy_params_panel.add_parameter("min_holding_period", "int", 1, "Min Holding Period (Bars)")
        self.strategy_params_panel.add_parameter("max_holding_period", "int", 100, "Max Holding Period (Bars)")
    
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
                self.update_data_display()
                self.update_current_features_display(metadata)
                self.status_bar.update_status("✅ Daten von App 3 geladen")
            else:
                self.status_bar.update_status("⚠️ Keine Daten von App 3 verfügbar")
                
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
    
    def update_current_features_display(self, metadata):
        """Aktuelle Features anzeigen"""
        self.current_features_text.config(state='normal')
        self.current_features_text.delete(1.0, tk.END)
        
        features_info = "📋 AKTUELLE FEATURES:\n\n"
        
        # Metadaten analysieren
        if metadata:
            features_info += f"Source App: {metadata.get('source_app', 'Unknown')}\n"
            features_info += f"Timestamp: {metadata.get('timestamp', 'Unknown')}\n"
            
            if 'indicators_added' in metadata:
                indicators = metadata['indicators_added']
                features_info += f"Indikatoren: {len(indicators)}\n"
                
            if 'is_multi_timeframe' in metadata:
                is_multi = metadata['is_multi_timeframe']
                features_info += f"Multi-Timeframe: {'Ja' if is_multi else 'Nein'}\n"
                
                if is_multi and 'timeframes' in metadata:
                    timeframes = metadata['timeframes']
                    features_info += f"Timeframes: {', '.join(timeframes)}\n"
        
        features_info += "\n🚀 VBT PRO FEATURES:\n"
        features_info += "✅ Blosc Compression\n"
        features_info += "✅ Memory Optimization\n"
        features_info += "✅ Performance Monitoring\n"
        features_info += "✅ Metadata Tracking\n"
        
        self.current_features_text.insert(1.0, features_info)
        self.current_features_text.config(state='disabled')
    
    def apply_features(self):
        """VBT Features anwenden"""
        if self.current_data is None:
            messagebox.showwarning("Warnung", "Keine Daten zum Anwenden der Features!")
            return
        
        self.status_bar.update_status("Wende VBT Features an...", 0)
        self.performance_monitor.start_timing()
        
        def apply_in_background():
            try:
                # Features-Konfiguration sammeln
                features_config = {key: var.get() for key, var in self.vbt_features.items()}
                strategy_config = self.strategy_params_panel.get_parameters()
                
                # VBT Data Object erstellen falls aktiviert
                if features_config.get('vbt_data_objects', False):
                    enhanced_data = data_manager.create_vbt_data_object()
                else:
                    enhanced_data = self.current_data
                
                # Metadaten erweitern
                metadata = {
                    'vbt_features_applied': features_config,
                    'strategy_parameters': strategy_config,
                    'features_timestamp': datetime.now().isoformat()
                }
                
                # Daten mit Features setzen
                data_manager.set_current_data(
                    enhanced_data,
                    source_app='app5_features',
                    metadata=metadata
                )
                
                self.root.after(0, self.update_data_display)
                self.root.after(0, lambda: self.update_current_features_display(metadata))
                self.root.after(0, lambda: self.status_bar.update_status("✅ VBT Features angewendet", 100))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Features-Fehler: {e}"))
        
        threading.Thread(target=apply_in_background, daemon=True).start()
    
    def save_data(self):
        """Daten mit Features speichern"""
        if self.current_data is None:
            messagebox.showwarning("Warnung", "Keine Daten zum Speichern!")
            return
        
        self.status_bar.update_status("Speichere Daten...", 0)
        
        def save_in_background():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"features_app5_{timestamp}.h5"
                
                file_path = data_manager.save_current_data(
                    filename=filename,
                    app_name='app5_features'
                )
                
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", f"Daten mit Features gespeichert:\n{file_path}"))
                self.root.after(0, lambda: self.status_bar.update_status("✅ Daten gespeichert", 100))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Speicher-Fehler: {e}"))
        
        threading.Thread(target=save_in_background, daemon=True).start()
    
    def generate_code(self):
        """Jupyter Code generieren"""
        if self.current_data is None:
            return
        
        try:
            features_config = {key: var.get() for key, var in self.vbt_features.items()}
            strategy_config = self.strategy_params_panel.get_parameters()
            
            code = f'''
# ⚙️ VBT PRO FEATURES & STRATEGIEPARAMETER - APP 5
# Generiert von VectorBT Pro GUI System am {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import vectorbtpro as vbt
import pandas as pd
import numpy as np

# VBT Pro Settings optimieren
{self.generate_vbt_settings_code(features_config)}

# Daten laden
data = vbt.Data.load("app3_output.h5")

# Strategieparameter
strategy_params = {json.dumps(strategy_config, indent=4)}

# VBT Pro Features anwenden
{self.generate_features_code(features_config)}

# Daten mit Features speichern
data.save(
    "app5_output.h5",
    compression="blosc" if {features_config.get('blosc_compression', True)} else None,
    compression_opts=9,
    shuffle=True,
    fletcher32=True
)

print("✅ VBT Pro Features angewendet und gespeichert")
'''
            
            self.code_viewer.set_code(code)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen: {e}")
    
    def generate_vbt_settings_code(self, features_config):
        """VBT Settings Code generieren"""
        code = ""
        
        if features_config.get('cache_optimization', True):
            code += "vbt.settings.caching['enabled'] = True\n"
        
        if features_config.get('parallel_processing', True):
            code += "vbt.settings.array_wrapper['freq'] = None\n"
        
        if features_config.get('numba_acceleration', True):
            code += "vbt.settings.numba['check_func_type'] = False\n"
        
        return code
    
    def generate_features_code(self, features_config):
        """Features Code generieren"""
        code = ""
        
        if features_config.get('memory_optimization', True):
            code += "# Memory Optimization\ndata = data.vbt.optimize_memory()\n\n"
        
        if features_config.get('data_validation', False):
            code += "# Data Validation\ndata = data.vbt.validate()\n\n"
        
        return code
    
    def go_to_app6(self):
        """Zu App 6 wechseln"""
        try:
            import app6_strategy_builder
            app6_window = tk.Toplevel(self.root)
            app6_strategy_builder.StrategyBuilderApp(app6_window)
        except ImportError:
            messagebox.showinfo("Info", "App 6 wird als nächstes entwickelt...")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = FeaturesApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
