# Release automation

This repository was used to test a new release automation setup for various packages I
work on. It's left here as a kind of template or example to grab bits (or the whole
setup) from as needed.

## How it works

### Branching model

The setup in this repository assumes the use of a modified versien of git-flow.
Development takes place on the `develop` branch, with new additions merged into there.
When the time to make a release comes, `develop` is merged into the `main` branch using
a merge commit. That commit gets tagged with the version, and then (unlike in git-flow)
`main` is merged back into `develop`. From that point on, development can continue using
feature branches as usual. Both `main` and `develop` can be protected branches, into
which you can't push directly.

Releases are made by merging `develop` into `main` using a pull request. There's no
release branch, only a direct merge. When a pull request into main is created, the
`prepare_release` workflow will be run by GitHub Actions.

### Release preparation workflow

This workflow will parse the title of the pull request, which must be `Release x.y.z`,
and the `CHANGELOG.md` file in the root of the repository, which must have a header `##
x.y.z` for each release and the latest release at the top. The versions are
cross-checked against each other, and an error will be posted to the PR if they do not
match.

If they do, the release notes for the version to be released will be extracted from
`CHANGELOG.md` and appended to the contents of `docs/source/overview.txt` to create the
release notes that will be shown on the GitHub release and on Zenodo, and a preview of
which is posted to the release PR.

Finally, Python packages are built and tested with `twine check`, to ensure that any
issues with the package definition can be fixed before releasing.

If all the tests pass, check the posted description of the release carefully for any
mistakes, and, if set up, check that the documentation is building correctly on
ReadTheDocs. If an error occurs or something is still not good, just add more commits to
`develop` fixing things until the `prepare_release` workflow (which will re-run
automatically on every change) passes.

### Release workflow

When everything is ready, the PR is merged using a merge commit, and the `do_release`
workflow automatically runs. This will tag the new commit on `main` with an annotated
tag `vx.y.z`, taking the version number from the change log, then merge `main` back
into `develop`.

Next, a release is made on GitHub, with the description created from
`docs/source/overview.txt` and `CHANGELOG.md` as described above. If Zenodo integration
is configured, then Zenodo will make a new record for it automatically, using the
release description. This is why `docs/source/overview.txt` is there, because only a
list of changes isn't very useful if you blunder into the Zenodo record and don't know
what the software is about.

When the release is tagged, Python packages are built and uploaded to TestPyPI and/or
PyPI automatically. You may want to disable one or the other workflow.

### Version management

Usually, you'll want to have the current version of your software available in a couple
different places. Git, so you can find back a particular released version, the metadata
of any package, so that users can install the right one, and the documentation, so that
users can read the right version of it.

To keep everything consistent, the git tags are the only source of version information,
with everything else picking up the version from there. We use `setuptools-scm` to pick
up the version from the git tags automatically when a Python package is built, and the
Sphinx configuration imports the package and gets its version tags for use in the
documentation, with a fallback to git and if that fails, "develop".

## Setting things up

Setting all this up involves connecting a bunch of cloud services together, and that's
always finicky, but hopefully it'll go fairly smoothly with these instructions.

### GitHub

The automation for all this relies on four workflow files, which you'll find in
`.github/workflows`, and need to put in the same directory in your repository. You'll
want to replace the instance of "Sanotehu" in `create_release_description.yml` with the
name of your package. In `do_release.yml`, you may want to add `if: false` to either
`publish-to-testpypi` or `publish-to-pypi` to disable either as you're setting things
up.

You don't have to protect the `develop` and `main` branches, but it's good practice and
this set-up allows it. Navigate to your repository's settings on GitHub, select Rules ->
Rulesets on the left, then create a new ruleset. Set `main` as a target branch, and
choose the restrictions. For this repository, the following are set:

- Restrict deletions
- Require a pull request before merging
- Require status checks to pass
- Block force pushes

For "Require status checks to pass", you'll need to specify which ones are required. If
you have the workflows on GitHub, then you should be able to select "Describe release
for an admin to check that all is well". This workflow job will only run if no errors
were detected.

Save the ruleset, then create another one, this time for `develop`. You can set the same
restrictions, including "Require a pull request before merging". That's a good idea, but
it does require building a way for the workflow to circumvent this protection, so that
it can merge `main` back into `develop` during the release.

