from django.contrib import admin
from django.contrib.auth.models import Group
from .models import (RequestMst, 
                     ApprovalMst, 
                     RequestData, 
                     OffdayRequestMst, 
                     InfoData, 
                     OffDayData,
                     OffdayKbnMst,
                     PeriodMst,
                     SeqMst,
                     SettingMst,
                     ImproveKbnMst,
                     EmployeeMst,
                     ) # models.pyで指定したクラス名
class OffDayAdmin(admin.ModelAdmin):
    model = OffdayRequestMst
    list_display  = ["u_id", "emmei"]

class OffDayDataAdmin(admin.ModelAdmin):
    model = OffDayData
    list_display  = ["usermei", "emp_id", "offday_kbn", "offday_date"]

class reqAdmin(admin.ModelAdmin):
    model = RequestData
    list_display  = ["requestID", "usermei", "ReqDate"]

class ApprovalAdmin(admin.ModelAdmin):
    model = ApprovalMst
    list_display  = ["umei", "apmei", "lsmei"]

admin.site.register(ImproveKbnMst) # models.pyで指定したクラス名
admin.site.register(EmployeeMst) # models.pyで指定したクラス名
admin.site.register(SettingMst) # models.pyで指定したクラス名
admin.site.register(SeqMst) # models.pyで指定したクラス名
admin.site.register(RequestMst) # models.pyで指定したクラス名
admin.site.register(ApprovalMst, ApprovalAdmin) # models.pyで指定したクラス名
admin.site.register(RequestData, reqAdmin) # models.pyで指定したクラス名
admin.site.register(OffdayRequestMst, OffDayAdmin) # models.pyで指定したクラス名
admin.site.register(InfoData) # models.pyで指定したクラス名
admin.site.register(OffDayData, OffDayDataAdmin) # models.pyで指定したクラス名
admin.site.register(OffdayKbnMst) # models.pyで指定したクラス名
admin.site.register(PeriodMst) # models.pyで指定したクラス名
admin.site.unregister(Group) 