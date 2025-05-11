import csv
import os
import django
from datetime import datetime
from predictor.models import Wrestler

# Setup Django manually if running standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WWE_CHAMPION_PREDICTOR.settings')
django.setup()

# Dynamically construct path to CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_file_path = os.path.join(BASE_DIR, 'predictor', 'data', 'cleaned_wrestling_data.csv')

def safe_int(value):
    try:
        return int(float(value)) if value not in ('', None) else None
    except (ValueError, TypeError):
        return None

def safe_float(value):
    try:
        return float(value) if value not in ('', None) else 0.0
    except (ValueError, TypeError):
        return 0.0

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

def load_wrestlers():
    print(f"Loading from: {csv_file_path}")

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            wrestler = Wrestler(
                name=row.get('name', '').strip(),
                belt=row.get('belt', '').strip(),
                total_reigns=safe_int(row.get('total_reigns')),
                total_days_as_champion=safe_int(row.get('total_days_as_champion')),
                average_reign_duration=safe_float(row.get('average_reign_duration')),
                longest_single_reign=safe_int(row.get('longest_single_reign')),
                shortest_single_reign=safe_int(row.get('shortest_single_reign')),
                most_recent_reign=parse_date(row.get('most_recent_reign')),
                first_reign=parse_date(row.get('first_reign')),
                most_recent_reign_end=parse_date(row.get('most_recent_reign_end')),
                days_since_last_reign=safe_int(row.get('days_since_last_reign')),
                title_diversity=safe_int(row.get('title_diversity')),
                career_span_days=safe_int(row.get('career_span_days')),
                avg_reigns_per_title=safe_float(row.get('avg_reigns_per_title')),
            )
            wrestler.save()
            count += 1

    print(f" Loaded {count} wrestlers successfully!")

if __name__ == '__main__':
    load_wrestlers()
