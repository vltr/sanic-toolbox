# sanic-toolbox

[![Latest PyPI version](https://img.shields.io/pypi/v/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![Python versions](https://img.shields.io/pypi/pyversions/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![Version status](https://img.shields.io/pypi/status/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![MIT License](https://img.shields.io/pypi/l/sanic-toolbox.svg)](https://raw.githubusercontent.com/vltr/sanic-toolbox/master/LICENSE)


Some useful classes to work with Sanic (that might depend on what you want to do with it).

To install:

```
$ pip install sanic-toolbox
```

_NOTE_: Those are likely (and mostly) experimentations with Sanic and probably will change over time until it reaches a stable version with all necessary tools working (and seamlessly).


## Features

- [x] Do not monkey patch things inside Sanic
- [x] Make middleware workflows presumable and simple to implement
- [x] Make simple Sanic structures "lazy" and "cloneable"
- [x] Ability to work with blueprints
- [ ] Plugin chaining
- [ ] More examples of how this can be useful

## License

MIT, the same as [sanic-jwt](https://raw.githubusercontent.com/ahopkins/sanic-jwt/dev/LICENSE), where the seed of sanic-toolbox came from.
