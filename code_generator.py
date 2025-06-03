#!/usr/bin/env python3
"""
💻 CODE GENERATOR - VectorBT Pro GUI System
Generiert fehlerfreien Python-Code für Jupyter Notebooks
- Template-basierte Code-Generierung
- VectorBT Pro optimiert
- Vollständig ausführbar
- Professionelle Code-Qualität
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

class CodeGenerator:
    """
    💻 JUPYTER CODE GENERATOR
    Generiert optimierten VectorBT Pro Code für alle Apps
    """
    
    def __init__(self):
        self.templates = self.load_templates()
        self.imports = {
            'basic': [
                "import pandas as pd",
                "import numpy as np",
                "import warnings",
                "warnings.filterwarnings('ignore')",
                "from datetime import datetime, timedelta"
            ],
            'vbt': [
                "import vectorbtpro as vbt",
                "# VBT Performance Settings",
                "vbt.settings.caching['enabled'] = True",
                "vbt.settings.array_wrapper['freq'] = None"
            ],
            'plotting': [
                "import matplotlib.pyplot as plt",
                "import plotly.graph_objects as go",
                "import plotly.express as px",
                "from plotly.subplots import make_subplots"
            ],
            'performance': [
                "import gc",
                "import time",
                "from concurrent.futures import ThreadPoolExecutor"
            ]
        }
    
    def load_templates(self):
        """Code-Templates laden"""
        return {
            'data_loading': '''
# 📊 DATEN LADEN - APP 1
# Generiert von VectorBT Pro GUI System am {timestamp}

{imports}

def load_historical_data(file_path, start_date=None, end_date=None):
    """
    Historische Daten mit VBT Pro Performance-Optimierungen laden
    """
    print(f"📊 Lade Daten: {{file_path}}")
    
    # VBT Data Object laden (20x schneller für Backtesting)
    {load_code}
    
    # Zeitraum filtern falls angegeben
    {filter_code}
    
    # Daten-Info anzeigen
    print(f"✅ Daten geladen: {{data.shape}} | Zeitraum: {{data.index[0]}} bis {{data.index[-1]}}")
    
    return data

# Daten laden
data = load_historical_data(
    file_path="{file_path}",
    start_date="{start_date}",
    end_date="{end_date}"
)

{save_code}
''',
            
            'resampling': '''
# 🔄 DATEN RESAMPLING - APP 2
# Generiert von VectorBT Pro GUI System am {timestamp}

{imports}

def resample_data(data, timeframes, method='last'):
    """
    Multi-Timeframe Resampling mit VBT Pro Optimierungen
    """
    print(f"🔄 Resampling zu Timeframes: {{timeframes}}")
    
    resampled_data = {{}}
    
    {resampling_code}
    
    return resampled_data

# Daten laden
{load_previous_data}

# Resampling durchführen
resampled_data = resample_data(
    data=data,
    timeframes={timeframes},
    method="{method}"
)

{save_code}
''',
            
            'indicators': '''
# 📈 INDIKATOREN - APP 3
# Generiert von VectorBT Pro GUI System am {timestamp}

{imports}

def calculate_indicators(data, indicators_config):
    """
    Indikatoren mit VBT Pro berechnen (Numba-optimiert)
    """
    print(f"📈 Berechne {{len(indicators_config)}} Indikatoren...")
    
    results = {{}}
    
    {indicators_code}
    
    return results

# Daten laden
{load_previous_data}

# Indikatoren-Konfiguration
indicators_config = {indicators_config}

# Indikatoren berechnen
indicators = calculate_indicators(data, indicators_config)

{save_code}
''',
            
            'strategy': '''
# 🎯 STRATEGIE - APP 6
# Generiert von VectorBT Pro GUI System am {timestamp}

{imports}

def create_strategy(data, indicators, strategy_config):
    """
    Trading-Strategie mit VBT Pro erstellen
    """
    print("🎯 Erstelle Trading-Strategie...")
    
    {strategy_code}
    
    return entries, exits

# Daten und Indikatoren laden
{load_previous_data}

# Strategie-Konfiguration
strategy_config = {strategy_config}

# Strategie erstellen
entries, exits = create_strategy(data, indicators, strategy_config)

{save_code}
''',
            
            'backtesting': '''
# 🚀 BACKTESTING - APP 8
# Generiert von VectorBT Pro GUI System am {timestamp}

{imports}

def run_backtest(data, entries, exits, backtest_config):
    """
    VBT Pro Backtesting mit allen Performance-Features
    """
    print("🚀 Starte Backtesting...")
    
    {backtest_code}
    
    return portfolio

# Daten, Entries und Exits laden
{load_previous_data}

# Backtest-Konfiguration
backtest_config = {backtest_config}

# Backtesting durchführen
portfolio = run_backtest(data, entries, exits, backtest_config)

# Ergebnisse anzeigen
{results_code}
'''
        }
    
    def generate_imports(self, required_modules):
        """Import-Statements generieren"""
        imports = []
        
        for module in required_modules:
            if module in self.imports:
                imports.extend(self.imports[module])
        
        return "\n".join(imports)
    
    def generate_data_loading_code(self, config):
        """Code für Daten-Laden generieren (App 1)"""
        
        # Load Code basierend auf VBT Verfügbarkeit
        if config.get('vbt_available', True):
            load_code = '''
    # VBT Data Object für maximale Performance
    if file_path.endswith('.h5'):
        vbt_data = vbt.Data.load(file_path)
        data = vbt_data.data
    else:
        data = pd.read_csv(file_path, index_col=0, parse_dates=True)
        # Memory-Optimierung
        for col in ['open', 'high', 'low', 'close']:
            if col in data.columns:
                data[col] = data[col].astype(np.float32)
        if 'volume' in data.columns:
            data['volume'] = data['volume'].astype(np.int32)
'''
        else:
            load_code = '''
    # Standard Pandas Loading
    if file_path.endswith('.h5'):
        data = pd.read_hdf(file_path, key='data')
    else:
        data = pd.read_csv(file_path, index_col=0, parse_dates=True)
'''
        
        # Filter Code
        filter_code = '''
    if start_date or end_date:
        if start_date:
            start_date = pd.to_datetime(start_date)
            data = data[data.index >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            data = data[data.index <= end_date]
'''
        
        # Save Code
        save_code = self.generate_save_code(config)
        
        return self.templates['data_loading'].format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            imports=self.generate_imports(['basic', 'vbt']),
            load_code=load_code,
            filter_code=filter_code,
            file_path=config.get('file_path', 'data.h5'),
            start_date=config.get('start_date', ''),
            end_date=config.get('end_date', ''),
            save_code=save_code
        )
    
    def generate_resampling_code(self, config):
        """Code für Resampling generieren (App 2)"""
        
        timeframes = config.get('timeframes', ['1H', '4H', '1D'])
        
        resampling_code = '''
    for tf in timeframes:
        print(f"  Resampling zu {tf}...")
        
        # OHLCV Resampling
        resampled = data.resample(tf).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        resampled_data[tf] = resampled
        print(f"    ✅ {tf}: {resampled.shape}")
'''
        
        return self.templates['resampling'].format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            imports=self.generate_imports(['basic', 'vbt']),
            resampling_code=resampling_code,
            load_previous_data=self.generate_load_previous_data(config),
            timeframes=timeframes,
            method=config.get('method', 'last'),
            save_code=self.generate_save_code(config)
        )
    
    def generate_indicators_code(self, config):
        """Code für Indikatoren generieren (App 3)"""
        
        indicators_config = config.get('indicators', {})
        
        indicators_code = '''
    for indicator_name, params in indicators_config.items():
        print(f"  Berechne {indicator_name}...")
        
        try:
            if indicator_name == 'RSI':
                results[indicator_name] = vbt.RSI.run(
                    data['close'], 
                    window=params.get('window', 14)
                ).rsi
                
            elif indicator_name == 'MACD':
                macd = vbt.MACD.run(
                    data['close'],
                    fast_window=params.get('fast_window', 12),
                    slow_window=params.get('slow_window', 26),
                    signal_window=params.get('signal_window', 9)
                )
                results[f'{indicator_name}_line'] = macd.macd
                results[f'{indicator_name}_signal'] = macd.signal
                results[f'{indicator_name}_histogram'] = macd.histogram
                
            elif indicator_name == 'BBANDS':
                bb = vbt.BBANDS.run(
                    data['close'],
                    window=params.get('window', 20),
                    alpha=params.get('alpha', 2)
                )
                results[f'{indicator_name}_upper'] = bb.upper
                results[f'{indicator_name}_middle'] = bb.middle
                results[f'{indicator_name}_lower'] = bb.lower
                
            # Weitere Indikatoren hier hinzufügen...
            
            print(f"    ✅ {indicator_name} berechnet")
            
        except Exception as e:
            print(f"    ❌ Fehler bei {indicator_name}: {e}")
'''
        
        return self.templates['indicators'].format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            imports=self.generate_imports(['basic', 'vbt']),
            indicators_code=indicators_code,
            load_previous_data=self.generate_load_previous_data(config),
            indicators_config=json.dumps(indicators_config, indent=4),
            save_code=self.generate_save_code(config)
        )
    
    def generate_strategy_code(self, config):
        """Code für Strategie generieren (App 6)"""
        
        strategy_config = config.get('strategy', {})
        
        strategy_code = '''
    # Entry Bedingungen
    entry_conditions = []
    
    # Exit Bedingungen  
    exit_conditions = []
    
    # Beispiel: RSI Strategie
    if 'rsi_entry' in strategy_config:
        rsi_threshold = strategy_config['rsi_entry']['threshold']
        entry_conditions.append(indicators['RSI'] < rsi_threshold)
    
    if 'rsi_exit' in strategy_config:
        rsi_threshold = strategy_config['rsi_exit']['threshold']
        exit_conditions.append(indicators['RSI'] > rsi_threshold)
    
    # Kombiniere Bedingungen
    if entry_conditions:
        entries = entry_conditions[0]
        for condition in entry_conditions[1:]:
            entries = entries & condition
    else:
        entries = pd.Series(False, index=data.index)
    
    if exit_conditions:
        exits = exit_conditions[0]
        for condition in exit_conditions[1:]:
            exits = exits & condition
    else:
        exits = pd.Series(False, index=data.index)
    
    print(f"✅ Strategie erstellt: {entries.sum()} Entries, {exits.sum()} Exits")
'''
        
        return self.templates['strategy'].format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            imports=self.generate_imports(['basic', 'vbt']),
            strategy_code=strategy_code,
            load_previous_data=self.generate_load_previous_data(config),
            strategy_config=json.dumps(strategy_config, indent=4),
            save_code=self.generate_save_code(config)
        )
    
    def generate_backtest_code(self, config):
        """Code für Backtesting generieren (App 8)"""
        
        backtest_config = config.get('backtest', {})
        
        backtest_code = '''
    # VBT Portfolio mit Performance-Optimierungen
    portfolio = vbt.Portfolio.from_signals(
        data['close'],
        entries=entries,
        exits=exits,
        init_cash=backtest_config.get('init_cash', 10000),
        fees=backtest_config.get('fees', 0.001),
        slippage=backtest_config.get('slippage', 0.001),
        freq='1D'
    )
    
    print("✅ Backtesting abgeschlossen")
'''
        
        results_code = '''
# Performance-Metriken
print("\\n📊 BACKTEST ERGEBNISSE:")
print(f"Total Return: {portfolio.total_return():.2%}")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio():.2f}")
print(f"Max Drawdown: {portfolio.max_drawdown():.2%}")
print(f"Win Rate: {portfolio.win_rate():.2%}")

# Plotting
portfolio.plot().show()
'''
        
        return self.templates['backtesting'].format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            imports=self.generate_imports(['basic', 'vbt', 'plotting']),
            backtest_code=backtest_code,
            load_previous_data=self.generate_load_previous_data(config),
            backtest_config=json.dumps(backtest_config, indent=4),
            results_code=results_code
        )
    
    def generate_load_previous_data(self, config):
        """Code zum Laden vorheriger Daten"""
        file_path = config.get('input_file', 'previous_data.h5')
        
        return f'''
# Vorherige Daten laden
data = vbt.Data.load("{file_path}").data if "{file_path}".endswith('.h5') else pd.read_csv("{file_path}", index_col=0, parse_dates=True)
print(f"📊 Daten geladen: {{data.shape}}")
'''
    
    def generate_save_code(self, config):
        """Code zum Speichern generieren"""
        output_file = config.get('output_file', 'output_data.h5')
        
        if config.get('vbt_features', {}).get('blosc_compression', True):
            return f'''
# Daten mit VBT Pro Performance-Features speichern
if hasattr(data, 'vbt'):
    # VBT Data Object
    data.vbt.save(
        "{output_file}",
        compression="blosc",
        compression_opts=9,
        shuffle=True,
        fletcher32=True
    )
else:
    # Standard DataFrame zu VBT Data Object konvertieren
    vbt_data = vbt.Data(data, freq='infer')
    vbt_data.save(
        "{output_file}",
        compression="blosc",
        compression_opts=9,
        shuffle=True,
        fletcher32=True
    )

print(f"💾 Daten gespeichert: {output_file}")
'''
        else:
            return f'''
# Standard Speicherung
data.to_hdf("{output_file}", key='data', mode='w', complevel=9)
print(f"💾 Daten gespeichert: {output_file}")
'''
    
    def generate_code(self, app_name, config):
        """Hauptmethode zur Code-Generierung"""
        
        generators = {
            'app1_data_loader': self.generate_data_loading_code,
            'app2_resampling': self.generate_resampling_code,
            'app3_indicators': self.generate_indicators_code,
            'app6_strategy_builder': self.generate_strategy_code,
            'app8_backtesting': self.generate_backtest_code
        }
        
        if app_name in generators:
            return generators[app_name](config)
        else:
            return f"# Code-Generator für {app_name} noch nicht implementiert\n# Konfiguration: {json.dumps(config, indent=2)}"

# Globale Instanz
code_generator = CodeGenerator()
