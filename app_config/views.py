from django.shortcuts import render, redirect, reverse  
from django.views import View  
  
class index(View):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('app_folder:top_page'))
index = index.as_view()