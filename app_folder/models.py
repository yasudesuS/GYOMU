from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid


class RequestMst(models.Model):
    class Meta:
        db_table = 'RequestMst' # DB内で使用するテーブル名
        verbose_name_plural = '申請マスタ' # Admionサイトで表示するテーブル名
    requestID = models.CharField('項目ID', max_length=5,primary_key=True,null=False, blank=True)
    RequestType = models.CharField('申請項目名', max_length=255, null=True, blank=True) # 文字列を格納
    needMeeting = models.BooleanField('要会議招集',default=False)
    needRingi = models.BooleanField('要稟議書',default=False)
    chkJimu = models.BooleanField('要事務所確認',default=False)
    del_flg = models.BooleanField(
        verbose_name=_("削除フラグ"),
        default=False
    )
    def __str__(self):
        return self.RequestType

class RequestData(models.Model):
    choice_ap = (
        (0, "未承認"),
        (1, "承認済"),
        (2, "却下"),
    )

    class Meta:
        db_table = 'RequestData' # DB内で使用するテーブル名
        verbose_name_plural = '申請データ' # Admionサイトで表示するテーブル名
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requestID = models.ForeignKey(
        RequestMst,
        on_delete=models.SET_NULL,
        verbose_name='申請項目',
        null=True,
        blank=False,
    )
    rq_account_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    ) 
    usermei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    user_email = models.EmailField(
        null=True,
        blank=True
    )
    ReqDate = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True)
    content = models.TextField(
        verbose_name='内容',
        null=True,
        blank=True,
    )
    attach = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='添付ファイル',
        null=True,
        blank=True,
    )
    approval_id = models.IntegerField(
        null=True,
        blank=True
    )
    apmei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    ap_email = models.EmailField(
        null=True,
        blank=True
    )
    approval_content = models.TextField(
        verbose_name=_("コメント"),
        null=True,
        blank=True,        
    )
    approval = models.IntegerField(
        verbose_name=_("承認"),
        default=0,
        choices=choice_ap,        
    )
    approval_read = models.BooleanField(default=False)
    last_approval_id = models.IntegerField(
        null=True,
        blank=True
    )
    lsmei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    ls_email = models.EmailField(
        null=True,
        blank=True
    )
    last_approval_content = models.TextField(
        verbose_name=_("コメント"),
        null=True,
        blank=True,
    )
    last_approval = models.IntegerField(
        verbose_name=_("最終承認"),
        default=0,
        choices=choice_ap,        
    )
    last_read = models.BooleanField(default=False)
    withdrawal = models.BooleanField(default=False)
    withdrawal_id = models.IntegerField(
        verbose_name=_("最終承認者"),
        null=True,
        blank=True
    )
    attach2 = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='添付ファイル',
        null=True,
        blank=True,
    )
    attach3 = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='添付ファイル',
        null=True,
        blank=True,
    )
    ap_no = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )
    chkJimu = models.BooleanField('要事務所確認',default=False)
    def __str__(self):
        return self.usermei

class ApprovalMst(models.Model):
    choices=[(i.id, i.first_name) for i in User.objects.all()]
    class Meta:
        db_table = 'ApprovalMst' # DB内で使用するテーブル名
        verbose_name_plural = '承認者マスタ' # Admionサイトで表示するテーブル名
    userid = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("ユーザー"),
        primary_key=True,
        unique=True,
        max_length=10,
    )
    umei = models.CharField(
        verbose_name=_("氏名"),
        max_length=40,
        null=True,
        blank=True
    )
    approval_id = models.IntegerField(
        verbose_name=_("承認者"),
        null=True,
        choices=choices,        
        blank=True
    )
    apmei = models.CharField(
        verbose_name=_("承認者氏名"),
        max_length=40,
        null=True,
        blank=True
    )
    ap_email = models.EmailField(
        verbose_name=_("承認者email"),
        null=True,
        blank=True
    )
    last_approval_id = models.IntegerField(
        verbose_name=_("最終承認者"),
        null=True,
        choices=choices,        
        blank=True
    )
    lsmei = models.CharField(
        verbose_name=_("最終承認者氏名"),
        max_length=40,
        null=True,
        blank=True
    )
    last_email = models.EmailField(
        verbose_name=_("最終承認email"),
        null=True,
        blank=True
    )
    del_flg = models.BooleanField(
        verbose_name=_("削除フラグ"),
        default=False
    )
    def __str__(self):
        return self.umei

