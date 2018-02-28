# Releasing

1. Make sure you've run the dev environment setup instructions in the README.
1. Run `source env/bin/activate`
1. Bump the version using: `make bumpversion_patch` or `make bumpversion_minor` or `bumpversion_major`.
1. Build and publish: `make release`.  This will publish the package, and push the commit and tag to GitHub.
1. Draft and publish a [new release on github](https://github.com/percy/python-percy-client/releases)
