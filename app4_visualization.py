#!/usr/bin/env python3
"""
📊 APP 4: VISUALISIERUNG (KONTROLLE)
VectorBT Pro GUI System - Charts und CSV-Export
- Visualisierung von Charts (TradingView-ähnlich)
- CSV-Export zur Kontrolle der Indikatoren
- Auswahl von Chart-Anzahl, Kerzen pro Chart, Zeitraum (Segmentierung)
- Auswahl der Exportmenge für CSV
- Code-Generierung für Jupyter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# Lokale Imports
from shared_components import (
    ModernStyle, StatusBar, FileSelector, ExportOptions, 
    CodeViewer, DataInfoPanel, PerformanceMonitor
)
from data_manager import data_manager
from code_generator import code_generator

class VisualizationApp:
    """📊 APP 4: VISUALISIERUNG (KONTROLLE)"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 VectorBT Pro - App 4: Visualisierung (Kontrolle)")
        self.root.geometry("1600x1000")
        self.root.configure(bg=ModernStyle.COLORS['bg_dark'])
        
        # Variablen
        self.current_data = None
        self.is_multi_timeframe = False
        self.timeframes = []
        self.selected_timeframe = tk.StringVar()
        self.chart_count = tk.IntVar(value=1)
        self.candles_per_chart = tk.IntVar(value=100)
        self.csv_export_rows = tk.IntVar(value=1000)
        
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
            text="📊 APP 4: VISUALISIERUNG (KONTROLLE)", 
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(0, 20))
        
        # Hauptbereich (3 Spalten)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Konfiguration
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Mittlere Spalte - Charts
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
        
        # Timeframe-Auswahl
        timeframe_frame = ttk.LabelFrame(left_frame, text="⏱️ Timeframe", padding="10")
        timeframe_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.timeframe_combo = ttk.Combobox(
            timeframe_frame,
            textvariable=self.selected_timeframe,
            state="readonly"
        )
        self.timeframe_combo.pack(fill=tk.X, pady=(0, 5))
        self.timeframe_combo.bind('<<ComboboxSelected>>', self.on_timeframe_change)
        
        # Chart-Konfiguration
        chart_frame = ttk.LabelFrame(left_frame, text="📈 Chart-Konfiguration", padding="10")
        chart_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Chart-Anzahl
        ttk.Label(chart_frame, text="Anzahl Charts:").pack(anchor=tk.W)
        chart_count_frame = ttk.Frame(chart_frame)
        chart_count_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Scale(
            chart_count_frame,
            from_=1, to=4,
            variable=self.chart_count,
            orient=tk.HORIZONTAL,
            command=self.on_chart_config_change
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(chart_count_frame, textvariable=self.chart_count).pack(side=tk.RIGHT)
        
        # Kerzen pro Chart
        ttk.Label(chart_frame, text="Kerzen pro Chart:").pack(anchor=tk.W)
        candles_frame = ttk.Frame(chart_frame)
        candles_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Scale(
            candles_frame,
            from_=50, to=500,
            variable=self.candles_per_chart,
            orient=tk.HORIZONTAL,
            command=self.on_chart_config_change
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(candles_frame, textvariable=self.candles_per_chart).pack(side=tk.RIGHT)
        
        # CSV-Export Konfiguration
        csv_frame = ttk.LabelFrame(left_frame, text="📄 CSV-Export", padding="10")
        csv_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(csv_frame, text="Anzahl Zeilen:").pack(anchor=tk.W)
        csv_rows_frame = ttk.Frame(csv_frame)
        csv_rows_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Scale(
            csv_rows_frame,
            from_=100, to=10000,
            variable=self.csv_export_rows,
            orient=tk.HORIZONTAL
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(csv_rows_frame, textvariable=self.csv_export_rows).pack(side=tk.RIGHT)
        
        # Aktions-Buttons
        actions_frame = ttk.LabelFrame(left_frame, text="🚀 Aktionen", padding="10")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            actions_frame, 
            text="📊 Charts erstellen", 
            command=self.create_charts,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="📄 CSV exportieren", 
            command=self.export_csv
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="💻 Code generieren", 
            command=self.generate_code
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            actions_frame, 
            text="➡️ Zu App 5", 
            command=self.go_to_app5
        ).pack(fill=tk.X)
        
        # === MITTLERE SPALTE ===
        
        # Chart-Container
        self.chart_frame = ttk.LabelFrame(middle_frame, text="📈 Charts", padding="10")
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder
        self.chart_placeholder = ttk.Label(
            self.chart_frame,
            text="📊 Charts werden hier angezeigt\n\nBitte laden Sie Daten und klicken Sie auf 'Charts erstellen'",
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
            
            if data is not None:
                self.current_data = data
                
                # Multi-Timeframe erkennen
                if isinstance(data, dict):
                    self.is_multi_timeframe = True
                    self.timeframes = list(data.keys())
                    self.timeframe_combo['values'] = self.timeframes
                    if self.timeframes:
                        self.selected_timeframe.set(self.timeframes[0])
                else:
                    self.is_multi_timeframe = False
                    self.timeframes = ['single']
                    self.timeframe_combo['values'] = ['Single Timeframe']
                    self.selected_timeframe.set('Single Timeframe')
                
                self.update_data_display()
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
                    self.is_multi_timeframe = False
                    self.timeframes = ['single']
                    
                    self.root.after(0, lambda: self.timeframe_combo.configure(values=['Single Timeframe']))
                    self.root.after(0, lambda: self.selected_timeframe.set('Single Timeframe'))
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
    
    def on_timeframe_change(self, event=None):
        """Timeframe geändert"""
        self.update_data_display()
    
    def on_chart_config_change(self, value=None):
        """Chart-Konfiguration geändert"""
        # Charts neu erstellen falls bereits vorhanden
        pass
    
    def get_current_timeframe_data(self):
        """Daten für aktuellen Timeframe abrufen"""
        if self.current_data is None:
            return None
        
        if self.is_multi_timeframe:
            selected_tf = self.selected_timeframe.get()
            if selected_tf in self.current_data:
                return self.current_data[selected_tf]
        else:
            return self.current_data
        
        return None
    
    def create_charts(self):
        """Charts erstellen"""
        data = self.get_current_timeframe_data()
        
        if data is None:
            messagebox.showwarning("Warnung", "Keine Daten für Charts verfügbar!")
            return
        
        self.status_bar.update_status("Erstelle Charts...", 0)
        self.performance_monitor.start_timing()
        
        def create_in_background():
            try:
                # Chart-Container leeren
                self.root.after(0, self.clear_charts)
                
                chart_count = self.chart_count.get()
                candles_per_chart = self.candles_per_chart.get()
                
                # Daten segmentieren
                total_rows = len(data)
                segment_size = min(candles_per_chart, total_rows // chart_count)
                
                charts_data = []
                for i in range(chart_count):
                    start_idx = i * segment_size
                    end_idx = min(start_idx + segment_size, total_rows)
                    
                    if start_idx < total_rows:
                        segment = data.iloc[start_idx:end_idx]
                        charts_data.append(segment)
                
                # Charts im Main Thread erstellen
                self.root.after(0, lambda: self.create_chart_widgets(charts_data))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"Chart-Fehler: {e}"))
        
        threading.Thread(target=create_in_background, daemon=True).start()
    
    def clear_charts(self):
        """Chart-Container leeren"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
    
    def create_chart_widgets(self, charts_data):
        """Chart-Widgets erstellen"""
        try:
            # Matplotlib Style
            plt.style.use('dark_background')
            
            chart_count = len(charts_data)
            
            # Grid Layout berechnen
            if chart_count == 1:
                rows, cols = 1, 1
            elif chart_count == 2:
                rows, cols = 1, 2
            elif chart_count <= 4:
                rows, cols = 2, 2
            else:
                rows, cols = 2, 3
            
            # Figure erstellen
            fig, axes = plt.subplots(rows, cols, figsize=(12, 8))
            fig.patch.set_facecolor('#2b2b2b')
            
            if chart_count == 1:
                axes = [axes]
            elif chart_count > 1 and rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            # Charts erstellen
            for i, segment_data in enumerate(charts_data):
                if i >= len(axes):
                    break
                
                ax = axes[i]
                
                # OHLC Candlestick (vereinfacht)
                if all(col in segment_data.columns for col in ['open', 'high', 'low', 'close']):
                    # Vereinfachte Candlestick-Darstellung
                    ax.plot(segment_data.index, segment_data['close'], color='white', linewidth=1, label='Close')
                    
                    # Indikatoren hinzufügen falls vorhanden
                    for col in segment_data.columns:
                        if col.lower() in ['rsi', 'macd', 'sma', 'ema']:
                            ax2 = ax.twinx()
                            ax2.plot(segment_data.index, segment_data[col], alpha=0.7, label=col)
                            ax2.legend(loc='upper right')
                
                ax.set_title(f"Chart {i+1} ({len(segment_data)} Kerzen)")
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                # X-Achse formatieren
                if hasattr(segment_data.index, 'to_pydatetime'):
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(segment_data)//5)))
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            # Leere Subplots ausblenden
            for i in range(chart_count, len(axes)):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            
            # Canvas erstellen
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.performance_monitor.stop_timing()
            self.status_bar.update_status(f"✅ {chart_count} Charts erstellt", 100)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Chart-Widget-Fehler: {e}")
    
    def export_csv(self):
        """CSV exportieren"""
        data = self.get_current_timeframe_data()
        
        if data is None:
            messagebox.showwarning("Warnung", "Keine Daten für CSV-Export verfügbar!")
            return
        
        # Datei-Dialog
        file_path = filedialog.asksaveasfilename(
            title="CSV exportieren",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.status_bar.update_status("Exportiere CSV...", 0)
        
        def export_in_background():
            try:
                # Anzahl Zeilen begrenzen
                export_rows = self.csv_export_rows.get()
                
                if len(data) > export_rows:
                    # Letzte N Zeilen exportieren
                    export_data = data.tail(export_rows)
                else:
                    export_data = data
                
                # CSV speichern
                export_data.to_csv(file_path, index=True)
                
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                self.root.after(0, lambda: self.status_bar.update_status(f"✅ CSV exportiert: {file_size_mb:.1f} MB", 100))
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", f"CSV exportiert:\n{file_path}\n\n{len(export_data):,} Zeilen, {file_size_mb:.1f} MB"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"CSV-Export-Fehler: {e}"))
        
        threading.Thread(target=export_in_background, daemon=True).start()
    
    def generate_code(self):
        """Jupyter Code generieren"""
        if self.current_data is None:
            return
        
        try:
            config = {
                'chart_count': self.chart_count.get(),
                'candles_per_chart': self.candles_per_chart.get(),
                'csv_export_rows': self.csv_export_rows.get(),
                'selected_timeframe': self.selected_timeframe.get(),
                'is_multi_timeframe': self.is_multi_timeframe,
                'input_file': 'app3_output.h5'
            }
            
            # Einfacher Visualisierungs-Code
            code = f'''
# 📊 VISUALISIERUNG - APP 4
# Generiert von VectorBT Pro GUI System am {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Daten laden
data = pd.read_hdf("{config['input_file']}", key='data')

# Chart-Konfiguration
chart_count = {config['chart_count']}
candles_per_chart = {config['candles_per_chart']}

# Daten segmentieren
total_rows = len(data)
segment_size = min(candles_per_chart, total_rows // chart_count)

# Charts erstellen
fig = make_subplots(
    rows=chart_count, cols=1,
    subplot_titles=[f"Chart {{i+1}}" for i in range(chart_count)],
    vertical_spacing=0.1
)

for i in range(chart_count):
    start_idx = i * segment_size
    end_idx = min(start_idx + segment_size, total_rows)
    segment = data.iloc[start_idx:end_idx]
    
    # Candlestick Chart
    fig.add_trace(
        go.Candlestick(
            x=segment.index,
            open=segment['open'],
            high=segment['high'],
            low=segment['low'],
            close=segment['close'],
            name=f"OHLC {{i+1}}"
        ),
        row=i+1, col=1
    )

fig.update_layout(
    title="VectorBT Pro Visualisierung",
    xaxis_rangeslider_visible=False,
    height=800
)

fig.show()

# CSV Export
export_data = data.tail({config['csv_export_rows']})
export_data.to_csv("visualization_export.csv")
print(f"✅ CSV exportiert: {{len(export_data):,}} Zeilen")
'''
            
            self.code_viewer.set_code(code)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen: {e}")
    
    def go_to_app5(self):
        """Zu App 5 wechseln"""
        try:
            import app5_features
            app5_window = tk.Toplevel(self.root)
            app5_features.FeaturesApp(app5_window)
        except ImportError:
            messagebox.showinfo("Info", "App 5 wird als nächstes entwickelt...")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = VisualizationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
