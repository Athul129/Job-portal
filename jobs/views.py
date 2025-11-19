from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializer import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from accounts.models import Follow

# Create your views here.


class JobPostView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ✅ Allow only Employer or Company
        if request.user.role not in ['employer', 'company']:
            return Response({
                "Success": False,
                "message": "You do not have permission to post a job.",
                "data": None,
                "errors": None
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = Jobserializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response({
                "Success": True,
                "message": "Job posted successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)

        return Response({
            "Success": False,
            "message": "Job posting failed",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, posted_by=request.user)
        except Job.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Job not found or you don't have permission to edit",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Restrict by role
        if request.user.role not in ['employer', 'company']:
            return Response({
                "Success": False,
                "message": "You do not have permission to edit job posts.",
                "data": None,
                "errors": None
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = Jobserializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "Job updated successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)

        return Response({
            "Success": False,
            "message": "Job update failed",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, posted_by=request.user)
        except Job.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Job not found or you don't have permission to delete",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Restrict by role
        if request.user.role not in ['employer', 'company']:
            return Response({
                "Success": False,
                "message": "You do not have permission to delete job posts.",
                "data": None,
                "errors": None
            }, status=status.HTTP_403_FORBIDDEN)

        job.delete()
        return Response({
            "Success": True,
            "message": "Job deleted successfully",
            "data": None,
            "errors": None
        }, status=status.HTTP_200_OK)


class MyJoblist(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            jobs = Job.objects.filter(
                posted_by=request.user).order_by('-created_at')
            serializer = Jobserializer(jobs, many=True)
            return Response({
                "Success": True,
                "message": "Your jobs fetched successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response({
                "Success": False,
                "message": "No jobs found for your account",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)


class Joblist(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            jobs = Job.objects.all().order_by('-created_at')
            serializer = Jobserializer(jobs, many=True)
            return Response({
                "Success": True,
                "message": "Jobs fetched successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response({
                "Success": False,
                "message": "No jobs found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)


class CreatePostView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(user=request.user)
            for image in request.FILES.getlist('images'):
                PostImage.objects.create(post=post, image=image)

            followers=Follow.objects.filter(following=request.user)
            for follower in followers:
                Notification.objects.create(
                    sender=request.user,
                    receiver=follower.follower,
                    message=f"{request.user.full_name} has created a new post."
                ) 
            return Response({
                "success": True,
                "message": "Post created successfully and notifications sent to followers",
                "data": PostSerializer(post).data,
                "errors": None
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response({
            "Success": True,
            "message": "All Posts fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def put(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, user=request.user)
        except Post.DoesNotExist:
            return Response({
                "success": False,
                "message": "Post not found or you do not have permission to edit this post",
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        if request.FILES.getlist('images'):
            return Response({
                "success": False,
                "message": "you cannot edit images.",
                "errors": None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Post updated successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, user=request.user)
            post.delete()
            return Response({
                "success": True,
                "message": "Post deleted successfully",
                "data": None,
                "errors": None
            }, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({
                "success": False,
                "message": "Post not found or you do not have permission to delete this post",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)


class PostListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response({
            "Success": True,
            "message": "Posts fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)


class DeletePostImageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, image_id):
        try:
            image = PostImage.objects.get(id=image_id, post__user=request.user)
            image.delete()
            return Response({
                "Success": True,
                "message": "Image deleted successfully",
                "data": None,
                "errors": None
            }, status=status.HTTP_200_OK)
        except PostImage.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Image not found or not authorized",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)


class CommentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Post not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response({
                "Success": True,
                "message": "Comment added successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id, user=request.user)
        except Comment.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Comment not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        # if comment.user != request.user:
        #     return Response({
        #         "Success": False,
        #         "message": "You are not allowed to edit this comment",
        #         "data": None,
        #         "errors": None
        #     }, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(
            comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "Comment updated successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)
        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        """Delete comment (by comment owner or post owner)"""
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Comment not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Allow comment owner or post owner to delete
        if comment.user != request.user and comment.post.user != request.user:
            return Response({
                "Success": False,
                "message": "You are not allowed to delete this comment",
                "data": None,
                "errors": None
            }, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({
            "Success": True,
            "message": "Comment deleted successfully",
            "data": None,
            "errors": None
        }, status=status.HTTP_200_OK)


class Comments(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, id):
        """List all comments under a post (only post owner can view)"""
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Post not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check if the logged-in user is the owner of the post
        if post.user != request.user:
            return Response({
                "Success": False,
                "message": "You are not authorized to view comments for this post",
                "data": None,
                "errors": None
            }, status=status.HTTP_403_FORBIDDEN)

        # ✅ Fetch comments only if authorized
        comments = Comment.objects.filter(post_id=id).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            "Success": True,
            "message": "Comments fetched successfully",
            "Total Comments": comments.count(),
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)


class PostLikeDislikeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Post not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        reaction = request.data.get('reaction')  # 'like' or 'dislike'

        if reaction not in ['like', 'dislike']:
            return Response({
                "Success": False,
                "message": "Invalid reaction type",
                "data": None,
                "errors": None
            }, status=status.HTTP_400_BAD_REQUEST)

        post_like, created = PostLike.objects.get_or_create(user=request.user, post=post)

        # If user clicked same reaction again, remove it (toggle off)
        if not created and post_like.reaction == reaction:
            post_like.delete()
            message = f"{reaction.capitalize()} removed"
        else:
            post_like.reaction = reaction
            post_like.save()
            message = f"Post {reaction}d successfully"

        return Response({
            "Success": True,
            "message": message,
            "data": {
                "likes_count": post.likes.filter(reaction='like').count(),
                "dislikes_count": post.likes.filter(reaction='dislike').count(),
            },
            "errors": None
        }, status=status.HTTP_200_OK)


class Likesget(APIView):

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Post not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        likes_count = post.likes.filter(reaction='like').count()
        dislikes_count = post.likes.filter(reaction='dislike').count()

        serializer = PostSerializer(post)

        return Response({
            "Success": True,
            "message": "Likes and dislikes count fetched successfully",
            "data": {
                "post": serializer.data,
                "likes_count": likes_count,
                "dislikes_count": dislikes_count,
            },
            "errors": None
        }, status=status.HTTP_200_OK)

class JobSearch(APIView):
    def get(self, request):
        jobs = Job.objects.all().order_by('-created_at')

        # --- Search ---
        search = request.query_params.get('search')
        if search:
            jobs = jobs.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(location__icontains=search) |
                models.Q(skills_required__icontains=search) |
                models.Q(qualifications__icontains=search) |
                models.Q(job_type__icontains=search) |
                models.Q(experience__icontains=search)
            )

        # --- Filters ---
        job_type = request.query_params.get('job_type')
        location = request.query_params.get('location')
        experience = request.query_params.get('experience')
        skills = request.query_params.get('skills')
        min_salary = request.query_params.get('min_salary')
        max_salary = request.query_params.get('max_salary')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if job_type:
            jobs = jobs.filter(job_type__iexact=job_type)

        if location:
            jobs = jobs.filter(location__icontains=location)

        if experience:
            jobs = jobs.filter(experience__icontains=experience)

        if skills:
            jobs = jobs.filter(skills_required__icontains=skills)

        # --- Salary Range Filter ---
        if min_salary:
            jobs = jobs.filter(salary__gte=min_salary)
        if max_salary:
            jobs = jobs.filter(salary__lte=max_salary)

        # --- Date Range Filter ---
        if start_date:
            jobs = jobs.filter(created_at__date__gte=start_date)
        if end_date:
            jobs = jobs.filter(created_at__date__lte=end_date)

        serializer = Jobserializer(jobs, many=True)
        return Response({
            "success": True,
            "message": "Jobs fetched successfully",
            "count": jobs.count(),
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)


class ApplyJobView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Job not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if user already applied
        if AppliedJob.objects.filter(job=job, user=request.user).exists():
            return Response({
                "Success": False,
                "message": "You have already applied to this job",
                "data": None,
                "errors": None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AppliedJobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, job=job)
            return Response({
                "Success": True,
                "message": "Job application submitted successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "Success": False,
                "message": "Invalid data",
                "data": None,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class AppliedJobsListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, job_id):
        user = request.user

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"Job not found."}, status=status.HTTP_404_NOT_FOUND)

        if user != job.posted_by:
            return Response(
                {"You do not have permission to view applications for this job."},
                status=status.HTTP_403_FORBIDDEN
            )

        applications = AppliedJob.objects.filter(job=job)
        serializer = AppliedJobSerializer(applications, many=True)
        return Response({
            "success": True,
            "message": "Applications fetched successfully.",
            "count": applications.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)



# class UpdateApplicationStatusView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def post(self, request, application_id):
#         try:
#             application = AppliedJob.objects.get(id=application_id)
#         except AppliedJob.DoesNotExist:
#             return Response({
#                 "Success": False,
#                 "message": "Application not found",
#                 "data": None,
#                 "errors": None
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         if application.job.posted_by != request.user:
#             return Response({
#                 "Success": False,
#                 "message": "You are not authorized to update this application",
#                 "data": None,
#                 "errors": None
#             }, status=status.HTTP_403_FORBIDDEN)

#         # Expected value: 'shortlisted' or 'rejected'
#         new_status = request.data.get('status')

#         if new_status not in ['shortlisted', 'Rejected']:
#             return Response({
#                 "Success": False,
#                 "message": "Invalid status. Use 'shortlisted' or 'Rejected'.",
#                 "data": None,
#                 "errors": None
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Update the status
#         application.status = new_status
#         application.save()


#         if new_status == 'shortlisted':
#             subject = "Your Application Has Been Shortlisted!"
#             message = f"Hi {application.user.full_name},\n\n" \
#                 f"Congratulations! Your application for the position '{application.job.title}' has been shortlisted for an interview.\n\n" \
#                 f"Regards,\n{application.job.posted_by.full_name}"
#         elif new_status == 'Rejected':
#             subject = "Your Application Update"
#             message = f"Hi {application.user.full_name},\n\n" \
#                 f"Thank you for applying for '{application.job.title}'. After careful review, we regret to inform you that you were not shortlisted at this stage.\n\n" \
#                 f"Regards,\n{application.job.posted_by.full_name}"

#         # Send email
#             send_mail(
#                 subject,
#                 message,
#                 from_email=application.job.posted_by.email,  # Job poster's email
#                 recipient_list=[application.user.email],
#                 fail_silently=False,
#             )

#         return Response({
#             "Success": True,
#             "message": f"Application {new_status} and email sent successfully.",
#             "errors": None
#         }, status=status.HTTP_200_OK)


from django.core.mail import EmailMessage
from django.conf import settings


class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, application_id):
        try:
            application = AppliedJob.objects.get(id=application_id)
        except AppliedJob.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Application not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        if application.job.posted_by != request.user:
            return Response({
                "Success": False,
                "message": "You are not authorized to update this application",
                "data": None,
                "errors": None
            }, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status')

        if new_status not in ['shortlisted', 'Rejected']:
            return Response({
                "Success": False,
                "message": "Invalid status. Use 'shortlisted' or 'rejected'.",
                "data": None,
                "errors": None
            }, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()

        if new_status == 'shortlisted':
            subject = "Your Application Has Been Shortlisted!"
            message = f"Hi {application.user.full_name},\n\n" \
                      f"Congratulations! Your application for the position '{application.job.title}' has been shortlisted for an interview.\n\n" \
                      f"Regards,\n{application.job.posted_by.full_name}"

        elif new_status == 'Rejected':
            subject = "Your Application Update"
            message = f"Hi {application.user.full_name},\n\n" \
                      f"Thank you for applying for '{application.job.title}'. After careful review, we regret to inform you that you were not shortlisted at this stage.\n\n" \
                      f"Regards,\n{application.job.posted_by.full_name}"

        # ✅ send_mail now always runs (for both statuses)
        # send_mail(
        #     subject,
        #     message,
        #     from_email=application.job.posted_by.email,
        #     recipient_list=[application.user.email],
        #     fail_silently=False,
        # )
        email=EmailMessage(
            subject,
            message,
            from_email=settings.EMAIL_HOST_USER,
            to=[application.user.email],
            reply_to=[application.job.posted_by.email],
        )
        email.send()

        return Response({
            "Success": True,
            "message": f"Application {new_status} and email sent successfully.",
            "errors": None
        }, status=status.HTTP_200_OK)


class GetAppliedJobsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        applications = AppliedJob.objects.filter(
            user=request.user).order_by('-applied_at')
        serializer = ApplicantSerializer(applications, many=True)
        return Response({
            "success": True,
            "message": "Your job applications fetched successfully.",
            "count": applications.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)



class NotificationListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        # unread_count = notifications.filter(is_read=False).count()

        return Response({
            "Success": True,
            "message": "Notifications fetched successfully",
            "total notifications": notifications.count(),
            # "unread_count": unread_count,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)
