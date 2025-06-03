#!/usr/bin/env python3
"""
📊 DATA MANAGER - VectorBT Pro GUI System
Zentrale Datenverwaltung für alle 9 Apps
- Datenfluss zwischen Apps
- Konfigurationsverwaltung
- State Management
- Metadaten-Tracking
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
import warnings
warnings.filterwarnings('ignore')

from performance_handler import PerformanceHandler

class DataManager:
    """
    📊 ZENTRALE DATENVERWALTUNG
    Verwaltet Datenfluss zwischen allen 9 Apps
    """
    
    def __init__(self):
        self.performance_handler = PerformanceHandler()
        self.current_data = None
        self.data_history = []
        self.app_configs = {}
        self.metadata = {}
        self.workflow_state = {
            'current_app': None,
            'completed_apps': [],
            'data_pipeline': []
        }
        
        # Standard-Pfade
        self.paths = {
            'input': 'historical_data',
            'output': 'output',
            'temp': 'temp',
            'configs': 'configs'
        }
        
        # Erstelle Ordner falls nicht vorhanden
        self.ensure_directories()
    
    def ensure_directories(self):
        """Erstelle notwendige Ordner"""
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
    
    def set_current_data(self, data, source_app, metadata=None):
        """
        Aktuelle Daten setzen
        
        Args:
            data: DataFrame oder VBT Data Object
            source_app: Name der App die die Daten erstellt hat
            metadata: Zusätzliche Metadaten
        """
        # Daten-Historie aktualisieren
        if self.current_data is not None:
            self.data_history.append({
                'data': self.current_data,
                'metadata': self.metadata.copy(),
                'timestamp': datetime.now(),
                'source_app': self.workflow_state.get('current_app', 'unknown')
            })
        
        # Neue Daten setzen
        self.current_data = data
        self.workflow_state['current_app'] = source_app
        
        # Metadaten aktualisieren
        self.metadata.update({
            'source_app': source_app,
            'timestamp': datetime.now().isoformat(),
            'data_shape': data.shape if hasattr(data, 'shape') else None,
            'data_type': type(data).__name__,
            'columns': list(data.columns) if hasattr(data, 'columns') else None,
            'index_range': {
                'start': str(data.index[0]) if hasattr(data, 'index') and len(data) > 0 else None,
                'end': str(data.index[-1]) if hasattr(data, 'index') and len(data) > 0 else None
            } if hasattr(data, 'index') else None
        })
        
        if metadata:
            self.metadata.update(metadata)
        
        # App als abgeschlossen markieren
        if source_app not in self.workflow_state['completed_apps']:
            self.workflow_state['completed_apps'].append(source_app)
        
        print(f"📊 Daten aktualisiert von {source_app}: {self.metadata.get('data_shape', 'Unknown shape')}")
    
    def get_current_data(self):
        """Aktuelle Daten abrufen"""
        return self.current_data
    
    def get_metadata(self):
        """Aktuelle Metadaten abrufen"""
        return self.metadata.copy()
    
    def save_current_data(self, filename, app_name, export_config=None):
        """
        Aktuelle Daten speichern
        
        Args:
            filename: Dateiname (ohne Pfad)
            app_name: Name der App
            export_config: Export-Konfiguration
        """
        if self.current_data is None:
            raise ValueError("Keine Daten zum Speichern vorhanden")
        
        # Datei-Pfad erstellen
        file_path = os.path.join(self.paths['output'], filename)
        
        # Export-Konfiguration anwenden
        if export_config is None:
            export_config = {
                'vbt_features': {
                    'blosc_compression': True,
                    'vbt_data_objects': True,
                    'memory_optimization': True,
                    'metadata_export': True,
                    'cache_enabled': True
                },
                'format': 'hdf5_blosc'
            }
        
        # Metadaten für Export erweitern
        save_metadata = self.metadata.copy()
        save_metadata.update({
            'export_app': app_name,
            'export_config': export_config,
            'export_timestamp': datetime.now().isoformat(),
            'file_path': file_path
        })
        
        # Daten speichern mit Performance-Optimierungen
        file_size = self.performance_handler.save_with_blosc(
            self.current_data,
            file_path,
            metadata=save_metadata
        )
        
        # Pipeline-Eintrag hinzufügen
        self.workflow_state['data_pipeline'].append({
            'app': app_name,
            'file_path': file_path,
            'file_size_mb': file_size,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"💾 Daten gespeichert: {file_path} ({file_size:.1f} MB)")
        return file_path
    
    def load_data(self, file_path):
        """
        Daten laden
        
        Args:
            file_path: Pfad zur Datei
        """
        data = self.performance_handler.load_with_performance(file_path)
        
        if data is not None:
            # Metadaten laden falls vorhanden
            metadata_path = file_path.replace('.h5', '_metadata.json')
            loaded_metadata = {}
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        loaded_metadata = json.load(f)
                except Exception as e:
                    print(f"⚠️ Metadaten-Lade-Fehler: {e}")
            
            # Daten setzen
            self.set_current_data(
                data, 
                source_app=loaded_metadata.get('source_app', 'loaded'),
                metadata=loaded_metadata
            )
        
        return data
    
    def get_app_config(self, app_name):
        """App-Konfiguration abrufen"""
        return self.app_configs.get(app_name, {})
    
    def set_app_config(self, app_name, config):
        """App-Konfiguration setzen"""
        self.app_configs[app_name] = config
        
        # Konfiguration speichern
        config_file = os.path.join(self.paths['configs'], f"{app_name}_config.json")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Config-Speicher-Fehler: {e}")
    
    def load_app_config(self, app_name):
        """App-Konfiguration laden"""
        config_file = os.path.join(self.paths['configs'], f"{app_name}_config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.app_configs[app_name] = config
                    return config
            except Exception as e:
                print(f"⚠️ Config-Lade-Fehler: {e}")
        
        return {}
    
    def get_workflow_state(self):
        """Workflow-Status abrufen"""
        return self.workflow_state.copy()
    
    def get_available_files(self, directory=None):
        """Verfügbare Dateien auflisten"""
        if directory is None:
            directory = self.paths['output']
        
        return self.performance_handler.parallel_file_scan(directory)
    
    def get_data_info(self):
        """Detaillierte Daten-Information"""
        if self.current_data is None:
            return {"status": "Keine Daten geladen"}
        
        data = self.current_data
        info = {
            "Datentyp": type(data).__name__,
            "Form": str(data.shape) if hasattr(data, 'shape') else "Unbekannt",
            "Spalten": len(data.columns) if hasattr(data, 'columns') else "Unbekannt",
            "Zeilen": len(data) if hasattr(data, '__len__') else "Unbekannt",
            "Speicherverbrauch": f"{data.memory_usage(deep=True).sum() / 1024**2:.1f} MB" if hasattr(data, 'memory_usage') else "Unbekannt",
            "Index-Typ": type(data.index).__name__ if hasattr(data, 'index') else "Unbekannt"
        }
        
        # Zeitbereich
        if hasattr(data, 'index') and len(data) > 0:
            try:
                info["Zeitbereich"] = f"{data.index[0]} bis {data.index[-1]}"
                info["Zeitspanne"] = str(data.index[-1] - data.index[0])
            except:
                pass
        
        # Spalten-Info
        if hasattr(data, 'columns'):
            info["Verfügbare Spalten"] = ", ".join(data.columns)
        
        # Metadaten hinzufügen
        info.update(self.metadata)
        
        return info
    
    def create_vbt_data_object(self, **kwargs):
        """VBT Data Object aus aktuellen Daten erstellen"""
        if self.current_data is None:
            raise ValueError("Keine Daten verfügbar")
        
        vbt_data = self.performance_handler.create_vbt_data_object(
            self.current_data, 
            **kwargs
        )
        
        # Als VBT Data Object setzen
        self.set_current_data(
            vbt_data,
            source_app=self.workflow_state.get('current_app', 'vbt_conversion'),
            metadata={'converted_to_vbt': True}
        )
        
        return vbt_data
    
    def get_performance_stats(self):
        """Performance-Statistiken abrufen"""
        return self.performance_handler.get_performance_stats()
    
    def cleanup(self):
        """Speicher aufräumen"""
        self.performance_handler.cleanup_memory()
        
        # Alte Historie begrenzen
        if len(self.data_history) > 10:
            self.data_history = self.data_history[-10:]
    
    def export_workflow_summary(self):
        """Workflow-Zusammenfassung exportieren"""
        summary = {
            'workflow_state': self.workflow_state,
            'current_metadata': self.metadata,
            'app_configs': self.app_configs,
            'performance_stats': self.get_performance_stats(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        summary_file = os.path.join(self.paths['output'], 'workflow_summary.json')
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)
            
            print(f"📋 Workflow-Zusammenfassung exportiert: {summary_file}")
            return summary_file
        except Exception as e:
            print(f"❌ Export-Fehler: {e}")
            return None

# Globale Instanz für alle Apps
data_manager = DataManager()
