[![Build Status](https://git.vauxoo.com/vauxoo/pima/badges/10.0/build.svg)](https://git.vauxoo.com/vauxoo/pima/pipelines)
[![Coverage Report](https://git.vauxoo.com/vauxoo/pima/badges/10.0/coverage.svg)](https://vauxoo.pages.vauxoo.com/instance/11.0/coverage)

Modules for vauxoo.com
===

Repositories which we depend from.
---

Read the oca_dependencies.txt file.

Deploy locally to hack it
---

1. Install travis2docker in order to a create local environment (docker
   container) copy of last changes on the instance repository:

    ```bash
    $ sudo pip install travis2docker
    ```
    `travis2docker` is a python tool created by vauxoo that receive a git repo
    and will create a dockerfile and two scripts that will let you to both
    build an image and create a new container that will have all you need
    installed and configured to create a database (demo or copy of production)
    of instance vauxoo for make functional tests or even for do new developments:
    as development enviroment is the best way for you to have an evironment
    close to the one used in production.

2. You will know that you properly install travis2docker when you are able to
   run travis2dockerfile command line command.

    ```bash
    $ travisfile2dockerfile
    usage: travisfile2dockerfile [-h] [--docker-user DOCKER_USER]
                                 [--docker-image DEFAULT_DOCKER_IMAGE]
                                 [--root-path ROOT_PATH] [--add-remote REMOTES]
                                 [--exclude-after-success]
                                 [--run-extra-args RUN_EXTRA_ARGS]
                                 [--run-extra-cmds [RUN_EXTRA_CMDS [RUN_EXTRA_CMDS ...]]]
                                 [--build-extra-args BUILD_EXTRA_ARGS]
                                 [--build-extra-cmds [BUILD_EXTRA_CMDS [BUILD_EXTRA_CMDS ...]]]
                                 [--travis-yml-path TRAVIS_YML_PATH] [--no-clone]
                                 [--add-rcfile ADD_RCFILE] [-v]
                                 git_repo_url git_revision
    ```

    In order to use travis2dockerfile it will require you to set a directory as
    the root path where the new files used to create the container will be
    adeed. As a standard this folter is always named t2d and is inside of
    you home folder. This directory need to be created manually by you, you can
    use the next command.

    ```bash
    mkdir ~/t2d
    ```

    Also, in order to use travis2dockerfile easly, we highly recommend that you
    create an alias to make the command shorter and to define by default some
    arguments that are required so you will not have to add this parameters by
    hand everytime that you run travis2tocker

    ```bash
    DOCKER_PATH="~/t2d"
    alias t2d="travisfile2dockerfile --root-path=${DOCKER_PATH} --run-extra-args='-it -e LANG=en_US.UTF-8' --add-remote=vauxoo"
    ```
3. Now we can use the t2d command. This will be accomplish by using the next
   command line:

    ```bash
    $ t2d git@git.vauxoo.com:vauxoo/pima.git 10.0
    ```

    The resulf after run this t2d script will be a log that have a list of
    local paths, in instance vauxoo case, will have a list of 2 pths

    ```bash
    ['/home/user/t2d/script/git_git.vauxoo.com_Vauxoo_instance.git/10.0/1',
    '/home/user/t2d/script/git_git.vauxoo.com_Vauxoo_instance.git/10.0/2']
    ```

    The first one /1 will reproduce the lint tests that are running by the CI,
    and the second one /2 will let us to create the enviroment to be able to
    create databases and have access to review or edit the related branches.
    Each path will have 2 scripts:

        - 10-build.sh: will create the image (docker build with a pre
          configured arguments)
        - 20-run.sh: will create the container (docker run with a pre
          configured arguments)

4. The next step is to run the last mentioned scripts, we highly recommend to
   add the next extra arguments.

    ```bash
    /home/user/t2d/script/git_git.vauxoo.com_Vauxoo_instance.git/10.0/2/10-build.sh --no-cache
    /home/user/t2d/script/git_git.vauxoo.com_Vauxoo_instance.git/10.0/2/20-run.sh --entrypoint=bash
    ```

5. After the last script is finish you will notice that your prompt has change,
   this happens because you are inside your new container. I will look something
   like this:

    ```bash
    [root@a458896bf8f5]~/build/vauxoo/pima$
    (10.0) $
    ```

    where a458896bf8f5 is your container id. Now you have access to the
    development environment that have clone of the repositories used for
    vauxoo instance:

        - main repository will be ALWAYS inside /root/build/vauxoo/pima
        - the oca dependencies repositories will be inside /root folder.

    The remotes has been already configured so can start working to create
    new branches in vauxoo-dev,

6. In order to test the demo database or to create new functionalities you
   will need to have, at least, a demo database running to locally tests
   your new changes. In order to accomplish this you will need to run the next
   command inside your container

    ```bash
    /entrypoints.sh
    ```

    This will run odoo server and will create two databases: openerp_template
    and openerp_test. The one you will use for development and tests is
    openerp_test: this one has installed all the modules required to make
    vauxoo instance run.

7. After this script is finish you can run the odoo server again on demmand
   using the next command:

    ```bash
    /root/odoo-11.0/odoo-bin -d openerp_test --db-filter=openerp_test
    ```

8. Last but not least, you will need to have more than one console view to your
   container, one for run the odoo server, another for use vim to add the changes
   to the code and to use the git commands. You can have several connections to
   your container with multiple docker exec, or, you can learn to use tmux in
   order to have only one connection to the container and have any amount of
   sub consoles you need.

    > **NOTE:** I personally recommend to have use tmux using the next tabs:
    >
    ```bash
    0: server
    1: git
    2: vim
    3; search
    ```

Deploy locally as a copy of production
---

TODO: Create a guide to build with **deployv** and the process to launch the instance with a copy of production for future references.
