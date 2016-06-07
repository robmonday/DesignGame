//alert("it worked!");

$(document).ready(function() {
  StartUp();
});

/*::::::DOM CACHE::::::*/
$newGame = $("#newGame");
$message = $("#message");
$newGameBtn = $("#newGameBtn");
var arrLines = [$("#letter-line0"), $("#letter-line1"), $("#letter-line2"), $("#letter-line3"), $("#letter-line4"), $("#letter-line5"), $("#letter-line6"), $("#letter-line7"), $("#letter-line8"), $("#letter-line9")];
var arrLetters = [$("#letter0"), $("#letter1"), $("#letter2"), $("#letter3"), $("#letter4"), $("#letter5"), $("#letter6"), $("#letter7"), $("#letter8"), $("#letter9")];
var arrGuesses = [$("#guess0"), $("#guess1"), $("#guess2"), $("#guess3"), $("#guess4")];
var arrBodyParts = [$("#head"), $("#torso"), $("#rightarm"), $("#leftarm"), $("#leftleg"), $("#rightleg")];
var arrButtons = [$("#a"), $("#b"), $("#c"), $("#d"), $("#e"), $("#f"), $("#g"), $("#h"), $("#i"), $("#j"), $("#k"), $("#l"), $("#m"), $("#n"), $("#o"), $("#o"), $("#p"), $("#q"), $("#r"), $("#s"), $("#t"), $("#u"), $("#v"), $("#w"), $("#x"), $("#y"), $("#z")];

/*::::::GLOBALS::::::*/
var guesses = 0;
var goodGuess = 0;
var randomWord;
var lastUsedWord;

function StartUp() {
  HideTheBody();
  ResetPlayingField();
  HideLines();
  SetupPlayingField();
  EnableButtons();
}

function HideTheBody() {
  //hide the svg man body parts
  $.each(arrBodyParts, function() {
    $(this).css('display', 'none');
  });
}

function HideLines() {
  //hide the good guess lines until we know how many are needed for the current game
  $.each(arrLines, function() {
    $(this).css('display', 'none');
  });
}

function ResetPlayingField() {
  //remove all good guess letters
  $.each(arrLetters, function(i) {
    this.text('');
  });
  //remove all bad guess letters
  $.each(arrGuesses, function() {
    this.text('');
  });

  //reset counters and hide new game display
  guesses = 0;
  goodGuess = 0;
  $newGame.css('visibility', 'hidden');
}

function GetRandomWord() {
  //generate a randomID 
  var _randomID = Math.floor((Math.random() * 10));

  //find the word having an ID that matches the randomID
  var _randomWord = jQuery.grep(words, function(word) {
    return word.id === _randomID;
  });

  return _randomWord;
}

function SetupPlayingField() {
  randomWord = GetRandomWord();

  //never use the same random word two times in a row
  if (randomWord[0].word === lastUsedWord) {
    //request a new random word
    SetupPlayingField();
  } else {
    //track the last random word used
    lastUsedWord = randomWord[0].word;
  }

  //displays a ? and line for each letter of the random word
  for (x = 0; x < randomWord[0].word.length; x++) {
    arrLines[x].css('display', 'inline');
    arrLetters[x].text("?");
  }

}

function EnableButtons() {
  $.each(arrButtons, function() {
    //enable all alphabet buttons when a new game begins
    $(this).attr('disabled', false);
  });
}

$("#a, #b, #c, #d, #e, #f, #g, #h, #i, #j, #k, #l, #m, #n, #o, #p, #q, #r, #s, #t, #u, #v, #w, #x, #y, #z").on('click', function(args) {
  //determine if the user made a good or bad guess
  CheckGuess(args.currentTarget.innerText);
  //disable alphabet buttons once selected
  $(this).attr('disabled', true);
});

$($newGameBtn).on('click', function() {
  StartUp();
});

function CheckGuess(_guess) {
  var _arrLetters = randomWord[0].word.split("");
  var _goodGuess = false;

  //determine if the user made a good guess
  $.each(_arrLetters, function(i) {
    if (_arrLetters[i] === _guess) {
      //show the chosen letter in its proper position (good guess)
      arrLetters[i].text(_guess);
      _goodGuess = true;
      goodGuess++;
    }
  });

  if (!_goodGuess) {
    if (guesses < 5) {
      //display the chosen letter (bad guess)
      arrGuesses[guesses].text(_guess);
    }
    //game ends on the 6th bad guess
    arrBodyParts[guesses].css('display', 'inline');
    guesses++;

    if (guesses === 6) {
      GameOver("loss");
    }
  } else {
    //game ends when the entire random word is displayed
    if (goodGuess === _arrLetters.length) {
      GameOver("win");
    }
  }
}

function GameOver(_result) {
  $.each(arrButtons, function() {
    //disable all alphabet buttons once the game ends
    $(this).attr('disabled', true);
  });

  if (_result === "win") {
    $message.text("You won! Play again!");
  } else {
    $message.text("You lost. The word was " + randomWord[0].word + ". Play again!");
  }

  //allow the user to start a new game
  $newGame.css('visibility', 'visible');
}

var words = [{
  "id": 0,
  "word": "COMPUTER"
}, {
  "id": 1,
  "word": "LAPTOP"
}, {
  "id": 2,
  "word": "CODE"
}, {
  "id": 3,
  "word": "INTERNET"
}, {
  "id": 4,
  "word": "HANGMAN"
}, {
  "id": 5,
  "word": "PROGRAMMER"
}, {
  "id": 6,
  "word": "AWESOME"
}, {
  "id": 7,
  "word": "HELLO"
}, {
  "id": 8,
  "word": "CHICKENS"
}, {
  "id": 9,
  "word": "FUN"
}];