class InfoData(models.Model):
    class Meta:
        db_table = 'InfoData' # DB内で使用するテーブル名
        verbose_name_plural = '案内データ' # Admionサイトで表示するテーブル名
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    if_account_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False, 
        blank=True
    ) 
    usermei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    user_email = models.EmailField(
        null=True,
        blank=True
    )
    ReqDate = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True)
    title = models.CharField(
        max_length=60,
        null=True,
        blank=False,
    )
    content = models.TextField(
        verbose_name='内容',
        null=True,
        blank=False,
    )
    attach = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='添付ファイル',
        null=True,
        blank=True,
    )
    permission = models.BooleanField(
        verbose_name='全従業員閲覧可',
        default=False
        )
    image = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='画像添付',
        null=True,
        blank=True,
    )
    pdf = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='PDF添付',
        null=True,
        blank=True,
    )
    def __str__(self):
        return self.title

class DepartmentMst(models.Model):
    class Meta:
        db_table = 'DepartmentMst' # DB内で使用するテーブル名
        verbose_name_plural = '部署マスタ' # Admionサイトで表示するテーブル名
    dmei = models.CharField(
        verbose_name=_("部署名"),
        max_length=40,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.dmei

class EmployeeMst(models.Model):
    class Meta:
        db_table = 'EmployeeMst' # DB内で使用するテーブル名
        verbose_name_plural = '従業員マスタ' # Admionサイトで表示するテーブル名
    emmei = models.CharField(
        verbose_name=_("従業員名"),
        max_length=40,
        null=True,
        blank=True
    )
    d_id = models.ForeignKey(
        DepartmentMst,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    ) 
    email = models.EmailField(
        null=True,
        blank=True
    )
    del_flg = models.BooleanField(
        verbose_name=_("削除フラグ"),
        default=False
    )
    def __str__(self):
        return self.emmei

class OffdayRequestMst(models.Model):
    class Meta:
        db_table = 'OffdayRequestMst' # DB内で使用するテーブル名
        verbose_name_plural = '勤怠申請対象者マスタ' # Admionサイトで表示するテーブル名
    u_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_("勤怠申請者"),
        null=True, 
        blank=True
    ) 
    emmei = models.CharField(
        verbose_name=_("従業員名"),
        max_length=40,
        null=True,
        blank=True
    )
    del_flg = models.BooleanField(
        verbose_name=_("削除フラグ"),
        default=False
    )
    def __str__(self):
        return self.emmei

class PeriodMst(models.Model):
    class Meta:
        db_table = 'PeriodMst' # DB内で使用するテーブル名
        verbose_name_plural = '期間マスタ' # Admionサイトで表示するテーブル名
    period = models.CharField(
        verbose_name=_("期間"),
        max_length=40,
        null=True,
        blank=True
    )
    del_flg = models.BooleanField(
        verbose_name=_("削除フラグ"),
        default=False
    )
    def __str__(self):
        return self.period

class OffdayKbnMst(models.Model):
    class Meta:
        db_table = 'OffdayKbnMst' # DB内で使用するテーブル名
        verbose_name_plural = '勤怠区分マスタ' # Admionサイトで表示するテーブル名
    kbnmei = models.CharField(
        verbose_name=_("勤怠区分"),
        max_length=40,
        null=True,
        blank=True
    )
    del_flg = models.BooleanField(
        verbose_name=_("削除フラグ"),
        default=False
    )
    def __str__(self):
        return self.kbnmei

