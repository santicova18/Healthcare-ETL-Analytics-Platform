#!/usr/bin/env python
"""
Script para re-entrenar el modelo con control de versiones.
Uso: python retrain_model.py
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ml.train import train_risk_model

if __name__ == "__main__":
    print("\n" + "="*70)
    print("REENTRENAMIENTO DEL MODELO DE RIESGO CLÍNICO")
    print("="*70 + "\n")
    
    resultado = train_risk_model()
    
    print("\n" + "="*70)
    print("✅ REENTRENAMIENTO COMPLETADO")
    print("="*70 + "\n")
