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



