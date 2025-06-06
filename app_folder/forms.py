from django.forms import ModelForm
from .models import RequestData
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import (RequestData,
                     ApprovalMst,
                     InfoData,
                     OffDayData,
                     OffdayRequestMst,
                     RequestMst,
                     OffdayKbnMst,
                     InfoConfirm,
                     ImprovementData,
                     SettingMst,
                     ImproveKbnMst,
                     EmployeeMst,
                     )
from django.forms.widgets import CheckboxInput

class RequestForm(ModelForm):
    class Meta:
        model = RequestData
        fields = ["requestID","content","attach"]

class DayoffCreateForm(forms.ModelForm):
    emp_id = forms.ModelChoiceField(
        label="従業員",
        queryset=OffdayRequestMst.objects.all(),#空の選択肢
        widget=forms.widgets.Select,
        required=True,
    )
    class Meta:
        # どのモデルをフォームにするか指定
        model = OffDayData
        # そのフォームの中から表示するフィールドを指定
        fields = ("emp_id","offday_date","end_offday_date","period_id","offday_kbn","content","reason","attach","attach2","attach3")

    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'

class InfoConfirmForm(forms.ModelForm):
    class Meta:
        # どのモデルをフォームにするか指定
        model = InfoConfirm
        # そのフォームの中から表示するフィールドを指定
        fields = ('if_id','content')

    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'

class RequestCreateForm(forms.ModelForm):
    class Meta:
        model = RequestData 
        fields = ("requestID","content","attach","attach2","attach3")
        widgets = {'requestID':forms.Select(attrs={'onchange':'requestCng()'})}
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'
    def clean(self):
        cleaned_data = super().clean()
        requestID = cleaned_data.get("requestID")
        for data in RequestMst.objects.all():
            if data.RequestType == str(requestID):
                if data.needRingi == True:
                    attach = cleaned_data.get("attach")
                    if not attach:
                        raise forms.ValidationError("本申請内容は稟議書が必要な項目です。")
        return cleaned_data
    
class RequestUpdateForm(forms.ModelForm):
    class Meta:
        model = RequestData 
        fields = ("content","attach","attach2","attach3")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'
    
class ApprovalForm(forms.ModelForm):
    class Meta:
        model = RequestData 
        fields = ("approval","approval_content")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'

class LastApprovalForm(forms.ModelForm):
    class Meta:
        model = RequestData 
        fields = ("last_approval","last_approval_content")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'

class ODApprovalForm(forms.ModelForm):
    class Meta:
        model = OffDayData 
        fields = ("approval","approval_content")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'

class ODLastApprovalForm(forms.ModelForm):
    class Meta:
        model = OffDayData 
        fields = ("last_approval","last_approval_content")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'

class InfoForm(forms.ModelForm):
    class Meta:
        model = InfoData 
        fields = ("permission","title","content","attach","image")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, CheckboxInput):
                field.widget.attrs['class'] = 'form-control p-1 m-3'
            else:
                field.widget.attrs['class'] = 'form-check-input p-1 m-1'
            
