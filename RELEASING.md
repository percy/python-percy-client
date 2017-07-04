# Releasing

1. Make sure you've run the dev environment setup instructions in the README.
1. Run `source env/bin/activate`
1. Bump the version using: `make bumpversion_patch` or `make bumpversion_minor` or `bumpversion_major`.
1. Build and publish: `make release`
1. Update the release notes
