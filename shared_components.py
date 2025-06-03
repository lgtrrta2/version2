#!/usr/bin/env python3
"""
🚀 SHARED COMPONENTS - VectorBT Pro GUI System
Gemeinsame GUI-Komponenten für alle 9 Apps
- Moderne Tkinter Widgets
- Konsistentes Design
- Performance-optimiert
- Wiederverwendbare Komponenten
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# VectorBT Pro Import
try:
    import vectorbtpro as vbt
    VBT_AVAILABLE = True
except ImportError:
    VBT_AVAILABLE = False

class ModernStyle:
    """🎨 Moderne GUI-Styles"""
    
    COLORS = {
        'bg_dark': '#2b2b2b',
        'bg_light': '#3c3c3c',
        'accent': '#0078d4',
        'success': '#107c10',
        'warning': '#ff8c00',
        'error': '#d13438',
        'text_light': '#ffffff',
        'text_dark': '#000000'
    }
    
    FONTS = {
        'title': ('Segoe UI', 16, 'bold'),
        'subtitle': ('Segoe UI', 12, 'bold'),
        'normal': ('Segoe UI', 10),
        'small': ('Segoe UI', 8),
        'code': ('Consolas', 9)
    }

class StatusBar(ttk.Frame):
    """📊 Status-Bar für alle Apps"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        
    def create_widgets(self):
        # Status Label
        self.status_var = tk.StringVar(value="Bereit")
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self, length=200, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=5)
        
        # Performance Info
        perf_info = "✅ VBT Pro" if VBT_AVAILABLE else "❌ VBT Pro"
        self.perf_label = ttk.Label(self, text=perf_info, font=ModernStyle.FONTS['small'])
        self.perf_label.pack(side=tk.RIGHT, padx=10)
    
    def update_status(self, message, progress=None):
        """Status aktualisieren"""
        self.status_var.set(message)
        if progress is not None:
            self.progress['value'] = progress
        self.update()

class FileSelector(ttk.Frame):
    """📁 Datei-Auswahl Komponente"""
    
    def __init__(self, parent, title="Datei auswählen", file_types=None, callback=None):
        super().__init__(parent)
        self.title = title
        self.file_types = file_types or [("HDF5 files", "*.h5"), ("All files", "*.*")]
        self.callback = callback
        self.selected_file = None
        self.create_widgets()
    
    def create_widgets(self):
        # Label
        ttk.Label(self, text=self.title, font=ModernStyle.FONTS['subtitle']).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame für Eingabe und Button
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Eingabefeld
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(input_frame, textvariable=self.file_var, state='readonly')
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Browse Button
        ttk.Button(input_frame, text="📁 Durchsuchen", command=self.browse_file).pack(side=tk.RIGHT)
        
        # Info Label
        self.info_var = tk.StringVar()
        self.info_label = ttk.Label(self, textvariable=self.info_var, font=ModernStyle.FONTS['small'])
        self.info_label.pack(anchor=tk.W)
    
    def browse_file(self):
        """Datei-Dialog öffnen"""
        file_path = filedialog.askopenfilename(
            title=self.title,
            filetypes=self.file_types
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_var.set(os.path.basename(file_path))
            
            # Datei-Info anzeigen
            try:
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                self.info_var.set(f"Größe: {size_mb:.1f} MB | Pfad: {file_path}")
            except:
                self.info_var.set(f"Pfad: {file_path}")
            
            # Callback ausführen
            if self.callback:
                self.callback(file_path)

class ParameterPanel(ttk.LabelFrame):
    """⚙️ Parameter-Panel für Indikatoren/Strategien"""
    
    def __init__(self, parent, title="Parameter"):
        super().__init__(parent, text=title, padding="10")
        self.parameters = {}
        self.widgets = {}
        
    def add_parameter(self, name, param_type, default_value, description="", options=None):
        """Parameter hinzufügen"""
        row = len(self.parameters)
        
        # Label
        ttk.Label(self, text=f"{name}:", font=ModernStyle.FONTS['normal']).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=2
        )
        
        # Widget basierend auf Typ
        if param_type == 'int':
            var = tk.IntVar(value=default_value)
            widget = ttk.Spinbox(self, from_=0, to=1000, textvariable=var, width=10)
        elif param_type == 'float':
            var = tk.DoubleVar(value=default_value)
            widget = ttk.Spinbox(self, from_=0.0, to=100.0, increment=0.1, textvariable=var, width=10)
        elif param_type == 'bool':
            var = tk.BooleanVar(value=default_value)
            widget = ttk.Checkbutton(self, variable=var)
        elif param_type == 'choice' and options:
            var = tk.StringVar(value=default_value)
            widget = ttk.Combobox(self, textvariable=var, values=options, state='readonly', width=15)
        else:
            var = tk.StringVar(value=str(default_value))
            widget = ttk.Entry(self, textvariable=var, width=20)
        
        widget.grid(row=row, column=1, sticky=tk.W, padx=(0, 10), pady=2)
        
        # Beschreibung
        if description:
            ttk.Label(self, text=description, font=ModernStyle.FONTS['small'], 
                     foreground='gray').grid(row=row, column=2, sticky=tk.W, pady=2)
        
        self.parameters[name] = {
            'type': param_type,
            'variable': var,
            'widget': widget,
            'default': default_value
        }
        self.widgets[name] = widget
    
    def get_parameters(self):
        """Alle Parameter-Werte abrufen"""
        values = {}
        for name, param in self.parameters.items():
            try:
                values[name] = param['variable'].get()
            except:
                values[name] = param['default']
        return values
    
    def set_parameters(self, values):
        """Parameter-Werte setzen"""
        for name, value in values.items():
            if name in self.parameters:
                try:
                    self.parameters[name]['variable'].set(value)
                except:
                    pass
    
    def reset_parameters(self):
        """Parameter auf Standard zurücksetzen"""
        for name, param in self.parameters.items():
            try:
                param['variable'].set(param['default'])
            except:
                pass

