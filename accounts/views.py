# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import random



class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)

            otp = str(random.randint(100000, 999999))
            EmailVerificationOtp.objects.create(user=user, otp=otp)

            send_mail(
                subject="Verify your Email",
                message=f"Hello {user.full_name or user.email}, your OTP is {otp}. It is valid for 5 minutes.",
                from_email="company@gmail.com",
                recipient_list=[user.email],
                fail_silently=False
            )
            print(f"OTP for {user.email} is {otp}")  # For testing purposes

            return Response({
                "success": True,
                "message": "OTP sent to email. Please verify to activate account.",
                "data": {"email": user.email},
                "errors": None,
                "otp": otp
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyRegistrationOtpView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        try:
            user = CustomUser.objects.get(email=email)
            otp_instance = EmailVerificationOtp.objects.filter(
                user=user, otp=otp
            ).latest("created_at")

            if otp_instance.is_expired():
                return Response({"success": False, "message": "OTP expired"}, 400)

            otp_instance.is_verified = True
            otp_instance.save()
            user.is_active = True
            user.save()

            return Response({
                "success": True,
                "message": "Email verified. Account activated.",
                "errors": None,
            }, status=status.HTTP_200_OK)

        except (CustomUser.DoesNotExist, EmailVerificationOtp.DoesNotExist):
            return Response({
                "success": False,
                "message": "Invalid email or OTP"
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "Login successful",
                "data": {
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                },
                "errors": None
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "message": "Invalid credentials",
            "errors": None
        }, status=status.HTTP_401_UNAUTHORIZED)


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Use JWT auth
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            Response_data = {
                "Success": True,
                "message": "Password changed successfully.",
                "data": None,
                "errors": None
            }
            return Response(Response_data, status=status.HTTP_200_OK)

        Response_data = {
            "Success": False,
            "message": "Password change failed.",
            "data": None,
            "errors": serializer.errors
        }
        return Response(Response_data, status=status.HTTP_400_BAD_REQUEST)


class RequestOtpView(APIView):
    def post(self, request):
        serializer = RequestOtpSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "Success": True,
                "message": "OTP sent to email",
                "data": None,
                "errors": None
            })
        return Response({
            "Success": False,
            "message": "Validation failed",
            "data": None,
            "errors": serializer.errors
        }, status=400)


class VerifyOtpView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "Success": True,
                "message": "OTP verified",
                "data": None,
                "errors": None
            })
        return Response({
            "Success": False,
            "message": "Validation failed",
            "data": None,
            "errors": serializer.errors
        }, status=400)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "Success": True,
                "message": "Password reset successful",
                "data": None,
                "errors": None
            })
        return Response({
            "Success": False,
            "message": "Validation failed",
            "data": None,
            "errors": serializer.errors
        }, status=400)



# class JobseekerProfileView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
            
#             profile = JobSeekerProfile.objects.get(user=request.user)
#         except JobSeekerProfile.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": "Profile not found",
#                 "errors": None
#             }, status=status.HTTP_404_NOT_FOUND)

#         serializer = JobseekerProfileSerializer(profile)
#         return Response({
#             "success": True,
#             "message": "Profile retrieved successfully",
#             "data": serializer.data,
#             "errors": None
#         }, status=status.HTTP_200_OK)

#     def put(self, request):
#         try:
#             profile = JobSeekerProfile.objects.get(user=request.user)
#         except JobSeekerProfile.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": "Profile not found",
#                 "errors": None
#             }, status=status.HTTP_404_NOT_FOUND)

#         serializer = JobseekerProfileSerializer(profile, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "success": True,
#                 "message": "Profile updated successfully",
#                 "data": serializer.data,
#                 "errors": None
#             }, status=status.HTTP_200_OK)

