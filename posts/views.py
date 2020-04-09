import csv, io
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from posts.models import Post
from posts.serializers import PostSerializer

@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
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
            return JsonResponse({ 'status': True, 'data': { 'message': 'The post with id {} has been updated'.format(id) } }, status=200)
        except Post.DoesNotExist:
            return JsonResponse({'status': False, "errors": { 'message': 'Post with id: {} does not exist'.format(id) } }, status=400)
        except:
            return JsonResponse({ 'status': False, 'errors': { 'message': 'Some unknown error occured while updating the post' } } ,status=500)

@csrf_exempt
def bulk_create(request):
    # create multiple posts from a file
    # accept a csv or an excel file
    file = request.FILES.get('file')

    # check if a file is uploaded
    if file == None:
        return JsonResponse({'status': False, "errors": { 'message': 'A \'file\' paramter should be sent.' } }, status=400)

    # check if the uploaded file is a csv, xls or an xlsx
    # @TODO handle the xls and xlsx file formats
    fct = file.content_type
    if fct != 'text/csv':
        return JsonResponse({'status': False, "errors": { 'message': 'A CSV \'file\' should be uploaded.' } }, status=400)

    data_set = file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)

    # skip the first line of the file
    next(io_string)

    reader = csv.reader(io_string, delimiter='|', quotechar="|")
    
    # restrict the user to add more than 5 posts at a time,
    # if number of posts is less than 0, send an error,
    # if number of posts is greater than 5, store 5 posts and let the user know that the remaining posts were not considered

    l = 0
    ids = []

    for row in reader:
        print(row)
        if l==5:
            # let the user know that the remaining data is truncated
            return JsonResponse({ 'status': True, 'data': { 'ids': ids, 'message': 'Only 5 rows were stored. The remaining data has been truncated as per our policy. Please upload a maximum of 5 posts at a time' } }, status=200)
        else:
            # store a post object
            p = Post.objects.create(title=row[0], content=row[1], author=row[2])
            p.save()
            ids.append(p.id)
            l = l+1
    
    if l == 0:
        return JsonResponse({ 'status': False, 'errors': { 'message': 'No posts were sent' } }, status=400)
    else:
        return JsonResponse({ 'status': True, 'data': { 'ids': ids } }, status=201)