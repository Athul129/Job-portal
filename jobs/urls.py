from django.urls import path
from .views import *

urlpatterns = [
    path('jobs/', JobPostView.as_view(), name='job-list-create'),
    path('jobs/<int:job_id>/', JobPostView.as_view(), name='job-detail-update-delete'),
    path('myjobs/',MyJoblist.as_view(),name='my-jobs'),
    path('jobslist/',Joblist.as_view(),name='all-jobs'),
    path('create-post/', CreatePostView.as_view(), name='create-post'),
    path('edit-post/<int:post_id>/', CreatePostView.as_view(), name='edit-post'),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('delete-post-image/<int:image_id>/', DeletePostImageView.as_view(), name='delete-post-image'),
    path('comment_post/<int:post_id>/', CommentView.as_view(), name='comment'),
    path('comment_edit/<int:comment_id>/', CommentView.as_view(), name='comment_edit'),
    path('comments/<int:id>/', Comments.as_view(), name='comments'),
    path('jobs_search/', JobSearch.as_view(), name='job-search'),
    path('apply-job/<int:job_id>/', ApplyJobView.as_view(), name='apply-job'),
    path('applied-jobs/<int:job_id>/', AppliedJobsListView.as_view(), name='applied-jobs'),
    path('applications/<int:application_id>/', UpdateApplicationStatusView.as_view(), name='update-application-status'),
    path('my-applications/', GetAppliedJobsView.as_view(), name='my-applications'),
    path('post_like/<int:post_id>/', PostLikeDislikeView.as_view(), name='post-like-dislike'),
    path('get_likes/<int:post_id>/', Likesget.as_view(), name='get-likes-dislikes'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
]  

