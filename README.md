

Website Modules for www.vauxoo.com.
===

On this branch you will find all the set of landing pages, features for cms and interactive elements which built toghether www.vauxoo.com and we decide for one reason or another not make them public.

Reasons because a module can be here.
---

1. The module is our own content to promote a product/service.
2. The feature is to give us a competitive advange and such feature is related to our process with no posibility to be generic.
3. It is a huge PoC which we are not sure it can be public for security/strategic reason.
4. It is a configuration module.
5. It is a overwrite of a formal report with our wired information.
6. It is NOT a website_* module which should be in the frontend on this other [repository](http://github.com/Vauxoo/page).
 
**If you are not on 1 to 6:** please create a module in [addons-vauxoo](https://github.com/addons-vauxoo).

CI Status.
---

[![Build Status](http://runbot.odoo.com/logo.png)](http://runbot.vauxoo.com/runbot/team/vauxoo-20#64)


This tests is what I need "only" tested/mixed with dependency repositories, and tested 1 by 1 modules on this repository in order to be sure they are all installables.


[![Build Status](https://magnum.travis-ci.com/Vauxoo/instance.svg?token=VAty1EWicYm2yKQxZptp&branch=8.0)](https://magnum.travis-ci.com/Vauxoo/instance)


Repositories which we depend from.
---

Read the .travis file

Hacking Our Website
---

Every module can work independent or not, you can find the app installer on [this repository](https://github.com/vauxoo/instance-vauxoo-com),
please check the [README](https://github.com/vauxoo/instance-vauxoo-com/blob/master/README.md) file there for more precise information.

The main idea is create a little how-to commit by commit to know how create our own themes, website features and services offers in a clean way.

How add a new features:
---

0. Clone this repository:

    ```bash
    $ git clone git@github.com:vauxoo/instance-vauxoo-com.git -b 8.0
    $ cd cms
    $ git remote add vauxoo-dev git@github.com:vauxoo-dev/instance-vauxoo-com.git # << to push your changes
    ```

1. Install all dependencies (read travis folder for more information). **note**: You will need some non normal packages (npm and lessc to be precise) when you have v8.0 normally installed, run this command in order to have them all in linux and avoid unexpected runtimes.

    ```bash
    $ cd cms
    $ ./travis/travis_install_cms_nightly
    $ ./travis/travis_install_mx_nightly
    ```

2. Create your own branch locally.

    ```bash
    $ git checkout -b 8.0-your_new_feature_theme
    ```

3. Push your first change branch to know you start to work on.

    ```bash
    $ git push -u origin 8.0-your_new_feature_theme
    ```

4. Prepare your enviroment to work with this repository and the mandatory ones to have all the enviroment ready.

    ```bash
    $ git clone https://github.com/odoo/odoo.git -b 8.0
    $ git clone https://github.com/vauxoo/addons-vauxoo.git -b 8.0
    $ git clone git@github.com:Vauxoo/web.git -b 8.0
    $ git clone git@github.com:Vauxoo/cms.git -b 8.0
    $ git clone git@github.com:oca/server-tools.git -b 8.0
    ```

5. Create a postgres user (only for this work to avoid problems not related to this enviroment).

    ```bash
    $ sudo su postgres
    $ createuser cmsuser -P
    # put your password just (1) for example.
    $ createdb cms -U cmsuser -O cmsuser -T remplate0 -E UTF8
    ```

6. Run the development enviroment.

    ```bash
    $ cd path/to/odoo/odoo
    $ ./openerp-server \
    --addons-path=addons/,../instance-vauxoo-com,../web,../cms,../vauxoo-web,../addons-vauxoo,../server-tools -r \
    cmsuser -w 1 --db-filter=cms \
    -i www_vauxoo_com -d cms
    ```

7. Do your code, and update it passing -u module -d cms (replacing this paramenter above).

8. Before be sure all is ok, we can delete and create db again with -i
   paramenter to ensure all install correctly.

    ```bash
    $ sudo su postgres
    $ dropbd cms
    $ createdb cms -U cmsuser -O cmsuser -T remplate0 -E UTF8
    $ ./openerp-server \
    --addons-path=addons/,../instance-vauxoo-com,../web,../cms,../addons-vauxoo,../server-tools -r \
    cmsuser -w 1 --db-filter=cms \
    -i www_vauxoo_com -d cms
    ```

9. If all is ok installing, please test your enviroment running your code with ‘test-enabled’.

    ```bash
    $ ./openerp-server --addons-path=addons/,../instance-vauxoo-com,../cms -r \
    cmsuser -w 1 --db-filter=cms \
    -i erp_vauxoo_com,www_vauxoo_com -d cms --test-enable
    ```

**Note:**

    This will take a time, just do it before commit your change and make push.

10. Add your changes to have them versioned.

    ```bash
    $ git add .
    ```

11. Commit your changes.

    ```bash
    $ git commit -m "[TAG] module: what you did"
    ```

12. Push your first change branch to know you start to work on.

    ```bash
    $ git push -u vauxoo-dev 8.0-your_new_feature_theme
    ```

13. Make a PR with your changes as you usually do it with graphical interface or using [hub](https://github.com/github/hub).