class CodeViewer(ttk.LabelFrame):
    """💻 Code-Viewer für generierten Code"""
    
    def __init__(self, parent, title="Generierter Code"):
        super().__init__(parent, text=title, padding="10")
        self.create_widgets()
    
    def create_widgets(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="📋 Kopieren", command=self.copy_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="💾 Speichern", command=self.save_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔄 Aktualisieren", command=self.refresh_code).pack(side=tk.LEFT)
        
        # Code Text Widget
        self.code_text = scrolledtext.ScrolledText(
            self, 
            height=15, 
            font=ModernStyle.FONTS['code'],
            wrap=tk.NONE
        )
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # Syntax Highlighting (einfach)
        self.code_text.tag_configure("keyword", foreground="blue")
        self.code_text.tag_configure("string", foreground="green")
        self.code_text.tag_configure("comment", foreground="gray")
    
    def set_code(self, code):
        """Code setzen"""
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, code)
        self.highlight_syntax()
    
    def get_code(self):
        """Code abrufen"""
        return self.code_text.get(1.0, tk.END)
    
    def copy_code(self):
        """Code in Zwischenablage kopieren"""
        code = self.get_code()
        self.clipboard_clear()
        self.clipboard_append(code)
        messagebox.showinfo("Erfolg", "Code in Zwischenablage kopiert!")
    
    def save_code(self):
        """Code in Datei speichern"""
        file_path = filedialog.asksaveasfilename(
            title="Code speichern",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.get_code())
                messagebox.showinfo("Erfolg", f"Code gespeichert: {file_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
    
    def refresh_code(self):
        """Code aktualisieren (Placeholder für Callback)"""
        pass
    
    def highlight_syntax(self):
        """Einfaches Syntax Highlighting"""
        content = self.code_text.get(1.0, tk.END)
        
        # Keywords
        keywords = ['import', 'from', 'def', 'class', 'if', 'else', 'for', 'while', 'try', 'except']
        for keyword in keywords:
            start = 1.0
            while True:
                pos = self.code_text.search(f"\\b{keyword}\\b", start, tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.code_text.tag_add("keyword", pos, end)
                start = end

class DataInfoPanel(ttk.LabelFrame):
    """📊 Daten-Info Panel"""
    
    def __init__(self, parent, title="Daten-Information"):
        super().__init__(parent, text=title, padding="10")
        self.create_widgets()
    
    def create_widgets(self):
        # Info Text
        self.info_text = scrolledtext.ScrolledText(
            self, 
            height=8, 
            font=ModernStyle.FONTS['small'],
            state='disabled'
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
    
    def update_info(self, data_info):
        """Daten-Info aktualisieren"""
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        
        if isinstance(data_info, dict):
            for key, value in data_info.items():
                self.info_text.insert(tk.END, f"{key}: {value}\n")
        else:
            self.info_text.insert(tk.END, str(data_info))
        
        self.info_text.config(state='disabled')

class PerformanceMonitor(ttk.LabelFrame):
    """⚡ Performance Monitor"""

    def __init__(self, parent, title="Performance"):
        super().__init__(parent, text=title, padding="5")
        self.create_widgets()
        self.start_time = None

    def create_widgets(self):
        # Performance Metriken
        self.metrics = {}

        metrics = [
            ("Verarbeitungszeit", "0.0s"),
            ("Speicherverbrauch", "0 MB"),
            ("Dateigröße", "0 MB"),
            ("Kompressionsrate", "0%")
        ]

        for i, (label, default) in enumerate(metrics):
            ttk.Label(self, text=f"{label}:", font=ModernStyle.FONTS['small']).grid(
                row=i, column=0, sticky=tk.W, padx=(0, 5)
            )

            var = tk.StringVar(value=default)
            ttk.Label(self, textvariable=var, font=ModernStyle.FONTS['small'],
                     foreground='blue').grid(row=i, column=1, sticky=tk.W)

            self.metrics[label] = var

    def start_timing(self):
        """Zeitmessung starten"""
        self.start_time = datetime.now()

    def stop_timing(self):
        """Zeitmessung stoppen"""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.metrics["Verarbeitungszeit"].set(f"{elapsed:.2f}s")

    def update_metric(self, name, value):
        """Metrik aktualisieren"""
        if name in self.metrics:
            self.metrics[name].set(str(value))

class TimeframeSelector(ttk.LabelFrame):
    """📅 Zeitrahmen-Auswahl Komponente"""

    def __init__(self, parent, title="Zeitrahmen"):
        super().__init__(parent, text=title, padding="10")
        self.create_widgets()

    def create_widgets(self):
        # Preset Buttons
        preset_frame = ttk.Frame(self)
        preset_frame.pack(fill=tk.X, pady=(0, 10))

        presets = [
            ("6M", "6 Monate"),
            ("1Y", "1 Jahr"),
            ("2Y", "2 Jahre"),
            ("4Y", "4 Jahre"),
            ("ALL", "Alle Daten")
        ]

        self.preset_var = tk.StringVar(value="1Y")

        for i, (value, text) in enumerate(presets):
            ttk.Radiobutton(
                preset_frame,
                text=text,
                variable=self.preset_var,
                value=value
            ).grid(row=0, column=i, padx=5, sticky=tk.W)

        # Custom Range
        custom_frame = ttk.LabelFrame(self, text="Benutzerdefiniert", padding="5")
        custom_frame.pack(fill=tk.X, pady=(10, 0))

        # Start Date
        ttk.Label(custom_frame, text="Von:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_date_var = tk.StringVar(value="2020-01-01")
        ttk.Entry(custom_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=1, padx=(0, 10))

        # End Date
        ttk.Label(custom_frame, text="Bis:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(custom_frame, textvariable=self.end_date_var, width=12).grid(row=0, column=3)

    def get_date_range(self):
        """Ausgewählten Zeitraum zurückgeben"""
        preset = self.preset_var.get()
        end_date = datetime.now()

        if preset == "6M":
            start_date = end_date - timedelta(days=180)
        elif preset == "1Y":
            start_date = end_date - timedelta(days=365)
        elif preset == "2Y":
            start_date = end_date - timedelta(days=730)
        elif preset == "4Y":
            start_date = end_date - timedelta(days=1460)
        elif preset == "ALL":
            return None, None  # Alle Daten
        else:
            # Custom
            try:
                start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
                end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
            except:
                start_date = end_date - timedelta(days=365)

        return start_date, end_date

class ExportOptions(ttk.LabelFrame):
    """💾 Export-Optionen Komponente"""

    def __init__(self, parent, title="Export-Optionen"):
        super().__init__(parent, text=title, padding="10")
        self.create_widgets()

    def create_widgets(self):
        # VBT Pro Features
        vbt_frame = ttk.LabelFrame(self, text="VectorBT Pro Features", padding="5")
        vbt_frame.pack(fill=tk.X, pady=(0, 10))

        self.vbt_features = {}
        features = [
            ("blosc_compression", "Blosc Kompression", True),
            ("vbt_data_objects", "VBT Data Objects", True),
            ("memory_optimization", "Memory Optimierung", True),
            ("metadata_export", "Metadata Export", True),
            ("cache_enabled", "Cache aktiviert", True)
        ]

        for i, (key, text, default) in enumerate(features):
            var = tk.BooleanVar(value=default)
            ttk.Checkbutton(vbt_frame, text=text, variable=var).grid(
                row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2
            )
            self.vbt_features[key] = var

        # Export Format
        format_frame = ttk.LabelFrame(self, text="Export Format", padding="5")
        format_frame.pack(fill=tk.X, pady=(0, 10))

        self.format_var = tk.StringVar(value="hdf5_blosc")
        formats = [
            ("hdf5_blosc", "HDF5 + Blosc"),
            ("hdf5_standard", "HDF5 Standard"),
            ("pickle_blosc", "Pickle + Blosc"),
            ("csv", "CSV (nur für kleine Daten)")
        ]

        for i, (value, text) in enumerate(formats):
            ttk.Radiobutton(
                format_frame,
                text=text,
                variable=self.format_var,
                value=value
            ).grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)

        # Output Directory
        output_frame = ttk.Frame(self)
        output_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(output_frame, text="Ausgabe-Ordner:").pack(anchor=tk.W)

        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=(5, 0))

        self.output_dir_var = tk.StringVar(value="output")
        ttk.Entry(dir_frame, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(dir_frame, text="📁", command=self.browse_output_dir).pack(side=tk.RIGHT)

    def browse_output_dir(self):
        """Ausgabe-Ordner auswählen"""
        directory = filedialog.askdirectory(title="Ausgabe-Ordner auswählen")
        if directory:
            self.output_dir_var.set(directory)

    def get_export_config(self):
        """Export-Konfiguration zurückgeben"""
        return {
            'vbt_features': {key: var.get() for key, var in self.vbt_features.items()},
            'format': self.format_var.get(),
            'output_dir': self.output_dir_var.get()
        }