#         return Response({
#             "success": False,
#             "message": "Validation failed",
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)    

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # If profile exists, get it. Otherwise, just show empty fields.
        profile, created = JobSeekerProfile.objects.get_or_create(user=user)

        serializer = UserProfileSerializer(profile)
        return Response({
            "Success": True,
            "message": "User profile fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        profile, created = JobSeekerProfile.objects.get_or_create(user=user)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "User profile updated successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)

        return Response({
            "Success": False,
            "message": "Profile update failed",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class UsersListview(APIView):
    def get(self, request):
        users = JobSeekerProfile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response({
            "Success": True,
            "message": "Users fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)    



class CompanyProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # If profile exists, get it. Otherwise, just show empty fields.
        profile, created = CompanyProfile.objects.get_or_create(user=user)

        serializer = CompanyProfileSerializer(profile)
        return Response({
            "Success": True,
            "message": "User profile fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        profile, created = CompanyProfile.objects.get_or_create(user=user)

        serializer = CompanyProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "User profile updated successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)

        return Response({
            "Success": False,
            "message": "Profile update failed",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ComapnyListView(APIView):
    def get(self, request):
        companies = CompanyProfile.objects.all()
        serializer = CompanyProfileSerializer(companies, many=True)
        return Response({
            "Success": True,
            "message": "Company profiles fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)

class CompanyReviewView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request,id):
        try:
            profile = CompanyProfile.objects.get(id=id)
        except CompanyProfile.DoesNotExist:
            return Response({
                "success": False,
                "message": "Company not found",
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(company=profile, reviewer=request.user)
            return Response({
                "success": True,
                "message": "Review submitted successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request,id):
        try:
            profile = CompanyProfile.objects.get(id=id)
        except CompanyProfile.DoesNotExist:
            return Response({
                "success": False,
                "message": "Company not found",
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        reviews = profile.reviews.all().order_by('-created_at')
        serializer = CompanyReviewSerializer(reviews, many=True)
        return Response({
            "success": True,
            "message": "Reviews retrieved successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)




# -------------------
# Follow a user
# -------------------
class FollowUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        follower = request.user

        if follower.id == user_id:
            return Response({"Success": False, "message": "You cannot follow yourself", "data": None, "errors": None})

        try:
            following_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"Success": False, "message": "User not found", "data": None, "errors": None})

        # Admin & Company cannot follow anyone
        if follower.role in ["company"]:
            return Response({"Success": False, "message": "Company cannot follow anyone", "data": None, "errors": None})


        # Create follow if not exists
        follow, created = Follow.objects.get_or_create(follower=follower, following=following_user)
        if not created:
            return Response({"Success": False, "message": "Already following this user", "data": None, "errors": None})

        # serializer = FollowSerializer(follow)
        return Response({"Success": True, "message": "Followed successfully", "errors": None})


# -------------------
# Unfollow a user
# -------------------
class UnfollowUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        follower = request.user
        try:
            follow = Follow.objects.get(follower=follower, following_id=user_id)
            follow.delete()
            return Response({"Success": True, "message": "Unfollowed successfully", "data": None, "errors": None})
        except Follow.DoesNotExist:
            return Response({"Success": False, "message": "You are not following this user", "data": None, "errors": None})

# -------------------
class FollowersListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        followers = Follow.objects.filter(following=request.user)
        serializer = FollowersSerializer(followers, many=True)
        return Response({"Success": True, "message": "Your followers fetched", "data": serializer.data, "errors": None})


# -------------------
# Users the logged-in user is following
# -------------------
class FollowingListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        following = Follow.objects.filter(follower=request.user)
        serializer = FollowSerializer(following, many=True)
        return Response({"Success": True, "message": "Your following list fetched", "data": serializer.data, "errors": None})
    


class FollowCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        followers_count = Follow.objects.filter(following=user).count()
        following_count = Follow.objects.filter(follower=user).count()

        return Response({
            "Success": True,
            "message": "Follow counts fetched successfully",
            "data": {
                "followers_count": followers_count,
                "following_count": following_count
            },
            "errors": None
        }, status=status.HTTP_200_OK)


