import io
import re
# import openpyxl  # pip install openpyxl
# from openpyxl.styles import Border, Side, PatternFill, Font, Alignment
import csv
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import datetime
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.contrib import messages
from django.db import transaction
from django.utils.timezone import now,make_aware

from app_folder.const import constant_text
# from django.utils import timezone
# from django.http import HttpResponse
# from django.template.loader import get_template
# from django.shortcuts import get_object_or_404
# from xhtml2pdf import pisa
# from django.utils.html import linebreaks

# モデルおよびフォームのインポート（実際のフィールド定義・バリデーション内容は別ファイルに記述）
from .models import (ImproveKbnMst, OffdayKbnMst, PeriodMst,
                     RequestData, 
                     ApprovalMst, 
                     InfoData, 
                     OffDayData, 
                     OffdayRequestMst,
                     RequestMst,
                     InfoConfirm,
                     SeqMst,
                     SettingMst,
                     ImprovementData,
                     EmployeeMst,
                     )
from .forms import (DayoffCreateForm, OpinionCreateForm,
                    RequestCreateForm, 
                    ApprovalForm, 
                    LastApprovalForm, 
                    ODApprovalForm, 
                    ODLastApprovalForm, 
                    InfoForm,
                    ApSearchForm, RequestUpdateForm, impSearchForm,
                    odSearchForm,
                    OdApSearchForm,
                    rqSearchForm,
                    InfoConfirmForm,
                    rqSearchForm2,
                    ImprovementCreateForm, 
                    ImpUp1Form,
                    ImpUp2Form,
                    CSVUploadForm,
                    )
#定数
emp_id = 20 #使いまわし従業員ID

# ──────────────────────────────────────────────────────────────#
# ログアウトおよび基本画面表示
# ──────────────────────────────────────────────────────────────#

def logout_view(request):
    # Django 標準のログアウト処理。ユーザーセッションを削除する
    logout(request)
    return redirect("login")  # ログインページへリダイレクト

def meetingroom(request):
    # ユーザー認証がなければログインページへリダイレクト
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    return render(request, "app_folder/meetingroom.html")  # 会議室画面をレンダリング

