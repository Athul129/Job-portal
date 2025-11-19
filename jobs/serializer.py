from rest_framework import serializers
from .models import *


class Jobserializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(
        source='posted_by.full_name', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'job_type', 'salary', 'experience', 'skills_required', 'qualifications', 'last_date', 'created_at','posted_by_name']
        read_only_fields = [ 'created_at','posted_by_name']

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']

class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    user=serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'created_at', 'images']
        read_only_fields = ['user','created_at','images']


    

class CommentSerializer(serializers.ModelSerializer):
    user=serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']    


class AppliedJobSerializer(serializers.ModelSerializer):
    user_name=serializers.CharField(source='user.full_name', read_only=True)
    email=serializers.CharField(source='user.email', read_only=True)
    job_title=serializers.CharField(source='job.title', read_only=True)
    class Meta:
        model = AppliedJob
        fields = ['id', 'user_name', 'email','job_title', 'job', 'cv', 'description', 'applied_at','user','status']
        read_only_fields = ['id', 'user', 'job', 'applied_at','user_name','email','job_title', 'status']

class ApplicantSerializer(serializers.ModelSerializer):
    user_name=serializers.CharField(source='user.full_name', read_only=True)
    job_title=serializers.CharField(source='job.title', read_only=True)
    class Meta:
        model = AppliedJob
        fields = ['id', 'job_title', 'user_name', 'cv', 'description', 'applied_at','status',]
        read_only_fields = ['id', 'user_name','cv', 'description', 'applied_at','status','job_title']



class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'sender_name', 'message', 'created_at']
