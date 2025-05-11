import os
from django.shortcuts import render
from django.conf import settings
import pandas as pd
from datetime import datetime
from predictor.views import admin_login_view



def index(request):
    return render(request, 'index.html')


# Utility function to get all wrestler results
def get_all_wrestler_results(wrestler_name, championship, gender, start_date, end_date):
    CSV_PATH = os.path.join(settings.BASE_DIR, 'predictor', 'data', 'cleaned_wrestling_data.csv')


    championship = championship.strip().lower() if championship else None
    gender = gender.strip().lower() if gender else None
    wrestler_name = wrestler_name.strip().lower() if wrestler_name else None

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()
    df['name'] = df['name'].str.strip().str.lower()
    df['belt'] = df['belt'].str.strip().str.lower()

    if 'gender' in df.columns:
        df['gender'] = df['gender'].str.strip().str.lower()

    if wrestler_name:
        df = df[df['name'].str.contains(wrestler_name, case=False, na=False)]
        if df.empty:
            return {'error': f"No data found for wrestler '{wrestler_name}'"}

    if championship:
        df = df[df['belt'].str.contains(championship, case=False, na=False)]
        if df.empty:
            return {'error': f"No data found for belt '{championship}'"}

    if gender and 'gender' in df.columns:
        df = df[df['gender'] == gender]
        if df.empty:
            return {'error': f"No data found for gender '{gender}'"}

    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        if df.empty:
            return {'error': "No data in selected date range."}

    belts = df['belt'].unique()
    total_reigns = df['total_reigns'].sum()
    total_days = df['total_days_as_champion'].sum()
    avg_days = df['average_reign_duration'].mean()
    longest = df['longest_single_reign'].max()
    shortest = df['shortest_single_reign'].min()
    first_win = df['date'].min().date()
    last_win = df['date'].max().date()
    delta = last_win - first_win
    years = delta.days // 365
    months = (delta.days % 365) // 30
    career_span = f"{years} years, {months} months"

    return {
        'wrestler_name': wrestler_name.title() if wrestler_name else "All Wrestlers",
        'belts': ', '.join(belts),
        'total_reigns': total_reigns,
        'total_reign_length': total_days,
        'average_reign_duration': round(avg_days, 2),
        'longest_reign': longest,
        'shortest_reign': shortest,
        'first_title_win': str(first_win),
        'most_recent_title_win': str(last_win),
        'career_span': career_span
    }


def user_dashboard(request):
    if request.method == 'POST':
        wrestler_name = request.POST.get('wrestler_name')
        championship = request.POST.get('championship')
        gender = request.POST.get('gender')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        results = get_all_wrestler_results(wrestler_name, championship, gender, start_date, end_date)

        if 'error' in results:
            return render(request, 'dashboard.html', {'error': results['error']})

        return render(request, 'dashboard.html', {'results': results})

    return render(request, 'dashboard.html')
