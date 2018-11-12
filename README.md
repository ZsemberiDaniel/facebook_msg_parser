```   
  \   |                                                                             |                         
  |\/ |   _ \   __|   __|   _ \  __ \    _` |   _ \   __|       _` |  __ \    _` |  |  |   | _  /   _ \   __| 
  |   |   __/ \__ \ \__ \   __/  |   |  (   |   __/  |         (   |  |   |  (   |  |  |   |   /    __/  |    
 _|  _| \___| ____/ ____/ \___| _|  _| \__, | \___| _|        \__,_| _|  _| \__,_| _| \__, | ___| \___| _|    
                                       |___/                                          ____/                   
```

# Introduction
This (for now) console application aims to help with analyzing your messenger conversations. You can search and filter
your messages, count words/regex in them, check how many messages you sent to each other, how many characters
you used, what emojis were used, who responded faster on average or even make beautiful charts like the ones below.

![Chart 1](https://i.imgur.com/Bp6KKKk.png "Character counts chart")
![Chart 2](https://i.imgur.com/o8zQfNz.png "Emoji emotions chart")
![Chart 3](https://i.imgur.com/ZHpWFzQ.png "Message distribution chart")

# Setup

You need Python 3 for this application to work and you need to download your facebook messages as JSON files.

##### Dependencies include:
  * [Colorama 0.4.0](https://pypi.org/project/colorama/) - for writing colorful console messages
  * [Texttable 1.4.0](https://pypi.org/project/texttable/) - for easily writing tables to console
  * [Emoji 0.5.1](https://pypi.org/project/emoji/) - for finding emojis and their unicode name
  * [Matplotlib 3.0.1](https://pypi.org/project/matplotlib/) - for plotting
  * [PIL 5.3.0](https://pypi.org/project/PIL/) - for handling images easily
  * [Sortedcontainers 2.0.5](https://pypi.org/project/sortedcontainers/) - for sorted lists
  * [Pyfiglet 0.7.6](https://pypi.org/project/pyfiglet/) - for ASCII character arts
  * [FTFY 5.5.0](https://github.com/LuminosoInsight/python-ftfy) - for fixing text encodings

### How to download facebook messages

1. Go to your Facebook settings <br />
![Facebook settings](https://i.imgur.com/HTZdN3T.png "Facebook settings")

2. Choose Your Facebook Information <br />
![Your Facebook Information](https://i.imgur.com/FwUeBIX.png "Your Facebook Information")

3. Choose View on Download Your Information <br />
![Download Your Information](https://i.imgur.com/fjvKNTK.png "Download Your Information")

4. Download your messages in JSON format <br />
![Download](https://i.imgur.com/q5zhCIY.png "Download")

5. It needs some time to get ready, mine was ready in a few hours, so it's not too bad. After you downloaded it unzip it
and then look for the messages folder and copy it's absolute path (with folder included). That's what you'll need to use
this application.

# How to use
You need to start `main.py` with the messages folder given to it as a parameter. After that you'll be taken to a console
([choose chat console](#choose-chat-console)) where you can choose which chat you want to analyze.

### Important definitions

  * response: response here is used as chunks of messages which are not separated by another person's message.
  * overnight messages: messages that are a response to a message from the day before.

### Consoles in general
Pipelines: you can easily chain commands via the `||` pipe symbol. For example `filter -d 2018.1.1 || write`/
`f -d 2018.1.1 || w` pipes the result of filter to a write function, which writes it out to the console.

Note that if you can enter another command line with a command you can pipe another command's inputs and then
only the remaining data will be used to start the command line. This is useful for example when you only want to
enter with this year's data: `filter -d 2018.1.1 || cmd_line`.

All consoles are capable of auto completion via the tab key. Command history is also available.

In this application a command won't write it's contents out just by calling the command, you usually need to pipe it to
the write command.

**write**, **help** and **quit** commands work in all consoles.
  * **write**: writes out the result of a pipeline, if applied by itself it is implementation dependant what it results.
    * *-f* [file_name]: You can redirect the result to a file, by giving it a name.
  * **help** (-cmd1)( -cmd2)(...): Writes out all the commands' help if no argument is given. If there are arguments
  then it only writes out the commands that are given as arguments.
  * **quit**: quits the current console. If there is a parent console (that started this one), it exits to that,
  otherwise it exits the application.

### Choose chat console
In this console you can choose which conversation you want to analyze.

##### Commands
  * **write**: Writes out the names of the conversations you have, so you can choose one.
  * **choose** [name]: You can choose one of your conversations this way. The name needs to be a substring of the
  conversation you want to choose. It is case insensitive. It opens a [chat console](#chat-console). First time
  choosing a conversation might take a while because it corrects some errors that come from downloading the file
  from Facebook, but after that it only takes a few milliseconds.
  * **filter** [name]: You can filter the conversations this way, by searching for a substring in the names of
  conversations. Mostly used with **write**: `filter apple || write`

### Chat console
This is where most of the fun happens.

##### Commands
  * **write**: writes out all the messages in this conversation.
  * **basic**: pipes basic data about the conversation for each participant. Examples are: message count, character
  count, response times (overnight responses included and not included), most used emoji etc.
  * **filter**: filter the messages by some attribute. Pipes the filtered messages.
    * *-d [year.month.day] [year.month.day]*: filter for the date of messages. The first one is from when and the second
    one is till when.<br />
    If no till date is given then today will be the till date.<br/>
    You can omit the from date with '_'. If no from date is given then it will be piped from the start of conversation.
    * *-p participant1(,participant2)(,participant3)(...)*: filters for participants.<br/>
    The names are checked with them being converted to lower case ASCII characters and as a substring of the real names
    of participants.<br />
    If more names are given separated by commas then the logical operator between them is or.
  * **search** [switches] [search_for]: searches in the content of the messages then pipes them forward.
    * *-h*: it will search for whole words.
    * *-r*: search_for will be treated as a regex expression. (-h is ignored)
    * *-i*: ignores cases
  * **count**: counts the messages then pipes the result forward.
    * *-p*: participants will be counted separately.
  * **chart**: makes charts. Omit every switch to get all the charts in default sizes.
    * *-m*: plots message count <br />
    ![Message count](https://i.imgur.com/AOfvWAj.png "Message counts")
    * *-c*: plots character count <br/>
    ![Character count](https://i.imgur.com/Bp6KKKk.png "Character counts chart")
    * *-d*: plots message distribution over hours <br>
    ![Message distribution](https://i.imgur.com/ZHpWFzQ.png "Message distribution chart")
    * *-e*: plots emojis <br/>
    ![Emojis cut](https://i.imgur.com/CWF8YDW.png "Emojis cut")<br />
    This image continues here: [Emojis](https://i.imgur.com/B1E7oRf.png "Emojis")
    * *-ey*: plots emojis yearly
    Same as the one before, except it groups them in years <br/>
    [Emojis yearly](https://i.imgur.com/QbQtz3u.png "Emojis yearly")
    * *-em*: plots emoji emotions <br />
    ![Emotions](https://i.imgur.com/o8zQfNz.png "Emoji emotions chart")
    * sizing:
      * *-sa [width]\(x[height])*: with this you can specify a size for all charts.
        * For emoji and emoji yearly charting height will be ignored. If only width is given then that will be used to
        calculate the height.
      * *-s [width]\(x[height])*: if you add this after a chart's switch you can specify only it's size, overriding the
      -sa.
        * Example: `chart -m -c -em -s 1000x2000 -sa 2000x1000`.
        Here the -m and -c will be 2000x1000 but the -em will be 1000x2000
    * other
      * *-r [count]*: you can specify how many emojis per row you want in for example -e or -ey
  * **markov** [layer_count]: you can enter the [markov console](#markov-console)
  * **emoji**: pipes forward only the messages that contain emojis
    * *-o*: rips the text from the messages (they only contain emojis)
    * *-a*: completely changes the behaviour of this command. With this you can enter the
    [emoji console](#emoji-console).
  * **titles**: You can pipe forward the top titles, for example most loving person, etc.
    * (If you omit which titles you want, you'll get all categories)
    * *-p*: Write out people category
    * *-m*: Write out month category
    * *-c [count]*: How many titles you want to write out per category

### Markov console
This console makes a Markov chain from your conversation. A markov chain analyzes the words you've used so far in this
conversation and can make up it's own sentences randomly based on that. Most of the time it makes funny incoherent
text, but if you choose your layer count right you can get some pretty good text.

**Layer count**: If you haven't spoken much in a conversation I would advise you to use a smaller layer count first. Start off with 2
and the lower them if it only takes sentences from the conversation and places them here and increase it if
it's too incoherent.

##### Commands:
  * **layer** [count]: the layer count can be changed with this.
  * **words** (switches) [count]: generate count amount of words with this command
    * *-p participant1(,part2)(,part3)(...)*: you can specify for which participant(s) to generate the words. From the
    2nd participant they are all optional.
    * *-a*: you can get words from the whole chat (involving all participants, not individuals).
    If participants are specified along with then still all participants will be included

### Emoji console
With this console you can analyze the emojis in your chat.

##### Commands
  * **write**: by itself it's not interpreted
    * *-d*: the dates of the emojis are written out as well (if it makes sense to write them out)
  * **filter**: works just like the filter command in the chat data console.
  * **top**: pipes top emojis per participant forward
    * *-c [count]*: how many emojis to forward
  * **overtime**: pipe forward the emojis/emotions overtime. That means which was the top emoji in a given month over
  the period, when the chat was active.
    * *-t*: if you want emotions instead of emojis with this switch.
    * *-m*: if you want the time period (for which we check the top) to be one month, add this switch.

# How the code works
MVC approach was used for dividing the code into parts.

### Model
The data classes are contained in `data.data.py`.
  * Reaction: a reaction to a message.
  * Message: a message in a conversation. Contains the photos, gifs, shared and reactions to the message. A special message
  is one with either a photo, gif or share.
  * Participant: just contains the name of the participant.
  * Response: a chunk of messages which were sent by the same participant not far from each other.
  * Chat: contains messages (in chronological order) and participants of a conversation.
  
There are also some data classes which contain data about facebook emojis. We read these from the `img/data.txt`.
  * Emoji: contains the name, aliases, codes, image path and emotions of a facebook emoji.
  * FacebookEmojis: a class that contains all the facebook emojis, so we can get an emoji by it's UTF-8 code with
  the help of this class.
  
### Controller
There are 2 types of controller classes: ones that get data from the files and ones that provides data for the view.
The ones that get data from the files are:
  * chat_decoder.py
    * Contains logic to decode and encode the data classes to JSON.
    * Can load data from the json files provided by the user.
  * folder_traversal.py
    * Goes through the folders provided by the user and gets the path to all of the user's conversations.

The ones that provide data for the view:
  * data_visualizer.py:
    * Contains all the plotting. Also saves the charts to files.
  * chat_analyzer.py:
    * Contains all the useful function for analyzing a chat. There are multiple types: character count analyzer,
    message analyzer (count, time), response analyzer (count, time), emoji analyzer, searching functions, date
    functions, misc functions.
    * All the functions require a chat instance but may return different values. Some return values can be
    quite complex, so when in doubt refer to the function documentation.
  * title_analyzer.py
    * Contains function which give out titles to the different attributes of a chat.
    * Each function can be given a category. For example there are function that return titles for the people
    in the chat (Most loving one, Most educated one, etc.).
    * Each of these categories have a separate collect function, which collects all the titles into one list
    and gives them the names, and a top function, which returns the ones which best fit the chat.
    
##### Markov chains

Markov chains are implemented in the `controller.markov.markov_chain.py` file. A `MarkovChain` has a `MarkovState`
variable which has transitions to other `MarkovState`s. It depends on the `layer_count` how many times we can go
down this tree of `MarkovState`s. For example if the `layer_count` is 3 then there are 2 `MarkovState`s which have
other `MarkovState`s in transitions, but the last one has no transitions, only states.
```
                                        5
                                       +---> MState(boy)
                                       |6
                            11  (eater)+---> MState(girl)
                           +--->MState +
                           |
                           |3   (hater) 3
                           +--->MState +---> MState(please)
                           |                 1
                           |5               +----> MState(.)
               19   (apple)+--->MState(good)|4
              +---->MState +                +----> MState(-)
              |
              |                 30    (would) 30
              |                +----->MState +-----> MState(we)
   95  (None) |47              |5                      +----> MState(I)
MC +-> MState +---->MState(why)+----->MState(am)+------+ 3
              |                |12                     +----> MState(is)
              |                +----->MState+--+         2
              |                       (have)   |12
              |29                              +------> MState(you)
              +---->MState+5                       1
                    (nice)+---->MState(boots) +--+------> MState(man)
                          |                      | 4
                          |9                     +------> MState(hehh)
                          +---->MState+--+9
                          |     (face)   +----> MState(you)
                          |15            10
                          +---->MState +-------> MState(not)
                                (code) | 3
                                       +-------> MState(but)
                                       | 1
                                       +-------> MState(you)


```
Here you can see a `MarkovChain`, where each arrow is a `MarkovTransition` and each number shows the transition's
chance to happen. For example if we start from the MC(`MarkovChain`) node we can go to `MState(nice)` with a chance of
`29/(47 + 19 + 29)`, from there we can go to `MState(code)` with a chance of `15/(5 + 9 + 15)`, from there we can go to
`MState(not)` with a chance of `10/(10 + 3 + 1)`. So we can reach `nice code not` with a chance of 
`(29 / 95) * (15 / 29) * (10 / 15) = 10 / 95`. After we got these words we can traverse down the tree via `code not`
to get a `MarkovState` that has these two as starting words and can ask for the next word randomly. Then do
the traversing down again and ask for a random word again. Rinse and repeat and you have yourself a text generator.

Note: because of the inner workings of a markov chain if you set it's layer count to be 2, it
will result in a layer count of 3, because the first one (`MState(None)`) is seen as one as well.

### View
##### Consoles
The consoles are implemented with one class being all of their parent class. That class is `view.console_input.py`.
It's a basic command interpreter. This implements basic **write**, **quit** and **help** functions. We can easily
add new command via the `add_command()` or `add_commands()` function. We need to provide aliases for this command
along with two lambdas: one that gets a console instance, the switches of a command, kwargs for a command and has
to execute the command. It can also return a dictionary which is then later added to the kwargs. This is how the
pipeline works. The other lambda we need to provide is the help lambda, gets nothing but needs to write out
the help for the command.

This console implementation also has some neat features: `_get_write_string()` can be implemented which then
later is used to write out the result of a pipeline. It gets passed the kwargs used along the pipeline.

You can also add a welcome and a quit message to the console.

##### Console implementations
The console above is implemented in the other consoles with help functions as static functions and command
execution function as member function. At the top of the class all commands can be seen, and then easily followed
to the help or execution function.

##### Console manager

The console manager can be used to manage more consoles easily. With this the consoles have no need to start their own
child consoles because this manager starts it for them. This has the advantage of being able to reach the current and
other consoles from the whole application and not just from the parent console. (Good for testing for example).

The manager runs on a separate thread and does the input handling instead of the consoles themselves. You can also
switch between consoles on the fly, and simply put the other console in the background.

##### Command history
Currently the built-in python command history functions are being used, which are in `readline`. In `console_init.py`
the setup happens and all the commands are written to `.msg_parser_history`. All consoles share one command history,
there is no separate command history for each console.

##### Auto complete
Auto completion is also available in the console via `readline`. All commands have a separate auto complete function
and that gets called in `console_input.py` based on what we want to complete. If we only want to complete the current
command then that gets handled by itself, but if we want to complete one of the parameters of the command then
the function implemented by the user gets called, which should return a list of possible candidates for completion.

The console manager also supports auto completion by setting and removing the correct auto completer when a console
switch happens.

##### Commands across consoles

There are commands which can be used in more consoles. Those are grouped in `view.commands` package. They all have
every function needed (command function itself, help function, auto complete, others if needed in the future)
in the file itself.

### Testing
In this application testing is used to test the commands in the command lines with edge cases and more complex commands.
Python unittests are used and all of them are in the `test` directory with conversations used for testing in `test.messages`.
All tests can be executed with `all_tests.py`.

For now testing the algorithms themselves is not implemented because in my opinion it's unnecessary to write test cases
for simple counting, max and min search algorithms. All the edge cases are tested via the command line.

## Oh god why
With the help of piping you can chain commands together which you may have not expected work:

```
basic || write || filter -d 2018.1.1 || write -f "out.txt" || search -i -r "p[eo]*p" || write || markov 2 || count -p || write
```

This gets executed and does the following in order:
  1. Writes out basic information about the chat `basic || write`
  2. Filters for messages after 2018.1.1 then writes them out to out.txt `f -d 2018.1.1 || w -f "out.txt"`
  3. Searches for the regex `p[eo]*p` with ignored case and then writes out the result (Note that this only searches
  in messages after 2018.01.01) `s -e -r "p[eo]*p" || w`
  4. Enters the markov command line with a layer count of 2 `markov 2`
  5. Counts the messages for each participant (that are left after filter and search) and then writes them out
  `count -p || write`
  6. After all that we are in the markov command line and we can do whatever we want in there
  
I'm not completely sure why you would do something like the command above (maybe this tool gets taught somewhere and
and the command above is a good test question), but hey, it works so please use stupid commands like the one above.

##### Entering multiple command lines
You can do
```
markov 1 || markov 2 || markov 3 || markov 4 || markov 5 || markov 6 (...)
```
as many times as you want. You can also sprinkle other consoles in there. This will result, first of all, if you did
it just enough times in your computer crashing. After restart you do it too many times again, so it crashes again.
Third time you get the number right and you have yourself, what I call is a console-ception. You have a console inside
another console inside another console inside... You get it. The console you are currently in is the last one.
You can quit from them via `quit`/`q`. Have fun and be safe!