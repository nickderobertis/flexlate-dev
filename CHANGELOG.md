# Changelog

All notable changes to this project will be documented in this file. See
[Conventional Commits](https://conventionalcommits.org) for commit guidelines.

## [0.21.0](https://github.com/nickderobertis/flexlate-dev/compare/v0.20.0...v0.21.0) (2023-01-28)


### Features

* Add auto-commit logic and clean up extra arguments for back sync ([09d8106](https://github.com/nickderobertis/flexlate-dev/commit/09d810658bfe04e95d6dbda1d325936dd087395b))
* Back-sync seems to be fulling working e2e with test ([69125a8](https://github.com/nickderobertis/flexlate-dev/commit/69125a89da7c066e0b2c1b641d9e13644ca2ee91))
* Get basic back sync logic working, and add untested back sync server logic ([509781e](https://github.com/nickderobertis/flexlate-dev/commit/509781ef83495fd9bf0f7c9d89363dc5f20ceaa6))
* Hook up back sync functionality on a background thread ([4b31e08](https://github.com/nickderobertis/flexlate-dev/commit/4b31e08e57bbcb94f2814f1ee4b07df77dd465f1))
* Show styled commit during back sync and remove a finished TODO ([d0446c6](https://github.com/nickderobertis/flexlate-dev/commit/d0446c6317c40d47edd83133ecfa46d6f737c22b))


### Bug Fixes

* Ensure back-sync does not sync the forward-sync commits. Also support multiple user commits in one server cycle ([f4242a0](https://github.com/nickderobertis/flexlate-dev/commit/f4242a02d7d55a6a6213fab1dbdb4f345d568e18))
* Fetch full git history when running tests as now tests depend on it ([85fd700](https://github.com/nickderobertis/flexlate-dev/commit/85fd700d00335ec64dbb4836afa9c977b2bf2718))
* Fix behavior for pure renames and add test ([7418fd7](https://github.com/nickderobertis/flexlate-dev/commit/7418fd7ce2bdaeb66fb577a37e5f9003b084dca3))
* Fix typing and install issues ([a56252b](https://github.com/nickderobertis/flexlate-dev/commit/a56252b16f363790c650f0c40dae480ded2aa3cd))
* Fix versions and lock poetry ([aedce03](https://github.com/nickderobertis/flexlate-dev/commit/aedce03251a7627040f15cfd19020fb5224174a4))
* Get back sync basically working e2e, need better test setup ([f2fccca](https://github.com/nickderobertis/flexlate-dev/commit/f2fcccacb9368f576ace420facd9de8f9fe52c39))
* Pause regular sync during back sync ([69b6188](https://github.com/nickderobertis/flexlate-dev/commit/69b6188ce686abeada05b340bf46ebf47046ef5e))
* Properly handle output subdirectory in templates for back sync ([b72dc6c](https://github.com/nickderobertis/flexlate-dev/commit/b72dc6c364fa52c8ed65016f6f71c3a91023e806))
