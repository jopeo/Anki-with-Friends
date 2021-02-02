# Change Log
## v1.21  11/20/20
- Order of cards displayed in Battle Deck changed from Due Priority to Random
- Deck progress algorithm optimized to account for users with 3 steps in New and Lapses

## v1.25  11/22/20
- Added radiobuttons on home window so players can choose the order that Battle Deck cards are displayed
- Fixed problem with communications when either player does not receive full Battle Deck size
- Added button on home window to set status as "Away"
- Changed "In Battle" values from "True" and "False" to "Yes" and "No"
- Optimized stylesheet background color for both Night Mode and non-Night Mode compatibility
- Changed text strings in battle window display table to more accurately reflect player status
- Battle Deck progress algorithm optimized to account for cards buried or suspended during battle

## v1.26  11/23/20
- Fixed battle window progress bar issue with starting at a nonzero percentage or unable to reach 100% with all cards answered
- Improved progress bar responsiveness. Fixed formatting of text labels in Battle Anki Request window
- "Send ittt" pushbutton renamed to "Send Request". Communications issue addressed in v1.23 update is now fixed for matched decks also

## v1.27  11/23/20
- Fixed label cycling on Set Away Status / Set to Ready pushbutton

## v1.28  11/26/20
- Fixed problem with opponent's progress bar resetting to 0% after reaching 100%

## v1.32  12/21/20
- Holiday Edition and badges and timing added

## v1.33  12/26/20
- Marathon Mode now toggleable. Multiplayer up to 6 players in one battle
 
## v1.35  12/29/20
- Added ability to join a battle in progress. Updated some aesthetics

## v2.08  12/31/20
- New Year's edition

## v2.10 1/5/21
- Compatible with Anki version 2.1.38
#### Changes to the UI
- Holiday images removed to avoid distraction
- Options now selected in pop-up window
- Several URL links added to assist in USMLE Step 1 studies
#### Backend changes
- Improved thread handling
- sys.exit is no longer called from the addon
- User profile dialog can now be accessed without having to restart Anki and disable Battle Anki

## v2.12 1/6/21
- Fixed error at end of battle
- Consolidated code, implemented several functions where applicable
- Logging implemented, all files stored locally on client machine

## v2.22 1/10/21
- Fixed error with deck names consisting of two words
- Spinbox for number of cards of Battle Deck now in Battle Window as well as Options Dialog
- Minor backend changes

## v2.24 2/1/21
- Fixed startup error
- Fixed error with Options dialog and Join function
- "Window close" button now accessible in Options dialog (and keeps changes).