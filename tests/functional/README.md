# Functional test scripts

Tests are divided into whether they require a lessee id specification or not. When testing, both `test-lessee-id.sh` and `test-no-lessee-id.sh` should be run.

The tests expect the following project structure: a project called `test1`, with 2 subprojects, called `test1-subproject` and `test1-subproject-1`, A project called `test2`, with 1 subproject called `test2-subproject`, and an admin project, called `admin`.

Currently, the uuid of `test1` is included as a variable called `project_id` at the top of the test scripts, since it is needed to create the dummy node. After making a project called `test1`, that uuid should be changed.

The project authentication info should be included in `clouds.yaml`, so the project for a command can be specified with `--os-cloud` in the scripts.
