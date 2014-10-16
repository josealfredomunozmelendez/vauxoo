FROM quay.io/ruiztulio/odoo-base-image:develop
MAINTAINER Tulio Ruiz <tulio@vauxoo.com>
RUN adduser --home=/home/odoo --disabled-password --gecos "" --shell=/bin/bash odoo

RUN echo 'root:odoo' |chpasswd

RUN mkdir /home/odoo/.ssh
ADD id_rsa /home/odoo/.ssh/id_rsa
RUN chown odoo:odoo -R /home/odoo \
    && chmod 600 /home/odoo/.ssh/id_rsa

USER odoo
RUN ssh-keyscan github.com > /home/odoo/.ssh/known_hosts \
    && ssh-keyscan launchpad.net >> /home/odoo/.ssh/known_hosts \
    && ssh-keyscan bitbucket.org >> /home/odoo/.ssh/known_hosts
RUN /bin/bash -c "mkdir -p /home/odoo/instance/{config,extra_addons}"
RUN cd /home/odoo/instance && git clone -b 8.0 --single-branch https://github.com/odoo/odoo.git odoo
RUN cd /home/odoo/instance/extra_addons \
    && git clone -b oml-8-dev-julio --single-branch git@bitbucket.org:julioserna/oml-v2-8-dev-julio.git oml \
    && git clone -b 8.0 --single-branch git@github.com:vauxoo-dev/cms.git cms \
    && git clone -b 8.0 --single-branch git@github.com:Vauxoo/odoo-network.git odoo_network \
    && git clone -b master --single-branch git@github.com:vauxoo/server-tools.git server_tools\
    && git clone -b 8.0 --single-branch git@github.com:vauxoo-dev/instance-vauxoo-com.git instance_vauxoo_com \
    && git clone -b 8.0 --single-branch git@github.com:Vauxoo/odoo-ifrs.git odoo_ifrs \
    && git clone git@bitbucket.org:julioserna/pdf-format.git pdf_format \
    && bzr branch lp:addons-vauxoo addons_vauxoo
ADD files/odoo.conf /home/odoo/instance/config/
ADD files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN rm /home/odoo/.ssh/id_rsa
RUN mkdir -p /home/odoo/.local/share
ENV XDG_DATA_HOME /home/odoo/.local/share

USER root
RUN mkdir /external_files
ADD files/odoo.conf /external_files/odoo.conf
ADD files/supervisord.conf /external_files/supervisord.conf
RUN wget -O /entry_point.py https://raw.githubusercontent.com/vauxoo-dev/docker_entrypoint/master/entry_point.py \
    && chmod +x /entry_point.py
RUN mkdir -p /var/log/supervisor
VOLUME ["/var/log/supervisor", \
        "/home/odoo/instance/odoo/openerp/filestore", \
        "/home/odoo/instance/odoo/config"]

EXPOSE 8069
CMD /entry_point.py
#ENTRYPOINT ["/entry_point.py"]
