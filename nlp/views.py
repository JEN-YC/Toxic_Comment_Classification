from django.shortcuts import render, get_object_or_404, redirect
from .models import Message
from django.views.generic import ListView, DetailView
from django.forms import ModelForm, Textarea
from django.db.models import Q
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from nlp.process import TOXIC_MODEL_PATH, SEVERE_MODEL_PATH, OBSCENE_MODEL_PATH, \
    THREAT_MODEL_PATH, INSULT_MODEL_PATH, HATE_MODEL_PATH, predict, process_comment, \
    TOXIC_WORD_PATH, SEVERE_WORD_PATH, OBSCENE_WORD_PATH, THREAT_WORD_PATH, \
    INSULT_WORD_PATH, HATE_WORD_PATH, TFIDF_MODEL_PATH, TOKENIZER_PATH, LSTM_MODEL, predict_LSTM
import tensorflow as tf
import pickle

with open(TFIDF_MODEL_PATH, 'rb') as f:
    tfidf = pickle.load(f)

with open(TOKENIZER_PATH, 'rb') as f:
    tokenizer = pickle.load(f)

with open(TOXIC_MODEL_PATH, 'rb') as f:
    toxic_model = pickle.load(f)

with open(SEVERE_MODEL_PATH, 'rb') as f:
    severe_model = pickle.load(f)

with open(OBSCENE_MODEL_PATH, 'rb') as f:
    obscene_model = pickle.load(f)

with open(THREAT_MODEL_PATH, 'rb') as f:
    threat_model = pickle.load(f)

with open(INSULT_MODEL_PATH, 'rb') as f:
    insult_model = pickle.load(f)

with open(HATE_MODEL_PATH, 'rb') as f:
    hate_model = pickle.load(f)
# LSTM_model = tf.contrib.keras.models.load_model(LSTM_MODEL)

RATIO_LIST = ['toxic_ratio', 'severe_ratio', 'obscene_ratio', 'insult_ratio', 'threat_ratio', 'hate_ratio',
              'L_toxic_ratio', 'L_severe_ratio', 'L_obscene_ratio', 'L_insult_ratio', 'L_threat_ratio', 'L_hate_ratio']
THRESHOLD = 70


class HomePageView(LoginRequiredMixin, ListView):
    template_name = 'index.html'
    model = Message
    context_object_name = 'SMSs'

    def get_queryset(self):
        contacts = super().get_queryset()
        return contacts


def submit_comment(request):
    if request.is_ajax():
        comment = request.POST['comment']
        value = dict()
        value['owner'] = request.user
        value['content'] = comment
        value['toxic_ratio'] = predict(comment, toxic_model, tfidf, TOXIC_MODEL_PATH)
        value['severe_ratio'] = predict(comment, severe_model, tfidf, SEVERE_MODEL_PATH)
        value['obscene_ratio'] = predict(comment, obscene_model, tfidf, OBSCENE_MODEL_PATH)
        value['threat_ratio'] = predict(comment, threat_model, tfidf, THREAT_MODEL_PATH)
        value['insult_ratio'] = predict(comment, insult_model, tfidf, INSULT_MODEL_PATH)
        value['hate_ratio'] = predict(comment, hate_model, tfidf, HATE_MODEL_PATH)

        lstm_predicts = predict_LSTM(comment, tokenizer)[0]
        value['L_toxic_ratio'] = round(lstm_predicts[0]*100, 4)
        value['L_severe_ratio'] = round(lstm_predicts[1]*100, 4)
        value['L_obscene_ratio'] = round(lstm_predicts[2]*100, 4)
        value['L_threat_ratio'] = round(lstm_predicts[3]*100, 4)
        value['L_insult_ratio'] = round(lstm_predicts[4]*100, 4)
        value['L_hate_ratio'] = round(lstm_predicts[5]*100, 4)

        value['toxic_words'] = process_comment(comment, TOXIC_WORD_PATH)
        value['severe_words'] = process_comment(comment, SEVERE_WORD_PATH)
        value['obscene_words'] = process_comment(comment, OBSCENE_WORD_PATH)
        value['hate_words'] = process_comment(comment, HATE_WORD_PATH)
        value['insult_words'] = process_comment(comment, INSULT_WORD_PATH)
        value['threat_words'] = process_comment(comment, THREAT_WORD_PATH)
        for ratio in RATIO_LIST:
            if value[ratio] > THRESHOLD:
                value['toxic_comment'] = True
                break
        for ratio in RATIO_LIST:
            value[ratio] = str(value[ratio]) + ' %'

        m = Message(**value)
        m.save()
        messages.success(
            request, 'Successfully add your comment!')

    return JsonResponse({'value': '成功', 'id': m.id, 'user_name': m.owner.username,
                         'time': m.date.strftime('%B %d %H:%M')})


class MessageDetailView(LoginRequiredMixin, DetailView):
    template_name = 'detail.html'
    model = Message
    context_object_name = 'SMS'


class UpdateForm(ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {'content': Textarea(attrs={'cols': 50, 'rows': 20}), }


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = UpdateForm
    template_name = 'update.html'
    context_object_name = 'SMS'

    def form_valid(self, form):
        instance = form.save(commit=False)
        comment = instance.content
        instance.toxic_ratio = predict(comment, toxic_model, tfidf, TOXIC_MODEL_PATH)
        instance.severe_ratio = predict(comment, severe_model, tfidf, SEVERE_MODEL_PATH)
        instance.obscene_ratio = predict(comment, obscene_model, tfidf, OBSCENE_MODEL_PATH)
        instance.threat_ratio = predict(comment, threat_model, tfidf, THREAT_MODEL_PATH)
        instance.insult_ratio = predict(comment, insult_model, tfidf, INSULT_MODEL_PATH)
        instance.hate_ratio = predict(comment, hate_model, tfidf, HATE_MODEL_PATH)
        instance.toxic_words = process_comment(comment, TOXIC_WORD_PATH)
        instance.severe_words = process_comment(comment, SEVERE_WORD_PATH)
        instance.obscene_words = process_comment(comment, OBSCENE_WORD_PATH)
        instance.hate_words = process_comment(comment, HATE_WORD_PATH)
        instance.insult_words = process_comment(comment, INSULT_WORD_PATH)
        instance.threat_words = process_comment(comment, THREAT_WORD_PATH)
        lstm_predicts = predict_LSTM(comment, tokenizer)[0]
        instance.L_toxic_ratio = round(lstm_predicts[0] * 100, 4)
        instance.L_severe_ratio = round(lstm_predicts[1] * 100, 4)
        instance.L_obscene_ratio = round(lstm_predicts[2] * 100, 4)
        instance.L_threat_ratio = round(lstm_predicts[3] * 100, 4)
        instance.L_insult_ratio = round(lstm_predicts[4] * 100, 4)
        instance.L_hate_ratio = round(lstm_predicts[5] * 100, 4)
        instance.save()
        messages.success(
            self.request, 'Your comment has been update!'
        )
        return redirect('detail', instance.pk)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'delete.html'
    success_url = '/'
    context_object_name = 'SMS'

    def delete(self, request, *args, **kwargs):
        messages.warning(
            self.request, 'Your comment has been deleted!')
        return super().delete(self, request, *args, **kwargs)


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('index')
