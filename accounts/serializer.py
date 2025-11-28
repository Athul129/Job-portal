from rest_framework import serializers
from .models import *
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import random



class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password', 'confirm_password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):

        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"})
        return data

    def create(self, validated_data):

        validated_data.pop('confirm_password')

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
            full_name=validated_data.get('full_name', '')
        )
        # if user.role == "jobseeker":
        #     JobSeekerProfile.objects.create(user=user)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = self.context['request'].user

        if not user.check_password(data['old_password']):
            raise serializers.ValidationError(
                {"old_password": "Old password is incorrect."})

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match."})

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class RequestOtpSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found"})

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        PasswordResetOtp.objects.create(user=user, otp=otp)

        # Send OTP
        send_mail(
            subject="Your Password Reset OTP",
            message=f"Hello {user.email}, your OTP for password reset is {otp}. It is valid for 2 minutes.",
            from_email="athulkp129@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"OTP for {user.email} is: {otp}")  # Debug only

        data["user"] = user
        return data

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")
        try:
            user = CustomUser.objects.get(email=email)
            otp_instance = PasswordResetOtp.objects.filter(
                user=user, otp=otp
            ).latest("created_at")

            if otp_instance.is_expired():
                raise serializers.ValidationError({"otp": "OTP expired"})

            otp_instance.is_verified = True
            otp_instance.save()
            data["user"] = user
        except (CustomUser.DoesNotExist, PasswordResetOtp.DoesNotExist):
            raise serializers.ValidationError({"otp": "Invalid email or OTP"})

        return data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        new_password = data.get("new_password")
        try:
            user = CustomUser.objects.get(email=email)
            otp_instance = PasswordResetOtp.objects.filter(
                user=user).latest("created_at")

            if not otp_instance.is_verified:
                raise serializers.ValidationError({"otp": "OTP not verified"})

            # Reset password
            user.set_password(new_password)
            user.save()

            otp_instance.delete()
            data["user"] = user
        except (CustomUser.DoesNotExist, PasswordResetOtp.DoesNotExist):
            raise serializers.ValidationError(
                {"email": "User not found or no OTP record"})

        return data



class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    full_name = serializers.CharField(source="user.full_name")  # editable
    email = serializers.EmailField(source="user.email", read_only=True)
    role=serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = JobSeekerProfile
        fields = ["id","full_name", "email", "phone_number",
                  "address", "skills", "experience", "about_me","role","profile","cover_image"]
        read_only_fields = ["email","id","role"]

    def update(self, instance, validated_data):
        # Handle user full_name update
        user_data = validated_data.pop('user', {})
        full_name = user_data.get('full_name')
        if full_name:
            instance.user.full_name = full_name
            instance.user.save()

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Convert comma-separated string to list in the response
        skills = instance.skills or ""
        ret["skills"] = [s.strip() for s in skills.split(",") if s.strip()]
        return ret

    


class CompanyProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name")

    class Meta:
        model = CompanyProfile
        fields = ['id','email', 'website', 'address',
                  'about_us', 'location', 'phone_number', 'logo','full_name']
        read_only_fields = ['email','id']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        full_name = user_data.get('full_name')
        if full_name:
            instance.user.full_name = full_name
            instance.user.save()
        return super().update(instance, validated_data)

class CompanyReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    company_name=serializers.CharField(source='company.user.full_name', read_only=True)
    rating = serializers.FloatField(min_value=1, max_value=5)
    class Meta:
        model = CompanyReview
        fields = ['id', 'company', 'company_name','reviewer', 'reviewer_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'reviewer', 'reviewer_name','company_name', 'company']



class FollowSerializer(serializers.ModelSerializer):
    following_name = serializers.CharField(source='following.full_name', read_only=True)

    class Meta:
        model = Follow
        fields = ['following', 'following_name', 'created_at']
        read_only_fields = [ 'created_at', 'follower', 'follower_name']

class FollowersSerializer(serializers.ModelSerializer):
    follower_name = serializers.CharField(source='follower.full_name', read_only=True)

    class Meta:
        model = Follow
        fields = ['follower', 'follower_name', 'created_at']
        read_only_fields = ['created_at', 'follower', 'follower_name']


