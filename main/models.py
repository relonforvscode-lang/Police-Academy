from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    # Hierarchical rank system (highest to lowest)
    RANK_CHOICES = [
        ('dev', 'Developer'),
        ('police_chief', 'Police Chief'),
        ('deputy_chief', 'Deputy Chief'),
        ('academy_commander', 'Academy Commander'),
        ('deputy_commander', 'Deputy Commander'),
        ('trainer', 'Trainer'),
        ('cadet', 'Cadet'),
    ]
    
    # Rank hierarchy (higher value = higher authority)
    RANK_HIERARCHY = {
        'dev': 6,
        'police_chief': 5,
        'deputy_chief': 4,
        'academy_commander': 3,
        'deputy_commander': 2,
        'trainer': 1,
        'cadet': 0,
    }
    
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='cadet')
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def get_rank_hierarchy(self):
        """Return the hierarchy level of this user's rank"""
        return self.RANK_HIERARCHY.get(self.rank, 0)
    
    def has_dashboard_access(self):
        """Check if user can access admin dashboard (all except trainer and cadet)"""
        return self.rank not in ['trainer', 'cadet']
    
    def can_add_users(self):
        """Check if user can add new users (all except trainer and cadet)"""
        return self.rank not in ['trainer', 'cadet']
    
    def can_manage_assignments(self):
        """Check if user can manage assignments (all except trainer and cadet)"""
        return self.rank not in ['trainer', 'cadet']
    
    def can_view_applications(self):
        """Check if user can view and manage applications (all except cadet)"""
        return self.rank != 'cadet'  # All except cadet
    
    def can_manage_user(self, target_user):
        """Check if this user can manage (edit/delete) another user"""
        # User cannot manage themselves
        if self.id == target_user.id:
            return False
        # User can only manage users with lower rank
        return self.get_rank_hierarchy() > target_user.get_rank_hierarchy()
    
    def get_manageable_ranks(self):
        """Get list of ranks this user can assign to new users"""
        my_hierarchy = self.get_rank_hierarchy()
        manageable = []
        for rank, level in self.RANK_HIERARCHY.items():
            if level < my_hierarchy:  # Can manage lower ranks only
                manageable.append(rank)
        return manageable

    def __str__(self):
        return f"{self.full_name} (@{self.username}) - {self.get_rank_display()}"

class Assignment(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer_assignments')
    cadet = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cadet_assignments')

    class Meta:
        unique_together = ('trainer', 'cadet')

class Evaluation(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_evaluations')
    cadet = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_evaluations')
    score = models.IntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


# --- New models for Applications and Testing ---
class Application(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('testing', 'Testing'),
        ('completed', 'Completed'),
    ]
    discord_id = models.CharField(max_length=64)
    character_name = models.CharField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)
    test_started_at = models.DateTimeField(blank=True, null=True)  # When test actually started (after 120s countdown)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    # If closed, admin can set either timer (datetime) or a custom message
    closed_message = models.TextField(blank=True, null=True)
    reopen_at = models.DateTimeField(blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"Application {self.id} - {self.character_name} ({self.discord_id})"


class ApplicationSetting(models.Model):
    """Singleton-ish settings for the application process."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    closed_message = models.TextField(blank=True, null=True)
    reopen_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ApplicationSetting ({self.status})"


class Question(models.Model):
    text = models.TextField()
    # store options as a JSON list of 4 strings
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_index = models.IntegerField(help_text='0..3')

    def options(self):
        return [self.option_a, self.option_b, self.option_c, self.option_d]

    def __str__(self):
        return f"Q{self.id}: {self.text[:50]}"


class TestSession(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)
    # store chosen question ids as a comma-separated list for reproducibility
    questions_order = models.TextField(blank=True, null=True)
    # unique token for security - ties the test to the original applicant
    session_token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    # Discord ID of the person who started this session (for security verification)
    discord_id = models.CharField(max_length=64, blank=True, null=True)

    def question_ids(self):
        if not self.questions_order:
            return []
        return [int(x) for x in self.questions_order.split(',') if x]


class ApplicantAnswer(models.Model):
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_index = models.IntegerField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer {self.id} (Q{self.question.id}) -> {self.selected_index}"


class AuditLog(models.Model):
    """Simple audit log for administrative and user actions."""
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        actor = self.actor.username if self.actor else 'system'
        return f"[{self.created_at.isoformat()}] {actor} - {self.action} -> {self.target or ''}"


class AuditTemplate(models.Model):
    """Editable templates for audit/notification messages.

    Fields:
    - key: short identifier for the template (e.g. 'final_accept')
    - template: a Python format string using {actor}, {target}, {details}
    """
    key = models.CharField(max_length=100, unique=True)
    template = models.TextField(help_text='Use {actor}, {target}, {details} placeholders')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Template {self.key}"
