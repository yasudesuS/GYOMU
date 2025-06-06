from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now
from app_folder.models import RequestData, User, OffDayData
from app_folder import views

class Command(BaseCommand):
    help = "最終承認者に未承認のデータ件数を通知"

    def handle(self, *args, **kwargs):
        # 最終承認がまだ行われていない申請を取得
        unapproved_count = RequestData.objects.filter(last_approval=0,approval=1).count()
        unoffdayap_count = OffDayData.objects.filter(last_approval=0,approval=1).count()

        hostmail = views.getHostAdress()
        opmail = views.getOpinionAdress()

        # メール送信
        subject = "【重要】未承認の申請について"
        message = (f"現在、{unapproved_count} 件の申請が最終承認待ちです。\n\n"
                    f"現在、{unoffdayap_count} 件の勤怠が最終承認待ちです。\n\n"
                "http://xs332906.xsrv.jp/app_folder/bulk_update_offday/"
        )

        # メール送信
        send_mail(
            subject,
            message,
            hostmail, 
            [opmail],
            fail_silently=False,
        )

        self.stdout.write(self.style.SUCCESS(f"通知メールを 送信しました。未承認: {unapproved_count} 件"))
