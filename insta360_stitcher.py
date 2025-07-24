#!/usr/bin/env python3
"""
Insta360 Video Stitcher Script
Automatizza l'estrazione di frame da video .insv usando la MediaSDK

Usage:
    python insta360_stitcher.py input.insv output_dir [algorithm]

Arguments:
    input.insv     : Path del video Insta360 (.insv)
    output_dir     : Directory di output per i frame
    algorithm      : template, dynamicstitch, optflow, aistitchv1, aistitchv2 (default: template)

Example:
    python insta360_stitcher.py /path/to/video.insv ./frames template
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path

# Configurazione paths SDK (modifica questi percorsi se necessario)
SDK_BASE_PATH = "/mnt/data/pdx/insta360sdk/libMediaSDK-dev-3.0.5.1-20250618_195946-amd64"
EXAMPLE_DIR = f"{SDK_BASE_PATH}/example"
CAMERA_SDK_LIB = f"{SDK_BASE_PATH}/../CameraSDK-20250418_145834-2.0.2-Linux/lib"
MEDIA_SDK_LIB = "/usr/lib"
MAIN_EXECUTABLE = f"{EXAMPLE_DIR}/main"
MODELFILE_DIR = f"{SDK_BASE_PATH}/modelfile"

# Mapping algoritmi
ALGORITHMS = {
    'template': 'template',
    'dynamicstitch': 'dynamicstitch', 
    'optflow': 'optflow',
    'aistitchv1': 'aistitch',
    'aistitchv2': 'aistitch'
}

# Modelli AI
AI_MODELS = {
    'aistitchv1': f'{MODELFILE_DIR}/ai_stitcher_v1.ins',
    'aistitchv2': f'{MODELFILE_DIR}/ai_stitcher_v2.ins'
}

def get_video_resolution(video_path):
    """
    Estrae la risoluzione del video usando ffprobe
    Ritorna (width, height) per il frame equirettangolare
    """
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Trova il primo stream video
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                width = int(stream['width'])
                height = int(stream['height'])
                
                # Per video Insta360, la risoluzione equirettangolare è tipicamente 2:1
                # Se il video originale è quadrato (es. 5632x5632), 
                # la risoluzione equirettangolare sarà il doppio della larghezza
                if width == height:  # Video quadrato (dual fisheye)
                    eq_width = width * 2
                    eq_height = width
                    print(f"Video risoluzione originale: {width}x{height}")
                    print(f"Risoluzione equirettangolare: {eq_width}x{eq_height}")
                    return eq_width, eq_height
                else:
                    # Se già in formato 2:1, usa quella risoluzione
                    print(f"Video risoluzione: {width}x{height}")
                    return width, height
                    
        raise ValueError("Nessun stream video trovato")
        
    except subprocess.CalledProcessError as e:
        print(f"Errore nell'esecuzione di ffprobe: {e}")
        print("Usando risoluzione di default 11520x5760")
        return 11520, 5760
    except Exception as e:
        print(f"Errore nell'analisi del video: {e}")
        print("Usando risoluzione di default 11520x5760")
        return 11520, 5760

def validate_paths():
    """Verifica che tutti i percorsi necessari esistano"""
    if not os.path.exists(MAIN_EXECUTABLE):
        print(f"ERRORE: Eseguibile main non trovato in {MAIN_EXECUTABLE}")
        print("Assicurati di aver compilato il progetto e verifica i percorsi SDK.")
        return False
        
    if not os.path.exists(CAMERA_SDK_LIB):
        print(f"ERRORE: Librerie CameraSDK non trovate in {CAMERA_SDK_LIB}")
        return False
        
    return True

def run_stitcher(video_path, output_dir, algorithm, width, height):
    """
    Esegue il stitcher con i parametri specificati
    """
    # Crea comando base (usa path assoluto per output_dir)
    cmd = [
        MAIN_EXECUTABLE,
        '-inputs', str(video_path),
        '-image_sequence_dir', str(output_dir.absolute()),
        '-image_type', 'jpg',
        '-output_size', f'{width}x{height}',
        '-stitch_type', ALGORITHMS[algorithm]
    ]
    
    # Aggiungi modello AI se necessario
    if algorithm in AI_MODELS:
        cmd.extend(['-ai_stitching_model', AI_MODELS[algorithm]])
        print(f"Usando modello AI: {AI_MODELS[algorithm]}")
    
    # Configura environment
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CAMERA_SDK_LIB}:{MEDIA_SDK_LIB}"
    
    print(f"Comando: {' '.join(cmd)}")
    print(f"LD_LIBRARY_PATH: {env['LD_LIBRARY_PATH']}")
    print(f"Avvio stitching...")
    
    try:
        # Esegui il comando
        result = subprocess.run(
            cmd, 
            env=env, 
            cwd=EXAMPLE_DIR,
            check=True,
            text=True,
            capture_output=False  # Mostra output in tempo reale
        )
        
        print(f"✅ Stitching completato con successo!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante lo stitching: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore imprevisto: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Insta360 Video Stitcher - Estrae frame equirettangolari da video .insv',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Algoritmi disponibili:
  template      - Veloce, geometria stabile (raccomandato per 3D/SFM)
  dynamicstitch - Buon compromesso qualità/velocità
  optflow       - Qualità giunzioni eccellente (può distorcere geometria)
  aistitchv1    - AI stitching per camere pre-X4
  aistitchv2    - AI stitching per X5 (può avere problemi)

Esempi:
  python insta360_stitcher.py video.insv ./frames
  python insta360_stitcher.py video.insv ./frames dynamicstitch
  python insta360_stitcher.py /path/to/video.insv /path/to/output optflow
        """
    )
    
    parser.add_argument('input_video', help='Path del video Insta360 (.insv)')
    parser.add_argument('output_dir', help='Directory di output per i frame')
    parser.add_argument('algorithm', nargs='?', default='template',
                       choices=['template', 'dynamicstitch', 'optflow', 'aistitchv1', 'aistitchv2'],
                       help='Algoritmo di stitching (default: template)')
    
    args = parser.parse_args()
    
    # Verifica input
    input_path = Path(args.input_video)
    if not input_path.exists():
        print(f"❌ ERRORE: File video non trovato: {input_path}")
        sys.exit(1)
        
    if not input_path.suffix.lower() in ['.insv', '.mp4']:
        print(f"⚠️  WARNING: File non è .insv, procedo comunque...")
    
    # Verifica SDK
    if not validate_paths():
        sys.exit(1)
    
    # Crea directory output
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Verifica permessi di scrittura
    if not os.access(output_path, os.W_OK):
        print(f"❌ ERRORE: Nessun permesso di scrittura in {output_path}")
        sys.exit(1)
        
    print(f"📁 Directory output: {output_path.absolute()}")
    
    # Analizza video per ottenere risoluzione
    print(f"🔍 Analisi video: {input_path}")
    width, height = get_video_resolution(input_path)
    
    # Esegui stitching
    print(f"🎯 Algoritmo: {args.algorithm}")
    print(f"📐 Risoluzione output: {width}x{height}")
    
    success = run_stitcher(input_path, output_path, args.algorithm, width, height)
    
    if success:
        # Conta frame generati
        frame_count = len(list(output_path.glob('*.jpg')))
        print(f"🎉 Processo completato! {frame_count} frame generati in {output_path}")
    else:
        print(f"💥 Processo fallito. Controlla i log sopra per dettagli.")
        sys.exit(1)

if __name__ == '__main__':
    main()