def diningroom(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    return render(request, "app_folder/diningroom.html")

def calendar(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    return render(request, "app_folder/calendar.html")

def message(request):
    # このビューは認証チェックを行っていない（必要なら追加する）
    return render(request, "app_folder/message.html")

def top_listing(request):
    # 掲示板（お知らせ）の一覧表示。更新日時の降順に並べ、ページネーションを適用
    contact_list = InfoData.objects.all().order_by('-update_at')
    if request.user.id == emp_id:
        contact_list = InfoData.objects.all().filter(permission=True).order_by('-update_at')
    paginator = Paginator(contact_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    return render(request, "app_folder/top_page.html", {"page_obj": page_obj})


# ──────────────────────────────────────────────────────────────#
# 申請ワークフロー関連のビュー
# ──────────────────────────────────────────────────────────────#

class RequestListView(LoginRequiredMixin, ListView):
    template_name = 'app_folder/request_list2.html'
    model = RequestData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        # 現在のユーザーが作成した申請のみをフィルタリング
        queryset = queryset.filter(rq_account_id=self.request.user.id).order_by('-update_at')
        if self.request.GET.get('kbn'):
            if self.request.GET.get('kbn') != "0":
                # リクエストパラメータ「kbn」に基づく申請種別フィルタ
                queryset = queryset.filter(requestID=self.request.GET.get('kbn'))
            if self.request.GET.get('stdt'):
                # 開始日フィルタ：指定日以降の申請
                queryset = queryset.filter(ReqDate__gt=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                # 終了日フィルタ：年月日を分割してフィルタリング（※処理の単純化のために改善の余地あり）
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')+ datetime.timedelta(days=1)
                queryset = queryset.filter(ReqDate__lte=eddt)
        else:
            queryset = queryset.none()  
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 検索フォームの初期値としてGETパラメータを利用
        context['search_form'] = rqSearchForm(self.request.GET)
        return context

    def get(self, request):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)

request_list2 = RequestListView.as_view()

class RequestListView3(LoginRequiredMixin, ListView):
    template_name = 'app_folder/request_list3.html'
    model = RequestData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        # 中間承認済み（last_approval=1）かつ事務チェック済み(chkJimu=True)の申請のみ
        queryset = queryset.filter(last_approval=1, chkJimu=True).order_by('-update_at')
        if self.request.GET.get('kbn'):
            if self.request.GET.get('kbn') != "0":
                queryset = queryset.filter(requestID=self.request.GET.get('kbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(ReqDate__gt=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')+ datetime.timedelta(days=1)
                queryset = queryset.filter(ReqDate__lte=eddt)
            if self.request.GET.get('no'):
                # 承認番号など、特定の文字列が含まれるかでフィルタリング
                queryset = queryset.filter(ap_no__contains=self.request.GET.get('no'))
        else:
            queryset = queryset.none() 
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = rqSearchForm2(self.request.GET)
        return context

    def get(self, request):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)

request_list3 = RequestListView3.as_view()

def request_listing(request):
    # ページネーション付きの申請一覧（ユーザー自身の申請）
    contact_list = RequestData.objects.filter(rq_account_id=request.user.id).order_by('-update_at')
    paginator = Paginator(contact_list, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    if request.user.id == emp_id:
        return redirect(reverse_lazy('app_folder:top_page'))
    return render(request, "app_folder/request_list.html", {"page_obj": page_obj})

class RequestDetail(LoginRequiredMixin, DetailView):
    template_name = 'app_folder/request_detail.html'
    model = RequestData

request_detail = RequestDetail.as_view()

class RequestCreate(LoginRequiredMixin, CreateView):
    template_name = 'app_folder/request_create.html'
    model = RequestData
    form_class = RequestCreateForm
    success_url = reverse_lazy('app_folder:request_list')

    def get(self, request, **kwargs):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        form = RequestCreateForm()
        # 現在のユーザーに関連するOffdayRequestMstをフィルタリングして選択肢を設定
        form.fields['requestID'].queryset = RequestMst.objects.all().filter(del_flg=False)
        datas = {'form': form}
        return render(self.request, self.template_name, datas)

    def form_valid(self, form):
        hostmail = getHostAdress()  # 補助関数でホストメールアドレスを取得
        instance = form.save(commit=False)  # ※変数名 "object" はビルトインと衝突するため、instance とするのが望ましい
        # 申請者情報の設定
        instance.rq_account_id = User.objects.get(id=self.request.user.id)
        instance.usermei = self.request.user.first_name
        instance.user_email = self.request.user.email
        # 承認者情報の取得
        approval = ApprovalMst.objects.get(userid=User.objects.get(id=self.request.user.id))
        if approval.approval_id:
            instance.approval_id = approval.approval_id
            instance.apmei = approval.apmei
            instance.ap_email = approval.ap_email
        instance.last_approval_id = approval.last_approval_id
        instance.lsmei = approval.lsmei
        instance.ls_email = approval.last_email
        # 添付ファイル有無のフラグ設定
        tempstr = 'あり' if instance.attach else 'なし'
        # 申請種別（RequestMst）に応じた各種属性設定
        rqMst = RequestMst.objects.get(RequestType=str(instance.requestID))
        instance.chkJimu = rqMst.chkJimu
        msgmeeting = ''
        ttlmeeting = ''
        # if rqMst.needMeeting:
        #     msgmeeting = "本申請内容は会議招集が必要な項目です。関係者に対して会議招集を行ってください。"
        #     ttlmeeting = "。本申請内容は会議招集が必要な項目です"
        # # メール通知用コンテキストを生成
        # context = {
        #     "msg": "以下の通り申請ワークフローが送信され、回覧・承認が行われております。",
        #     "msg2": msgmeeting,
        #     "title": str(instance.requestID),
        #     "usermei": instance.usermei,
        #     "date": datetime.datetime.now,
        #     "attach": tempstr,
        #     "content": instance.content,
        #     "url": "http://" + self.request.META.get("HTTP_HOST") +
        #            "/app_folder/request_detail/" + str(instance.uuid),
        # }
        # html_content = render_to_string("mailer/base.html", context)
        # text_content = strip_tags(html_content)
        # # 申請者へメール通知
        # send_mail("申請ワークフローが送信されました" + ttlmeeting,
        #           text_content,
        #           hostmail,
        #           [instance.user_email],
        #           fail_silently=False)
        if not instance.approval_id:
            instance.approval = 1
            # 最終承認者へメール通知
            context = {
                "msg": "以下の通り申請ワークフローが送信されました、最終承認者として承認・取り下げを行ってください。",
                "title": str(instance.requestID),
                "usermei": instance.usermei,
                "date": datetime.datetime.now,
                "attach": tempstr,
                "content": instance.content,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/last_approval_detail/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/base.html", context)
            text_content = strip_tags(html_content)
            send_mail("申請ワークフローが届いています",
                      text_content,
                      hostmail,
                      [instance.ls_email],
                      fail_silently=False)
        else:
            # 中間承認者へメール通知
            context = {
                "msg": "以下の通り申請ワークフローが送信されました、中間承認者として承認・取り下げを行ってください。",
                "title": str(instance.requestID),
                "usermei": instance.usermei,
                "date": datetime.datetime.now,
                "attach": tempstr,
                "content": instance.content,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/approval_detail/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/base.html", context)
            text_content = strip_tags(html_content)
            send_mail("申請ワークフローが届いています",
                      text_content,
                      hostmail,
                      [instance.ap_email],
                      fail_silently=False)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 申請種別（RequestMst）の情報をテンプレートに渡す
        context['reqmst'] = RequestMst.objects.all()
        return context

request_create = RequestCreate.as_view()

class RequestDelete(LoginRequiredMixin, DeleteView):
    template_name = 'app_folder/request_delete.html'
    model = RequestData
    success_url = reverse_lazy('app_folder:request_list')
    
request_delete = RequestDelete.as_view()

class RequestUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'app_folder/request_update.html'
    model = RequestData
    form_class = RequestUpdateForm
    success_url = reverse_lazy('app_folder:request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reqmst'] = RequestMst.objects.all()
        return context

    def form_valid(self, form):
        hostmail = getHostAdress()
        instance = form.save(commit=False)
        tempstr = 'あり' if instance.attach else 'なし'
        msgmeeting = ''
        ttlmeeting = ''
        # if rqMst.needMeeting:
        #     msgmeeting = "本申請内容は会議招集が必要な項目です。関係者に対して会議招集を行ってください。"
        #     ttlmeeting = "。本申請内容は会議招集が必要な項目です"
        # context = {
        #     "msg": "以下の通り申請ワークフローが送信され、回覧・承認が行われております。",
        #     "msg2": msgmeeting,
        #     "title": str(instance.requestID),
        #     "usermei": instance.usermei,
        #     "date": datetime.datetime.now,
        #     "attach": tempstr,
        #     "content": instance.content,
        #     "url": "http://" + self.request.META.get("HTTP_HOST") +
        #            "/app_folder/request_detail/" + str(instance.uuid),
        # }
        # html_content = render_to_string("mailer/base.html", context)
        # text_content = strip_tags(html_content)
        # send_mail("申請ワークフローが送信されました" + ttlmeeting,
        #           text_content,
        #           hostmail,
        #           [instance.user_email],
        #           fail_silently=False)
        if not instance.approval_id:
            instance.approval = 1
            context = {
                "msg": "以下の通り申請ワークフローが送信されました、最終承認者として承認・取り下げを行ってください。",
                "title": str(instance.requestID),
                "usermei": instance.usermei,
                "date": datetime.datetime.now,
                "attach": tempstr,
                "content": instance.content,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/last_approval_detail/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/base.html", context)
            text_content = strip_tags(html_content)
            send_mail("申請ワークフローが届いています",
                      text_content,
                      hostmail,
                      [instance.ls_email],
                      fail_silently=False)
        else:
            context = {
                "msg": "以下の通り申請ワークフローが送信されました、中間承認者として承認・取り下げを行ってください。",
                "title": str(instance.requestID),
                "usermei": instance.usermei,
                "date": datetime.datetime.now,
                "attach": tempstr,
                "content": instance.content,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/approval_detail/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/base.html", context)
            text_content = strip_tags(html_content)
            send_mail("申請ワークフローが届いています",
                      text_content,
                      hostmail,
                      [instance.ap_email],
                      fail_silently=False)
        return super().form_valid(form)

request_update = RequestUpdate.as_view()


# ──────────────────────────────────────────────────────────────#
# 承認処理関連のビュー
# ──────────────────────────────────────────────────────────────#

class ApprovalListView(LoginRequiredMixin, ListView):
    template_name = 'app_folder/approval_list.html'
    model = RequestData

    def get(self, request):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)
    
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        # 現在のユーザーが中間承認者として担当する申請のみ
        queryset = queryset.filter(approval_id=self.request.user.id).order_by('-update_at')
        if self.request.GET.get('kbn'):
            queryset = queryset.filter(approval=self.request.GET.get('kbn'))
            if self.request.GET.get('rkbn'):
                if self.request.GET.get('rkbn') != "0":
                    queryset = queryset.filter(requestID=self.request.GET.get('rkbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(ReqDate__gt=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')+ datetime.timedelta(days=1)
                queryset = queryset.filter(ReqDate__lte=eddt)
            if self.request.GET.get('mei'):
                queryset = queryset.filter(usermei__contains=self.request.GET.get('mei'))
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ApSearchForm(self.request.GET)
        return context

approval_list = ApprovalListView.as_view()

class ApprovalDetail(LoginRequiredMixin, DetailView):
    template_name = 'app_folder/approval_detail.html'
    model = RequestData

approval_detail = ApprovalDetail.as_view()

class ApprovalUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'app_folder/approval_update.html'
    model = RequestData
    form_class = ApprovalForm
    success_url = reverse_lazy('app_folder:approval_list')

    def form_valid(self, form):
        hostmail = getHostAdress()
        instance = form.save(commit=False)
        tempstr = 'あり' if instance.attach else 'なし'
        # 承認状態に応じたメッセージ設定
        rmsg = ""
        rttl = ""
        # if instance.approval == 1:
        #     rmsg = ("以下の通り申請ワークフローでの申請内容が中間承認者によって承認されましたので報告致します。"
        #             "引き続き、最終承認者にて回覧・承認が行われます。")
        #     rttl = "申請内容が中間承認者によって承認されました"
        # elif instance.approval == 2:
        if instance.approval == 2:
            rmsg = "以下の通り申請ワークフローでの申請内容が中間承認者によって却下されましたので報告致します。"
            rttl = "申請内容が中間承認者によって却下されました"
        elif instance.approval == 0:
            rmsg = "以下の通り申請ワークフローでの申請内容が中間承認者によって承認が取り下げられましたので報告致します。"
            rttl = "申請内容が中間承認者によって取り下げられました"
        if not instance.approval == 1:
            context = {
                "msg": rmsg,
                "title": str(instance.requestID),
                "usermei": instance.usermei,
                "date": datetime.datetime.now,
                "attach": tempstr,
                "content": instance.content,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                    "/app_folder/request_detail/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/base.html", context)
            text_content = strip_tags(html_content)
            # 申請者へメール送信
            send_mail(rttl,
                    text_content,
                    hostmail,
                    [instance.user_email],
                    fail_silently=False)
        # # 承認者へメール送信
        # context = {
        #     "msg": "以下の申請の返答を送信しました",
        #     "title": str(instance.requestID),
        #     "usermei": instance.usermei,
        #     "date": datetime.datetime.now,
        #     "attach": tempstr,
        #     "content": instance.content,
        #     "url": "http://" + self.request.META.get("HTTP_HOST") +
        #            "/app_folder/approval_detail/" + str(instance.uuid),
        # }
        # html_content = render_to_string("mailer/base.html", context)
        # text_content = strip_tags(html_content)
        # send_mail("申請の返答を送信しました",
        #           text_content,
        #           hostmail,
        #           [instance.ap_email],
        #           fail_silently=False)
        if instance.approval == 1:
            # 最終承認者へメール送信
            context = {
                "msg": "以下の通り申請ワークフローが送信されました、最終承認者として承認・取り下げを行ってください。",
                "title": str(instance.requestID),
                "usermei": instance.usermei,
                "date": datetime.datetime.now,
                "attach": tempstr,
                "content": instance.content,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/last_approval_detail/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/base.html", context)
            text_content = strip_tags(html_content)
            send_mail("申請ワークフローが届いています",
                      text_content,
                      hostmail,
                      [instance.ls_email],
                      fail_silently=False)
        return super().form_valid(form)

approval_update = ApprovalUpdate.as_view()


# ──────────────────────────────────────────────────────────────#
# 最終承認処理関連のビュー
# ──────────────────────────────────────────────────────────────#

class LastApprovalListView(LoginRequiredMixin, ListView):
    template_name = 'app_folder/last_approval_list.html'
    model = RequestData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        # 最終承認者として担当する申請（かつ中間承認済み）のみを表示
        queryset = queryset.filter(last_approval_id=self.request.user.id, approval=1).order_by('-update_at')
        if self.request.GET.get('kbn'):
            queryset = queryset.filter(last_approval=self.request.GET.get('kbn'))
            if self.request.GET.get('rkbn'):
                if self.request.GET.get('rkbn') != "0":
                    queryset = queryset.filter(requestID=self.request.GET.get('rkbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(ReqDate__gt=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')+ datetime.timedelta(days=1)
                queryset = queryset.filter(ReqDate__lte=eddt)
            if self.request.GET.get('mei'):
                queryset = queryset.filter(usermei__contains=self.request.GET.get('mei'))
        else:
            queryset = queryset.none() 
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ApSearchForm(self.request.GET)
        return context

    def get(self, request):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)
    
last_approval_list = LastApprovalListView.as_view()

class LastApprovalDetail(LoginRequiredMixin, DetailView):
    template_name = 'app_folder/last_approval_detail.html'
    model = RequestData

last_approval_detail = LastApprovalDetail.as_view()

class LastApprovalUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'app_folder/last_approval_update.html'
    model = RequestData
    form_class = LastApprovalForm
    success_url = reverse_lazy('app_folder:last_approval_list')

    def form_valid(self, form):
        hostmail = getHostAdress()
        instance = form.save(commit=False)
        tempstr = 'あり' if instance.attach else 'なし'
        rmsg = ""
        rttl = ""
        if instance.last_approval == 1:
            rmsg = "以下の通り申請ワークフローでの申請内容が最終承認者によって承認されましたので報告致します。"
            rttl = "申請内容が最終承認者によって承認されました"
            instance.ap_no = getApprovalNo()
        elif instance.last_approval == 2:
            rmsg = "以下の通り申請ワークフローでの申請内容が最終承認者によって却下されましたので報告致します。"
            rttl = "申請内容が最終承認者によって却下されました"
            instance.ap_no = ""
        elif instance.last_approval == 0:
            rmsg = "以下の通り申請ワークフローでの申請内容が最終承認者によって承認が取り下げられましたので報告致します。"
            rttl = "申請内容が最終承認者によって取り下げられました"
            instance.ap_no = ""
        context = {
            "msg": rmsg,
            "title": str(instance.requestID),
            "usermei": instance.usermei,
            "date": datetime.datetime.now,
            "attach": tempstr,
            "content": instance.content,
            "no": instance.ap_no,
            "url": "http://" + self.request.META.get("HTTP_HOST") +
                   "/app_folder/request_detail/" + str(instance.uuid),
        }
        html_content = render_to_string("mailer/base.html", context)
        text_content = strip_tags(html_content)
        # 申請者へメール通知
        send_mail(rttl,
                  text_content,
                  hostmail,
                  [instance.user_email],
                  fail_silently=False)
        if instance.approval_id:
            # 中間承認者へメール通知
            context = {
                "msg": rmsg,
                "title": str(instance.requestID),
                "usermei": instance.usermei,
                "date": datetime.datetime.now,
                "attach": tempstr,
                "content": instance.content,
                "no": instance.ap_no,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/approval_detail/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/base.html", context)
            text_content = strip_tags(html_content)
            send_mail(rttl,
                      text_content,
                      hostmail,
                      [instance.ap_email],
                      fail_silently=False)
        return super().form_valid(form)

last_approval_update = LastApprovalUpdate.as_view()


# ──────────────────────────────────────────────────────────────#
# 掲示板（お知らせ）機能のビュー
# ──────────────────────────────────────────────────────────────#

class InfoCreate(LoginRequiredMixin, CreateView):
    template_name = 'app_folder/info_create.html'
    model = InfoData
    form_class = InfoForm
    success_url = reverse_lazy('app_folder:top_page')

    def form_valid(self, form):
        hostmail = getHostAdress()
        instance = form.save(commit=False)
        # 掲示板投稿者情報の設定
        instance.if_account_id = User.objects.get(id=self.request.user.id)
        instance.usermei = self.request.user.first_name
        instance.user_email = self.request.user.email
        tempstr = 'あり' if instance.attach else 'なし'
        # メール通知用コンテキストの生成
        context = {
            "msg": "以下の内容で掲示板に書き込みがあります。確認もしくは返信してください。",
            "title": str(instance.title),
            "usermei": instance.usermei,
            "date": datetime.datetime.now,
            "attach": tempstr,
            "content": instance.content,
            "url": "http://" + self.request.META.get("HTTP_HOST") +
                   "/app_folder/info_detail/" + str(instance.uuid),
        }
        html_content = render_to_string("mailer/info.html", context)
        text_content = strip_tags(html_content)
        employees_email = getEmployeesAdress()
        manager_email = getManagerAdress()
        # 全ユーザーへ通知（メールアドレスをリストで取得）
        if instance.permission == 1:
            send_mail("掲示板に書き込みがあります。",
                  text_content,
                  hostmail,
                  [employees_email,manager_email],
                  fail_silently=False)
        else:
            send_mail("掲示板に書き込みがあります。",
                  text_content,
                  hostmail,
                  [manager_email],
                  fail_silently=False)
        return super().form_valid(form)

    def get(self, request):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)
    
info_create = InfoCreate.as_view()

class ConfirmCreate(LoginRequiredMixin, CreateView):
    template_name = 'app_folder/info_confirm.html'
    model = InfoConfirm
    form_class = InfoConfirmForm
    success_url = reverse_lazy('app_folder:top_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 対象のお知らせ情報を取得してコンテキストに追加
        context['info'] = InfoData.objects.get(pk=self.kwargs['if_id'])
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.if_id_id = self.request.POST.get('info')
        instance.if_account_id = User.objects.get(id=self.request.user.id)
        instance.usermei = self.request.user.first_name
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app_folder:info_detail', kwargs=dict(pk=self.request.POST.get('info')))

info_confirm = ConfirmCreate.as_view()

class InfoDetail(LoginRequiredMixin, DetailView):
    template_name = 'app_folder/info_detail.html'
    model = InfoData

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 対象のお知らせに対する返信一覧を追加
        context['info'] = InfoConfirm.objects.filter(if_id=self.kwargs['pk']).order_by('update_at')
        return context

info_detail = InfoDetail.as_view()

class InfoDelete(LoginRequiredMixin, DeleteView):
    template_name = 'app_folder/info_delete.html'
    model = InfoData
    success_url = reverse_lazy('app_folder:top_page')

info_delete = InfoDelete.as_view()

class InfoUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'app_folder/info_update.html'
    model = InfoData
    form_class = InfoForm
    success_url = reverse_lazy('app_folder:top_page')

info_update = InfoUpdate.as_view()


# ──────────────────────────────────────────────────────────────#
# 勤怠（オフデー）申請機能のビュー
# ──────────────────────────────────────────────────────────────#

class OffDayListView(LoginRequiredMixin, ListView):
    template_name = 'app_folder/offday_list2.html'
    model = OffDayData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        if self.request.GET.get('kbn'):
            # ユーザー自身の勤怠申請を取得
            queryset = queryset.filter(od_account_id=self.request.user.id).order_by('-update_at')
            if self.request.GET.get('kbn') != "0":
                queryset = queryset.filter(offday_kbn=self.request.GET.get('kbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(offday_date__gte=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')
                queryset = queryset.filter(offday_date__lte=eddt)
            if self.request.GET.get('istdt'):
                queryset = queryset.filter(update_at__gte=self.request.GET.get('istdt'))
            if self.request.GET.get('ieddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('ieddt'), '%Y-%m-%d')+ datetime.timedelta(days=1)
                queryset = queryset.filter(update_at__lte=eddt)
            if self.request.GET.get('mei'):
                queryset = queryset.filter(emp_id__emmei__contains=self.request.GET.get('mei'))
        else:
            queryset = queryset.none() 
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = odSearchForm(self.request.GET)
        return context

    def get(self, request):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)
    
offday_list2 = OffDayListView.as_view()

def offday_listing(request):
    # ページネーション付きの勤怠申請一覧（ユーザー向け）
    contact_list = OffDayData.objects.filter(od_account_id=request.user.id).order_by('-update_at')
    paginator = Paginator(contact_list, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    if request.user.id == emp_id:
        return redirect(reverse_lazy('app_folder:top_page'))
    return render(request, "app_folder/offday_list.html", {"page_obj": page_obj})

class OffDayList3View(LoginRequiredMixin, ListView):
    template_name = 'app_folder/offday_list3.html'
    model = OffDayData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        if self.request.GET.get('kbn'):
            # 中間承認済みの勤怠申請を取得（スタッフユーザー向け）
            queryset = queryset.filter(last_approval=1).order_by('-update_at')
            if self.request.GET.get('kbn') != "0":
                queryset = queryset.filter(offday_kbn=self.request.GET.get('kbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(offday_date__gte=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')
                queryset = queryset.filter(offday_date__lte=eddt)
            if self.request.GET.get('istdt'):
                queryset = queryset.filter(update_at__gte=self.request.GET.get('istdt'))
            if self.request.GET.get('ieddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('ieddt'), '%Y-%m-%d')+ datetime.timedelta(days=1)
                queryset = queryset.filter(update_at__lte=eddt)
            if self.request.GET.get('mei'):
                queryset = queryset.filter(emp_id__emmei__contains=self.request.GET.get('mei'))
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = odSearchForm(self.request.GET)
        return context

    def get(self, request):
        # スタッフユーザーでなければトップページへリダイレクトする
        if not request.user.is_staff:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)

offday_list3 = OffDayList3View.as_view()

class OffDayDetail(LoginRequiredMixin, DetailView):
    template_name = 'app_folder/offday_detail.html'
    model = OffDayData

offday_detail = OffDayDetail.as_view()

class OffDayCreate(LoginRequiredMixin, CreateView):
    template_name = 'app_folder/offday_create.html'
    model = OffDayData
    form_class = DayoffCreateForm
    success_url = reverse_lazy('app_folder:offday_list')

    def get(self, request, **kwargs):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        form = DayoffCreateForm()
        # 現在のユーザーに関連するOffdayRequestMstをフィルタリングして選択肢を設定
        form.fields['emp_id'].queryset = OffdayRequestMst.objects.all().filter(u_id=self.request.user, del_flg=False)
        datas = {'form': form}
        return render(self.request, self.template_name, datas)

    def form_valid(self, form):
        hostmail = getHostAdress()
        instance = form.save(commit=False)
        instance.od_account_id = User.objects.get(id=self.request.user.id)
        instance.usermei = self.request.user.first_name
        instance.user_email = self.request.user.email
        approval = ApprovalMst.objects.get(userid=User.objects.get(id=self.request.user.id))
        instance.approval_id = approval.approval_id
        instance.apmei = approval.apmei
        instance.ap_email = approval.ap_email
        instance.last_approval_id = approval.last_approval_id
        instance.lsmei = approval.lsmei
        instance.ls_email = approval.last_email
        tempstr = 'あり' if instance.attach else 'なし'
        offdate = instance.offday_date.strftime('%Y年%m月%d日')
        if instance.end_offday_date:
            offdate += "～" + instance.end_offday_date.strftime('%Y年%m月%d日')
        if instance.approval_id:
            context = {
                "msg": "以下の通り勤怠申請が送信されました、中間承認者として承認・取り下げを行ってください。",
                "emp": str(instance.emp_id),
                "kbn": str(instance.offday_kbn),
                "date": offdate,
                "period": str(instance.period_id),
                "usermei": instance.usermei,
                "biko": instance.content,
                "reason": instance.reason,
                "attach": tempstr,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/ap_offday_update/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/offday.html", context)
            text_content = strip_tags(html_content)
            send_mail("勤怠申請が届いています",
                      text_content,
                      hostmail,
                      [instance.ap_email],
                      fail_silently=False)
        else:
            instance.approval = 1
            context = {
                "msg": "以下の通り勤怠申請が送信されました、最終承認者として承認・取り下げを行ってください。",
                "emp": str(instance.emp_id),
                "kbn": str(instance.offday_kbn),
                "date": offdate,
                "period": str(instance.period_id),
                "usermei": instance.usermei,
                "biko": instance.content,
                "reason": instance.reason,
                "attach": tempstr,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/ls_offday_update/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/offday.html", context)
            text_content = strip_tags(html_content)
            send_mail("勤怠申請が届いています",
                      text_content,
                      hostmail,
                      [instance.ls_email],
                      fail_silently=False)
        return super().form_valid(form)

offday_create = OffDayCreate.as_view()

class OffDayDelete(LoginRequiredMixin, DeleteView):
    template_name = 'app_folder/offday_delete.html'
    model = OffDayData
    success_url = reverse_lazy('app_folder:offday_list')

offday_delete = OffDayDelete.as_view()

# ──────────────────────────────────────────────────────────────#
# 中間承認者向け 勤怠申請処理のビュー
# ──────────────────────────────────────────────────────────────#

class ApOffDayListView(LoginRequiredMixin, ListView):
    template_name = 'app_folder/ap_offday_list.html'
    model = OffDayData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        # 現在のユーザーに担当される中間承認の勤怠申請を取得
        queryset = queryset.filter(approval_id=self.request.user.id).order_by('-update_at')
        if self.request.GET.get('kbn'):
            queryset = queryset.filter(approval=self.request.GET.get('kbn'))
            if self.request.GET.get('okbn'):
                if self.request.GET.get('okbn') != "0":
                    queryset = queryset.filter(offday_kbn=self.request.GET.get('okbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(offday_date__gte=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')
                queryset = queryset.filter(offday_date__lte=eddt)
            if self.request.GET.get('mei'):
                queryset = queryset.filter(usermei__contains=self.request.GET.get('mei'))
            if self.request.GET.get('emmei'):
                queryset = queryset.filter(emp_id__emmei__contains=self.request.GET.get('emmei'))
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = OdApSearchForm(self.request.GET)
        return context

    def get(self, request):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)

ap_offday_list = ApOffDayListView.as_view()

class ApOffDayUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'app_folder/ap_offday_update.html'
    model = OffDayData
    form_class = ODApprovalForm
    success_url = reverse_lazy('app_folder:ap_offday_list')

    def form_valid(self, form):
        hostmail = getHostAdress()
        instance = form.save(commit=False)
        tempstr = 'あり' if instance.attach else 'なし'
        rmsg = ""
        rttl = ""
        # if instance.approval == 1:
        #     rmsg = ("以下の通り勤怠申請での申請内容が中間承認者によって承認されましたので報告致します。"
        #             "引き続き、最終承認者にて回覧・承認が行われます。")
        #     rttl = "申請内容が中間承認者によって承認されました"
        # elif instance.approval == 2:
        if instance.approval == 2:
            rmsg = "以下の通り勤怠申請での申請内容が中間承認者によって却下されましたので報告致します。"
            rttl = "申請内容が中間承認者によって却下されました"
        elif instance.approval == 0:
            rmsg = "以下の通り勤怠申請での申請内容が中間承認者によって承認が取り下げられましたので報告致します。"
            rttl = "申請内容が中間承認者によって取り下げられました"
        offdate = instance.offday_date.strftime('%Y年%m月%d日')
        if instance.end_offday_date:
            offdate += "～" + instance.end_offday_date.strftime('%Y年%m月%d日')
        if not instance.approval == 1:
            context = {
                "msg": rmsg,
                "emp": str(instance.emp_id),
                "kbn": str(instance.offday_kbn),
                "date": offdate,
                "period": str(instance.period_id),
                "usermei": instance.usermei,
                "biko": instance.content,
                "reason": instance.reason,
                "attach": tempstr,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                    "/app_folder/offday_detail/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/offday.html", context)
            text_content = strip_tags(html_content)
            send_mail(rttl,
                    text_content,
                    hostmail,
                    [instance.user_email],
                    fail_silently=False)
        # context = {
        #     "msg": "以下の申請の返答を送信しました。",
        #     "emp": str(instance.emp_id),
        #     "kbn": str(instance.offday_kbn),
        #     "date": offdate,
        #     "period": str(instance.period_id),
        #     "usermei": instance.usermei,
        #     "biko": instance.content,
        #     "reason": instance.reason,
        #     "attach": tempstr,
        #     "url": "http://" + self.request.META.get("HTTP_HOST") +
        #            "/app_folder/ap_offday_update/" + str(instance.uuid),
        # }
        # html_content = render_to_string("mailer/offday.html", context)
        # text_content = strip_tags(html_content)
        # send_mail("申請の返答を送信しました",
        #           text_content,
        #           hostmail,
        #           [instance.ap_email],
        #           fail_silently=False)
        if instance.approval == 1:
            context = {
                "msg": "以下の通り勤怠申請が送信されました、最終承認者として承認・取り下げを行ってください。",
                "emp": str(instance.emp_id),
                "kbn": str(instance.offday_kbn),
                "date": offdate,
                "period": str(instance.period_id),
                "usermei": instance.usermei,
                "biko": instance.content,
                "reason": instance.reason,
                "attach": tempstr,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/ls_offday_update/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/offday.html", context)
            text_content = strip_tags(html_content)
            send_mail("勤怠申請が届いています",
                      text_content,
                      hostmail,
                      [instance.ls_email],
                      fail_silently=False)
        return super().form_valid(form)

ap_offday_update = ApOffDayUpdate.as_view()

# ──────────────────────────────────────────────────────────────#
# 最終承認者向け 勤怠申請処理のビュー
# ──────────────────────────────────────────────────────────────#

class LsOffDayListView(LoginRequiredMixin, ListView):
    template_name = 'app_folder/ls_offday_list.html'
    model = OffDayData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        # 最終承認者として担当する申請（中間承認済みかつ承認済み）のみ
        queryset = queryset.filter(last_approval_id=self.request.user.id, approval=1).order_by('-update_at')
        if self.request.GET.get('kbn'):
            queryset = queryset.filter(last_approval=self.request.GET.get('kbn'))
            if self.request.GET.get('okbn'):
                if self.request.GET.get('okbn') != "0":
                    queryset = queryset.filter(offday_kbn=self.request.GET.get('okbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(offday_date__gte=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')
                queryset = queryset.filter(offday_date__lte=eddt)
            if self.request.GET.get('mei'):
                queryset = queryset.filter(usermei__contains=self.request.GET.get('mei'))
            if self.request.GET.get('emmei'):
                queryset = queryset.filter(emp_id__emmei__contains=self.request.GET.get('emmei'))
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = OdApSearchForm(self.request.GET)
        return context

    def get(self, request):
        if request.user.id == emp_id:
            return redirect(reverse_lazy('app_folder:top_page'))
        return super().get(request)

ls_offday_list = LsOffDayListView.as_view()

class LsOffDayUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'app_folder/ls_offday_update.html'
    model = OffDayData
    form_class = ODLastApprovalForm
    success_url = reverse_lazy('app_folder:ls_offday_list')

    def form_valid(self, form):
        hostmail = getHostAdress()
        offdaymail = getOffdayAdress()
        instance = form.save(commit=False)
        tempstr = 'あり' if instance.attach else 'なし'
        offdate = instance.offday_date.strftime('%Y年%m月%d日')
        if instance.end_offday_date:
            offdate += "～" + instance.end_offday_date.strftime('%Y年%m月%d日')
        rmsg = ""
        rttl = ""
        if instance.last_approval == 1:
            rmsg = "以下の通り勤怠申請での申請内容が最終承認者によって承認されましたので報告致します。"
            rttl = "申請内容が最終承認者によって承認されました"
            instance.ap_no = getOffDayApprovalNo()
        elif instance.last_approval == 2:
            rmsg = "以下の通り勤怠申請での申請内容が最終承認者によって却下されましたので報告致します。"
            rttl = "申請内容が最終承認者によって却下されました"
            instance.ap_no = ""
        elif instance.last_approval == 0:
            rmsg = "以下の通り勤怠申請での申請内容が最終承認者によって承認が取り下げられましたので報告致します。"
            rttl = "申請内容が最終承認者によって取り下げられました"
            instance.ap_no = ""
        context = {
            "msg": rmsg,
            "emp": str(instance.emp_id),
            "kbn": str(instance.offday_kbn),
            "date": offdate,
            "period": str(instance.period_id),
            "usermei": instance.usermei,
            "biko": instance.content,
            "reason": instance.reason,
            "attach": tempstr,
            "no": instance.ap_no,
            "url": "http://" + self.request.META.get("HTTP_HOST") +
                   "/app_folder/offday_detail/" + str(instance.uuid),
        }
        html_content = render_to_string("mailer/offday.html", context)
        text_content = strip_tags(html_content)
        send_mail(rttl,
                  text_content,
                  hostmail,
                  [instance.user_email],
                  fail_silently=False)
        if not instance.approval_id:
            context = {
                "msg": rmsg,
                "emp": str(instance.emp_id),
                "kbn": str(instance.offday_kbn),
                "date": offdate,
                "period": str(instance.period_id),
                "usermei": instance.usermei,
                "biko": instance.content,
                "reason": instance.reason,
                "attach": tempstr,
                "no": instance.ap_no,
                "url": "http://" + self.request.META.get("HTTP_HOST") +
                       "/app_folder/ap_offday_update/" + str(instance.uuid),
            }
            html_content = render_to_string("mailer/offday.html", context)
            text_content = strip_tags(html_content)
            send_mail(rttl,
                      text_content,
                      hostmail,
                      [instance.ap_email],
                      fail_silently=False)
        if instance.last_approval == 1:
            # 打刻依頼のためのメール送信（入力依頼）
            context = {
                "msg": "以下の勤怠の入力をお願いします。",
                "emp": str(instance.emp_id),
                "kbn": str(instance.offday_kbn),
                "date": offdate,
                "period": str(instance.period_id),
                "usermei": instance.usermei,
                "biko": instance.content,
                "reason": instance.reason,
                "no": instance.ap_no,
                "url": "",
            }
            html_content = render_to_string("mailer/offday.html", context)
            text_content = strip_tags(html_content)
            send_mail("勤怠入力依頼",
                      text_content,
                      hostmail,
                      [offdaymail],
                      fail_silently=False)
        return super().form_valid(form)

ls_offday_update = LsOffDayUpdate.as_view()


# ──────────────────────────────────────────────────────────────#
# 改善提案機能のビュー
# ──────────────────────────────────────────────────────────────#

class ImprovementCreate(LoginRequiredMixin, CreateView):
    template_name = 'app_folder/improvement_create.html'
    model = ImprovementData
    form_class = ImprovementCreateForm
    success_url = reverse_lazy('app_folder:message')

    def form_valid(self, form):
        instance = form.save(commit=False)
        # 改善提案作成者情報の設定
        employee = EmployeeMst.objects.get(emmei=instance.emp_id)
        instance.emp_mei = employee.emmei
        instance.emp_email = employee.email
        instance.imp_no = getImpNo()
        return super().form_valid(form)

improvement_create = ImprovementCreate.as_view()

# @login_required
# def export_improvementdata_excel(request):
#     """
#     ImprovementData のデータを検索して Excel ファイルに出力するビュー。
    
#     GETパラメータ:
#       - 'q'          : 検索キーワード (emp_mei など)
#       - 'start_date' : 検索期間の開始日 (YYYY-MM-DD)
#       - 'end_date'   : 検索期間の終了日 (YYYY-MM-DD)
#       - 'kbn'        : カテゴリー（ImproveKbnMst の pk）を選択（コンボボックス）
#       - 'export'     : このパラメータがある場合は Excel ファイルを出力、ない場合は検索フォーム画面を表示
#     """
#     # 1. GETパラメータの取得
#     start_date_str    = request.GET.get("start_date", "").strip()
#     end_date_str      = request.GET.get("end_date", "").strip()
#     selected_category = request.GET.get("kbn", "").strip()
    
#     # 2. 基本のクエリセット取得（更新日時降順）
#     queryset = ImprovementData.objects.all().order_by('-update_at')
        
#     # 4. フィルタ: カテゴリー（ForeignKey: kbn_id）
#     if selected_category:
#         queryset = queryset.filter(kbn_id=selected_category)
    
#     # 5. フィルタ: 検索期間（ReqDate）
#     if start_date_str:
#         try:
#             start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
#             queryset = queryset.filter(ReqDate__gte=start_date)
#         except ValueError:
#             pass
#     if end_date_str:
#         try:
#             end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
#             queryset = queryset.filter(ReqDate__lte=end_date)
#         except ValueError:
#             pass
    
#     # 6. Excel出力処理
#     if "export" in request.GET:
#         wb = openpyxl.Workbook()
#         ws = wb.active
#         ws.title = "ImprovementData Export"
        
#         # ヘッダー行の設定
#         headers = [
#             "氏名",
#             "Email",
#             "カテゴリー",
#             "書込日",
#             "更新日",
#             "タイトル",
#             "内容",
#             "回答者",
#             "回答内容",
#             "重要度",
#             "優先度",
#             "添付ファイルパス",
#             "改善提案No.",
#         ]
#         ws.append(headers)
#         # ヘッダーのスタイル設定
#         thin_border = Border(
#             left=Side(style='thin'),
#             right=Side(style='thin'),
#             top=Side(style='thin'),
#             bottom=Side(style='thin')
#         )
#         header_fill = PatternFill(start_color="00B0F0", end_color="00B0F0", fill_type="solid")
#         header_font = Font(bold=True)
#         header_alignment = Alignment(horizontal="center", vertical="center")
#         # ヘッダー行は1行目なので ws[1]
#         for cell in ws[1]:
#             cell.border = thin_border
#             cell.fill = header_fill
#             cell.font = header_font
#             cell.alignment = header_alignment
        
#         # データ行の追加
#         for obj in queryset:
#             req_date = timezone.localtime(obj.ReqDate).strftime("%Y-%m-%d") if obj.ReqDate else ""
#             upd_date = timezone.localtime(obj.update_at).strftime("%Y-%m-%d") if obj.update_at else ""
#             importance = obj.get_Importance_display() if hasattr(obj, "get_Importance_display") else obj.Importance
#             priority = obj.get_priority_display() if hasattr(obj, "get_priority_display") else obj.priority
#             attached = str(obj.attach) if obj.attach else ""
            
#             row = [
#                 obj.emp_mei or "",
#                 obj.emp_email or "",
#                 str(obj.kbn_id) if obj.kbn_id else "",
#                 req_date,
#                 upd_date,
#                 obj.ttl or "",
#                 obj.content or "",
#                 obj.ans_mei or "",
#                 obj.answer or "",
#                 importance,
#                 priority,
#                 attached,
#                 obj.imp_no or "",
#             ]
#             ws.append(row)
            
#         # 各列の幅を手動で指定（必要に応じて調整してください）
#         column_widths = {
#             'A': 15,
#             'B': 20,
#             'C': 20,
#             'D': 12,
#             'E': 12,
#             'F': 30,
#             'G': 50,
#             'H': 15,
#             'I': 50,
#             'J': 10,
#             'K': 10,
#             'L': 30,
#             'M': 15,
#         }
#         for col_letter, width in column_widths.items():
#             ws.column_dimensions[col_letter].width = width
        
#         # ファイル名に現在日付 (YYYYMMDD形式) を付与
#         current_date = datetime.datetime.now().strftime("%Y%m%d")
#         file_name = f"ImprovementData_Export_{current_date}.xlsx"
        
#         response = HttpResponse(
#             content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
#         response["Content-Disposition"] = f"attachment; filename={file_name}"
#         wb.save(response)
#     else:
#         # 7. 検索フォーム画面を表示するためのコンテキスト作成
#         categories = ImproveKbnMst.objects.all()
#         context = {
#             "start_date": start_date_str,
#             "end_date": end_date_str,
#             "selected_category": selected_category,
#             "categories": categories,
#             "result_count": queryset.count(),
#         }
#         return render(request, "app_folder/export_improvementdata.html", context)

class ImproveListView(LoginRequiredMixin, ListView):
    template_name = 'app_folder/improve_list.html'
    model = ImprovementData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.filter().order_by('-update_at')
        if self.request.GET.get('kbn'):
            if self.request.GET.get('kbn') != "0":
                queryset = queryset.filter(kbn_id=self.request.GET.get('kbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(ReqDate__gte=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')+ datetime.timedelta(days=1)
                queryset = queryset.filter(ReqDate__lte=eddt)
            if self.request.GET.get('emmei'):
                queryset = queryset.filter(emp_id__emmei__contains=self.request.GET.get('emmei'))
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = impSearchForm(self.request.GET)
        return context

improve_list = ImproveListView.as_view()

class ImproveListView2(LoginRequiredMixin, ListView):
    template_name = 'app_folder/improve_list2.html'
    model = ImprovementData

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.filter().order_by('-update_at')
        if self.request.GET.get('kbn'):
            if self.request.GET.get('kbn') != "0":
                queryset = queryset.filter(kbn_id=self.request.GET.get('kbn'))
            if self.request.GET.get('stdt'):
                queryset = queryset.filter(ReqDate__gte=self.request.GET.get('stdt'))
            if self.request.GET.get('eddt'):
                eddt = datetime.datetime.strptime(self.request.GET.get('eddt'), '%Y-%m-%d')+ datetime.timedelta(days=1)
                queryset = queryset.filter(ReqDate__lte=eddt)
            if self.request.GET.get('emmei'):
                queryset = queryset.filter(emp_id__emmei__contains=self.request.GET.get('emmei'))
        else:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = impSearchForm(self.request.GET)
        return context

improve_list2 = ImproveListView2.as_view()

class ImproveDetail(LoginRequiredMixin, DetailView):
    template_name = 'app_folder/improve_detail.html'
    model = ImprovementData

improve_detail = ImproveDetail.as_view()

class ImproveUpdate1(LoginRequiredMixin, UpdateView):
    template_name = 'app_folder/improve_update1.html'
    model = ImprovementData
    form_class = ImpUp1Form
    success_url = reverse_lazy('app_folder:improve_list2')

    def form_valid(self, form):
        instance = form.save(commit=False)
        # 改善提案作成者情報の設定
        instance.ans_mei = self.request.user.first_name
        instance.user_email = self.request.user.email
        return super().form_valid(form)

improve_update1 = ImproveUpdate1.as_view()

class ImproveUpdate2(LoginRequiredMixin, UpdateView):
    template_name = 'app_folder/improve_update2.html'
    model = ImprovementData
    form_class = ImpUp2Form
    success_url = reverse_lazy('app_folder:improve_list2')

    def form_valid(self, form):
        instance = form.save(commit=False)
        # 改善提案作成者情報の設定
        employee = EmployeeMst.objects.get(emmei=instance.emp_id)
        instance.emp_mei = employee.emmei
        instance.emp_email = employee.email
        return super().form_valid(form)

improve_update2 = ImproveUpdate2.as_view()

# @login_required
# def improve_pdf(request, pk):
#     """
#     ImprovementData の指定したレコードを PDF 出力するビュー。
#     詳細画面からボタン押下でこの URL にアクセスする前提です。
#     """
#     # 対象のレコードを取得
#     record = get_object_or_404(ImprovementData, pk=pk)
#     record.content = re.sub(r'(\w{40})', r'\1<br>', linebreaks(record.content))
#     record.answer = re.sub(r'(\w{40})', r'\1<br>', linebreaks(record.answer))
#     # HTML テンプレートを読み込み、PDF 用のコンテキストを設定
#     template = get_template("app_folder/improvementdata_pdf.html")
#     context = {
#         "record": record,
#         "req_date": timezone.localtime(record.ReqDate).strftime("%Y-%m-%d %H:%M:%S") if record.ReqDate else "",
#         "update_at": timezone.localtime(record.update_at).strftime("%Y-%m-%d %H:%M:%S") if record.update_at else "",
#     }
#     html = template.render(context)
    
#     # HTML から PDF を生成
#     result = io.BytesIO()
#     pdf = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=result)
    
#     if not pdf.err:
#         current_date = datetime.datetime.now().strftime("%Y%m%d")
#         file_name = f"ImprovementData_{pk}_{current_date}.pdf"
#         response = HttpResponse(result.getvalue(), content_type="application/pdf")
#         response["Content-Disposition"] = f"attachment; filename={file_name}"
#         return response
#     else:
#         return HttpResponse("PDFの生成に失敗しました。", status=500)

def opinion_create(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    if request.method == "POST":
        form = OpinionCreateForm(request.POST)
        if form.is_valid():
            # フォームデータの取得
            name_id = form.cleaned_data["mei"]
            message = form.cleaned_data["content"]
            # 名前取得
            if name_id == "0":
                name = "匿名希望"
            else:
                employee = EmployeeMst.objects.filter(id=name_id).first()
                name = employee.emmei if employee else "不明"

            # 送信者の情報を付加
            full_message = f"送信者: {name} \n\n{message}"
            hostmail = getHostAdress()
            opimail = getOpinionAdress()

            # メール送信
            send_mail(
                "意見箱",
                full_message,
                hostmail,  # 送信元 (settings.py で設定)
                [opimail],  # 送信先 (settings.py で設定)
                fail_silently=False,
            )

            return render(request, "app_folder/message.html", {"name": name})
    else:
        form = OpinionCreateForm()

    return render(request, "app_folder/opinion_create.html", {"form": form})    

def import_offday_csv(request):
    """
    CSV を取り込み、ログインユーザーの情報と紐付けて OffDayData に保存するビュー
    """
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    if request.user.id == emp_id:
        return redirect(reverse_lazy('app_folder:top_page'))
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["file"]

            # CSV ファイルのエンコーディングを考慮（UTF-8 で処理）
            try:
                decoded_file = csv_file.read().decode("utf-8")
            except UnicodeDecodeError:
                messages.error(request, "CSV ファイルのエンコードを UTF-8 にしてください。")
                return redirect("app_folder:import_offday_csv")

            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            header = next(reader)  # ヘッダーをスキップ

            appr = 1
            approval_id =None
            apmei =None
            ap_email =None
            approval = ApprovalMst.objects.get(userid=User.objects.get(id=request.user.id))
            if approval.approval_id:
                approval_id = approval.approval_id
                apmei = approval.apmei
                ap_email = approval.ap_email
                appr = 0
            last_approval_id = approval.last_approval_id
            lsmei = approval.lsmei
            ls_email = approval.last_email
            # ログインユーザーの情報を取得
            user = request.user

            with transaction.atomic():  # 途中でエラーが発生した場合にロールバック
                for row_number, row in enumerate(reader, start=2):  # 2行目以降
                    try:
                        try:
                            emp = OffdayRequestMst.objects.get(u_id=request.user.id,emmei=row[0])  # emp_id
                        except OffdayRequestMst.DoesNotExist:
                            raise ValueError(f"エラー: {row_number}行目 - 従業員 ID {row[0]} が存在しません。")

                        try:
                            period = PeriodMst.objects.get(period=row[1])  # period_id
                        except PeriodMst.DoesNotExist:
                            raise ValueError(f"エラー: {row_number}行目 - 期間 ID {row[1]} が存在しません。")

                        try:
                            offday_kbn = OffdayKbnMst.objects.get(kbnmei=row[2])  # offday_kbn
                        except OffdayKbnMst.DoesNotExist:
                            raise ValueError(f"エラー: {row_number}行目 - 勤怠区分 ID {row[2]} が存在しません。")

                        # 日付フィールドの変換
                        try:
                            offday_date = datetime.datetime.strptime(row[3], "%Y-%m-%d").date()
                        except ValueError:
                            raise ValueError(f"エラー: {row_number}行目 - offday_date ({row[3]}) の形式が不正です。")

                        end_offday_date = (
                            datetime.datetime.strptime(row[4], "%Y-%m-%d").date()
                            if row[4] else None
                        )
                        req_date = now()
                        update_at = now()

                        
                        ap_no=getOffDayApprovalNo()

                        OffDayData.objects.create(
                            od_account_id=user,
                            usermei=user.first_name,
                            user_email=user.email,
                            emp_id=emp,
                            period_id=period,
                            offday_kbn=offday_kbn,
                            offday_date=offday_date,
                            end_offday_date=end_offday_date,
                            ReqDate=req_date,
                            update_at=update_at,
                            content=row[5],
                            reason=row[6],
                            approval_id=approval_id,
                            apmei=apmei,
                            ap_email=ap_email,
                            approval_content=None,
                            approval=appr,
                            approval_read=False,
                            last_approval_id=last_approval_id,
                            lsmei=lsmei,
                            ls_email=ls_email,
                            last_approval_content=None,
                            last_approval=0,
                            attach=None,
                            attach2=None,
                            attach3=None,
                            ap_no=ap_no,
                        )
                    except Exception as e:
                        messages.error(request, f"データの読み込み中にエラーが発生しました: {str(e)}")
                        return redirect("app_folder:import_offday_csv")
            
            hostmail = getHostAdress()
            # context = {
            #     "msg": "CSVによって勤怠申請が送信され、回覧・承認が行われております。",
            #     "url": "http://" + request.META.get("HTTP_HOST") +
            #        "/app_folder/offday_list2/" ,
            # }
            # html_content = render_to_string("mailer/offday.html", context)
            # text_content = strip_tags(html_content)
            # send_mail("勤怠申請が送信されました",
            #         text_content,
            #         hostmail,
            #         [request.user.email],
            #         fail_silently=False)
            if approval_id:
                context = {
                    "msg": "CSVによって勤怠申請が送信されました、中間承認者として承認・取り下げを行ってください。",
                    "usermei": user.first_name,
                    "url": "http://" + request.META.get("HTTP_HOST") +
                    "/app_folder/ap_offday_list/" ,
                }
                html_content = render_to_string("mailer/offday.html", context)
                text_content = strip_tags(html_content)
                send_mail("勤怠申請が届いています",
                        text_content,
                        hostmail,
                        [ap_email],
                        fail_silently=False)
            else:
                context = {
                    "msg": "CSVによって勤怠申請が送信されました、最終承認者として承認・取り下げを行ってください。",
                    "usermei": user.first_name,
                    "url": "http://" + request.META.get("HTTP_HOST") +
                    "/app_folder/bulk_update_offday/" ,
                }
                html_content = render_to_string("mailer/offday.html", context)
                text_content = strip_tags(html_content)
                send_mail("勤怠申請が届いています",
                        text_content,
                        hostmail,
                        [ls_email],
                        fail_silently=False)

            messages.success(request, "CSV のデータを正常に取り込みました。")
            return redirect("app_folder:import_offday_csv")
    else:
        form = CSVUploadForm()

    return render(request, "app_folder/import_offday_csv.html", {"form": form})

def bulk_update_offday(request):
    """
    OffDayData の一覧を表示し、チェックが入ったレコードのみ更新＆メール送信するビュー
    """
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    if request.user.id == emp_id:
        return redirect(reverse_lazy('app_folder:top_page'))
    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_ids")  # チェックされたレコードのIDリスト
        approval_status = request.POST.get("approval_status")  # 更新する承認ステータス

        if not selected_ids:
            messages.error(request, "更新対象が選択されていません。")
            return redirect("app_folder:bulk_update_offday")

        hostmail = getHostAdress()

        try:
            with transaction.atomic():
                # 更新対象のレコードを取得
                updated_records = OffDayData.objects.filter(uuid__in=selected_ids)

                for record in updated_records:
                    # 新しい承認ステータスを設定
                    record.last_approval = approval_status

                    # 承認済みに設定された場合は、承認番号を付与
                    if approval_status == "1" and not record.ap_no:
                        record.ap_no = getOffDayApprovalNo()

                    record.save()

                    rmsg = ""
                    rttl = ""
                    # if approval_status == "1":
                    #     rmsg = "以下の通り勤怠申請での申請内容が最終承認者によって承認されましたので報告致します。"
                    #     rttl = "申請内容が最終承認者によって承認されました"
                    # elif approval_status == "2":
                    if approval_status == "2":
                        rmsg = "以下の通り勤怠申請での申請内容が最終承認者によって却下されましたので報告致します。"
                        rttl = "申請内容が最終承認者によって却下されました"
                    elif approval_status == "0":
                        rmsg = "以下の通り勤怠申請での申請内容が最終承認者によって承認が取り下げられましたので報告致します。"
                        rttl = "申請内容が最終承認者によって取り下げられました"
                    if not approval_status == "1":
                        context = {
                            "msg": rmsg,
                            "emp": str(record.emp_id),
                            "kbn": str(record.offday_kbn),
                            "date": record.offday_date,
                            "period": str(record.period_id),
                            "usermei": record.usermei,
                            "biko": record.content,
                            "reason": record.reason,
                            "no": record.ap_no,
                            "url": "http://" + request.META.get("HTTP_HOST") +
                                "/app_folder/offday_detail/" + str(record.uuid),
                        }
                        html_content = render_to_string("mailer/offday.html", context)
                        text_content = strip_tags(html_content)
                        send_mail(rttl,
                                text_content,
                                hostmail,
                                [record.user_email],
                                fail_silently=False)
            if approval_status == "1":
                # メール送信処理
                subject = "勤怠申請一括更新"
                message = (
                    "勤怠申請の承認ステータスが一括更新されました。\n\n"
                    "詳細はシステムをご確認ください。"
                )
                offdaymail = getOffdayAdress()
                
                send_mail(
                    subject,
                    message,
                    hostmail,
                    [offdaymail],
                    fail_silently=False,
                )

            messages.success(request, f"{len(selected_ids)} 件の勤怠データを更新し、通知メールを送信しました。")

        except Exception as e:
            messages.error(request, f"更新中にエラーが発生しました: {e}")

        return redirect("app_folder:bulk_update_offday")

    # データ一覧を取得
    offday_data = OffDayData.objects.all().filter(last_approval=0,approval=1).order_by("-update_at")
    return render(request, "app_folder/bulk_update_offday.html", {"offday_data": offday_data})

def bulk_update_offday2(request):
    """
    OffDayData の一覧を表示し、チェックが入ったレコードのみ更新＆メール送信するビュー
    """
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=%s' % request.path)
    if request.user.id == emp_id:
        return redirect(reverse_lazy('app_folder:top_page'))
    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_ids")  # チェックされたレコードのIDリスト
        approval_status = request.POST.get("approval_status")  # 更新する承認ステータス

        if not selected_ids:
            messages.error(request, "更新対象が選択されていません。")
            return redirect("app_folder:bulk_update_offday2")

        hostmail = getHostAdress()
        ls_email = ""

        try:
            with transaction.atomic():
                # 更新対象のレコードを取得
                updated_records = OffDayData.objects.filter(uuid__in=selected_ids)

                for record in updated_records:
                    # 新しい承認ステータスを設定
                    record.approval = approval_status


                    record.save()
                    ls_email = record.ls_email
                    rmsg = ""
                    rttl = ""
                    # if approval_status == "1":
                    #     rmsg = ("以下の通り勤怠申請での申請内容が中間承認者によって承認されましたので報告致します。"
                    #             "引き続き、最終承認者にて回覧・承認が行われます。")
                    #     rttl = "申請内容が中間承認者によって承認されました"
                    # elif approval_status == "2":
                    if approval_status == "2":
                        rmsg = "以下の通り勤怠申請での申請内容が中間承認者によって却下されましたので報告致します。"
                        rttl = "申請内容が中間承認者によって却下されました"
                    elif approval_status == "0":
                        rmsg = "以下の通り勤怠申請での申請内容が中間承認者によって承認が取り下げられましたので報告致します。"
                        rttl = "申請内容が中間承認者によって取り下げられました"
                    if not approval_status == "1":
                        context = {
                            "msg": rmsg,
                            "emp": str(record.emp_id),
                            "kbn": str(record.offday_kbn),
                            "date": record.offday_date,
                            "period": str(record.period_id),
                            "usermei": record.usermei,
                            "biko": record.content,
                            "reason": record.reason,
                            "no": "",
                            "url": "http://" + request.META.get("HTTP_HOST") +
                                "/app_folder/offday_detail/" + str(record.uuid),
                        }
                        html_content = render_to_string("mailer/offday.html", context)
                        text_content = strip_tags(html_content)
                        send_mail(rttl,
                                text_content,
                                hostmail,
                                [record.user_email],
                                fail_silently=False)
            if approval_status == "1":
                # メール送信処理
                subject = "勤怠申請中間承認一括更新"
                message = (
                    "中間承認者によって勤怠申請の承認ステータスが一括更新されました。\n\n"
                    "詳細はシステムをご確認ください。\n\n"
                    "http://" + request.META.get("HTTP_HOST") + "/app_folder/bulk_update_offday/"
                )
                
                send_mail(
                    subject,
                    message,
                    hostmail,
                    [ls_email],
                    fail_silently=False,
                )

            messages.success(request, f"{len(selected_ids)} 件の勤怠データを更新し、通知メールを送信しました。")

        except Exception as e:
            messages.error(request, f"更新中にエラーが発生しました: {e}")

        return redirect("app_folder:bulk_update_offday2")

    # データ一覧を取得
    offday_data = OffDayData.objects.all().filter(approval=0,approval_id=request.user.id).order_by("-update_at")
    return render(request, "app_folder/bulk_update_offday2.html", {"offday_data": offday_data})

# ──────────────────────────────────────────────────────────────#
# 補助関数（共通処理）
# ──────────────────────────────────────────────────────────────#

def getApprovalNo():
    # 承認番号の自動生成
    seq = SeqMst.objects.first()
    setting = SettingMst.objects.first()
    no = seq.approval_no + 1
    seq.approval_no = no
    seq.save()
    nostr = setting.ap_str + str(no).zfill(setting.ap_digit)
    return nostr

def getOffDayApprovalNo():
    # 勤怠申請の承認番号の自動生成
    seq = SeqMst.objects.first()
    setting = SettingMst.objects.first()
    no = seq.offday_ap_no + 1
    seq.offday_ap_no = no
    seq.save()
    nostr = setting.od_str + str(no).zfill(setting.ap_digit)
    return nostr

def getImpNo():
    # 改善提案番号の自動生成
    seq = SeqMst.objects.first()
    setting = SettingMst.objects.first()
    no = seq.imp_no + 1
    seq.imp_no = no
    seq.save()
    nostr = setting.imp_str + str(no).zfill(setting.ap_digit)
    return nostr

def getHostAdress():
    # ホストメールアドレスを設定テーブルから取得
    setting = SettingMst.objects.first()
    return setting.host_email

def getRequestAdress():
    # 申請用メールアドレス取得
    setting = SettingMst.objects.first()
    return setting.request_email

def getOffdayAdress():
    # 勤怠申請用メールアドレス取得
    setting = SettingMst.objects.first()
    return setting.offday_email

def getOpinionAdress():
    # 意見箱メールアドレス取得
    setting = SettingMst.objects.first()
    return setting.opinion_email

def getEmployeesAdress():
    # 従業員メールアドレス取得
    setting = SettingMst.objects.first()
    return setting.employees_email

def getManagerAdress():
    # 管理者メールアドレス取得
    setting = SettingMst.objects.first()
    return setting.manager_email

# ※ 以下、未使用のコードはコメントアウト
#     user = {
#         'sample1': [1, 2, 3],
#         'sample2': [3, 6, 9],
#     } 
#     return JsonResponse(user)
