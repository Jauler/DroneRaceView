# Timer Setup

In order to enable DroneRaceView to visualize race progression and results with the context of race format - race-format-specific timer setup must be prepared.
This page lists a few such configurations.

## Prerequisites

### DroneRaceView configuration

This assumes that all the required DroneRaceView configuration is already done and all the connections (e.g. WireGuard if necessary) is established. 
See [Getting Started](getting-started.md) for more info.

### Frequency setup

In order to show frequencies in various tables, DroneRaceView takes them from the "Frequency Setup" tab in "Settings" page in RotorHazard timer.
You may setup your channels hoewer you like, but here is an example setup where channels:
- R2
- R3
- R6
- R7

are being used:

![Frequency Setup Example](../img/frequency-setup.png)

## Heats view

Heats are displayed directly from the timer, therefore configuring classes and heats in timer will immediately prompt DroneRaceView to show them.

For example, create a class called "Part 1" in RotorHazard "Format" page:

![Empty new class](../img/empty-class.png)

And then add a few heats and pilots:

![Classes and Heats](../img/class-setup.png)

This results in the following table showing up:

![Classes and Heats in DroneRaceView](../img/drone-race-view-classes-and-heats.png)


## Race formats

Currently the following result formats has been added to DroneRaceView:
- points - a results view showing a table of cumulative points of each pilot and a graph of progression. This view was used during race with "King Of The Hill" race format
- consecutives - A most common view which displays a table of pilots ranked by best consecutive time
- eliminations - A view showing elimination brackets
- finals - A view showing progression of finals where pilots compete until one of the pilots wins two times

### Consecutives

Consecutives is generally the simplest to setup.

__Step 1:__ Create a race format, which has "display=consecutives" in its name.

![Qualifier Race Format](../img/qualifier-race-format.png)

__Step 2:__ Assign this race format to the class

![Qualifier Class Setup](../img/qualifier-class-setup.png)

__Step 3:__ Do some races and verify that consecutives table is being displayed in `/results`

![Qualifier view](../img/consecutives-view.png)

Consecutive results form all classes having `display=consecutives` in its assigned race format is merged into one and shown in a single table.


### Points

__Step 1:__ In the same manner like for "Consecutives" view, prepare a Race Format which has `display=points` in its name.

__Step 2:__ In the "Race Format" setup "Points Assignment" to be "Position" (and setup point value for each position by clicking gear icon.

__Step 3:__ In the same manner like for "Consecutives view - assign this Race Format to a class intended for points accumulation

__Step 4:__ In a class for which points are being calculated - select "Ranking" to be "Cumulative Points"

__Step 5:__ Do some races, and observe the point table and progression table being shown

![Points table](../img/points-table.png)

![Points Progression graph](../img/points-progression-table.png)


### Eliminations

__Step 1:__ In the same manner like for other views - setup a race format with "display=eliminations" in its name.

__Step 2:__ Create all relevant classes (e.g. all stages and heats of elimination) with all the heats, pilots may not be assigned at this point.
For example if you are doing double elimination format for 16 pilots with FAI format - you will need three rounds (and thus three classes) in winnders track and 4 rounds (therefore four classes) in loosers track.
Hence you will need to setup 7 classes in total.

__Step 3:__ This one is a bit tricky, but one needs to fill in metadata about the class and heats for each of the classes. Metadata must include:
- track - normally "winner" or "looser" track. Each distinct track name gets its own brackets view.
- number - round number in a track. E.g. first round in winners track, second round in winners track, first round in loosers track etc.
- displayname - just a name to display in this track. This is a bit redudant, as the name is taken only from the first class in the track
- previous_connection_type - Can be "square", "straight" or null. This defines the lines between brackets.
- next connection-type - Can be "square", "straight" or null. This defines the lines between brackets.

This medatada must be formatted as JSON and added to describtion of the class. For example, if we have track: "loosers", "number": 2, "display name "Loosers elimination" and some connection types, we would get the following text:
```JSON
{"number": 2, "track": "loosers", "displayname":"2nd Elimination","previous_connection_type":"straight","next_connection_type":"square"}
```
It is very important to strictly follow JSON format.

For example here is one such example setup of the class:

![Elimination Class setup](../img/elimination-setup.png)

And once all the relevant classes are correctly setup, one gets view like this:

![Elimination View](../img/brackets.png)





