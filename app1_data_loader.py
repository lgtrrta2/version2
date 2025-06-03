#!/usr/bin/env python3
"""
📊 APP 1: HISTORISCHE DATEN LOADER
VectorBT Pro GUI System - Daten laden und verarbeiten
- Historische Daten laden (bereits bereinigt)
- Informationen anzeigen
- Zeitraumauswahl (6M, 1J, 2J, 4J, benutzerdefiniert)
- Speichern als VBT-konforme Datei mit Performance-Features
- Code-Generierung für Jupyter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import pandas as pd
from datetime import datetime
import threading

# Lokale Imports
from shared_components import (
    ModernStyle, StatusBar, FileSelector, TimeframeSelector, 
    ExportOptions, CodeViewer, DataInfoPanel, PerformanceMonitor
)
from data_manager import data_manager
from code_generator import code_generator

class DataLoaderApp:
    """📊 APP 1: HISTORISCHE DATEN LOADER"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 VectorBT Pro - App 1: Historische Daten Loader")
        self.root.geometry("1400x900")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Variablen
        self.current_data = None
        self.selected_file = None
        
        # GUI erstellen
        self.create_widgets()
        
        # Verfügbare Dateien scannen
        self.scan_available_files()
    
    def create_widgets(self):
        """GUI-Elemente erstellen"""
        
        # Hauptcontainer
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_container, 
            text="📊 APP 1: HISTORISCHE DATEN LOADER", 
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
        
        # Datei-Auswahl
        self.file_selector = FileSelector(
            left_frame,
            title="📁 Historische Daten auswählen",
            file_types=[
                ("HDF5 files", "*.h5"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            callback=self.on_file_selected
        )
        self.file_selector.pack(fill=tk.X, pady=(0, 20))
        
        # Verfügbare Dateien
        available_frame = ttk.LabelFrame(left_frame, text="📋 Verfügbare Dateien", padding="10")
        available_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Listbox für verfügbare Dateien
        self.files_listbox = tk.Listbox(available_frame, height=8, font=ModernStyle.FONTS['small'])
        self.files_listbox.pack(fill=tk.X, pady=(0, 5))
        self.files_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        # Refresh Button
        ttk.Button(available_frame, text="🔄 Aktualisieren", command=self.scan_available_files).pack()
        
        # Zeitrahmen-Auswahl
        self.timeframe_selector = TimeframeSelector(left_frame, title="📅 Zeitraum auswählen")
        self.timeframe_selector.pack(fill=tk.X, pady=(0, 20))
        
        # Export-Optionen
        self.export_options = ExportOptions(left_frame, title="💾 Export-Optionen")
        self.export_options.pack(fill=tk.X, pady=(0, 20))
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(left_frame, text="🚀 Aktionen", padding="10")
        actions_frame.pack(fill=tk.X)
        
        ttk.Button(
            actions_frame, 
            text="📊 Daten laden", 
            command=self.load_data,
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
            text="➡️ Zu App 2", 
            command=self.go_to_app2
        ).pack(fill=tk.X)
        
        # === MITTLERE SPALTE ===
        
        # Daten-Information
        self.data_info = DataInfoPanel(middle_frame, title="📊 Daten-Information")
        self.data_info.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
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
    
    def scan_available_files(self):
        """Verfügbare Dateien scannen"""
        self.status_bar.update_status("Scanne verfügbare Dateien...", 0)
        
        def scan_in_background():
            try:
                # Historische Daten Ordner scannen
                historical_data_path = "historical_data"
                if not os.path.exists(historical_data_path):
                    os.makedirs(historical_data_path, exist_ok=True)
                
                available_files = data_manager.get_available_files(historical_data_path)
                
                # GUI im Main Thread aktualisieren
                self.root.after(0, lambda: self.update_files_list(available_files))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_bar.update_status(f"Scan-Fehler: {e}", 0))
        
        threading.Thread(target=scan_in_background, daemon=True).start()
    
    def update_files_list(self, available_files):
        """Dateiliste aktualisieren"""
        self.files_listbox.delete(0, tk.END)
        
        if not available_files:
            self.files_listbox.insert(0, "Keine Dateien gefunden")
            self.status_bar.update_status("Keine Dateien gefunden", 100)
            return
        
        for asset_name, file_info in available_files.items():
            display_text = f"{asset_name} ({file_info['file_size_mb']:.1f} MB)"
            self.files_listbox.insert(tk.END, display_text)
        
        self.status_bar.update_status(f"{len(available_files)} Dateien gefunden", 100)
    
    def on_listbox_select(self, event):
        """Datei aus Liste auswählen"""
        selection = self.files_listbox.curselection()
        if selection:
            # Hole Datei-Info
            historical_data_path = "historical_data"
            available_files = data_manager.get_available_files(historical_data_path)
            
            if available_files:
                asset_names = list(available_files.keys())
                if selection[0] < len(asset_names):
                    asset_name = asset_names[selection[0]]
                    file_info = available_files[asset_name]
                    
                    # Datei-Selektor aktualisieren
                    self.file_selector.selected_file = file_info['file_path']
                    self.file_selector.file_var.set(file_info['file_name'])
                    self.file_selector.info_var.set(
                        f"Größe: {file_info['file_size_mb']:.1f} MB | Pfad: {file_info['file_path']}"
                    )
                    
                    self.selected_file = file_info['file_path']
    
    def on_file_selected(self, file_path):
        """Callback wenn Datei ausgewählt wird"""
        self.selected_file = file_path
        self.status_bar.update_status(f"Datei ausgewählt: {os.path.basename(file_path)}")
    
    def load_data(self):
        """Daten laden"""
        if not self.selected_file:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Datei aus!")
            return
        
        self.status_bar.update_status("Lade Daten...", 0)
        self.performance_monitor.start_timing()
        
        def load_in_background():
            try:
                # Daten laden
                data = data_manager.load_data(self.selected_file)
                
                if data is not None:
                    # Zeitraum filtern
                    start_date, end_date = self.timeframe_selector.get_date_range()
                    
                    if start_date and end_date:
                        original_len = len(data)
                        data = data[(data.index >= start_date) & (data.index <= end_date)]
                        filtered_len = len(data)
                        
                        self.root.after(0, lambda: self.status_bar.update_status(
                            f"Zeitraum gefiltert: {original_len:,} → {filtered_len:,} Zeilen"
                        ))
                    
                    # Memory-Optimierung
                    data = data_manager.performance_handler.optimize_data_types(data)
                    
                    # Daten setzen
                    data_manager.set_current_data(
                        data, 
                        source_app='app1_data_loader',
                        metadata={
                            'source_file': self.selected_file,
                            'timeframe_filter': {
                                'start_date': str(start_date) if start_date else None,
                                'end_date': str(end_date) if end_date else None
                            }
                        }
                    )
                    
                    self.current_data = data
                    
                    # GUI aktualisieren
                    self.root.after(0, self.update_data_display)
                    
                else:
                    self.root.after(0, lambda: messagebox.showerror("Fehler", "Daten konnten nicht geladen werden!"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Lade-Fehler: {e}"))
                self.root.after(0, lambda: self.status_bar.update_status(f"Lade-Fehler: {e}", 0))
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_data_display(self):
        """Daten-Anzeige aktualisieren"""
        if self.current_data is not None:
            # Performance Monitor stoppen
            self.performance_monitor.stop_timing()
            
            # Daten-Info aktualisieren
            data_info = data_manager.get_data_info()
            self.data_info.update_info(data_info)
            
            # Performance-Metriken aktualisieren
            memory_mb = self.current_data.memory_usage(deep=True).sum() / (1024 * 1024)
            self.performance_monitor.update_metric("Speicherverbrauch", f"{memory_mb:.1f} MB")
            
            # Status aktualisieren
            self.status_bar.update_status(
                f"✅ Daten geladen: {self.current_data.shape[0]:,} Zeilen, {self.current_data.shape[1]} Spalten", 
                100
            )
            
            # Code generieren
            self.generate_code()
    
    def save_data(self):
        """Daten speichern"""
        if self.current_data is None:
            messagebox.showwarning("Warnung", "Keine Daten zum Speichern vorhanden!")
            return
        
        self.status_bar.update_status("Speichere Daten...", 0)
        
        def save_in_background():
            try:
                # Export-Konfiguration abrufen
                export_config = self.export_options.get_export_config()
                
                # Dateiname generieren
                base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{base_name}_app1_{timestamp}.h5"
                
                # Speichern
                file_path = data_manager.save_current_data(
                    filename=filename,
                    app_name='app1_data_loader',
                    export_config=export_config
                )
                
                # Performance-Metriken aktualisieren
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                self.root.after(0, lambda: self.performance_monitor.update_metric("Dateigröße", f"{file_size_mb:.1f} MB"))
                
                self.root.after(0, lambda: self.status_bar.update_status(f"✅ Daten gespeichert: {filename}", 100))
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", f"Daten erfolgreich gespeichert:\n{file_path}"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Speicher-Fehler: {e}"))
                self.root.after(0, lambda: self.status_bar.update_status(f"Speicher-Fehler: {e}", 0))
        
        threading.Thread(target=save_in_background, daemon=True).start()
    
    def generate_code(self):
        """Jupyter Code generieren"""
        if self.current_data is None:
            return
        
        try:
            # Konfiguration für Code-Generator
            config = {
                'file_path': self.selected_file,
                'start_date': self.timeframe_selector.start_date_var.get(),
                'end_date': self.timeframe_selector.end_date_var.get(),
                'vbt_available': True,
                'vbt_features': self.export_options.get_export_config()['vbt_features'],
                'output_file': f"app1_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
            }
            
            # Code generieren
            code = code_generator.generate_code('app1_data_loader', config)
            
            # Code anzeigen
            self.code_viewer.set_code(code)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen: {e}")
    
    def go_to_app2(self):
        """Zu App 2 wechseln"""
        if self.current_data is None:
            messagebox.showwarning("Warnung", "Bitte laden Sie zuerst Daten!")
            return
        
        # App 2 starten
        try:
            import app2_resampling
            app2_window = tk.Toplevel(self.root)
            app2_resampling.ResamplingApp(app2_window)
        except ImportError:
            messagebox.showinfo("Info", "App 2 wird als nächstes entwickelt...")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = DataLoaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
