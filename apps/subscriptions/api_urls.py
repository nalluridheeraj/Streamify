from django.urls import path
from rest_framework import serializers, generics, permissions
from .models import Plan, Subscription
from django.utils import timezone


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class PlanListAPIView(generics.ListAPIView):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'plan_name', 'status', 'start_date', 'end_date', 'auto_renew']
        read_only_fields = ['status', 'start_date', 'end_date']


class MySubscriptionAPIView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscriptions.all()


urlpatterns = [
    path('plans/', PlanListAPIView.as_view(), name='api_plans'),
    path('my/', MySubscriptionAPIView.as_view(), name='api_my_subscription'),
]
