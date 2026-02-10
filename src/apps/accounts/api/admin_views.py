from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.models import User, AuditLog
from apps.accounts.permissions import IsAdmin
from apps.core.api.messages import MESSAGES
from apps.core.api.utils import api_response


class AdminAgentsListAPIView(APIView):
    """
    API لإرجاع قائمة الوكلاء (للإدارة)
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        agents = User.objects.filter(role='AGENT').values(
            'id',
            'username',
            'is_active'
        )

        return api_response(
            code='SUCCESS',
            message=MESSAGES['SUCCESS'],
            http_status=status.HTTP_200_OK,
            data=list(agents)
        )


class ToggleAgentStatusAPIView(APIView):
    """
    API لتفعيل / إيقاف وكيل
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, agent_id):
        try:
            agent = User.objects.get(id=agent_id, role='AGENT')
        except User.DoesNotExist:
            return api_response(
                code='AGENT_NOT_FOUND',
                message=MESSAGES['AGENT_NOT_FOUND'],
                http_status=status.HTTP_404_NOT_FOUND
            )

        agent.is_active = not agent.is_active
        agent.save()

        if agent.is_active:
            action = 'ACTIVATE_AGENT'
            msg_code = 'AGENT_ACTIVATED'
        else:
            action = 'SUSPEND_AGENT'
            msg_code = 'AGENT_SUSPENDED'

        # 🧾 Audit Log
        AuditLog.objects.create(
            actor=request.user,
            action=action,
            target_user=agent,
            message=f'تم {"تفعيل" if agent.is_active else "إيقاف"} الوكيل عبر API: {agent.username}'
        )

        return api_response(
            code=msg_code,
            message=MESSAGES[msg_code],
            http_status=status.HTTP_200_OK
        )
