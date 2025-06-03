#!/usr/bin/env python3
"""
🔄 APP 2: DATEN RESAMPLING
VectorBT Pro GUI System - Multi/Single-Timeframe Resampling
- Geladene Daten von App 1 laden
- Informationen anzeigen
- Resampling: Single- oder Multi-Timeframe
- Timeframe-Auswahl (1m, 2m, ..., 1w)
- Speichern als VBT-konforme Datei mit Performance-Features
- Code-Generierung für Jupyter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import threading

# Lokale Imports
from shared_components import (
    ModernStyle, StatusBar, FileSelector, ExportOptions, 
    CodeViewer, DataInfoPanel, PerformanceMonitor
)
from data_manager import data_manager
from code_generator import code_generator

class ResamplingApp:
    """🔄 APP 2: DATEN RESAMPLING"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔄 VectorBT Pro - App 2: Daten Resampling")
        self.root.geometry("1400x900")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Variablen
        self.current_data = None
        self.resampled_data = {}
        self.resampling_mode = tk.StringVar(value="single")
        self.selected_timeframes = []
        
        # GUI erstellen
        self.create_widgets()
        
        # Daten von App 1 laden falls vorhanden
        self.load_previous_data()
    
    def create_widgets(self):
        """GUI-Elemente erstellen"""
        
        # Hauptcontainer
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_container, 
            text="🔄 APP 2: DATEN RESAMPLING", 
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(0, 20))
        
        # Hauptbereich (3 Spalten)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Konfiguration
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Mittlere Spalte - Daten-Info
        middle_frame = ttk.Frame(content_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Rechte Spalte - Code
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === LINKE SPALTE ===
        
        # Daten-Quelle
        source_frame = ttk.LabelFrame(left_frame, text="📊 Daten-Quelle", padding="10")
        source_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Datei-Auswahl für externe Daten
        self.file_selector = FileSelector(
            source_frame,
            title="📁 Externe Datei laden (optional)",
            file_types=[("HDF5 files", "*.h5"), ("CSV files", "*.csv")],
            callback=self.on_file_selected
        )
        self.file_selector.pack(fill=tk.X, pady=(0, 10))
        
        # Button für App 1 Daten
        ttk.Button(
            source_frame, 
            text="📊 Daten von App 1 laden", 
            command=self.load_previous_data
        ).pack(fill=tk.X)
        
        # Resampling-Modus
        mode_frame = ttk.LabelFrame(left_frame, text="🔄 Resampling-Modus", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Radiobutton(
            mode_frame, 
            text="Single-Timeframe", 
            variable=self.resampling_mode, 
            value="single",
            command=self.on_mode_change
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            mode_frame, 
            text="Multi-Timeframe", 
            variable=self.resampling_mode, 
            value="multi",
            command=self.on_mode_change
        ).pack(anchor=tk.W)
        
        # Timeframe-Auswahl
        self.timeframe_frame = ttk.LabelFrame(left_frame, text="⏱️ Timeframe-Auswahl", padding="10")
        self.timeframe_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_timeframe_widgets()
        
        # Resampling-Optionen
        options_frame = ttk.LabelFrame(left_frame, text="⚙️ Resampling-Optionen", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # OHLC Methoden
        ttk.Label(options_frame, text="OHLC Methode:", font=ModernStyle.FONTS['normal']).pack(anchor=tk.W)
        self.ohlc_method = tk.StringVar(value="standard")
        
        methods_frame = ttk.Frame(options_frame)
        methods_frame.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Radiobutton(methods_frame, text="Standard", variable=self.ohlc_method, value="standard").pack(side=tk.LEFT)
        ttk.Radiobutton(methods_frame, text="VWAP", variable=self.ohlc_method, value="vwap").pack(side=tk.LEFT, padx=(10, 0))
        
        # Dropna Option
        self.dropna_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Leere Zeilen entfernen", variable=self.dropna_var).pack(anchor=tk.W)
        
        # Export-Optionen
        self.export_options = ExportOptions(left_frame, title="💾 Export-Optionen")
        self.export_options.pack(fill=tk.X, pady=(0, 20))
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(left_frame, text="🚀 Aktionen", padding="10")
        actions_frame.pack(fill=tk.X)
        
        ttk.Button(
            actions_frame, 
            text="🔄 Resampling starten", 
            command=self.start_resampling,
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
            text="➡️ Zu App 3", 
            command=self.go_to_app3
        ).pack(fill=tk.X)
        
        # === MITTLERE SPALTE ===
        
        # Daten-Information
        self.data_info = DataInfoPanel(middle_frame, title="📊 Original Daten")
        self.data_info.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Resampled Daten Info
        self.resampled_info = DataInfoPanel(middle_frame, title="🔄 Resampled Daten")
        self.resampled_info.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Performance Monitor
        self.performance_monitor = PerformanceMonitor(middle_frame, title="⚡ Performance")
        self.performance_monitor.pack(fill=tk.X)
        
        # === RECHTE SPALTE ===
        
        # Code Viewer
        self.code_viewer = CodeViewer(right_frame, title="💻 Generierter Jupyter Code")
        self.code_viewer.pack(fill=tk.BOTH, expand=True)
        
        # === STATUS BAR ===
        self.status_bar = StatusBar(main_container)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def create_timeframe_widgets(self):
        """Timeframe-Auswahl Widgets erstellen"""
        # Alle vorhandenen Widgets entfernen
        for widget in self.timeframe_frame.winfo_children():
            widget.destroy()
        
        # Verfügbare Timeframes
        timeframes = [
            ("1min", "1 Minute"),
            ("2min", "2 Minuten"),
            ("5min", "5 Minuten"),
            ("15min", "15 Minuten"),
            ("30min", "30 Minuten"),
            ("1H", "1 Stunde"),
            ("2H", "2 Stunden"),
            ("4H", "4 Stunden"),
            ("6H", "6 Stunden"),
            ("12H", "12 Stunden"),
            ("1D", "1 Tag"),
            ("1W", "1 Woche")
        ]
        
        if self.resampling_mode.get() == "single":
            # Single-Timeframe: Dropdown
            ttk.Label(self.timeframe_frame, text="Ziel-Timeframe:").pack(anchor=tk.W, pady=(0, 5))
            
            self.single_timeframe = tk.StringVar(value="1H")
            timeframe_combo = ttk.Combobox(
                self.timeframe_frame,
                textvariable=self.single_timeframe,
                values=[f"{tf[0]} ({tf[1]})" for tf in timeframes],
                state="readonly"
            )
            timeframe_combo.pack(fill=tk.X)
            
        else:
            # Multi-Timeframe: Checkboxes
            ttk.Label(self.timeframe_frame, text="Ziel-Timeframes (mehrere auswählen):").pack(anchor=tk.W, pady=(0, 5))
            
            self.timeframe_vars = {}
            
            # 2 Spalten Layout
            for i, (tf_code, tf_name) in enumerate(timeframes):
                row = i // 2
                col = i % 2
                
                var = tk.BooleanVar()
                self.timeframe_vars[tf_code] = var
                
                cb = ttk.Checkbutton(
                    self.timeframe_frame,
                    text=f"{tf_code} ({tf_name})",
                    variable=var
                )
                cb.grid(row=row, column=col, sticky=tk.W, padx=(0, 10), pady=2)
            
            # Standard-Auswahl
            self.timeframe_vars["1H"].set(True)
            self.timeframe_vars["4H"].set(True)
            self.timeframe_vars["1D"].set(True)
    
    def on_mode_change(self):
        """Resampling-Modus geändert"""
        self.create_timeframe_widgets()
    
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
                self.status_bar.update_status("✅ Daten von App 1 geladen")
            else:
                self.status_bar.update_status("⚠️ Keine Daten von App 1 verfügbar")
                
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
            # Original Daten-Info
            data_info = data_manager.get_data_info()
            self.data_info.update_info(data_info)
            
            # Performance-Metriken
            memory_mb = self.current_data.memory_usage(deep=True).sum() / (1024 * 1024)
            self.performance_monitor.update_metric("Speicherverbrauch", f"{memory_mb:.1f} MB")
    
    def get_selected_timeframes(self):
        """Ausgewählte Timeframes abrufen"""
        if self.resampling_mode.get() == "single":
            # Single-Timeframe
            tf_text = self.single_timeframe.get()
            tf_code = tf_text.split(" (")[0]  # Extrahiere Code vor dem Namen
            return [tf_code]
        else:
            # Multi-Timeframe
            selected = []
            for tf_code, var in self.timeframe_vars.items():
                if var.get():
                    selected.append(tf_code)
            return selected
    
    def start_resampling(self):
        """Resampling starten"""
        if self.current_data is None:
            messagebox.showwarning("Warnung", "Keine Daten zum Resampling vorhanden!")
            return
        
        selected_timeframes = self.get_selected_timeframes()
        
        if not selected_timeframes:
            messagebox.showwarning("Warnung", "Bitte wählen Sie mindestens einen Timeframe aus!")
            return
        
        self.status_bar.update_status("Starte Resampling...", 0)
        self.performance_monitor.start_timing()
        
        def resample_in_background():
            try:
                self.resampled_data = {}
                total_timeframes = len(selected_timeframes)
                
                for i, timeframe in enumerate(selected_timeframes):
                    progress = int((i / total_timeframes) * 100)
                    self.root.after(0, lambda p=progress: self.status_bar.update_status(f"Resampling {timeframe}...", p))
                    
                    # OHLCV Resampling
                    if self.ohlc_method.get() == "vwap" and 'volume' in self.current_data.columns:
                        # VWAP-basiertes Resampling
                        resampled = self.current_data.resample(timeframe).apply({
                            'open': 'first',
                            'high': 'max',
                            'low': 'min',
                            'close': 'last',
                            'volume': 'sum'
                        })
                        
                        # VWAP berechnen
                        vwap = (self.current_data['close'] * self.current_data['volume']).resample(timeframe).sum() / \
                               self.current_data['volume'].resample(timeframe).sum()
                        resampled['vwap'] = vwap
                        
                    else:
                        # Standard OHLC Resampling
                        agg_dict = {
                            'open': 'first',
                            'high': 'max',
                            'low': 'min',
                            'close': 'last'
                        }
                        
                        if 'volume' in self.current_data.columns:
                            agg_dict['volume'] = 'sum'
                        
                        resampled = self.current_data.resample(timeframe).agg(agg_dict)
                    
                    # Leere Zeilen entfernen falls gewünscht
                    if self.dropna_var.get():
                        resampled = resampled.dropna()
                    
                    # Memory-Optimierung
                    resampled = data_manager.performance_handler.optimize_data_types(resampled)
                    
                    self.resampled_data[timeframe] = resampled
                
                # GUI aktualisieren
                self.root.after(0, self.update_resampled_display)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Resampling-Fehler: {e}"))
                self.root.after(0, lambda: self.status_bar.update_status(f"Resampling-Fehler: {e}", 0))
        
        threading.Thread(target=resample_in_background, daemon=True).start()
    
    def update_resampled_display(self):
        """Resampled Daten-Anzeige aktualisieren"""
        self.performance_monitor.stop_timing()
        
        if self.resampled_data:
            # Info für resampled Daten
            info = {}
            total_memory = 0
            
            for timeframe, data in self.resampled_data.items():
                memory_mb = data.memory_usage(deep=True).sum() / (1024 * 1024)
                total_memory += memory_mb
                
                info[f"{timeframe} Shape"] = str(data.shape)
                info[f"{timeframe} Memory"] = f"{memory_mb:.1f} MB"
                info[f"{timeframe} Zeitraum"] = f"{data.index[0]} bis {data.index[-1]}" if len(data) > 0 else "Leer"
            
            info["Gesamt Memory"] = f"{total_memory:.1f} MB"
            info["Anzahl Timeframes"] = len(self.resampled_data)
            
            self.resampled_info.update_info(info)
            
            # Performance-Metriken aktualisieren
            self.performance_monitor.update_metric("Speicherverbrauch", f"{total_memory:.1f} MB")
            
            # Daten im Data Manager setzen (Multi-Timeframe als Dict oder Single als DataFrame)
            if len(self.resampled_data) == 1:
                # Single-Timeframe: DataFrame setzen
                timeframe = list(self.resampled_data.keys())[0]
                data_manager.set_current_data(
                    self.resampled_data[timeframe],
                    source_app='app2_resampling',
                    metadata={
                        'resampling_mode': 'single',
                        'timeframe': timeframe,
                        'original_shape': self.current_data.shape,
                        'resampled_shape': self.resampled_data[timeframe].shape
                    }
                )
            else:
                # Multi-Timeframe: Dict setzen
                data_manager.set_current_data(
                    self.resampled_data,
                    source_app='app2_resampling',
                    metadata={
                        'resampling_mode': 'multi',
                        'timeframes': list(self.resampled_data.keys()),
                        'original_shape': self.current_data.shape
                    }
                )
            
            self.status_bar.update_status(f"✅ Resampling abgeschlossen: {len(self.resampled_data)} Timeframes", 100)
            
            # Code generieren
            self.generate_code()
    
    def save_data(self):
        """Resampled Daten speichern"""
        if not self.resampled_data:
            messagebox.showwarning("Warnung", "Keine resampled Daten zum Speichern vorhanden!")
            return
        
        self.status_bar.update_status("Speichere Daten...", 0)
        
        def save_in_background():
            try:
                export_config = self.export_options.get_export_config()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if len(self.resampled_data) == 1:
                    # Single-Timeframe
                    timeframe = list(self.resampled_data.keys())[0]
                    filename = f"resampled_{timeframe}_app2_{timestamp}.h5"
                    
                    file_path = data_manager.save_current_data(
                        filename=filename,
                        app_name='app2_resampling',
                        export_config=export_config
                    )
                    
                    self.root.after(0, lambda: messagebox.showinfo("Erfolg", f"Daten gespeichert:\n{file_path}"))
                    
                else:
                    # Multi-Timeframe: Jedes Timeframe separat speichern
                    saved_files = []
                    
                    for timeframe, data in self.resampled_data.items():
                        # Temporär als aktuell setzen
                        data_manager.set_current_data(data, 'app2_resampling_temp')
                        
                        filename = f"resampled_{timeframe}_app2_{timestamp}.h5"
                        file_path = data_manager.save_current_data(
                            filename=filename,
                            app_name='app2_resampling',
                            export_config=export_config
                        )
                        saved_files.append(file_path)
                    
                    # Multi-Timeframe Daten wieder setzen
                    data_manager.set_current_data(self.resampled_data, 'app2_resampling')
                    
                    files_text = "\n".join([os.path.basename(f) for f in saved_files])
                    self.root.after(0, lambda: messagebox.showinfo("Erfolg", f"Multi-Timeframe Daten gespeichert:\n{files_text}"))
                
                self.root.after(0, lambda: self.status_bar.update_status("✅ Daten gespeichert", 100))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Speicher-Fehler: {e}"))
        
        threading.Thread(target=save_in_background, daemon=True).start()
    
    def generate_code(self):
        """Jupyter Code generieren"""
        if not self.resampled_data:
            return
        
        try:
            config = {
                'timeframes': list(self.resampled_data.keys()),
                'method': self.ohlc_method.get(),
                'dropna': self.dropna_var.get(),
                'resampling_mode': self.resampling_mode.get(),
                'input_file': 'app1_output.h5',  # Placeholder
                'output_file': f"app2_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5",
                'vbt_features': self.export_options.get_export_config()['vbt_features']
            }
            
            code = code_generator.generate_code('app2_resampling', config)
            self.code_viewer.set_code(code)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen: {e}")
    
    def go_to_app3(self):
        """Zu App 3 wechseln"""
        if not self.resampled_data:
            messagebox.showwarning("Warnung", "Bitte führen Sie zuerst das Resampling durch!")
            return
        
        try:
            import app3_indicators
            app3_window = tk.Toplevel(self.root)
            app3_indicators.IndicatorsApp(app3_window)
        except ImportError:
            messagebox.showinfo("Info", "App 3 wird als nächstes entwickelt...")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = ResamplingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
