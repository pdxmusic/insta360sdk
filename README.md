# Insta360 MediaSDK & CameraSDK Setup (Linux)

Questa guida mostra i passaggi per installare e compilare la demo di stitching per convertire video `.insv` in frame equirettangolari.

## 1. Installazione delle dipendenze di sistema

```bash
sudo apt update
sudo apt install vulkan-tools mesa-utils libopencv-dev
```

## 2. Installazione della MediaSDK

```bash
sudo dpkg -i libMediaSDK-dev-3.0.5.1-20250618_195946-amd64/libMediaSDK-dev-3.0.5.1-20250618_195946-amd64.deb
```

## 3. Verifica della libreria MediaSDK

La libreria condivisa viene installata in `/usr/lib/libMediaSDK.so`.

## 4. Compilazione della demo di stitching

Spostati nella cartella dell'esempio:

```bash
cd libMediaSDK-dev-3.0.5.1-20250618_195946-amd64/example
```

Compila con:

```bash
g++ -std=c++11 \
    -I../include \
    -I../../CameraSDK-20250418_145834-2.0.2-Linux/include \
    -I/usr/include/opencv4 \
    -L../../CameraSDK-20250418_145834-2.0.2-Linux/lib \
    -L/usr/lib \
    main.cc \
    -lopencv_core -lopencv_imgcodecs -lopencv_imgproc -lopencv_highgui -lopencv_videoio \
    -lCameraSDK -lMediaSDK \
    -o main
```

## 5. Algoritmi di Stitching Supportati

## 5. Algoritmi di Stitching Supportati

### ✅ Algoritmi Funzionanti

#### Template Stitch (Raccomandato per geometria stabile)
```bash
cd libMediaSDK-dev-3.0.5.1-20250618_195946-amd64/example
mkdir -p output_frames

LD_LIBRARY_PATH=../../CameraSDK-20250418_145834-2.0.2-Linux/lib:/usr/lib ./main \
    -inputs /mnt/data/datasets/video/fisheye/VID_20250610_092308_00_099.insv \
    -image_sequence_dir output_frames \
    -image_type jpg \
    -output_size 11520x5760 \
    -stitch_type template
```
**Pro:** Geometria stabile, veloce, non distorce
**Contro:** Qualità giunzioni inferiore per scene vicine

#### Dynamic Stitch (Buon compromesso)
```bash
LD_LIBRARY_PATH=../../CameraSDK-20250418_145834-2.0.2-Linux/lib:/usr/lib ./main \
    -inputs /mnt/data/datasets/video/fisheye/VID_20250610_092308_00_099.insv \
    -image_sequence_dir output_frames \
    -image_type jpg \
    -output_size 11520x5760 \
    -stitch_type dynamicstitch
```
**Pro:** Buona qualità, gestisce movimento, geometria più stabile di optflow
**Contro:** Più lento di template

#### AI Stitch v1 (Funziona con camere pre-X4)
```bash
LD_LIBRARY_PATH=../../CameraSDK-20250418_145834-2.0.2-Linux/lib:/usr/lib ./main \
    -inputs /mnt/data/datasets/video/fisheye/VID_20250610_092308_00_099.insv \
    -image_sequence_dir output_frames \
    -image_type jpg \
    -output_size 11520x5760 \
    -stitch_type aistitch \
    -ai_stitching_model ../modelfile/ai_stitcher_v1.ins
```
**Pro:** Qualità AI, buone giunzioni
**Contro:** Richiede modello, più lento

#### ⚠️ Optical Flow (Qualità alta ma può distorcere)
```bash
LD_LIBRARY_PATH=../../CameraSDK-20250418_145834-2.0.2-Linux/lib:/usr/lib ./main \
    -inputs /mnt/data/datasets/video/fisheye/VID_20250610_092308_00_099.insv \
    -image_sequence_dir output_frames \
    -image_type jpg \
    -output_size 11520x5760 \
    -stitch_type optflow
```
**Pro:** Qualità giunzioni eccellente, gestisce movimento complesso
**Contro:** Può introdurre distorsioni geometriche, meno stabile per ricostruzioni 3D

### ❌ Algoritmi Problematici

#### AI Stitch v2 (Issue noto con X5)
```bash
# ⚠️ NON FUNZIONA - ConvolutionDepthwise non supportato da MNN CUDA backend
LD_LIBRARY_PATH=../../CameraSDK-20250418_145834-2.0.2-Linux/lib:/usr/lib ./main \
    -inputs /mnt/data/datasets/video/fisheye/VID_20250723_162432_00_136.insv \
    -image_sequence_dir output_frames \
    -image_type jpg \
    -output_size 11520x5760 \
    -stitch_type aistitch \
    -ai_stitching_model ../modelfile/ai_stitcher_v2.ins
```

