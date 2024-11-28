from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .serializers import PostSerializer
from .models import Post
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from rest_framework.views import APIView
from utils.send_email import send_email
    
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostList(APIView):
    # authentication_classes = (JWTAuthentication, CookieJWTAuthentication)
    # permission_classes = (IsAuthenticated,)
    @swagger_auto_schema(
        operation_summary="取得文章列表",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search keyword for title and content", type=openapi.TYPE_STRING),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Posts successfully retrieved",
                schema=PostSerializer(many=True)
            ),
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }
    )
    def get(self, request):
        # input_data = request.GET.dict()
        # input_data = dict(request.query_params)
        # print(input_data)
        search_keyword = request.query_params.get('search', '')
        # default order: pk ascending order
        # The - prefix means descending order
        posts = Post.objects.filter(
            Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword)
        ).order_by('-updated_at')
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @swagger_auto_schema(
        # operation_description="Create a new post.",
        operation_summary="新增文章",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description="標題"),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description="內容"),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Post successfully created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }   
    )
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetail(APIView):
    # authentication_classes = (CookieJWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    
    @swagger_auto_schema(
        operation_summary="取得文章",
    )
    def get(self, _, pk):
        return self._process_request(pk, 'get')
    
    @swagger_auto_schema(
        operation_summary="更新文章",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description="標題"),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description="內容"),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Post successfully updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: "Bad request"
        }
    )
    def put(self, request, pk):
        return self._process_request(pk, 'put', request.data)
    
    @swagger_auto_schema(
        operation_summary="刪除文章",
    )
    def delete(self, _, pk):
        return self._process_request(pk, 'delete')

    def _process_request(self, pk, method, data=None):
        
        try:
            post = Post.objects.get(pk=pk)
            if method == 'get':
                serializer = PostSerializer(post)
                return Response(serializer.data)
            elif method == 'put':
                serializer = PostSerializer(post, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
            elif method == 'delete':
                post.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class SendEmailTest(APIView):
    def post(self, request):
        check, error_message = send_email(subject="test", email="wendy.hsieh@big-data.com.tw", message="Good day!")
        print('check', check, 'error_message', error_message)
        return Response(status=status.HTTP_200_OK)