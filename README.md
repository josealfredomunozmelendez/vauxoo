Site Services Vauxoo
---

On this branch we created the modules necesaries to init the isntance to work with our erp.

The main idea is create a little how-to commit by commit to know how create our own themes in a clean way.

How add a new theme/features:
---

1. Clone this repository:

    ```
    git clone git@github.com:vauxoo-dev/instance-vauxoo-com.git
    ```

2. Create your own branch locally.

    ```
    git checkout -b 8.0-your_new_feature_theme
    ```

3. Push your first change branch to know you start to work on.

    ```
    git push -u origin 8.0-your_new_feature_theme
    ```

4. Code, clean and test as usual (declaring this folder as part of your addons-path).

5. Add your changes to have them versioned.

    ```
    git add .
    ```

6. Commit your changes.

    ```
    git commit -m "[TAG] module: what you did"
    ```

7. Push your first change branch to know you start to work on.

    ```
    git push -u origin 8.0-your_new_feature_theme
    ```

Style rules on this repository:
---

What is on this repository:
---

What is NOT on this repository:
---

Modules:
---

Building the docker instance
---

0. Install docker.

    ```
    sudo apt-get install docker.io
    sudo adduser your_username docker
    ```

1. Create a hard link to your private key (if you dont push the image your key will be only local)

    ```
    # Inside the folder of this branch
    cd deployment_files/docker_files/
    cp ~/.ssh/id_rsa .
    ```

2. Build the Dockerfile image.

    ```
    docker build -t tag_name:odoo .
    ```

3. After the build is done the image can be run in this way.

    ```
    docker run -p 8069:8069 -d --env DB_SERVER=db_host --env DB_PORT=db_port -t tag_name:odoo /entry_point.py
    ```
4. Watch if docker is running.

    ```
    docker ps
    ```

5. Watch if docker is running.

    ```
    docker stop container_id
    ```

    Optionally you can set the container name with --name option (name must be unique)

    ```
    docker run --name my_odoo_container -p 8069:8069 -d --env DB_SERVER=db_host --env DB_PORT=db_port -t tag_name:odoo /entry_point.py
    ```

You can  run as many images as you want, but be sure to attach them to diferents ports:

    docker run --name my_odoo_container01 -p 8060:8069 -d --env DB_SERVER=db_host --env DB_PORT=db_port -t tag_name:odoo /entry_point.py
    docker run --name my_odoo_container02 -p 8070:8069 -d --env DB_SERVER=db_host --env DB_PORT=db_port -t tag_name:odoo /entry_point.py
    docker run --name my_odoo_container03 -p 8080:8069 -d --env DB_SERVER=db_host --env DB_PORT=db_port -t tag_name:odoo /entry_point.py

Read more about docker run options in: https://docs.docker.com/reference/run/

Building using ansible scripts
---

### Install ansible

Follow this link according to your preferred method http://docs.ansible.com/intro_installation.html, installing using pip is recommended http://docs.ansible.com/intro_installation.html#latest-releases-via-pip

You''ll need **python-dev**, **build-essential** and **sshpass** packages previously installed

### Install docker_facts

Docker_facts is a module developed by Patrick Galbraith (https://github.com/CaptTofu), you can simply run:

    sudo wget -O /usr/share/ansible/cloud/docker_facts https://raw.githubusercontent.com/CaptTofu/ansible/docker_facts/library/cloud/docker_facts

### Running ansible playbook

cd to the **deployment_files/ansible_files** folder and run:

    ansible-playbook site.yml -i inventory --ask-sudo-pass

This will run ansible in your localhost and ask for sudo password (to perform the installation of basic dependencies for running docker containers)

If you need to change ssh_keys to download git and bzr repos just edit them in the *vars.yml* file, read the comments for other configuration options, by deffault it will use the users keys
