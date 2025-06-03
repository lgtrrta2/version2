#!/usr/bin/env python3
"""
📈 APP 3: INDIKATOREN MANAGER
VectorBT Pro GUI System - Indikatoren hinzufügen und konfigurieren
- Daten von App 2 laden
- Informationen anzeigen (erkennt Multi/Single-Timeframe)
- Auswahl aus 551 Indikatoren
- Parameteränderung für Indikatoren (mit Validierung)
- Unterschiedliche Indikatoren für verschiedene Zeiteinheiten bei Multi-Timeframe
- Speichern als VBT-konforme Datei mit Performance-Features
- Code-Generierung für Jupyter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import pandas as pd
from datetime import datetime
import threading

# Lokale Imports
from shared_components import (
    ModernStyle, StatusBar, FileSelector, ExportOptions, 
    CodeViewer, DataInfoPanel, PerformanceMonitor, ParameterPanel
)
from data_manager import data_manager
from code_generator import code_generator

class IndicatorsApp:
    """📈 APP 3: INDIKATOREN MANAGER"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📈 VectorBT Pro - App 3: Indikatoren Manager")
        self.root.geometry("1600x1000")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Variablen
        self.current_data = None
        self.is_multi_timeframe = False
        self.timeframes = []
        self.indicators_config = {}
        self.calculated_indicators = {}
        self.available_indicators = {}
        
        # Indikatoren-Parameter laden
        self.load_indicators_parameters()
        
        # GUI erstellen
        self.create_widgets()
        
        # Daten von App 2 laden falls vorhanden
        self.load_previous_data()
    
    def load_indicators_parameters(self):
        """Indikatoren-Parameter aus JSON laden"""
        try:
            with open('vectorbt_all_indicators_params.json', 'r', encoding='utf-8') as f:
                self.available_indicators = json.load(f)
            
            print(f"✅ {len(self.available_indicators)} Indikatoren geladen")
            
        except FileNotFoundError:
            print("⚠️ vectorbt_all_indicators_params.json nicht gefunden")
            # Fallback: Basis-Indikatoren
            self.available_indicators = {
                "vbt:RSI": {
                    "description": "Relative Strength Index",
                    "run_params": {
                        "close": {"required": True, "type": "Series"},
                        "window": {"default": "14", "required": False, "type": "int"}
                    }
                },
                "vbt:MACD": {
                    "description": "Moving Average Convergence Divergence",
                    "run_params": {
                        "close": {"required": True, "type": "Series"},
                        "fast_window": {"default": "12", "required": False, "type": "int"},
                        "slow_window": {"default": "26", "required": False, "type": "int"},
                        "signal_window": {"default": "9", "required": False, "type": "int"}
                    }
                }
            }
        except Exception as e:
            print(f"❌ Fehler beim Laden der Indikatoren: {e}")
            self.available_indicators = {}
    
    def create_widgets(self):
        """GUI-Elemente erstellen"""
        
        # Hauptcontainer
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_container, 
            text="📈 APP 3: INDIKATOREN MANAGER", 
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(0, 20))
        
        # Hauptbereich (4 Spalten)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Spalte 1 - Daten-Quelle & Timeframe
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Spalte 2 - Indikatoren-Auswahl
        middle_left_frame = ttk.Frame(content_frame)
        middle_left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Spalte 3 - Parameter & Info
        middle_right_frame = ttk.Frame(content_frame)
        middle_right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Spalte 4 - Code
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === SPALTE 1: DATEN-QUELLE ===
        
        # Daten-Quelle
        source_frame = ttk.LabelFrame(left_frame, text="📊 Daten-Quelle", padding="10")
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            source_frame, 
            text="📊 Daten von App 2 laden", 
            command=self.load_previous_data
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.file_selector = FileSelector(
            source_frame,
            title="📁 Externe Datei",
            file_types=[("HDF5 files", "*.h5")],
            callback=self.on_file_selected
        )
        self.file_selector.pack(fill=tk.X)
        
        # Timeframe-Info
        self.timeframe_frame = ttk.LabelFrame(left_frame, text="⏱️ Timeframe-Info", padding="10")
        self.timeframe_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(left_frame, text="🚀 Aktionen", padding="10")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            actions_frame, 
            text="📈 Indikatoren berechnen", 
            command=self.calculate_indicators,
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
            text="➡️ Zu App 4", 
            command=self.go_to_app4
        ).pack(fill=tk.X)
        
        # === SPALTE 2: INDIKATOREN-AUSWAHL ===
        
        # Indikatoren-Suche
        search_frame = ttk.LabelFrame(middle_left_frame, text="🔍 Indikatoren-Suche", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=ModernStyle.FONTS['normal'])
        search_entry.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Suche nach Name oder Beschreibung", font=ModernStyle.FONTS['small']).pack()
        
        # Indikatoren-Liste
        indicators_frame = ttk.LabelFrame(middle_left_frame, text="📈 Verfügbare Indikatoren", padding="10")
        indicators_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox mit Scrollbar
        list_frame = ttk.Frame(indicators_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.indicators_listbox = tk.Listbox(
            list_frame, 
            font=ModernStyle.FONTS['small'],
            selectmode=tk.SINGLE
        )
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.indicators_listbox.yview)
        self.indicators_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.indicators_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.indicators_listbox.bind('<<ListboxSelect>>', self.on_indicator_select)
        
        # Ausgewählte Indikatoren
        selected_frame = ttk.LabelFrame(middle_left_frame, text="✅ Ausgewählte Indikatoren", padding="10")
        selected_frame.pack(fill=tk.X)
        
        self.selected_listbox = tk.Listbox(selected_frame, height=6, font=ModernStyle.FONTS['small'])
        self.selected_listbox.pack(fill=tk.X, pady=(0, 5))
        self.selected_listbox.bind('<<ListboxSelect>>', self.on_selected_indicator_select)
        
        selected_buttons_frame = ttk.Frame(selected_frame)
        selected_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(selected_buttons_frame, text="➕ Hinzufügen", command=self.add_indicator).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(selected_buttons_frame, text="➖ Entfernen", command=self.remove_indicator).pack(side=tk.LEFT)
        
        # === SPALTE 3: PARAMETER & INFO ===
        
        # Indikator-Details
        details_frame = ttk.LabelFrame(middle_right_frame, text="📋 Indikator-Details", padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.details_text = tk.Text(details_frame, height=4, font=ModernStyle.FONTS['small'], state='disabled')
        self.details_text.pack(fill=tk.X)
        
        # Parameter-Panel
        self.parameter_panel = ParameterPanel(middle_right_frame, title="⚙️ Parameter")
        self.parameter_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Daten-Information
        self.data_info = DataInfoPanel(middle_right_frame, title="📊 Daten-Information")
        self.data_info.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Performance Monitor
        self.performance_monitor = PerformanceMonitor(middle_right_frame, title="⚡ Performance")
        self.performance_monitor.pack(fill=tk.X)
        
        # === SPALTE 4: CODE ===
        
        # Code Viewer
        self.code_viewer = CodeViewer(right_frame, title="💻 Generierter Jupyter Code")
        self.code_viewer.pack(fill=tk.BOTH, expand=True)
        
        # === STATUS BAR ===
        self.status_bar = StatusBar(main_container)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Indikatoren-Liste füllen
        self.populate_indicators_list()
    
    def populate_indicators_list(self):
        """Indikatoren-Liste füllen"""
        self.indicators_listbox.delete(0, tk.END)
        
        for indicator_name, indicator_info in self.available_indicators.items():
            display_name = indicator_name.replace("vbt:", "")
            description = indicator_info.get("description", "")
            
            display_text = f"{display_name} - {description}"
            self.indicators_listbox.insert(tk.END, display_text)
        
        self.status_bar.update_status(f"{len(self.available_indicators)} Indikatoren verfügbar")
    
    def on_search_change(self, *args):
        """Suche in Indikatoren"""
        search_term = self.search_var.get().lower()
        
        self.indicators_listbox.delete(0, tk.END)
        
        for indicator_name, indicator_info in self.available_indicators.items():
            display_name = indicator_name.replace("vbt:", "")
            description = indicator_info.get("description", "")
            
            # Suche in Name und Beschreibung
            if (search_term in display_name.lower() or 
                search_term in description.lower()):
                
                display_text = f"{display_name} - {description}"
                self.indicators_listbox.insert(tk.END, display_text)
    
    def on_indicator_select(self, event):
        """Indikator aus Liste ausgewählt"""
        selection = self.indicators_listbox.curselection()
        if not selection:
            return
        
        # Hole Indikator-Info
        selected_text = self.indicators_listbox.get(selection[0])
        indicator_name = selected_text.split(" - ")[0]
        
        # Finde vollständigen Namen
        full_name = None
        for name in self.available_indicators.keys():
            if name.replace("vbt:", "") == indicator_name:
                full_name = name
                break
        
        if full_name:
            self.show_indicator_details(full_name)
    
    def show_indicator_details(self, indicator_name):
        """Indikator-Details anzeigen"""
        indicator_info = self.available_indicators.get(indicator_name, {})
        
        # Details-Text aktualisieren
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        
        details = f"Name: {indicator_name}\n"
        details += f"Beschreibung: {indicator_info.get('description', 'Keine Beschreibung')}\n"
        details += f"Parameter: {len(indicator_info.get('run_params', {}))}\n"
        
        self.details_text.insert(1.0, details)
        self.details_text.config(state='disabled')
        
        # Parameter-Panel aktualisieren
        self.update_parameter_panel(indicator_name)
    
    def update_parameter_panel(self, indicator_name):
        """Parameter-Panel für Indikator aktualisieren"""
        # Alte Parameter löschen
        for widget in self.parameter_panel.winfo_children():
            widget.destroy()
        
        self.parameter_panel.parameters = {}
        self.parameter_panel.widgets = {}
        
        indicator_info = self.available_indicators.get(indicator_name, {})
        run_params = indicator_info.get('run_params', {})
        
        for param_name, param_info in run_params.items():
            # Skip data parameters (close, high, low, etc.)
            if param_name.lower() in ['close', 'high', 'low', 'open', 'volume']:
                continue
            
            required = param_info.get('required', False)
            default_value = param_info.get('default', '')
            param_type = param_info.get('type', 'str')
            
            # Parse default value
            if default_value.startswith('Default(value='):
                default_value = default_value.replace('Default(value=', '').replace(')', '').strip("'\"")
            
            # Bestimme Parameter-Typ
            if param_type == 'int' or default_value.isdigit():
                self.parameter_panel.add_parameter(
                    param_name, 'int', int(default_value) if default_value.isdigit() else 14,
                    f"{'*' if required else ''} {param_type}"
                )
            elif param_type == 'float' or '.' in str(default_value):
                try:
                    default_float = float(default_value)
                    self.parameter_panel.add_parameter(
                        param_name, 'float', default_float,
                        f"{'*' if required else ''} {param_type}"
                    )
                except:
                    self.parameter_panel.add_parameter(
                        param_name, 'str', str(default_value),
                        f"{'*' if required else ''} {param_type}"
                    )
            else:
                self.parameter_panel.add_parameter(
                    param_name, 'str', str(default_value),
                    f"{'*' if required else ''} {param_type}"
                )
    
    def add_indicator(self):
        """Indikator zu Auswahl hinzufügen"""
        selection = self.indicators_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Indikator aus!")
            return
        
        selected_text = self.indicators_listbox.get(selection[0])
        indicator_name = selected_text.split(" - ")[0]
        
        # Finde vollständigen Namen
        full_name = None
        for name in self.available_indicators.keys():
            if name.replace("vbt:", "") == indicator_name:
                full_name = name
                break
        
        if full_name and full_name not in self.indicators_config:
            # Parameter abrufen
            parameters = self.parameter_panel.get_parameters()
            
            # Timeframe-spezifische Konfiguration
            if self.is_multi_timeframe:
                # Für Multi-Timeframe: Indikator für alle Timeframes hinzufügen
                for timeframe in self.timeframes:
                    config_key = f"{full_name}_{timeframe}"
                    self.indicators_config[config_key] = {
                        'indicator': full_name,
                        'timeframe': timeframe,
                        'parameters': parameters.copy()
                    }
            else:
                # Für Single-Timeframe
                self.indicators_config[full_name] = {
                    'indicator': full_name,
                    'timeframe': 'single',
                    'parameters': parameters
                }
            
            self.update_selected_indicators_list()
            self.status_bar.update_status(f"Indikator hinzugefügt: {indicator_name}")
    
    def remove_indicator(self):
        """Indikator aus Auswahl entfernen"""
        selection = self.selected_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Indikator zum Entfernen aus!")
            return
        
        selected_text = self.selected_listbox.get(selection[0])
        
        # Finde und entferne Indikator
        to_remove = []
        for config_key in self.indicators_config.keys():
            if config_key in selected_text or selected_text in config_key:
                to_remove.append(config_key)
        
        for key in to_remove:
            del self.indicators_config[key]
        
        self.update_selected_indicators_list()
        self.status_bar.update_status("Indikator entfernt")
    
    def update_selected_indicators_list(self):
        """Liste der ausgewählten Indikatoren aktualisieren"""
        self.selected_listbox.delete(0, tk.END)
        
        for config_key, config in self.indicators_config.items():
            indicator_name = config['indicator'].replace("vbt:", "")
            timeframe = config['timeframe']
            
            if timeframe == 'single':
                display_text = indicator_name
            else:
                display_text = f"{indicator_name} ({timeframe})"
            
            self.selected_listbox.insert(tk.END, display_text)
    
    def on_selected_indicator_select(self, event):
        """Ausgewählten Indikator bearbeiten"""
        selection = self.selected_listbox.curselection()
        if not selection:
            return

        # Hier könnte Parameter-Bearbeitung implementiert werden
        pass

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

                # Multi-Timeframe erkennen
                if isinstance(data, dict):
                    self.is_multi_timeframe = True
                    self.timeframes = list(data.keys())
                else:
                    self.is_multi_timeframe = False
                    self.timeframes = ['single']

                self.update_data_display()
                self.update_timeframe_info()
                self.status_bar.update_status("✅ Daten von App 2 geladen")
            else:
                self.status_bar.update_status("⚠️ Keine Daten von App 2 verfügbar")

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
                    self.is_multi_timeframe = False
                    self.timeframes = ['single']

                    self.root.after(0, self.update_data_display)
                    self.root.after(0, self.update_timeframe_info)
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

    def update_timeframe_info(self):
        """Timeframe-Information aktualisieren"""
        # Alte Widgets entfernen
        for widget in self.timeframe_frame.winfo_children():
            widget.destroy()

        if self.is_multi_timeframe:
            ttk.Label(
                self.timeframe_frame,
                text="📊 Multi-Timeframe Daten",
                font=ModernStyle.FONTS['subtitle']
            ).pack(anchor=tk.W, pady=(0, 5))

            for i, timeframe in enumerate(self.timeframes):
                data_shape = self.current_data[timeframe].shape
                ttk.Label(
                    self.timeframe_frame,
                    text=f"  {timeframe}: {data_shape[0]:,} × {data_shape[1]}",
                    font=ModernStyle.FONTS['small']
                ).pack(anchor=tk.W)
        else:
            ttk.Label(
                self.timeframe_frame,
                text="📊 Single-Timeframe Daten",
                font=ModernStyle.FONTS['subtitle']
            ).pack(anchor=tk.W, pady=(0, 5))

            if hasattr(self.current_data, 'shape'):
                data_shape = self.current_data.shape
                ttk.Label(
                    self.timeframe_frame,
                    text=f"  Shape: {data_shape[0]:,} × {data_shape[1]}",
                    font=ModernStyle.FONTS['small']
                ).pack(anchor=tk.W)

    def calculate_indicators(self):
        """Indikatoren berechnen"""
        if self.current_data is None:
            messagebox.showwarning("Warnung", "Keine Daten zum Berechnen vorhanden!")
            return

        if not self.indicators_config:
            messagebox.showwarning("Warnung", "Keine Indikatoren ausgewählt!")
            return

        self.status_bar.update_status("Berechne Indikatoren...", 0)
        self.performance_monitor.start_timing()

        def calculate_in_background():
            try:
                self.calculated_indicators = {}
                total_indicators = len(self.indicators_config)

                for i, (config_key, config) in enumerate(self.indicators_config.items()):
                    progress = int((i / total_indicators) * 100)
                    indicator_name = config['indicator']
                    timeframe = config['timeframe']
                    parameters = config['parameters']

                    self.root.after(0, lambda p=progress, name=indicator_name:
                                  self.status_bar.update_status(f"Berechne {name}...", p))

                    try:
                        # Daten für Timeframe abrufen
                        if self.is_multi_timeframe:
                            data = self.current_data[timeframe]
                        else:
                            data = self.current_data

                        # Indikator berechnen
                        result = self.calculate_single_indicator(indicator_name, data, parameters)

                        if result is not None:
                            self.calculated_indicators[config_key] = {
                                'indicator': indicator_name,
                                'timeframe': timeframe,
                                'data': result,
                                'parameters': parameters
                            }

                    except Exception as e:
                        print(f"❌ Fehler bei {indicator_name}: {e}")

                # GUI aktualisieren
                self.root.after(0, self.update_indicators_display)

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Berechnungs-Fehler: {e}"))

        threading.Thread(target=calculate_in_background, daemon=True).start()

    def calculate_single_indicator(self, indicator_name, data, parameters):
        """Einzelnen Indikator berechnen"""
        try:
            # VectorBT Pro Indikator-Berechnung
            import vectorbtpro as vbt

            # Basis-Indikatoren implementieren
            if indicator_name == "vbt:RSI":
                window = parameters.get('window', 14)
                return vbt.RSI.run(data['close'], window=window).rsi

            elif indicator_name == "vbt:MACD":
                fast_window = parameters.get('fast_window', 12)
                slow_window = parameters.get('slow_window', 26)
                signal_window = parameters.get('signal_window', 9)

                macd = vbt.MACD.run(
                    data['close'],
                    fast_window=fast_window,
                    slow_window=slow_window,
                    signal_window=signal_window
                )

                return {
                    'macd': macd.macd,
                    'signal': macd.signal,
                    'histogram': macd.histogram
                }

            elif indicator_name == "vbt:BBANDS":
                window = parameters.get('window', 20)
                alpha = parameters.get('alpha', 2)

                bb = vbt.BBANDS.run(data['close'], window=window, alpha=alpha)

                return {
                    'upper': bb.upper,
                    'middle': bb.middle,
                    'lower': bb.lower
                }

            elif indicator_name == "vbt:ATR":
                window = parameters.get('window', 14)
                return vbt.ATR.run(data['high'], data['low'], data['close'], window=window).atr

            elif indicator_name == "vbt:ADX":
                window = parameters.get('window', 14)
                return vbt.ADX.run(data['high'], data['low'], data['close'], window=window).adx

            # Weitere Indikatoren können hier hinzugefügt werden
            else:
                print(f"⚠️ Indikator {indicator_name} noch nicht implementiert")
                return None

        except Exception as e:
            print(f"❌ Fehler bei Indikator-Berechnung {indicator_name}: {e}")
            return None

    def update_indicators_display(self):
        """Indikatoren-Anzeige aktualisieren"""
        self.performance_monitor.stop_timing()

        if self.calculated_indicators:
            # Berechnete Indikatoren zu Daten hinzufügen
            if self.is_multi_timeframe:
                enhanced_data = {}
                for timeframe, data in self.current_data.items():
                    enhanced_data[timeframe] = data.copy()

                    # Indikatoren für diesen Timeframe hinzufügen
                    for config_key, indicator_result in self.calculated_indicators.items():
                        if indicator_result['timeframe'] == timeframe:
                            indicator_data = indicator_result['data']
                            indicator_name = indicator_result['indicator'].replace("vbt:", "")

                            if isinstance(indicator_data, dict):
                                # Multi-Output Indikator (z.B. MACD)
                                for output_name, output_data in indicator_data.items():
                                    column_name = f"{indicator_name}_{output_name}"
                                    enhanced_data[timeframe][column_name] = output_data
                            else:
                                # Single-Output Indikator
                                enhanced_data[timeframe][indicator_name] = indicator_data

                # Enhanced Data setzen
                data_manager.set_current_data(
                    enhanced_data,
                    source_app='app3_indicators',
                    metadata={
                        'indicators_added': list(self.calculated_indicators.keys()),
                        'is_multi_timeframe': True,
                        'timeframes': self.timeframes
                    }
                )

            else:
                # Single-Timeframe
                enhanced_data = self.current_data.copy()

                for config_key, indicator_result in self.calculated_indicators.items():
                    indicator_data = indicator_result['data']
                    indicator_name = indicator_result['indicator'].replace("vbt:", "")

                    if isinstance(indicator_data, dict):
                        for output_name, output_data in indicator_data.items():
                            column_name = f"{indicator_name}_{output_name}"
                            enhanced_data[column_name] = output_data
                    else:
                        enhanced_data[indicator_name] = indicator_data

                # Enhanced Data setzen
                data_manager.set_current_data(
                    enhanced_data,
                    source_app='app3_indicators',
                    metadata={
                        'indicators_added': list(self.calculated_indicators.keys()),
                        'is_multi_timeframe': False
                    }
                )

            # Anzeige aktualisieren
            self.update_data_display()

            self.status_bar.update_status(
                f"✅ {len(self.calculated_indicators)} Indikatoren berechnet", 100
            )

            # Code generieren
            self.generate_code()

    def save_data(self):
        """Daten mit Indikatoren speichern"""
        if not self.calculated_indicators:
            messagebox.showwarning("Warnung", "Keine berechneten Indikatoren zum Speichern!")
            return

        self.status_bar.update_status("Speichere Daten...", 0)

        def save_in_background():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"indicators_app3_{timestamp}.h5"

                file_path = data_manager.save_current_data(
                    filename=filename,
                    app_name='app3_indicators'
                )

                self.root.after(0, lambda: messagebox.showinfo("Erfolg", f"Daten mit Indikatoren gespeichert:\n{file_path}"))
                self.root.after(0, lambda: self.status_bar.update_status("✅ Daten gespeichert", 100))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Speicher-Fehler: {e}"))

        threading.Thread(target=save_in_background, daemon=True).start()

    def generate_code(self):
        """Jupyter Code generieren"""
        if not self.calculated_indicators:
            return

        try:
            config = {
                'indicators': {
                    key: {
                        'indicator': val['indicator'],
                        'parameters': val['parameters']
                    }
                    for key, val in self.calculated_indicators.items()
                },
                'is_multi_timeframe': self.is_multi_timeframe,
                'timeframes': self.timeframes,
                'input_file': 'app2_output.h5',
                'output_file': f"app3_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
            }

            code = code_generator.generate_code('app3_indicators', config)
            self.code_viewer.set_code(code)

        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen: {e}")

    def go_to_app4(self):
        """Zu App 4 wechseln"""
        if not self.calculated_indicators:
            messagebox.showwarning("Warnung", "Bitte berechnen Sie zuerst Indikatoren!")
            return

        try:
            import app4_visualization
            app4_window = tk.Toplevel(self.root)
            app4_visualization.VisualizationApp(app4_window)
        except ImportError:
            messagebox.showinfo("Info", "App 4 wird als nächstes entwickelt...")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = IndicatorsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
