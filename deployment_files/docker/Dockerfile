FROM vauxoo/odoo-80-image
MAINTAINER Tulio Ruiz <tulio@vauxoo.com>
RUN adduser --home=/home/odoo --disabled-password --gecos "" --shell=/bin/bash odoo
RUN echo 'root:odoo' |chpasswd
RUN mkdir /home/odoo/.ssh
ADD files/id_rsa /home/odoo/.ssh/id_rsa
RUN chown odoo:odoo -R /home/odoo \
    && chmod 600 /home/odoo/.ssh/id_rsa
ADD files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN pip install gitpython
USER odoo
ENV HOME /home/odoo
ENV ODOO_CONFIG_FILE /home/odoo/.openerp_serverrc
ENV ODOO_FILESTORE_PATH /home/odoo/.local/share/Odoo/filestore
RUN ssh-keyscan github.com > /home/odoo/.ssh/known_hosts \
    && ssh-keyscan bazaar.launchpad.net >> /home/odoo/.ssh/known_hosts \
    && ssh-keyscan launchpad.net >> /home/odoo/.ssh/known_hosts \
    && ssh-keyscan bitbucket.org >> /home/odoo/.ssh/known_hosts
RUN /bin/bash -c "mkdir -p /home/odoo/instance/extra_addons"
RUN bzr lp-login coward
RUN cd /home/odoo/instance && git clone -b 8.0 --single-branch --depth=1 https://github.com/vauxoo/odoo.git odoo
RUN cd /home/odoo/instance/extra_addons \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:vauxoo/odoo-mexico-v2.git oml \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:vauxoo/cms.git cms \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:Vauxoo/odoo-network.git odoo_network \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:oca/server-tools.git server_tools\
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:vauxoo/instance-vauxoo-com.git vauxoo \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:Vauxoo/odoo-ifrs.git odoo_ifrs \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:Vauxoo/odoo-afr.git odoo_afr \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:Vauxoo/odoo-themes.git odoo_themes \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:Vauxoo/addons-vauxoo.git addons_vauxoo \
    && git clone -b 8.0 --single-branch --depth=1 git@github.com:Vauxoo/l10n-mx-invoice-pdf-formats.git 
ADD files/openerp_serverrc /home/odoo/.openerp_serverrc
RUN rm /home/odoo/.ssh/id_rsa
ENV XDG_DATA_HOME /home/odoo/.local/share
USER root
RUN mkdir /external_files
ADD files/supervisord.conf /external_files/supervisord.conf
ADD files/openerp_serverrc /external_files/openerp_serverrc
RUN mkdir -p /var/log/supervisor
RUN wget -q -O /entry_point.py https://raw.githubusercontent.com/Vauxoo/docker_entrypoint/master/entry_point.py \
    && chmod +x /entry_point.py
VOLUME ["/var/log/supervisor", "/home/odoo/.local/share/Odoo", "/home/odoo/.ssh", "/tmp"]
EXPOSE 8069
EXPOSE 8072
CMD /entry_point.py