To do that, we can [use a deploy
key](https://github.com/orgs/community/discussions/25305#discussioncomment-10728028).
This needs to be generated locally, using (on GNU/Linux):

```
ssh-keygen -t ed25519 -C "myemail@example.com" -f deploy_key
```

where you replace the email address with your own. This will ask you for a password,
which must be empty (just type Enter). You'll now have two files, `deploy_key` and
`deploy_key.pub`.

Go to your repository on GitHub, open the Settings, then select Deploy keys on the left.
Add a new key with a descriptive name, and paste the contents of `deploy_key.pub` into
the Key field. Check the "Allow write access" box, then add the key.

Go back to Rulesets, edit the ruleset for `develop`, and use the "Add bypass" button to
add a bypass for "Deploy keys". Select "Exempt" for the type of bypass, and save the
ruleset using the button at the bottom.

### Pyproject.toml

Setting up setuptools-scm in `pyproject.toml` is quite easy, just add it to the build
requirements and then put `dynamic = ['version']` in the project description. You can
build a package locally using `python3 -m build` to see if it picks up the version from
git. This repository has a very simple `pyproject.toml` demonstrating this.

### PyPI

To be able to publish automatically to PyPI, we'll need to integrate the repository with
PyPI. There's
[documentation](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
on how to do that online. The workflow described on that page is already there, so you
only have to do the part where you create a new PyPI project for your repository. Use
`pypi` for the environment name on the real PyPI, and `testpypi` on TestPyPI. The
pending publishers should then be picked up on your next release and made permanent.

### Sphinx

This repository is set up to render documentation using Sphinx, and the workflows
integrate with that. When making a release on GitHub, a description is required, and
it's nice if that description gives both a brief general overview of the software, and
the latest changes. That overview should also be in the documentation, and the changes
in the `CHANGELOG.md` file.

To accomplish that, the overview is in a separate file `docs/source/overview.txt`. It
gets included into the Sphinx documentation, and it gets read by the release workflows
and put into the description. Note that the Sphinx source is ReStructuredText, while the
release description is MarkDown, so the formatting needs to be valid for both. Stick
with a paragraph or two of plain text, and bullets are also okay, as shown in this
repository.

When you create a new Sphinx `docs` directory using `sphinx-quickstart`, it asks you
whether to put the sources and `conf.py` into `docs/source` or directly into `docs`.
This repository is set up with the former option, if you have the latter then you'll
have to tweak the workflows accordingly. A search-and-replace in
`create_release_description.yml` should do it, and you need to update
`.readthedocs.yaml` to point to the right location of `conf.py`.

### ReadTheDocs

ReadTheDocs can be set up as usualy, but needs a few extra settings to work with
setuptools-scm, which you can take from `.readthedocs.yaml` in the root directory. The
`post_checkout` operation will download the tags, so that `setuptools-scm` knows which
version this is, and the `pre_install` keeps the local changes that RTD makes from
messing up the version number. If you have an `environment.yml` then you'll need to add
that here at the end, because that also gets modified apparently.

Finally, the package needs to be installed before building the documentation for
`conf.py` to be able to pick up the current version from it. See the `get_version()`
function at the top of that file for the implementation.

When you're setting up ReadTheDocs, be sure to enable building the documentatino for
pull requests. That will give you a nice preview of the documentation as it will be
rendered for the next release. Note that the version will be wrong in the preview,
because there's no tag yet at that point, but that should be fixed when the release is
made.

### Zenodo

Zenodo integration can be set up in the usual way, it'll make a Zenodo record
automatically when the GitHub release is made, with the same description.

## Release process

(You may want to put this in the developers' documentation of your repository.)

### Choose the next version number

It should be of the form `x.y.z`, and be larger than all previous versions.

### Update the change log

Edit `CHANGELOG.md` and add `## x.y.z` at the top with a description of the new version.

### Create a release PR

It should merge `develop` into `main`, and be titled `Release x.y.z`. Wait for the
checks to run, then check

- that the release description is what you want (see the comment posted by the workflow)
- that the documentation rendered correctly on ReadTheDocs (click the RTD check)
- that there were no warnings in the package build (click on the "Build distribution"
  check)

If there are any issues, put more commits onto `develop` to fix them; the PR will update
accordingly as you go.

### Merge the release PR

Merge the PR, and check that the `do_release` workflow finished correctly.
Congratulations, you have a release!

