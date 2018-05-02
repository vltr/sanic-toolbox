# sanic-toolbox

[![Latest PyPI version](https://img.shields.io/pypi/v/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![Python versions](https://img.shields.io/pypi/pyversions/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![Version status](https://img.shields.io/pypi/status/sanic-toolbox.svg)](https://pypi.python.org/pypi/sanic-toolbox)
[![MIT License](https://img.shields.io/pypi/l/sanic-toolbox.svg)](https://raw.githubusercontent.com/vltr/sanic-toolbox/master/LICENSE)
[![Build Status](https://travis-ci.org/vltr/sanic-toolbox.svg?branch=master)](https://travis-ci.org/vltr/sanic-toolbox)

Some useful classes to work with Sanic (that might depend on what you want to do with it).

To install:

```
$ pip install sanic-toolbox
```

**NOTE**: Those are likely (and mostly) experimentations with Sanic and probably will change over time until it reaches a stable version with all _necessary_<sup>1</sup> tools working (and seamlessly).

<sup>[1]</sup> definition needed yet.


## Features

- [x] Do not monkey patch things inside Sanic
- [x] ~Make middleware workflows presumable and simple to implement~
- [x] Make simple Sanic structures "lazy" and "reusable"
- [x] Ability to work with blueprints, too!
- [x] Utilities to import Python modules dynamically (is that really necessary?)
- [ ] ~Plugin chaining~
- [ ] Support for a wide range of plugins usage
- [ ] More examples of how this can be useful
- [ ] Documentation!

## License

MIT, the same as [sanic-jwt](https://raw.githubusercontent.com/ahopkins/sanic-jwt/dev/LICENSE), where the seed of sanic-toolbox came from.
