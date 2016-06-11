"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

# JSON include --------
import json
from pprint import pprint

with open('words.json') as data_file:    
    data = json.load(data_file)
pprint(data)
# JSON include --------

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    score_avg = ndb.IntegerProperty(default=0)

    def update_avg_score(self):
        """Updates average score for user"""
        print "update_avg_score method called from within user object"
        score_sum = 0
        print score_sum
        score_count = 0        
        scores = Score.query(Score.user==self.key) # Score.key==self.key ...need to add filter to get only scores for THIS user
        
        for score in scores:
            print "+ "+ str(score.points)
            score_sum += score.points
            score_count += 1
            print "= "+str(score_sum)

        print "scores counted: "+str(score_count)

        if score_count > 0:
            self.score_avg = score_sum / score_count
            self.put()

    def to_form(self, message):
        """Returns a UserForm representation of the User"""
        form = UserForm()
        form.name = self.name
        form.score_avg = self.score_avg
        return form

class Game(ndb.Model):
    """Game object"""
    target = ndb.StringProperty(required=True)
    remaining_letters = ndb.StringProperty(repeated=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=5)
    game_over = ndb.BooleanProperty(default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    cancelled = ndb.BooleanProperty(default=False)
    history = ndb.StringProperty(repeated=True)
    current_state = ndb.StringProperty()

    def generate_current_state(self, remaining_letters, target):
        original_letters = list(target)
        print original_letters
        current_state_build = ""
        for letter in original_letters:
            try:
                letter_index = remaining_letters.index(letter)
                current_state_build += remaining_letters[letter_index]
                print current_state_build
            except:
                current_state_build += "_"
                print current_state_build
            current_state_build += " "
        return current_state_build

    @classmethod
    def new_game(cls, user, attempts):
        """Creates and returns a new game"""
        word_selected = random.choice(data["words"])
        list_of_letters = list(word_selected)

        game = Game(user=user,
                    target=word_selected,
                    remaining_letters = list_of_letters,
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False, 
                    current_state=generate_current_state(list_of_letters, word_selected))
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
        form.current_state = self.current_state
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
            if attempts_made == 0:
                points = 1000 # to prevent possible division by zero
            else:
                points = int(float(correct_attempts)/float(attempts_made)*1000) # calculates the score for a game won
        else:
            self.cancelled = cancelled
        self.put()
        # Add the game to the score 'board'
        if cancelled == False:
            score = Score(user=self.user, date=date.today(), won=won, 
                guesses=attempts_made, points=points)
            score.put()
            # print "game result recorded in scores table!"

            user_object = User.query(self.user==User.key).get()
            # print "user record queried " + user_object.name

            user_object.update_avg_score()
            # print "update_avg_score called for " + user_object.name

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
    current_state = messages.StringField(7) # show which letters are missing: maybe '_ _ g' (for 'dog')

class GameForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, default=5)

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

class UserForm(messages.Message):
    """UserForm for outbound user state information"""
    name = messages.StringField(1, required=True)
    score_avg = messages.IntegerField(2, required=True)

class UserForms(messages.Message):
    """Return multiple UserForms"""
    items = messages.MessageField(UserForm, 1, repeated=True)

class GameHistoryForm(messages.Message):
    """GameHistoryForm for outbound game history information"""
    urlsafe_key = messages.StringField(1, required=True)
    history = messages.StringField(2, repeated=True)
    game_over = messages.BooleanField(3, required=True)
