"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    score_avg = ndb.IntegerProperty(default=0)

    def update_avg_score(self):
        """Updates average score for user"""
        score_sum = 0
        score_count = 0        
        scores = Score.ancestor(self.key)
        for score in scores:
            score_sum += score.points
            score_count += 1

        self.score_avg = score_sum / score_count




class Game(ndb.Model):
    """Game object"""
    target = ndb.StringProperty(required=True)
    remaining_letters = ndb.StringProperty(repeated=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=5)
    game_over = ndb.BooleanProperty(default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    cancelled = ndb.BooleanProperty(default=False)


    @classmethod
    def new_game(cls, user, attempts):
        """Creates and returns a new game"""
        # if max < min:
        #     raise ValueError('Maximum must be greater than minimum')
        
        word_selected = random.choice(["car", "plane", "train"])
        list_of_letters = list(word_selected)

        game = Game(user=user,
                    target=word_selected,
                    remaining_letters = list_of_letters,
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        form.cancelled = self.cancelled
        return form

    def end_game(self, won, cancelled):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost or cancelled."""
        points = 0
        attempts_made = self.attempts_allowed - self.attempts_remaining
        correct_attempts = len(self.target)

        self.game_over = True
        if won == True:  
            self.cancelled = False # makes sure a game can't be both won and cancelled
            points = int(float(correct_attempts)/float(attempts_made)*1000) # calculates the score for a game won
        else:
            self.cancelled = cancelled
        self.put()
        # Add the game to the score 'board'
        if cancelled == False:
            score = Score(user=self.user, date=date.today(), won=won, 
                guesses=attempts_made, points=points)
            score.put()
            user_object = User(self.user==User.key).get()
            user_object.update_avg_score()






class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)
    points = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses, points=self.points)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    cancelled = messages.BooleanField(6)

class GameForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(4, default=5)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)
    cancelled = messages.BooleanField(5)
    points = messages.IntegerField(6)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
