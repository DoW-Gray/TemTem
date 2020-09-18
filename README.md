# TemTem
An open-source TemTem code library

## Purpose
I put a detailed explanation of why I created this library [here](
https://www.playtemtem.com/forums/threads/a-temtem-code-library.9687/#post-50309
).

Previously no code was available, and formulas and mechanics were often tricky
to track down, lacking information, and sometimes I couldn't find them online
at all.

My hope is that an open-source library of TemTem code should allow anyone who
wants to create something TemTem-related can do so much more easily, and be
much more confident that their code will output the correct result.

## Language
Python3.8 was chosen for a number of reasons:
 - It's an easy language to learn and that's the first language many people are
    taught, making this more accessible.
 - It's practically pseudocode, so if you want to use another OO language it
    should be pretty simple to translate over.
 - It's the most fun to use, and the language I'm most used to using.

## Completeness
- [x] Import / Export TemTems from the text format
- [x] Correct stat calculation, including boosts
- [x] Static data for all tems and attacks, which can be read into python
- [x] Damage calculation, excluding weird things like Traits, Items, or
    Hyperkinetic Strike
- [x] Statuses (mostly done, but a few things left to handle)
- [ ] Handling stamina (mostly done)
- [x] Most move effects e.g. boosting stats (shouldn't take much effort)
- [x] Handling Traits
- [x] Handling Items
- [ ] Actually simulating a whole battle - there's a few more things that need
    to be coded for this, e.g. attack targeting, move priority, move hold, what
    happens to tems that are switched out, etc.

## Data
Most of the mechanics details are taken from the
[temtem wiki](https://temtem.gamepedia.com/Temtem_Wiki), with some details
taken from my own research or discussion on discord, with results from these
often then being uploaded to the wiki.

Temtem and Move data were initially taken from the wiki, but are now being
taken largely from [maael's api](https://github.com/maael/temtem-api/).

Sets data is taken from [temtemstrat](https://temtemstrat.com/en/strategic-rank).

## Contributing
Please feel free to add to this codebase! If you'd like to work on one of the
above points, or have an idea you'd like to build, please feel free to talk to
me about it, or even just start working on it!

Pull requests are also welcome! It would be great if you could confirm that
pytest and flake8 pass. Adding your own tests would also be helpful!

## Licensing and Credits
All code is copyright (c) DoW 2020, and licensed under GPL 2.0.

Thanks to the wiki contributors, various discord users, Maael, and the guys at
temtemstrat for the various information they made publically available, that
was used here.