class ApSearchForm(forms.Form):
    kbn = forms.fields.ChoiceField(
        label=("承認"),
        choices = (
        (0, "未承認"),
        (1, "承認済"),
        (2, "却下"),
        ),
        required=False,
        widget=forms.widgets.Select
    )
    choices =[("0", "------")]
    try:
        choices+=[(i.requestID, i.RequestType) for i in RequestMst.objects.all()]
    except:
        pass  # データベースにアクセスできない初回マイグレーション時の対策
    rkbn = forms.fields.ChoiceField(
        label=("申請区分"),
        choices=choices, #初回ビルド時は削除要
        required=False,
        widget=forms.widgets.Select
    )
    stdt = forms.DateField(
        label=("日時(始)"),
        required=False,
    )
    eddt = forms.DateField(
        label=("日時(終)"),
        required=False,
    )
    mei = forms.CharField(
        label=("申請者氏名"),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
class OdApSearchForm(forms.Form):
    kbn = forms.fields.ChoiceField(
        label=("承認"),
        choices = (
        (0, "未承認"),
        (1, "承認済"),
        (2, "却下"),
        ),
        required=False,
        widget=forms.widgets.Select
    )
    choices =[(0, "------")]
    try:
        choices+=[(i.id, i.kbnmei) for i in OffdayKbnMst.objects.all()]
    except:
        pass  # データベースにアクセスできない初回マイグレーション時の対策
    okbn = forms.fields.ChoiceField(
        label=("勤怠区分"),
        choices=choices, #初回ビルド時は削除要
        required=False,
        widget=forms.widgets.Select
    )
    stdt = forms.DateField(
        label=("日時(始)"),
        required=False,
    )
    eddt = forms.DateField(
        label=("日時(終)"),
        required=False,
    )
    emmei = forms.CharField(
        label=("従業員氏名"),
        required=False,
    )
    mei = forms.CharField(
        label=("申請者氏名"),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
class rqSearchForm(forms.Form):
    choices =[("0", "------")]
    try:
        choices+=[(i.requestID, i.RequestType) for i in RequestMst.objects.all()]
    except:
        pass  # データベースにアクセスできない初回マイグレーション時の対策
    kbn = forms.fields.ChoiceField(
        label=("申請区分"),
        choices=choices, #初回ビルド時は削除要
        required=False,
        widget=forms.widgets.Select
    )
    stdt = forms.DateField(
        label=("日時(始)"),
        required=False,
    )
    eddt = forms.DateField(
        label=("日時(終)"),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
class rqSearchForm2(forms.Form):
    choices =[("0", "------")]
    try:
        choices+=[(i.requestID, i.RequestType) for i in RequestMst.objects.all()]
    except:
        pass  # データベースにアクセスできない初回マイグレーション時の対策
    kbn = forms.fields.ChoiceField(
        label=("申請区分"),
        choices=choices, #初回ビルド時は削除要
        required=False,
        widget=forms.widgets.Select
    )
    stdt = forms.DateField(
        label=("日時(始)"),
        required=False,
    )
    eddt = forms.DateField(
        label=("日時(終)"),
        required=False,
    )
    no = forms.CharField(
        label=("承認番号"),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
class odSearchForm(forms.Form):
    # kbn = forms.fields.ChoiceField(
    #     label=("勤怠区分"),
    #     choices=[(i.id, i.kbnmei) for i in OffdayKbnMst.objects.all()], #初回ビルド時は削除要
    #     required=False,
    #     widget=forms.widgets.Select
    # )
    choices =[(0, "------")]
    try:
        choices+=[(i.id, i.kbnmei) for i in OffdayKbnMst.objects.all()]
    except:
        pass  # データベースにアクセスできない初回マイグレーション時の対策
    
    kbn = forms.fields.ChoiceField(
        label=("勤怠区分"),
        choices=choices, #初回ビルド時は削除要
        required=False,
        widget=forms.widgets.Select
    )
    stdt = forms.DateField(
        label=("日時(始)"),
        required=False,
    )
    eddt = forms.DateField(
        label=("日時(終)"),
        required=False,
    )
    istdt = forms.DateField(
        label=("更新日時(始)"),
        required=False,
    )
    ieddt = forms.DateField(
        label=("更新日時(終)"),
        required=False,
    )
    mei = forms.CharField(
        label=("氏名"),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ImprovementCreateForm(forms.ModelForm):
    class Meta:
        model = ImprovementData 
        fields = ("emp_id","kbn_id","ttl","content","attach")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'
    
from django import forms
from .models import EmployeeMst

class OpinionCreateForm(forms.Form):
    # EmployeeMst から選択肢を取得
    choices = [(0, "匿名希望")]
    try:
        choices += [(i.id, i.emmei) for i in EmployeeMst.objects.all()]
    except:
        pass  # データベースにアクセスできない初回マイグレーション時の対策

    mei = forms.ChoiceField(
        label="氏名",
        choices=choices,
        required=False,
        widget=forms.Select
    )
    content = forms.CharField(
        label="メッセージ", 
        widget=forms.Textarea(attrs={"rows": 4, "cols": 50}),
        required=True
    )
    class Meta:
        fields = ("pw","mei","content")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'
    
class impSearchForm(forms.Form):
    choices =[(0, "------")]
    try:
        choices+=[(i.id, i.kbnmei) for i in ImproveKbnMst.objects.all()]
    except:
        pass  # データベースにアクセスできない初回マイグレーション時の対策
    kbn = forms.fields.ChoiceField(
        label=("カテゴリ"),
        choices=choices, #初回ビルド時は削除要
        required=False,
        widget=forms.widgets.Select
    )
    stdt = forms.DateField(
        label=("日時(始)"),
        required=False,
    )
    eddt = forms.DateField(
        label=("日時(終)"),
        required=False,
    )
    mei = forms.CharField(
        label=("氏名"),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ImpUp1Form(forms.ModelForm):
    class Meta:
        model = ImprovementData 
        fields = ("answer","Importance","priority")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'
            
class ImpUp2Form(forms.ModelForm):
    class Meta:
        model = ImprovementData 
        fields = ("emp_id","kbn_id","ttl","content","attach")
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'
            
class CSVUploadForm(forms.Form):
    file = forms.FileField(label="CSVファイルを選択", required=True)
    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control p-1 m-3'
    