class OffDayData(models.Model):
    choice_ap = (
        (0, "未承認"),
        (1, "承認済"),
        (2, "却下"),
    )

    class Meta:
        db_table = 'OffDayData' # DB内で使用するテーブル名
        verbose_name_plural = '勤怠申請データ' # Admionサイトで表示するテーブル名
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    od_account_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    ) 
    usermei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    user_email = models.EmailField(
        null=True,
        blank=True
    )
    emp_id = models.ForeignKey(
        OffdayRequestMst,
        on_delete=models.SET_NULL,
        verbose_name=_("従業員"),
        null=True, 
        blank=True
    ) 
    period_id = models.ForeignKey(
        PeriodMst,
        on_delete=models.SET_NULL,
        verbose_name=_("期間"),
        null=True, 
        blank=True
    ) 
    offday_kbn = models.ForeignKey(
        OffdayKbnMst,
        on_delete=models.SET_NULL,
        verbose_name=_("勤怠区分"),
        null=True, 
        blank=True
    ) 
    ReqDate = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True)
    offday_date = models.DateField(
        verbose_name=_("日時"),
        blank=False,
        null=False,
    )
    content = models.TextField(
        verbose_name=_("備考"),
        null=True,
        blank=True,
    )
    reason = models.TextField(
        verbose_name=_("理由"),
        null=True,
        blank=True,
    )
    approval_id = models.IntegerField(
        null=True,
        blank=True
    )
    apmei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    ap_email = models.EmailField(
        null=True,
        blank=True
    )
    approval_content = models.TextField(
        verbose_name=_("コメント"),
        null=True,
        blank=True,        
    )
    approval = models.IntegerField(
        verbose_name=_("承認"),
        default=0,
        choices=choice_ap,        
    )
    approval_read = models.BooleanField(default=False)
    last_approval_id = models.IntegerField(
        null=True,
        blank=True
    )
    lsmei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    ls_email = models.EmailField(
        null=True,
        blank=True
    )
    last_approval_content = models.TextField(
        verbose_name=_("コメント"),
        null=True,
        blank=True,
    )
    last_approval = models.IntegerField(
        verbose_name=_("最終承認"),
        default=0,
        choices=choice_ap,        
    )
    attach = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='添付ファイル',
        null=True,
        blank=True,
    )
    end_offday_date = models.DateField(
        verbose_name=_("日時(至)"),
        blank=True,
        null=True,
    )
    attach2 = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='添付ファイル',
        null=True,
        blank=True,
    )
    attach3 = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='添付ファイル',
        null=True,
        blank=True,
    )
    ap_no = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )
    emp_mei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.usermei

class InfoConfirm(models.Model):
    class Meta:
        db_table = 'InfoConfirm' # DB内で使用するテーブル名
        verbose_name_plural = '案内確認' # Admionサイトで表示するテーブル名
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    if_id = models.ForeignKey(
        InfoData,
        on_delete=models.CASCADE,
        null=False, 
        blank=True
    ) 
    if_account_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    ) 
    usermei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    ReqDate = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True)
    content = models.TextField(
        verbose_name='コメント',
        null=True,
        blank=True,
    )
    def __str__(self):
        return self.title

class SeqMst(models.Model):
    class Meta:
        db_table = 'SeqMst' # DB内で使用するテーブル名
        verbose_name_plural = 'シーケンスマスタ' # Admionサイトで表示するテーブル名
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    approval_no = models.IntegerField(
        verbose_name=_("申請承認番号"),
        default=0,
    )
    offday_ap_no = models.IntegerField(
        verbose_name=_("勤怠承認番号"),
        default=0,
    )
    imp_no = models.IntegerField(
        verbose_name=_("改善提案番号"),
        default=0,
    )

