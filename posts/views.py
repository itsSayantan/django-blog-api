from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from posts.models import Post
from posts.serializers import PostSerializer

def posts(request):
    # list all posts
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return JsonResponse({ 'status': True, 'data': { 'posts': serializer.data } }, safe=False)

    # create a post
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({ 'status': True, 'data': { 'id': serializer.data.get('id') } }, status=201)
        return JsonResponse({ 'status': False, 'errors': serializer.errors }, status=400)

def post(request):
    # fetch a post by id
    if request.method == 'GET':
        id = request.GET.get('id', None)

        if id == None:
            return JsonResponse({ 'status': False, 'errors': { 'message': 'An \'id\' parameter is required' }  }, status=400)

        try:
            post = Post.objects.get(id=id)
            
            serializer = PostSerializer(post, many=False)
            return JsonResponse({ 'status': True, 'data': { 'post': serializer.data } }, safe=False)
        except Post.DoesNotExist:
            return JsonResponse({'status': False, "errors": { 'message': 'Post with id: {} does not exist'.format(id) } }, status=400)

def update_post(request):
    # update a post by id
    if request.method == 'PUT':
        id = request.GET.get('id', None)

        if id == None:
            return JsonResponse({ 'status': False, 'errors': { 'message': 'An \'id\' parameter is required' }  }, status=400)

        try:
            data = JSONParser().parse(request)

            post = Post.objects.get(id=id)
            
            Post.objects.filter(id=id).update(**data)
            return JsonResponse({ 'status': True, 'message': 'The post with id {} has been updated'.format(id) }, status=200)
        except Post.DoesNotExist:
            return JsonResponse({'status': False, "errors": { 'message': 'Post with id: {} does not exist'.format(id) } }, status=400)
        except:
            return JsonResponse({ 'status': False, 'errors': { 'message': 'Some unknown error occured while updating the post' } } ,status=500)