from django.shortcuts import render
from manager.models import dish
from django import http
from django.views import View
from django.core import serializers
import json, dicttoxml, xmltodict