class SettingMst(models.Model):
    class Meta:
        db_table = 'SettingMst' # DB内で使用するテーブル名
        verbose_name_plural = '設定マスタ' # Admionサイトで表示するテーブル名
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host_email = models.EmailField(
        verbose_name=_("ホストメールアドレス"),
        null=True,
        blank=True
    )
    request_email = models.EmailField(
        verbose_name=_("申請承認済宛先"),
        null=True,
        blank=True
    )
    offday_email = models.EmailField(
        verbose_name=_("勤怠承認済宛先"),
        null=True,
        blank=True
    )
    ap_digit = models.IntegerField(
        verbose_name=_("承認番号桁"),
        default=0,
    )
    ap_str = models.CharField(
       verbose_name=_("申請承認附番"),
        max_length=2,
        null=True,
        blank=True
    )
    od_str = models.CharField(
       verbose_name=_("勤怠承認附番"),
        max_length=2,
        null=True,
        blank=True
    )
    send_pass = models.CharField(
        verbose_name=_("改善提案パスワード"),
        max_length=8,
        null=True,
        blank=True
    )
    imp_str = models.CharField(
       verbose_name=_("改善提案附番"),
        max_length=2,
        null=True,
        blank=True
    )
    opinion_email = models.EmailField(
        verbose_name=_("意見箱宛先"),
        null=True,
        blank=True
    )
    employees_email = models.EmailField(
        verbose_name=_("従業員宛先"),
        null=True,
        blank=True
    )
    manager_email = models.EmailField(
        verbose_name=_("管理者宛先"),
        null=True,
        blank=True
    )

class ImproveKbnMst(models.Model):
    class Meta:
        db_table = 'ImproveKbnMst' # DB内で使用するテーブル名
        verbose_name_plural = '改善提案区分マスタ' # Admionサイトで表示するテーブル名
    kbnmei = models.CharField(
        verbose_name=_("カテゴリー"),
        max_length=40,
        null=True,
        blank=True
    )
    del_flg = models.BooleanField(
        verbose_name=_("削除フラグ"),
        default=False
    )
    def __str__(self):
        return self.kbnmei

class ImprovementData(models.Model):
    choice_ap = (
        (0, "　"),
        (1, "低"),
        (2, "中"),
        (3, "高"),
    )

    class Meta:
        db_table = 'ImprovementData' # DB内で使用するテーブル名
        verbose_name_plural = '改善提案データ' # Admionサイトで表示するテーブル名
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emp_id = models.ForeignKey(
        EmployeeMst,
        on_delete=models.SET_NULL,
        verbose_name=_("氏名"),
        null=True, 
        blank=False
    ) 
    emp_mei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    emp_email = models.EmailField(
        null=True,
        blank=True
    )
    kbn_id = models.ForeignKey(
        ImproveKbnMst,
        on_delete=models.SET_NULL,
        verbose_name=_("カテゴリー"),
        null=True, 
        blank=False
    ) 
    ReqDate = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True)
    ttl = models.CharField(
        verbose_name=_("題名"),
        max_length=40,
        null=True,
        blank=False
    )
    content = models.TextField(
        verbose_name=_("内容"),
        null=True,
        blank=False,
    )
    answer_id = models.IntegerField(
        verbose_name=_("回答者"),
        null=True,
        blank=True
    )
    ans_mei = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    answer_email = models.EmailField(
        null=True,
        blank=True
    )
    answer = models.TextField(
        verbose_name=_("コメント"),
        null=True,
        blank=True,        
    )
    Importance = models.IntegerField(
        verbose_name=_("重要度"),
        default=0,
        choices=choice_ap,        
    )
    priority = models.IntegerField(
        verbose_name=_("優先度"),
        default=0,
        choices=choice_ap,        
    )
    attach = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='添付ファイル',
        null=True,
        blank=True,
    )
    imp_no = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.usermei

