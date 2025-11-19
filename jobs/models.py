from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
        ('Remote', 'Remote'),
    ]

    posted_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    experience = models.CharField(max_length=50, null=True, blank=True)
    qualifications = models.TextField(null=True, blank=True)
    skills_required = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.full_name}"



class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="post_images/",null=True,blank=True)

    def __str__(self):
        return f"Image for {self.post.user.full_name}'s post"
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.full_name} on {self.post.id}"    

class PostLike(models.Model):
    LIKE_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="post_reactions")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    reaction = models.CharField(max_length=10, choices=LIKE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Each user can react only once per post

    def __str__(self):
        return f"{self.user.full_name} {self.reaction}d {self.post.id}"


class AppliedJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applied_jobs')
    cv = models.FileField(upload_to='cvs/')
    description = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
        
    

    def __str__(self):
        return f"{self.user.full_name} applied to {self.job.title} - {self.status}"


class Notification(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification from {self.sender} to {self.receiver}"
