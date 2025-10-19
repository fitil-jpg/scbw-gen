#!/usr/bin/env python3
"""
Скрипт для запуску Blender пайплайну
Використовується для автоматизації рендерингу сцен
"""

import sys
import os
import argparse
from pathlib import Path
import json
import yaml

# Додавання шляху до модулів
sys.path.append(str(Path(__file__).parent / "blender"))

def main():
    parser = argparse.ArgumentParser(description="Blender Pipeline Runner")
    parser.add_argument("--shot-id", required=True, help="ID шоту для рендерингу")
    parser.add_argument("--config", help="Шлях до конфігураційного файлу")
    parser.add_argument("--template", help="Назва шаблону для створення шоту")
    parser.add_argument("--output-dir", default="renders/blender", help="Директорія виводу")
    parser.add_argument("--export-format", choices=["blend", "fbx", "obj", "usd"], help="Формат експорту")
    parser.add_argument("--batch", help="Шлях до файлу з конфігурацією пакетного рендерингу")
    parser.add_argument("--validate-only", action="store_true", help="Тільки валідація без рендерингу")
    
    args = parser.parse_args()
    
    try:
        # Імпорт модулів (тільки після парсингу аргументів)
        from integrated_blender_pipeline import IntegratedBlenderPipeline
        
        # Ініціалізація пайплайну
        pipeline = IntegratedBlenderPipeline("assets", args.output_dir)
        
        if args.batch:
            # Пакетний рендеринг
            with open(args.batch, 'r', encoding='utf-8') as f:
                if args.batch.endswith('.json'):
                    shots_config = json.load(f)
                else:
                    shots_config = yaml.safe_load(f)
            
            results = pipeline.batch_process_shots(shots_config)
            
            # Вивід результатів
            successful = sum(1 for r in results.values() if r["status"] == "success")
            failed = sum(1 for r in results.values() if r["status"] == "error")
            
            print(f"Пакетний рендеринг завершено:")
            print(f"  Успішних: {successful}")
            print(f"  Помилок: {failed}")
            
            for shot_id, result in results.items():
                if result["status"] == "success":
                    print(f"  {shot_id}: {len(result['rendered_files'])} файлів")
                else:
                    print(f"  {shot_id}: ПОМИЛКА - {result['error']}")
        
        else:
            # Одиночний рендеринг
            shot_config = None
            
            if args.config:
                # Завантаження з файлу
                with open(args.config, 'r', encoding='utf-8') as f:
                    if args.config.endswith('.json'):
                        shot_config = json.load(f)
                    else:
                        shot_config = yaml.safe_load(f)
            
            elif args.template:
                # Створення з шаблону
                shot_config = pipeline.create_shot_from_template(
                    args.template, 
                    args.shot_id
                )
            
            else:
                # Використання стандартної конфігурації
                shot_config = {
                    "shot_id": args.shot_id,
                    "terrain": {
                        "type": "plane",
                        "size": [20, 20]
                    },
                    "buildings": [
                        {
                            "name": "Test Building",
                            "type": "cube",
                            "position": [0, 0, 0],
                            "scale": [2, 2, 1.5]
                        }
                    ],
                    "camera": {
                        "position": [0, -10, 5],
                        "rotation": [60, 0, 0]
                    },
                    "render_settings": {
                        "engine": "CYCLES",
                        "samples": 64,
                        "resolution": [1920, 1080],
                        "output_format": "PNG"
                    }
                }
            
            # Валідація
            errors = pipeline.validate_shot_config(shot_config)
            if errors:
                print(f"Помилки валідації: {errors}")
                return 1
            
            if args.validate_only:
                print("Валідація пройшла успішно")
                return 0
            
            # Рендеринг
            result = pipeline.process_shot(args.shot_id, shot_config)
            
            if result["status"] == "success":
                print(f"Рендеринг завершено успішно:")
                print(f"  Шот: {result['shot_id']}")
                print(f"  Файлів: {len(result['rendered_files'])}")
                print(f"  Маніфест: {result['manifest']}")
                
                # Експорт якщо потрібно
                if args.export_format:
                    export_path = pipeline.export_scene(args.shot_id, args.export_format)
                    print(f"  Експорт: {export_path}")
                
                return 0
            else:
                print(f"Помилка рендерингу: {result['error']}")
                return 1
    
    except Exception as e:
        print(f"Критична помилка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
