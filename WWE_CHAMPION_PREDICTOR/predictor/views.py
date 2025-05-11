import logging
import os
import pandas as pd
import datetime
from datetime import datetime as dt, date as dt_date
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.shortcuts import render, redirect
from .models import Prediction
from .forms import PredictionForm

logger = logging.getLogger(__name__)

# Utility to safely get a date object from mixed datetime/date/NaT
def ensure_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, dt):
        return val.date()
    if isinstance(val, dt_date):
        return val
    try:
        return pd.to_datetime(val, errors='coerce').date()
    except Exception:
        return None

# Admin dashboard with analytics
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser or not request.session.get('admin_logged_in'):
        messages.error(request, "You must log in as admin first.")
        return redirect('admin_login')

    wrestler_data = Prediction.objects.values('wrestler_name') \
        .annotate(total_predictions=Count('wrestler_name')) \
        .order_by('-total_predictions')

    if not wrestler_data:
        wrestler_data = [{'wrestler_name': 'No Data', 'total_predictions': 0}]

    total_predictions = Prediction.objects.count()
    successful_predictions = Prediction.objects.filter(success=True).count()
    success_rate = (successful_predictions / total_predictions) * 100 if total_predictions > 0 else 0

    context = {
        'wrestler_data': wrestler_data,
        'total_predictions': total_predictions,
        'successful_predictions': successful_predictions,
        'success_rate': round(success_rate, 2),
    }

    return render(request, 'predictor/admin_dashboard.html', context)

# Home view
@login_required
def home(request):
    context = {
        'message': 'Welcome to the WWE Champion Predictor!',
    }
    return render(request, 'predictor/home.html', context)

# User panel view (fixes AttributeError for 'user_dashboard')
@login_required
def user_panel(request):
    return render(request, 'predictor/user_panel.html', {
        'user': request.user,
        'message': 'Welcome to your user panel!'
    })

# Prediction result view
@login_required
def prediction_result(request):
    if request.method == 'POST':
        # Handle the form submission for a prediction
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction = form.save(commit=False)
            prediction.user = request.user
            prediction.save()
            messages.success(request, "Prediction saved successfully!")
            return redirect('predictor:prediction_result')
        else:
            messages.error(request, "There was an error with your prediction.")
    else:
        # If no form submission, just show the form
        form = PredictionForm()

    return render(request, 'predictor/prediction_result.html', {
        'form': form,
        'message': 'Enter your prediction and submit it!'
    })

# Wrestler result logic
def get_all_wrestler_results(wrestler_name, championship, gender, start_date, end_date):
    CSV_PATH = os.path.join(settings.BASE_DIR, 'predictor', 'data', 'cleaned_wrestling_data.csv')

    championship = championship.strip().lower() if championship else None
    gender = gender.strip().lower() if gender else None
    wrestler_name = wrestler_name.strip().lower() if wrestler_name else None

    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        return {'error': f"Error reading the CSV file: {str(e)}"}

    df.columns = df.columns.str.strip()
    df['name'] = df['name'].str.strip().str.lower()
    df['belt'] = df['belt'].str.strip().str.lower()

    for date_col in ['first_reign', 'most_recent_reign', 'most_recent_reign_end']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    logger.debug(f"CSV Columns: {df.columns}")

    if wrestler_name:
        df = df[df['name'].str.contains(wrestler_name, case=False, na=False)]
        if df.empty:
            logger.error(f"No data found for wrestler '{wrestler_name}'")
            return {'error': f"No data found for wrestler '{wrestler_name}'"}

    if championship:
        df = df[df['belt'].str.contains(championship, case=False, na=False)]
        if df.empty:
            logger.error(f"No data found for belt '{championship}'")
            return {'error': f"No data found for belt '{championship}'"}

    if gender and 'gender' in df.columns:
        df = df[df['gender'] == gender]
        if df.empty:
            logger.error(f"No data found for gender '{gender}'")
            return {'error': f"No data found for gender '{gender}'"}

    date_column = None
    for possible_date_column in ['first_reign', 'most_recent_reign', 'most_recent_reign_end']:
        if possible_date_column in df.columns:
            date_column = possible_date_column
            break

    if not date_column:
        logger.error(f"No valid date column found in the dataset. Available columns: {', '.join(df.columns)}")
        return {'error': f"No valid date column found in the dataset. Available columns: {', '.join(df.columns)}"}

    if start_date and end_date:
        try:
            start_date = pd.to_datetime(start_date).date()
            end_date = pd.to_datetime(end_date).date()
            df[date_column] = df[date_column].dt.date
            df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
        except Exception as e:
            logger.error(f"Error filtering by date range: {str(e)}")
            return {'error': f"Error filtering by date range: {str(e)}"}

        if df.empty:
            logger.error("No data found within the specified date range.")
            return {'error': "No data in selected date range."}

    logger.debug(f"Filtered Data: {df.head()}")

    belts = df['belt'].unique()
    total_reigns = df['total_reigns'].sum()
    total_days = df['total_days_as_champion'].sum()
    avg_days = df['average_reign_duration'].mean()
    longest = df['longest_single_reign'].max()
    shortest = df['shortest_single_reign'].min()

    if not df[date_column].isna().all():
        first_win = ensure_date(df[date_column].min())
        last_win = ensure_date(df[date_column].max())
    else:
        first_win = None
        last_win = None

    logger.debug(f"First win: {first_win}, Last win: {last_win}")

    if first_win and last_win:
        delta = last_win - first_win
        years = delta.days // 365
        months = (delta.days % 365) // 30
        career_span = f"{years} years, {months} months"
    else:
        career_span = "N/A"

    return {
        'wrestler_name': wrestler_name.title() if wrestler_name else "All Wrestlers",
        'belts': ', '.join(belts),
        'total_reigns': total_reigns,
        'total_reign_length': total_days,
        'average_reign_duration': round(avg_days, 2),
        'longest_reign': longest,
        'shortest_reign': shortest,
        'first_title_win': str(first_win) if first_win else "N/A",
        'most_recent_title_win': str(last_win) if last_win else "N/A",
        'career_span': career_span
    }

# Admin login view
def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('predictor:admin_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                login(request, user)
                request.session['admin_logged_in'] = True
                return redirect('predictor:admin_dashboard')
            else:
                return render(request, 'predictor/admin_login.html', {
                    'form': form,
                    'error': 'Only admins can log in here.'
                })
    else:
        form = AuthenticationForm()

    return render(request, 'predictor/admin_login.html', {'form': form})

# Signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
        else:
            messages.error(request, "Error creating the account. Please try again.")
    else:
        form = UserCreationForm()

    return render(request, 'predictor/signup.html', {'form': form})

# Edit profile view
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('predictor:user_panel')
        else:
            messages.error(request, "Error updating profile.")
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'predictor/profile_edit.html', {'form': form})

def home(request):
    return render(request, 'predictor/home.html')

@login_required
def user_dashboard(request):
    context = {
        'user': request.user,
        'message': 'Welcome to your dashboard!'
    }
    return render(request, 'predictor/user_dashboard.html', context)