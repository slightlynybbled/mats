# Manufacturing Automated Test System (MATS)

[![Test, Document, Publish](https://github.com/slightlynybbled/mats/actions/workflows/publish.yml/badge.svg)](https://github.com/slightlynybbled/mats/actions/workflows/publish.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4b8a81bf06eb48279531756d90fe598f)](https://www.codacy.com/gh/slightlynybbled/mats/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=slightlynybbled/mats&amp;utm_campaign=Badge_Grade)

`MATS` is a hardware-oriented test environment intended for production 
testing in a manufacturing environment.  The `MATS` framework is a test 
template and test sequence executor which includes an implementation for 
basic user input and feedback.

## Features

- Test runner
- Auto-start option
- Triggered-start option (i.e. "Start Button")
- Auto-save of data
- Hardware Setup / Teardown
- Automatic teardown on exception
- Automatic GUI integration

MATS could be considered an automated test framework which imposes a 
consistent work flow and reduces the amount of mind share that you need 
to dedicate to developing automated device tests.

Checkout the [documentation](https://slightlynybbled.github.io/mats/) 
for more details!

## Example GUI

At this time, the automatic GUI is only built within `tkinter`; however, the 
techniques used to create the `MatsFrame` should be applicable to any other
GUI framework.  Contributions welcome!

Below is a screenshot created on Windows, but the linux version behaves
identically.

![GUI](docs/images/tkmats-animation.gif)

## Contribution Guidelines

Contribution guidelines are outlined in the 
[documentation](https://slightlynybbled.github.io/mats/pages/contribution_guidelines.html).

Please read before contributing!
