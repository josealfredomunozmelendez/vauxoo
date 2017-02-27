[![Build Status](https://git.vauxoo.com/vauxoo/instance/badges/10.0/build.svg)](https://git.vauxoo.com/vauxoo/instance/pipelines)
[![Coverage Report](https://git.vauxoo.com/vauxoo/instance/badges/10.0/coverage.svg)](https://git.vauxoo.com/vauxoo/instance/commits/10.0)

Modules for vauxoo.com
===

Repositories which we depend from.
---

Read the oca_dependencies.txt file

Deploy locally to hack it
---

1. Install travis2dockerfile in order to create local separate enviroment copy
   of last changes of the instance repository:

    ```bash
    $ sudo pip install travis2docker
    ```
    travis2docker is a python tool created by vauxoo that receive a git repo and
    will create a dockerfile and two scripts that will let you to both build an
    image and create a new container that will have all you need installed and
    configured to create a database (demo or copy of production) of instance
    vauxoo for make functional tests or even for development. As development
    enviroment is the best way you will have to have the most close enviroment
    to the one used in production.

2. travis2docker will require you to set a directory as the root path where the
   new files that you will use be created. For standard we create a directory
   named t2d in your home folder.

    ```bash
    mkdir ~/t2d
    ```

3. Create an alias t2d with some basic configurations to manage travis2docker

    ```bash
    DOCKER_PATH="~/t2d"
    alias t2d="travisfile2dockerfile --root-path=${DOCKER_PATH} --run-extra-args='-it -e LANG=en_US.UTF-8' --add-remote=vauxoo"
    ```

4. Run the command to generate your local environment:

    ```bash
    $ t2d git@git.vauxoo.com:Vauxoo/instance.git 10.0
    ```

5. The t2d script will return you a list of 2 paths. Something similar to:

    ```bash
    ['/home/kathy/t2d/script/git_git.vauxoo.com_Vauxoo_instance.git/10.0/1',
    '/home/kathy/t2d/script/git_git.vauxoo.com_Vauxoo_instance.git/10.0/2']
    ```

    In this case each of this path will have 2 scripts:

    - 10-build.sh: will create the image
    - 20-run.sh: will create the container

6. In order to create a container were you will have a running odoo instance
   you will need to run the two scripts ordered from the path that ends in /2

    ```bash
    /home/kathy/t2d/script/git_git.vauxoo.com_Vauxoo_instance.git/10.0/2/10-build.sh --no-cache
    /home/kathy/t2d/script/git_git.vauxoo.com_Vauxoo_instance.git/10.0/2/20-run.sh --entrypoint=bash
    ```

7. Then you will get inside the container and this can be known when you see
   your prompt with a different style: You will have a name like this

    ```bash
    [root@a458896bf8f5]~/build/vauxoo/instance$
    (10.0) $
    ```

8. There you will need to run the next command that will create the databases
   where you will work by running the odoo server and installing all the
   modules that instance vauxoo needs.

    ```bash
    /entrypoints.sh
    ```

Deploy locally as a copy of production
---

TODO: Create a guide to build with **deployv** and the process to launch the instance with a copy of production for future references.
