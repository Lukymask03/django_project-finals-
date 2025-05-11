from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    wrestler_name = models.CharField(max_length=100)
    championship = models.CharField(max_length=100)
    prediction_date = models.DateField()
    success = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.wrestler_name} - {self.championship}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


class Belt(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Reign(models.Model):
    wrestler = models.ForeignKey('Wrestler', on_delete=models.CASCADE, related_name='reigns')
    championship = models.ForeignKey('Belt', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    length = models.IntegerField()  # Length of reign in days

    def __str__(self):
        return f"{self.wrestler.name} - {self.championship.name}"


class Wrestler(models.Model):
    name = models.CharField(max_length=100)
    belt = models.CharField(max_length=100, default="Unknown")
    total_reigns = models.IntegerField()
    total_days_as_champion = models.IntegerField()
    average_reign_duration = models.FloatField(default=0.0)
    longest_single_reign = models.IntegerField()
    shortest_single_reign = models.IntegerField()
    most_recent_reign = models.DateField(null=True, blank=True)
    first_reign = models.DateField(null=True, blank=True)
    most_recent_reign_end = models.DateField(null=True, blank=True)
    days_since_last_reign = models.IntegerField()
    title_diversity = models.IntegerField()
    avg_gap_between_reigns = models.FloatField()
    career_span_days = models.IntegerField()
    avg_reigns_per_title = models.FloatField()

    def __str__(self):
        return self.name

    # Helper methods
    def total_reigns_count(self):
        return self.total_reigns

    def total_reign_length(self):
        return self.total_days_as_champion

    def longest_reign(self):
        return self.longest_single_reign

    def shortest_reign(self):
        return self.shortest_single_reign

    def first_title_win(self):
        return self.first_reign if self.first_reign else "N/A"

    def most_recent_title_win(self):
        return self.most_recent_reign if self.most_recent_reign else "N/A"

    def career_span(self):
        if self.career_span_days:
            years = self.career_span_days // 365
            months = (self.career_span_days % 365) // 30
            return f"{years} years, {months} months"
        return "N/A"
