import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import  News 
from .serializers import ProfileSerializer, UserSerializer 
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
import random
from rest_framework.permissions import IsAuthenticatedOrReadOnly  # Optional for API authentication

from .models import VerificationCode
from .utils import updateNote, getNoteDetail, deleteNote, getNotesList, createNote
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CrimeData
from .serializers import CrimeDataSerializer
from rest_framework.pagination import PageNumberPagination
from .serializers import ResetPasswordSerializer
from django.utils.crypto import get_random_string
import joblib
import numpy as np

def send_verification_code(email, verification_code):
    subject = 'Your Verification Code'
    message = f'Your verification code is {verification_code}.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


def verify_email(request, user_id, token):
    user = get_object_or_404(User, id=user_id)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Email verified, you can now login.')
    else:
        return HttpResponse('Verification link is invalid!', status=400)
def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    verification_link = request.build_absolute_uri(f'/verify-email/{user.id}/{token}/')

    # Send the email (you can use Django's EmailMessage)
    subject = 'Verify your email'
    message = f'Click the link to verify your email: {verification_link}'
    user.email_user(subject, message)

class ResetPasswordRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            # Generate a random password reset link/token (you'll need to implement the logic to handle this)
            token = get_random_string(32)
            # Send the email with the reset link (make sure to include the token in the link)
            reset_link = f"http://localhost:5173/reset-password?token={token}&email={email}"
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return Response({"success": "Password reset link sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def patch(self, request, token):
        email = request.data.get('email')
        new_password = request.data.get('password')

        # Validate token and email, then reset password
        # Note: You need to implement token validation logic here.
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return Response({"success": "Password has been reset."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Invalid token or email."}, status=status.HTTP_400_BAD_REQUEST)
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    set= get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(user, self.request)
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""@csrf_exempt
def RegisterUser(request):
    if request.method == 'POST':
        requestBody = json.loads(request.body)
        print(requestBody)
        return JsonResponse({"message": 'HI'})"""

@api_view(['GET'])
def get_user_data(request):
    if request.user.is_authenticated:
        user_data = {
            
            'username': request.user.username,
          
            # Add more fields as needed
        }
        return Response(user_data)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.data['username']).first()
        if user and not user.is_active:
            return Response({'error': 'Email not verified'}, status=403)

        if user and user.check_password(request.data['password']):
            # Generate a verification code
            verification_code = random.randint(100000, 999999)
            VerificationCode.objects.update_or_create(user=user, defaults={'code': verification_code})

            # Send the code via email
            send_verification_code(user.email, verification_code)
            return Response({'message': 'Verification code sent to your email'})

        return Response({'error': 'Invalid credentials'}, status=403)
    

class VerifyCodeView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        code = request.data.get('code')
        user = User.objects.filter(username=username).first()

        if user:
            verification_code = VerificationCode.objects.filter(user=user).first()
            if verification_code and str(verification_code.code) == code:
                # Code is valid, generate tokens
                refresh = RefreshToken.for_user(user)
                verification_code.delete()  # Remove the code after successful verification

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
def Users(request):

    user= get_user_model()

    users= user.objects.all()

    return Response(users)



@api_view(['GET'])
def getRoutes(request):

    routes = [
        {
            'Endpoint': '/notes/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of notes'
        },
        {
            'Endpoint': '/notes/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a single note object'
        },
        {
            'Endpoint': '/notes/create/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Creates new note with data sent in post request'
        },
        {
            'Endpoint': '/notes/id/update/',
            'method': 'PUT',
            'body': {'body': ""},
            'description': 'Creates an existing note with data sent in post request'
        },
        {
            'Endpoint': '/notes/id/delete/',
            'method': 'DELETE',
            'body': None,
            'description': 'Deletes and exiting note'
        },
    ]
    return Response(routes)


# /notes GET
# /notes POST
# /notes/<id> GET
# /notes/<id> PUT
# /notes/<id> DELETE

@api_view(['GET', 'POST'])

def getNotes(request):

    if request.method == 'GET':
        return getNotesList(request)

    if request.method == 'POST':
        return createNote(request)


@api_view(['GET', 'PUT', 'DELETE'])
def getNote(request, pk):

    if request.method == 'GET':
        return getNoteDetail(request, pk)

    if request.method == 'PUT':
        return updateNote(request, pk)

    if request.method == 'DELETE':
        return deleteNote(request, pk)
    
@api_view(['POST'])
def save_news(request, news_id):
    try:
        news_item = News.objects.get(id=news_id)
        profile = request.user.profile
        if news_item in profile.saved_news.all():
            profile.saved_news.remove(news_item)  # Unsave news
            return Response({"message": "News item removed from saved list"}, status=status.HTTP_200_OK)
        else:
            profile.saved_news.add(news_item)  # Save news
            return Response({"message": "News item saved"}, status=status.HTTP_200_OK)
    except News.DoesNotExist:
        return Response({"error": "News item not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_history(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def history(request, news_id):
    try:
        news_item = News.objects.get(id=news_id)
        profile = request.user.profile
        if news_item in profile.history.all():
            profile.history.remove(news_item)  # Unsave news
            profile.history.add(news_item)  # Unsave news
            return Response({"message": "News item updated from history list"}, status=status.HTTP_200_OK)
        else:
            profile.history.add(news_item)  # Save news
            return Response({"message": "News item added to history"}, status=status.HTTP_200_OK)
    except News.DoesNotExist:
        return Response({"error": "News item not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_saved_news(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

class CrimeDataPagination(PageNumberPagination):
    page_size = 100  # Number of records per page

class CrimeDataListView(generics.ListAPIView):
    queryset = CrimeData.objects.all()
    serializer_class = CrimeDataSerializer
    pagination_class = CrimeDataPagination


from django.http import JsonResponse
import numpy as np
import joblib

# Load the model (update the path to your model file)
# Load your trained model
model = joblib.load('api/model/random_forest_model.pkl')

chicago_community_areas = {
    1: "Rogers Park", 2: "West Ridge", 3: "Uptown", 4: "Lincoln Square", 5: "North Center", 
    6: "Lakeview", 7: "Lincoln Park", 8: "Near North Side", 9: "Edison Park", 10: "Norwood Park", 
    11: "Jefferson Park", 12: "Forest Glen", 13: "North Park", 14: "Albany Park", 15: "Portage Park", 
    16: "Irving Park", 17: "Dunning", 18: "Montclare", 19: "Belmont Cragin", 20: "Hermosa", 
    21: "Avondale", 22: "Logan Square", 23: "Humboldt Park", 24: "West Town", 25: "Austin", 
    26: "West Garfield Park", 27: "East Garfield Park", 28: "Near West Side", 29: "North Lawndale", 
    30: "South Lawndale", 31: "Lower West Side", 32: "Loop", 33: "Near South Side", 34: "Armour Square", 
    35: "Douglas", 36: "Oakland", 37: "Fuller Park", 38: "Grand Boulevard", 39: "Kenwood", 
    40: "Washington Park", 41: "Hyde Park", 42: "Woodlawn", 43: "South Shore", 44: "Chatham", 
    45: "Avalon Park", 46: "South Chicago", 47: "Burnside", 48: "Calumet Heights", 49: "Roseland", 
    50: "Pullman", 51: "South Deering", 52: "East Side", 53: "West Pullman", 54: "Riverdale", 
    55: "Hegewisch", 56: "Garfield Ridge", 57: "Archer Heights", 58: "Brighton Park", 59: "McKinley Park", 
    60: "Bridgeport", 61: "New City", 62: "West Elsdon", 63: "Gage Park", 64: "Clearing", 
    65: "West Lawn", 66: "Chicago Lawn", 67: "West Englewood", 68: "Englewood", 69: "Greater Grand Crossing", 
    70: "Ashburn", 71: "Auburn Gresham", 72: "Beverly", 73: "Washington Heights", 74: "Mount Greenwood", 
    75: "Morgan Park", 76: "O'Hare", 77: "Edgewater"
}

chicago_community_names = {v.lower(): k for k, v in chicago_community_areas.items()}

primary_crimes = {
    0: 'ARSON', 1: 'ASSAULT', 2: 'BATTERY', 3: 'BURGLARY', 4: 'CONCEALED CARRY LICENSE VIOLATION',
    5: 'CRIM SEXUAL ASSAULT', 6: 'CRIMINAL DAMAGE', 7: 'CRIMINAL SEXUAL ASSAULT', 8: 'CRIMINAL TRESPASS',
    9: 'DECEPTIVE PRACTICE', 10: 'GAMBLING', 11: 'HOMICIDE', 12: 'HUMAN TRAFFICKING', 13: 'INTERFERENCE WITH PUBLIC OFFICER',
    14: 'INTIMIDATION', 15: 'KIDNAPPING', 16: 'LIQUOR LAW VIOLATION', 17: 'MOTOR VEHICLE THEFT', 18: 'NARCOTICS',
    19: 'NON - CRIMINAL', 20: 'NON-CRIMINAL (SUBJECT SPECIFIED)', 21: 'NON-CRIMINAL', 22: 'OBSCENITY', 
    23: 'OFFENSE INVOLVING CHILDREN', 24: 'OTHER NARCOTIC VIOLATION', 25: 'OTHER OFFENSE', 
    26: 'PROSTITUTION', 27: 'PUBLIC INDECENCY', 28: 'PUBLIC PEACE VIOLATION', 29: 'ROBBERY', 
    30: 'SEX OFFENSE', 31: 'STALKING', 32: 'THEFT', 33: 'WEAPONS VIOLATION'
}


class CommunityDataAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]  # Optional

    def post(self, request):
        user_input = request.data.get('community', '').strip().lower()

        # Check if the input is a valid community name
        if user_input in chicago_community_names:
            community_number = chicago_community_names[user_input]
            community_name = chicago_community_areas[community_number]

            # Generate prediction using model (replace with actual features if available)
            total_crimes = int(np.random.uniform(500, 5000))  # Example dummy prediction
            crime_rate = round(np.random.uniform(0.5, 10.0), 2)
            description = f"Sample description for {community_name}."
            common_crime = primary_crimes[np.random.randint(0, 34)]

            # Replace with actual lat/lon data for each community
            lat = 41.8781 + (np.random.randn() / 100)  # Sample latitude
            lon = -87.6298 + (np.random.randn() / 100)  # Sample longitude

            return Response({
                'name': community_name,
                'total_crimes': total_crimes,
                'crime_rate': crime_rate,
                'description': description,
                'common_crime': common_crime,
                'lat': lat,
                'lon': lon
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Community area not found.'}, status=status.HTTP_404_NOT_FOUND)