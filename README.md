# Railgun

Railgun is a very simple tool to send emails using MailGun e-mail sending service.

## Dependencies

Railgun uses `python3` and requires `requests` library to function properly.
All other dependencies are present in Python 3's standard library.

## Installation

Railgun can be installed anywhere in your system. By default, the Configuration
file is searched under `../conf` file, but this can be also changed from the
beginning of the code.

## Configuration

Railgun needs some configuration before becoming operational. Most of this
configuration is related to MailGun itself. An example configuration file is
included in `conf/` folder with `railgun.conf.example` name.

Copy the file as `railgun.conf` and fill the options. Options are self
explanatory.