**Errore tipico:** `CUDABackend The Creator Don't support type ConvolutionDepthwise`

## 6. Confronto Qualità vs Velocità vs Stabilità Geometrica

| Algoritmo | Qualità Giunzioni | Velocità | Stabilità Geometrica | Compatibilità | Uso Raccomandato |
|-----------|-------------------|----------|---------------------|---------------|------------------|
| **Template** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Tutte | **Ricostruzioni 3D/SFM** |
| **Dynamic Stitch** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Tutte | **Uso Generale** |
| **AI Stitch v1** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ✅ Pre-X4 | Qualità premium |
| **Optical Flow** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ✅ Tutte | VR/Video editing |
| **AI Stitch v2** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ❓ | ❌ X5 | Non disponibile |

### Scelta dell'Algoritmo per Caso d'Uso

**Per ricostruzioni 3D/SFM/fotogrammetria:** `template`
- Geometria più stabile e prevedibile
- Meno distorsioni introdotte dall'algoritmo

**Per uso generale/archivio:** `dynamicstitch`  
- Buon compromesso qualità/velocità
- Gestisce bene scene miste

**Per VR/video editing:** `optflow` (con cautela)
- Migliori giunzioni visive
- Attenzione alle distorsioni geometriche

**Per camere pre-X4 con AI:** `aistitch` + `ai_stitcher_v1.ins`
- Qualità premium quando disponibile

## 7. Nota Importante sulla Geometria

**La distorsione non riguarda la proiezione equirettangolare** (che rimane identica per tutti gli algoritmi), ma la **stabilità geometrica** degli oggetti nell'immagine:

- **Template/Dynamic:** Mantengono la geometria originale delle scene catturate
- **Optical Flow:** Può "correggere" la geometria basandosi sul movimento, introducendo distorsioni per migliorare la fluidità visiva
- **AI:** Dipende dal training del modello - può ottimizzare per qualità visiva a scapito della fedeltà geometrica

### Per Applicazioni Che Richiedono Precisione Geometrica
- **Fotogrammetria**
- **Ricostruzioni 3D** 
- **Structure from Motion (SFM)**
- **Misurazioni metriche**

**Raccomandazione:** Usa `template` o `dynamicstitch` per preservare la geometria originale.

## 8. Modelli AI Disponibili

La cartella `libMediaSDK-dev-3.0.5.1-20250618_195946-amd64/modelfile` contiene:

- `ai_stitcher_v1.ins` - ✅ Funziona con camere pre-X4
- `ai_stitcher_v2.ins` - ❌ Issue con X5 (ConvolutionDepthwise)
- `colorplus_model.ins` - Miglioramento colori
- `deflicker_86ccba0d.ins` - Riduzione flickering
- `defringe_hr_dynamic_7b56e80f.ins` - Riduzione aberrazioni cromatiche
- `jpg_denoise_9d006262.ins` - Denoising immagini

## 9. Risoluzione Problemi

### AI v2 non funziona con X5
- **Causa:** MNN framework non supporta ConvolutionDepthwise su CUDA
- **Soluzione:** Usa **Optical Flow** per qualità simile
- **Status:** Issue segnalato a Insta360

### Performance CUDA
- **CUDA_ERROR_SYSTEM_DRIVER_MISMATCH:** Normale, SDK passa automaticamente a software decoding
- **Non influisce** sulla qualità finale dello stitching

### Frame neri in output
- Verifica che la cartella output esista: `mkdir -p output_frames`
- Controlla i permessi di scrittura
- Riduci risoluzione di test: `-output_size 2880x1440`

## 11. Script di Automazione

Per semplificare l'uso, è disponibile uno script Python che automatizza tutto il processo:

### Installazione dello Script

Salva il seguente script come `insta360_stitcher.py`:

