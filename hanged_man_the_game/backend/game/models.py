from django.db import models

class Execution(models.Model):
    execution_id = models.AutoField(primary_key=True)
    games_to_play = models.IntegerField()
    min_letters = models.IntegerField(default=2)
    max_letters = models.IntegerField(default=128)
    language = models.CharField(max_length=128)

    class Meta:
        db_table = 'execution'
        app_label = 'game'


class Word(models.Model):
    word_id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=128)
    language = models.CharField(max_length=128)
    letters = models.IntegerField()

    class Meta:
        db_table = 'word'
        app_label = 'game'


class GameResult(models.Model):
    game_result_id = models.AutoField(primary_key=True)
    execution = models.ForeignKey(Execution, on_delete=models.RESTRICT)
    word_to_guess = models.ForeignKey(Word, on_delete=models.RESTRICT)
    remaining_lives = models.IntegerField()
    used_letters = models.CharField(max_length=256)  # Added max_length
    won = models.BooleanField()

    class Meta:
        db_table = 'game_result'
        app_label = 'game'


class GameStep(models.Model):
    game_step_id = models.AutoField(primary_key=True)
    game_result = models.ForeignKey(GameResult, on_delete=models.RESTRICT)
    guess = models.CharField(max_length=2)

    class Meta:
        db_table = 'game_step'
        app_label = 'game'