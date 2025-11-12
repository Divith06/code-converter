# models.py
from django.db import models

class Feedback(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    source_lang = models.CharField(max_length=32)
    target_lang = models.CharField(max_length=32)
    previous_code = models.TextField(blank=True)
    feedback_text = models.TextField()
    refined_code = models.TextField(blank=True)

    def __str__(self):
        return f"Feedback {self.id} {self.created_at}"