```python
#!/usr/bin/env python3
"""
Insta360 Video Stitcher Script
Automatizza l'estrazione di frame da video .insv usando la MediaSDK

Usage:
    python insta360_stitcher.py input.insv output_dir [algorithm]

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
    """Estrae la risoluzione del video usando ffprobe"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                width = int(stream['width'])
                height = int(stream['height'])
                
                if width == height:  # Video quadrato (dual fisheye)
                    eq_width = width * 2
                    eq_height = width
                    print(f"Video risoluzione originale: {width}x{height}")
                    print(f"Risoluzione equirettangolare: {eq_width}x{eq_height}")
                    return eq_width, eq_height
                else:
                    print(f"Video risoluzione: {width}x{height}")
                    return width, height
                    
        raise ValueError("Nessun stream video trovato")
        
    except Exception as e:
        print(f"Errore nell'analisi del video: {e}")
        print("Usando risoluzione di default 11520x5760")
        return 11520, 5760

def validate_paths():
    """Verifica che tutti i percorsi necessari esistano"""
    if not os.path.exists(MAIN_EXECUTABLE):
        print(f"ERRORE: Eseguibile main non trovato in {MAIN_EXECUTABLE}")
        return False
    if not os.path.exists(CAMERA_SDK_LIB):
        print(f"ERRORE: Librerie CameraSDK non trovate in {CAMERA_SDK_LIB}")
        return False
    return True

def run_stitcher(video_path, output_dir, algorithm, width, height):
    """Esegue il stitcher con i parametri specificati"""
    cmd = [
        MAIN_EXECUTABLE,
        '-inputs', str(video_path),
        '-image_sequence_dir', str(output_dir.absolute()),
        '-image_type', 'jpg',
        '-output_size', f'{width}x{height}',
        '-stitch_type', ALGORITHMS[algorithm]
    ]
    
    if algorithm in AI_MODELS:
        cmd.extend(['-ai_stitching_model', AI_MODELS[algorithm]])
        print(f"Usando modello AI: {AI_MODELS[algorithm]}")
    
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CAMERA_SDK_LIB}:{MEDIA_SDK_LIB}"
    
    print(f"Avvio stitching...")
    
    try:
        subprocess.run(cmd, env=env, cwd=EXAMPLE_DIR, check=True, capture_output=False)
        print(f"✅ Stitching completato con successo!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante lo stitching: {e}")
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
        """
    )
    
    parser.add_argument('input_video', help='Path del video Insta360 (.insv)')
    parser.add_argument('output_dir', help='Directory di output per i frame')
    parser.add_argument('algorithm', nargs='?', default='template',
                       choices=['template', 'dynamicstitch', 'optflow', 'aistitchv1', 'aistitchv2'],
                       help='Algoritmo di stitching (default: template)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_video)
    if not input_path.exists():
        print(f"❌ ERRORE: File video non trovato: {input_path}")
        sys.exit(1)
    
    if not validate_paths():
        sys.exit(1)
    
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not os.access(output_path, os.W_OK):
        print(f"❌ ERRORE: Nessun permesso di scrittura in {output_path}")
        sys.exit(1)
    
    print(f"📁 Directory output: {output_path.absolute()}")
    print(f"🔍 Analisi video: {input_path}")
    
    width, height = get_video_resolution(input_path)
    
    print(f"🎯 Algoritmo: {args.algorithm}")
    print(f"📐 Risoluzione output: {width}x{height}")
    
    success = run_stitcher(input_path, output_path, args.algorithm, width, height)
    
    if success:
        frame_count = len(list(output_path.glob('*.jpg')))
        print(f"🎉 Processo completato! {frame_count} frame generati in {output_path}")
    else:
        print(f"💥 Processo fallito. Controlla i log sopra per dettagli.")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### Uso dello Script

```bash
# Uso base con template (raccomandato per 3D/SFM)
python insta360_stitcher.py video.insv ./frames

# Specifica algoritmo
python insta360_stitcher.py video.insv ./frames template
python insta360_stitcher.py video.insv ./frames dynamicstitch
python insta360_stitcher.py video.insv ./frames optflow

# AI stitching (solo per camere compatibili)
python insta360_stitcher.py video.insv ./frames aistitchv1

# Help completo
python insta360_stitcher.py --help
```

### Caratteristiche dello Script

- ✅ **Auto-risoluzione:** Usa `ffprobe` per rilevare automaticamente la risoluzione corretta
- ✅ **Creazione directory:** Crea automaticamente la cartella di output
- ✅ **Validazione:** Controlla paths, permessi e file di input
- ✅ **Gestione AI:** Seleziona automaticamente il modello corretto per AI v1/v2
- ✅ **Report finale:** Mostra il numero di frame generati
- ✅ **Path assoluti:** Usa percorsi completi per evitare errori di salvataggio

**Per ricostruzioni 3D/fotogrammetria:** `template`
**Per uso generale/archivio:** `dynamicstitch` 
**Per VR/editing video (priorità qualità visiva):** `optflow`
**Per camere pre-X4 con qualità premium:** `aistitch` + `ai_stitcher_v1.ins`

> **Nota Importante:** Se noti che optical flow "distorce tutto", è normale - questo algoritmo privilegia la qualità visiva delle giunzioni rispetto alla fedeltà geometrica. Per applicazioni che richiedono precisione geometrica, usa `template` o `dynamicstitch`.
