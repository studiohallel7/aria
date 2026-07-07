"""
Módulo VTuber do Agente Unificado.

Fornece renderização de avatar PNG com sincronização labial,
expressões emocionais e descoberta automática de assets.
"""

from .png_engine import VtuberPngEngine, Emotion, AssetPack

__all__ = ['VtuberPngEngine', 'Emotion', 'AssetPack']
