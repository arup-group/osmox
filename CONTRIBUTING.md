# Contributing

When it comes to planning in the built environment, we think transparency is critical. The shape and operations of our shared infrastructure and public spaces impacts individuals’ access to employment opportunities, education, social communities, clean air, and safe mobility options. 
We think open source, agent based models are the future for transparent, granular city planning. To help make these models a little bit more realistic, we built OSMOX - a tool for extracting locations and features from OpenStreetMap (OSM) data.

Thank you for considering contributing to OSMOX! We're really excited to hear your opinions on the project and any ideas you may have on how it can be better!

Please note we have a code of conduct. Please follow it in all your interactions with the project.

## Ways to Contribute

There are a number of ways you can contribute to the project. The major two are:
- Submitting a GitHub issue. This could involve:
    - Logging a bug or undesirable behaviour
    - Recording area of possible improvement
    - Requesting a change or addition of a new feature
- Contributing code. Our work is never done, if you have an idea how you could make OSMOX better or if you think you could generalise it:
    - You can outline the new feature or desired behaviour in a GitHub issue and send us an email on [citymodelling@arup.com](mailto:citymodelling@arup.com) 
    to let us know you're willing to work on it. We may invite you for a brief rubber-ducking session to go through your idea in more detail. The aim is to mature your idea with one (or more) OSMOX developers and to flag any possible blocks or implementation issues to be aware of.
    - Please follow advice below on Contributing Code, working in a branch and the Pull Request process.
    - You may continue to, and are encouraged to, keep in touch and reach out to us throughout your development work.

See this helpful site on [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/) for more ideas on how you could contribute. Get in touch with us via email [citymodelling@arup.com](mailto:citymodelling@arup.com).

## Submitting Issues

If you have an idea for an enhancement, a change or addition of new feature or behaviour for OSMOX or a record of a bug you can communicate this to us in detail by sending us an email on [citymodelling@arup.com](mailto:citymodelling@arup.com) 
 
A good issue will outline the problem in a full written format. It is helpful to include screenshots, especially to highlight any physical issues with the network. It is also helpful to include why you think the new feature would be useful, what problem is it solving and whether there is a real-world cases study that would benefit from this 
improvement.

In case of bugs, please provide the full error message, the OS and 
information about the environment in which the process had been ran. It is also helpful to include a small 
(if possible) set of data on which the problem can be recreated---at the very least, a thorough description of the input data should be included.

## Contributing Code - Pull Request Process

1. All new work is done in a branch taken from master, details can be found here:
[feature branch workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow)
2. Ensure your work is covered by unit tests to the required percentage level. This script 
[`scripts/code-coverage.sh`](https://github.com/arup-group/osmox/blob/master/scripts/code-coverage.sh)
 will help both in checking that the coverage level is satisfied and investigating places in code that have not been covered by the tests (via an output file `reports/coverage/index.html` which can be viewed in a browser).
3. Provide [docstrings](https://www.python.org/dev/peps/pep-0257/) for new methods.
4. Perform linting locally using ```flake8 . --max-line-length 120 --count  --show-source --statistics --exclude=scripts,tests```
5. Add or update dependencies in `requirements.txt` if applicable.
6. Ensure the CI build pipeline (Actions tab in GitHub) completes successfully for your branch. The pipeline performs automated `PEP8` checks and runs unit tests in a fresh environment, as well as installation of all dependencies.
7. You may use example data already in `example_data` directory of this repo, or add more (small amount of) data to it to show off your new features.
8. Add section in the `README.md` which shows usage of your new feature.
9. Submit your Pull Request (see [GitHub Docs on Creating a Pull Request](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)),
 describing the feature, linking to any relevant GitHub issues and request review from at 
least two developers. (Please take a look at latest commits to find out which developers you should request review from).
10. You may merge the Pull Request in once you have the sign-off of two other developers, or if you 
do not have permission to do that, please request one of the reviewers to merge it for you.

## Attribution

The Contribution Guide was adapted from [PurpleBooth's Template](https://gist.github.com/PurpleBooth/b24679402957c63ec426).