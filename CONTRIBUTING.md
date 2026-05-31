# flatpak-indicator

## Setup

```bash
sudo apt install python3-gi gir1.2-ayatanaappindicator3-0.1 gir1.2-notify-0.7 flatpak debhelper
```

or you can use the older `gir1.2-appindicator3-0.1` in place of `gir1.2-ayatanaappindicator3-0.1`

## Development Tasks:

* Install dependencies: `make install`
* Run dev: `make run`
* Run the test suite: `make test`
* Run lint checks: `make lint`
* Auto-format: `make format`
* Build deb package: `make build`

## This project uses:

* [poetry](https://python-poetry.org/) for dependency management
* [flake8](https://pypi.org/project/flake8/) for linting and
* [black](https://github.com/psf/black) for code formatting
* [isort](https://github.com/timothycrosley/isort) for import sorting
