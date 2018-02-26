# Railgun

Railgun is a very simple tool to send emails using [Mailgun](https://www.mailgun.com) email sending service.

## Dependencies

Railgun uses `python3` and requires `requests` library to function properly.
All other dependencies are present in Python 3's standard library.

## Installation

Railgun can be installed anywhere in your system. By default, the configuration
file is searched under `../conf/railgun.conf` file, but this can be changed
from the beginning of the code.

## Configuration

Railgun needs some configuration before becoming operational. Most of this
configuration is related to Mailgun itself. An example configuration file is
included in `conf/` folder with `railgun.conf.example` name.

Copy the file as `railgun.conf` and fill the options. Options are self
explanatory.

## Usage

After setting up Railgun, usage is simple. Only required parameters are
`subject` and `body`. `Body` can be multiline or HTML. Just pass as
it is (Between quotations), and Mailgun will take care of the rest.

Railgun can be invoked directly as `./railgun SUBJECT BODY`. Railgun
will check whether its configuration is sane and will report any errors
if something goes wrong, unless `--quiet` switch is set. In `--quiet`
mode, Railgun reports nothing including critical errors. In that case,
observing the return code of the Railgun will inform the caller whether
the execution was successful or not. Railgun will return `0` if
everything is alright, or will return `1` otherwise. 
